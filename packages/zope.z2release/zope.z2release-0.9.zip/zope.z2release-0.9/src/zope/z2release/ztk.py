import os
import sys
import urllib

BASE_URL = 'http://svn.zope.org/*checkout*/zopetoolkit/'


def main():
    if len(sys.argv) != 3:
        print('Usage: ztk_kgs <tag-name> <destination-dirname>')
        print('Example: ztk_kgs tags/1.1.2 '
            '/var/www/download.zope.org/zopetoolkit/index/1.1.2/')
        sys.exit(1)

    tag = sys.argv[1]
    dirname = sys.argv[2]
    if not os.path.exists(dirname):
        print('Creating index directory: %s' % dirname)
        os.makedirs(dirname)

    versions_url = BASE_URL + '%s/ztk-versions.cfg' % tag
    print('Fetching %s' % versions_url)
    response = urllib.urlopen(versions_url)
    if response.code == 200:
        data = response.read()
        version_file = os.path.join(dirname, 'ztk-versions.cfg')
        with open(version_file, 'w') as fd:
            fd.write(data)
    else:
        print('Failed to fetch %s' % versions_url)

    if tag.split('/')[-1].startswith('2'):
        # ZTK 2.0+ no longer have a zopeapp-versions file
        return

    app_versions_url = BASE_URL + '%s/zopeapp-versions.cfg' % tag
    print('Fetching %s' % app_versions_url)
    response = urllib.urlopen(app_versions_url)
    if response.code == 200:
        data = response.read()
        app_version_file = os.path.join(dirname, 'zopeapp-versions.cfg')
        with open(app_version_file, 'w') as fd:
            fd.write(data)
    else:
        print('Failed to fetch %s' % app_versions_url)


if __name__ == '__main__':
    main()
