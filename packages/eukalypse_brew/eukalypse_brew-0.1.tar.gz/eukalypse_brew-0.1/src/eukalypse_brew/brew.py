import requests
from lxml import etree
from xml.dom import minidom
from furl import furl


class Brew:

    sitemap_schema_url = 'http://www.sitemaps.org/schemas/sitemap/0.9'

    def __init__(self, domain):
        self.domain = domain
        self.urls_exist = ['/']
        self.urls_sitemap = ['sitemap.xml']
        self.urls_robots = ['robots.txt']

    def _create_url(self, url):
        f = furl(self.domain)
        f.path = url
        return f.url

    def check_exist(self):
        for url in self.urls_exist:
            response = requests.get(self._create_url(url))
            if not response.status_code == 200:
                raise Exception("url ({0}) response not 200".format(url))

    def check_sitemap(self):
        for url in self.urls_sitemap:
            response = requests.get(self._create_url(url))
            if not response.status_code == 200:
                raise Exception("sitemap({0}) response not 200".format(url))
            r = requests.get(self.sitemap_schema_url + '/siteindex.xsd')
            if not r.status_code == 200:
                raise Exception("sitemap schema ({0}) response not 200".format(url))

            if r.status_code == 200:
                xmlschema_doc = etree.XML(r.content)
                xmlschema = etree.XMLSchema(xmlschema_doc)
                xmldoc = etree.XML(response.content)
                if not xmlschema.validate(xmldoc):
                    raise Exception("sitemap does not validate")

            #if the xml is valid but can not get parsed, this will raise an exception
            minidom.parseString(response.content)

    def check_robots(self):
        for url in self.urls_robots:
            response = requests.get(self._create_url(url))
            if not response.status_code == 200:
                raise Exception("robots({0}) response not 200".format(url))
            for line in response.content.splitlines():
                if not line.startswith(('User-agent: ', 'Disallow: ', 'Allow: ')):
                    raise Exception("robots.txt ({0}) has strange content".format(url))

    def check_all(self):
        """ find all functions starting with "check_" and call them"""
        #find out the name of the current function so that we can ignore it later
        import inspect
        name_of_current_function = inspect.stack()[0][3]

        for fname in dir(self):
            if fname.startswith('check_') and fname != name_of_current_function:
                f = getattr(self, fname)
                f()
