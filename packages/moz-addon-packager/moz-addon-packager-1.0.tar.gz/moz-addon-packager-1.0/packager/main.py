import argparse
import os
import uuid
from xml.sax.saxutils import escape

from jinja2 import Environment, FunctionLoader


RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'resources')
FIREFOX_GUID = '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}'


def main():
    parser = argparse.ArgumentParser('Mozilla Add-on Packager')

    parser.add_argument('output_path',
                        help='The path at which to place the final product')
    parser.add_argument('-f',
                        '--features',
                        help='A space-delimited list of features to include.')

    parser.add_argument('--id',
                        required=True,
                        help='The <em:id> value of the add-on.')
    parser.add_argument('--version',
                        required=True,
                        help='The <em:version> value of the add-on.')
    parser.add_argument('--name',
                        required=True,
                        help='The <em:name> value of the add-on.')
    parser.add_argument('--description',
                        required=False,
                        help='A description of your add-on.')
    parser.add_argument('--author-name',
                        required=True,
                        help="The name of the add-on's author.")
    parser.add_argument('--contributors',
                        required=False,
                        help='A comma-delimited list of contributor names.')
    parser.add_argument('--targetapps',
                        required=True,
                        help='A semicolon-delimited list of target '
                             'application GUIDs, min, and max versions '
                             '(separated by commas).')

    args = parser.parse_args()

    def parse_targetapps(raw):
        for targetapp in raw.split(';'):
            guid, min_ver, max_ver = targetapp.split(',')
            yield {'guid': guid,
                   'min_ver': min_ver,
                   'max_ver': max_ver}

    packager({'id': args.id,
              'version': args.version,
              'name': args.name,
              'description': args.description,
              'author_name': args.author_name,
              'contributors': '\n'.join(args.contributors.split(',')) if
                                  args.contributors else '',
              'targetapplications': list(parse_targetapps(args.targetapps)),
              'uuid': uuid.uuid4().hex,
              'slug': _slugify(args.name)},
             xpi_path=args.output_path,
             features=set(args.features.split()) if args.features else set())


def _slugify(value):
    """Return a simple slugified value."""
    value = value.lower().strip()
    value = value.replace(' ', '_')
    return ''.join(c for c in value if c.isalnum() or c == '_')


def packager(data, xpi_path, features):
    """
    Package an add-on from input data. The resulting package will be saved as
    xpi_path.

    Format:
        - id : <em:id> value
        - version : <em:version>
        - name : <em:name>
        - description : <em:description>
        - author_name : <em:author>
        - contributors : \n-delimited list of contributors
        - targetapplications : Dict in the form of:
            {
            "min_ver": "3.6",
            "max_ver": "6.0a1",
            "guid": "...",
            "enabled": True # Must be True!
            }
        - uuid : A UUID value that is unique to this package
        - slug : A slug value based on the name which will be used as a package
                 identifier.

    xpi_path should be the file path to build the XPI at.

    features should be a set containing string names of each of the features to
        include.
    """

    # Instantitate the XPI Manager
    from validator.xpi import XPIManager
    xpi = XPIManager(xpi_path, mode='w')

    is_firefox = any(app['guid'] == FIREFOX_GUID for
                     app in data['targetapplications'])

    xpi.write('install.rdf', build_installrdf(data, features))
    xpi.write('chrome.manifest',
              build_chrome_manifest(data, features, is_firefox))
    _write_resource('defaults/preferences/prefs.js', xpi, data)
    _write_resource('chrome/content/overlay.js', xpi, data)
    _write_resource('chrome/skin/overlay.css', xpi, data)
    _write_resource('chrome/locale/en-US/overlay.dtd', xpi, data)
    _write_resource('chrome/locale/en-US/overlay.properties', xpi, data)

    if 'about_dialog' in features:
        _write_resource('chrome/content/about.xul', xpi, data)
        _write_resource('chrome/locale/en-US/about.dtd', xpi)

    if 'preferences_dialog' in features:
        _write_resource('chrome/content/options.xul', xpi, data)
        _write_resource('chrome/locale/en-US/options.dtd', xpi, data)

    if 'toolbar_button' in features:
        _write_resource('chrome/skin/toolbar-button.png', xpi)

    if 'sidebar_support' in features:
        _write_resource('chrome/content/ff-sidebar.js', xpi)
        _write_resource('chrome/content/ff-sidebar.xul', xpi, data)

    # Multiple features require ff-overlay.xul
    if any(feature in features for feature in ('toolbar',
                                               'toolbar_button',
                                               'context_menu_command',
                                               'main_menu_command',
                                               'sidebar_support')):
        xpi.write('chrome/content/ff-overlay.xul',
                  build_ffoverlay_xul(data, features, is_firefox))
        _write_resource('chrome/content/ff-overlay.js', xpi, data)

    xpi.zf.close()
    return xpi_path


def _get_path(filename):
    return os.path.join(RESOURCES_PATH, filename)


def _get_resource(filename, data=None):
    """
    A shortcut to get the contents of a file.

    If data is specified, each of the keys will be replaced (in the format of
    %key% from the contents of the file) with the value from data.
    """
    resource = open(_get_path(filename))
    output = _apply_data(resource.read(), filename, data)

    resource.close()
    return output.strip()


def _apply_data(blob, filename, data=None):
    """Apply a dict of variables to the file as a basic template."""
    if data:
        # JS files are incompatible with .format() because of the curly
        # braces. Instead, named string formatting is used (%(foo)s)
        if not filename.endswith(('.js', '.css')):
            blob = blob.format(**data)
        else:
            blob = blob % data

    return blob


def _write_resource(filename, xpi, data=None):
    """A shortcut to write a resource to an XPI."""
    if not data:
        xpi.write_file(filename, _get_path(filename))
    else:
        xpi.write(filename, _get_resource(filename, data))


def build_installrdf(data, features):

    template = JINJA_ENV.get_template('install.rdf')

    contributors = (data['contributors'].split('\n') if
                    data['contributors'] else
                    [])
    return template.render(
            id=data['id'],
            version=data['version'],
            name=data['name'],
            description=data['description'],
            author_name=data['author_name'],
            contributors=contributors,
            targetapplications=data['targetapplications'],
            preferences_dialog='preferences_dialog' in features,
            about_dialog='about_dialog' in features,
            slug=data['slug'])


def build_chrome_manifest(data, features, is_firefox=False):

    chrome_manifest = [_get_resource('chrome.manifest', data)]
    if is_firefox:
        chrome_manifest.append(('overlay\t'
                                'chrome://browser/content/browser.xul\t'
                                'chrome://%s/content/ff-overlay.xul') %
                                    data['slug'])

    if 'toolbar_button' in features:
        chrome_manifest.append(
                ('style\t'
                 'chrome://global/content/customizeToolbar.xul\t'
                 'chrome://%s/skin/overlay.css') % data['slug'])

    return '\n'.join(chrome_manifest)


def build_ffoverlay_xul(data, features, is_firefox=False):
    """Build the ff-overlay.xul file."""

    template = JINJA_ENV.get_template('chrome/content/ff-overlay.xul')
    return template.render(features=features,
                           is_firefox=is_firefox,
                           slug=data['slug'])


JINJA_ENV = Environment(loader=FunctionLoader(_get_resource))

if __name__ == '__main__':
    main()

