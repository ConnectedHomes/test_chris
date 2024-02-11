import json
import responses

# from digital_Web_CI_Stack.python_lambdas.lib.slack.slack import POST_MESSAGE_URL
# from digital_Web_CI_Stack.python_lambdas.lib.slack.slack import UPDATE_MESSAGE_URL
POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
UPDATE_MESSAGE_URL = 'https://slack.com/api/chat.update'

ENGINES_VERSION = '5.0.1'
ADDON_VERSION = '50.0.1-3.16'
UKH_WEB_ADDON_PARENT_DEPENDENCIES_VERSION = f'ukh-web-addon-child-dependencies#{ADDON_VERSION}'
PENDING_COMMENT_ID = 'dummy_comment_id'
slack_calls_tracking = {}
BASE_GITHUB_URL = 'https://api.github.com/repos/ConnectedHomes'

from .aws_stack import ENGINE_REPO_NAMES

def post_or_update_message_callback(request):
    print('📘 debug slack post_or_update message', request.url, request.path_url, request.params, request.body)
    if request.url not in slack_calls_tracking:
        slack_calls_tracking[request.url] = []
    payload = json.loads(request.body)
    payload['ts'] = 'dummy_timestamp'
    payload['message'] = {
        'attachments': payload['attachments']# not sure why it's needed
    }
    payload['ok'] = True
    slack_calls_tracking[request.url].append(payload)
    return (200, {}, json.dumps(payload))

def mock_slack_calls(repo_name):
    slack_calls_tracking.clear()
    responses.add_callback(
        responses.POST,
        POST_MESSAGE_URL,
        callback=post_or_update_message_callback,
        content_type='application/json'
    )
    responses.add_callback(
        responses.POST,
        UPDATE_MESSAGE_URL,
        callback=post_or_update_message_callback,
        content_type='application/json'
    )
