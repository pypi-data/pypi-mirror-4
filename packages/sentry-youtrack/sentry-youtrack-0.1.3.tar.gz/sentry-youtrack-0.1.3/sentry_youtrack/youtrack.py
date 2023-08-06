import requests
from BeautifulSoup import BeautifulStoneSoup


class YouTrackClient(object):

    LOGIN_URL = '/rest/user/login'
    PROJECT_URL = '/rest/admin/project/<project_id>'
    PROJECTS_URL = '/rest/project/all'
    CREATE_URL = '/rest/issue'
    CUSTOM_FIELD_VALUES = '/rest/admin/customfield/<param_name>/<param_value>'

    API_KEY_COOKIE_NAME = 'jetbrains.charisma.main.security.PRINCIPAL'

    def __init__(self, url, username=None, password=None, api_key=None):
        self.url = url.rstrip('/') if url else ''
        if api_key is None:
            self._login(username, password)
        else:
            self.cookies = {self.API_KEY_COOKIE_NAME: api_key}
            self.api_key = api_key

    def _login(self, username, password):
        credentials = {
            'login': username,
            'password': password
        }
        url = self.url + self.LOGIN_URL
        self._request(url, data=credentials, method='post')
        self.cookies = self.response.cookies
        self.api_key = self.cookies.get(self.API_KEY_COOKIE_NAME)

    def _request(self, url, data=None, method='get'):
        if method not in ['get', 'post']:
            raise AttributeError("Invalid method %s" % method)

        kwargs = {
            'url': url,
            'data': data,
        }
        if hasattr(self, 'cookies'):
            kwargs['cookies'] = self.cookies

        if method == 'get':
            self.response = requests.get(**kwargs)
        elif method == 'post':
            self.response = requests.post(**kwargs)
        self.response.raise_for_status()
        return BeautifulStoneSoup(self.response.text)

    def get_project_name(self, project_id):
        url = self.url + self.PROJECT_URL.replace('<project_id>', project_id)
        soap = self._request(url, method='get')
        return soap.project['name']

    def get_projects(self):
        url = self.url + self.PROJECTS_URL
        soap = self._request(url, method='get')
        return soap.projects

    def get_priorities(self):
        values = self.get_custom_field_values('bundle', 'Priorities')
        return [item.text for item in values.enumeration]

    def get_issue_types(self):
        values = self.get_custom_field_values('bundle', 'Types')
        return [item.text for item in values.enumeration]

    def get_custom_field_values(self, name, value):
        url = self.url + (self.CUSTOM_FIELD_VALUES
                          .replace("<param_name>", name)
                          .replace('<param_value>', value))

        response = requests.get(url, cookies=self.cookies)
        return BeautifulStoneSoup(response.text)

    def create_issue(self, data):
        url = self.url + self.CREATE_URL
        soap = self._request(url, data=data, method='post')
        return soap.issue
