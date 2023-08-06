import os

from werckercli.decorators import login_required
from werckercli.git import get_remote_options
from werckercli.cli import get_term, puts
from werckercli.client import Client
from werckercli.printer import print_hr, print_line, store_highest_length
from werckercli.config import get_value, set_value, VALUE_PROJECT_ID


@login_required
def project_list(valid_token=None):

    if not valid_token:
        raise ValueError("A valid token is required!")

    c = Client()

    response, result = c.get_applications(valid_token)

    header = ['name', 'author', 'status', 'followers', 'url']
    props = [
        'name',
        'author',
        'status',
        'totalFollowers',
        'url'
    ]

    max_lengths = []

    for i in range(len(header)):
        max_lengths.append(0)

    store_highest_length(max_lengths, header)

    puts("Found %d result(s)...\n" % len(result))
    for row in result:
        store_highest_length(max_lengths, row, props)

    result = sorted(result, key=lambda k: k['name'])
    print_hr(max_lengths, first=True)
    print_line(max_lengths, header)
    print_hr(max_lengths)

    for row in result:
        print_line(max_lengths, row, props)
    print_hr(max_lengths)


@login_required
def project_link(valid_token=None):
    if not valid_token:
        raise ValueError("A valid token is required!")

    puts("Searching for git remote information... ")
    options = get_remote_options(os.curdir)

    puts("Retreiving list of applications...")
    c = Client()

    response, result = c.get_applications(valid_token)

    for option in options:
        for app in result:
            if app['url'] == option.url:
                set_value(VALUE_PROJECT_ID, app['id'])
                return


@login_required
def project_check_repo(valid_token=None, failure_confirmation=False):
    if not valid_token:
        raise ValueError("A valid token is required!")

    term = get_term()

    puts("Checking permissions...")

    while(True):

        c = Client()
        code, response = c.check_permissions(
            valid_token,
            get_value(VALUE_PROJECT_ID)
        )

        if response['success'] is True:
            if response['data']['hasAccess'] is True:
                puts("Werckerbot has access")
                break
            else:
                if "details" in response['data']:
                    # puts
                    puts(
                        term.yellow("Warning: ") +
                        response['data']['details']
                    )

                if failure_confirmation is True:
                    from werckercli import prompt

                    exit = not prompt.yn(
                        "Please make sure the permissions on the\
 project are correct, do you want wercker to check the permissions again?",
                        default="y"
                    )
                else:
                    exit = True

                if exit:
                    break


@login_required
def project_build(valid_token=None):
    if not valid_token:
        raise ValueError("A valid token is required!")

    puts("Triggering build")

    c = Client()
    code, response = c.trigger_build(valid_token, get_value(VALUE_PROJECT_ID))

    if response['success'] is False:
        puts("Unable to trigger a build on the default/master branch")
        if "errorMessage" in response:
            puts(term.red("Error: ") + response['errorMessage'])
    else:
        puts("A new build has been created")
    # print code, response
