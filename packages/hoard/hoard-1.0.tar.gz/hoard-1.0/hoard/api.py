import json
import os

import requests


class NoDeploymentVars(Exception): pass
class EnvDoesNotExist(Exception): pass
class ProjectDoesNotExist(Exception): pass


def get_token(url, username, password):
    payload = {'username': username, 'password': password}
    r = requests.post(os.path.join(url, 'login'), data=payload)
    r.raise_for_status()
    return r.json()['token']


class API(object):
    def __init__(self, url, token):
        self.headers = {
            'Authorization': 'Token {0}'.format(token),
            'Content-Type': 'application/json',
        }
        self.url = url

    def _delete(self, url):
        return requests.delete(os.path.join(self.url, url), headers=self.headers)

    def _get(self, url):
        return requests.get(os.path.join(self.url, url), headers=self.headers)

    def _list_or_detail(self, url, name):
        if name:
            url = os.path.join(url, name)

        r = self._get(url)
        r.raise_for_status()
        return r.json()

    def _put(self, url, payload):
        return requests.put(os.path.join(self.url, url), headers=self.headers, data=json.dumps(payload))

    def envs(self, name=None):
        url = 'envs'
        return self._list_or_detail(url, name)

    def pairs(self, project, env, payload=None):
        url = os.path.join('projects', project, 'envs', env)

        if payload:
            r = self._put(url, payload)
        else:
            r = self._get(url)

            if r.ok:
                if not r.json():
                    raise NoDeploymentVars
                return r.json()

        if r.status_code == requests.codes.not_found:
            try:
                projects = self.projects(project)
            except requests.exceptions.HTTPError:
                raise ProjectDoesNotExist
            else:
                if not env in projects['envs']:
                    raise EnvDoesNotExist

        r.raise_for_status()

    def projects(self, name=None):
        url = 'projects'
        return self._list_or_detail(url, name)

    def rm(self, project, env, key):
        url = os.path.join('projects', project, 'envs', env, 'keys', key)
        r = self._delete(url)

        if r.status_code == requests.codes.not_found:
            try:
                projects = self.projects(project)
            except requests.exceptions.HTTPError:
                raise ProjectDoesNotExist
            else:
                if not env in projects['envs']:
                    raise EnvDoesNotExist

        r.raise_for_status()

