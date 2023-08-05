import requests
from bs4 import BeautifulSoup


class Github:
    """
    sanity checks for projects on Github
    """

    readme_locator = "#readme .entry-content"

    def __init__(self, user, project):
        self.user = user
        self.project = project

    def _create_url(self, path=None):
        return "http://github.com/{0}/{1}/".format(self.user, self.project)

    def check_readme(self):
        """Checks if the README of a project on github got any broken links in a tags or images"""
        response = requests.get(self._create_url())
        if not response.status_code == 200:
            raise Exception("url ({0}) response not 200".format(self._create_url()))
        soup = BeautifulSoup(response.content)
        a_elements = soup.find(id="readme").find_all('a')
        img_elements = soup.find(id="readme").find_all('img')
        for a_element in a_elements:
            link = a_element.get('href')
            if not link.startswith('#') and not link == self._create_url():
                response = requests.get(link)
                if not response.status_code == 200:
                    raise Exception("url ({0}) response {1}".format(link, response.status_code))

        for img_element in img_elements:
            link = img_element.get('src')
            if link:
                response = requests.get(link)
                if not response.status_code == 200:
                    raise Exception("url ({0}) response is {1}".format(link, response.status_code))
            else:
                raise Exception("found image without or empty src attribute {0}".format(img_element))
