import os
import urlparse

from ConfigParser import RawConfigParser as ConfigParser


class CasePreservingConfigParser(ConfigParser):

    def optionxform(self, option):
        return option  # don't flatten case!


def write_index(server, package, version, dirname):
    if '-' in package:
        exists = server.search(dict(name=package))
        if not exists:
            package = package.replace('-', '_')

    print('Package %s==%s' % (package, version))
    dest_dir = os.path.join(dirname, package)
    if os.path.exists(dest_dir):
        print("Don't override package %s==%s" % (package, version))
        return

    os.makedirs(dest_dir)
    index_html = os.path.join(dest_dir, 'index.html')

    with open(index_html, 'w') as fp:
        fp.write('<html><body>')
        lst = server.release_urls(package, version)
        if lst:
            # package hosted on PyPI
            for d in lst:
                link = '<a href="%s">%s</a>' % (d['url'], d['filename'])
                fp.write(link + '<br/>')
        else:
            # for externally hosted packages we need to rely on the
            # download_url metadata
            rel_data = server.release_data(package, version)
            download_url = rel_data['download_url']
            if download_url == 'UNKNOWN':
                raise RuntimeError(
                    'Incorrect download_url for package %s' % package)
            filename = os.path.basename(urlparse.urlparse(download_url)[2])
            link = '<a href="%s">%s</a>' % (download_url, filename)
            fp.write(link + '<br/>')

        fp.write('</body></html>')
