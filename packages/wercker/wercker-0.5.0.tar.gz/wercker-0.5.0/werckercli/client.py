import json
import requests

from werckercli.cli import puts
from werckercli.config import get_value, VALUE_WERCKER_URL

PATH_BASIC_ACCESS_TOKEN = 'oauth/basicauthaccesstoken'
PATH_GET_TEMPLATES = 'project/gettemplates'
PATH_CREATE_PROJECT = 'project/create'
PATH_BUILD_PROJECT = 'projects/triggerbuild'
PATH_CREATE_DEPLOYTARGET = 'deploytargets/create'
PATH_DEPLOY_TARGETS_BY_PROJECT = 'deploytargets/byproject'
PATH_GET_APPLICATIONS = 'applications'
PATH_DEPLOY = 'deploy'
PATH_CHECK_PERMISSIONS = 'application/{projectId}/validateAccess'
PATH_GET_BUILDS = 'project/{projectId}/builds'
# PATH_PROJECT_LIST = 'project/gettemplates'


class LegacyClient():
    wercker_url = get_value(VALUE_WERCKER_URL)
    api_version = '1.0'

    def __init__(self):
        self.wercker_url = get_value(VALUE_WERCKER_URL)

    def do_post(self, path, data):
        """Make the request to the server."""

        url = self.wercker_url + '/api/' + self.api_version + '/' + path

        data_string = json.dumps(data)

        puts("communicating with %s ..." % self.wercker_url)

        result = requests.post(
            url,
            data=data_string,
            headers={'Content-Type': 'application/json'})
        puts("done...")

        return result.status_code, json.loads(result.text)

    def request_oauth_token(self, username, password, scope='cli'):
        """Request oauth token"""

        return self.do_post(
            PATH_BASIC_ACCESS_TOKEN,
            {
                'username': username,
                'password': password,
                'oauthscope': scope
            })

    def create_project(self, git_url, source_control, token):
        return self.do_post(
            PATH_CREATE_PROJECT,
            {
                'gitUrl': git_url,
                # 'userName': user,
                # 'projectName': project,
                'sourceControl': source_control,
                'token': token,
            })

    def create_deploy_target(self, token, project, deploy_name, heroku_token):
        return self.do_post(
            PATH_CREATE_DEPLOYTARGET,
            {
                'token': token,
                'projectId': project,
                'appName': deploy_name,
                'apiKey': heroku_token,
            }
        )

    def get_deploy_targets_by_project(self, token, project):
        return self.do_post(
            PATH_DEPLOY_TARGETS_BY_PROJECT,
            {
                'token': token,
                'projectId': project
            }
        )

    def trigger_build(self, token, project):
        return self.do_post(
            PATH_BUILD_PROJECT,
            {
                'token': token,
                'projectId': project
            })

    def do_deploy(self, token, build, deploy_target):
        return self.do_post(
            PATH_DEPLOY,
            {
                'token': token,
                'targetId': deploy_target,
                'buildId': build
            })


class Client(LegacyClient):
    wercker_url = get_value(VALUE_WERCKER_URL)

    def do_get(self, path, data):
        url = self.wercker_url + "/api/" + path

        # data_string = json.dumps(data)

        result = requests.get(
            url,
            params=data)

        return result.status_code, json.loads(result.text)

    def get_applications(self, token):
        return self.do_get(PATH_GET_APPLICATIONS, {'token': token})

    def get_builds(self, token, project):
        return self.do_get(
            PATH_GET_BUILDS.format(projectId=project),
            {'token': token}
        )

    def check_permissions(self, token, project):

        return self.do_get(
            PATH_CHECK_PERMISSIONS.format(projectId=project),
            {'token': token}
        )

    # def do_deploy(self, token, build, target):

    #     return self.
