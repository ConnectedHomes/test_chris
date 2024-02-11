import base64
import json
import responses
from datetime import datetime
from .github_event import PR_NUMBER
from .aws_stack import ENGINE_REPO_NAMES

ENGINES_VERSION = '5.0.1-LARGE-small'
ADDON_VERSION = '50.0.1-3.16-LARGE-small'
UKH_WEB_ADDON_PARENT_DEPENDENCIES_VERSION = f'ukh-web-addon-child-dependencies#{ADDON_VERSION}'
PENDING_COMMENT_ID = 'dummy_comment_id'
github_calls_tracking = {}
BASE_GITHUB_URL = 'https://api.github.com/repos/ConnectedHomes'
REPO_PACKAGE_VERSION = 'dummy_repo_package_version'
PAYLOAD_MAKEFILE = '{"anything_containing_the_right_string": "asaINT1fsfd"}'
PAYLOAD_TOPICS = {"names": ["api-java-11"]}

def post_comment_callback(request):
    print('debug github post comment', request.url, request.path_url, request.params, request.body)
    if request.url not in github_calls_tracking:
        github_calls_tracking[request.url] = []
    comment = json.loads(request.body)
    comment['id'] = PENDING_COMMENT_ID
    comment['created_at'] = datetime.now().isoformat() + 'Z'#API sends a "Z" at the end which is not parsed by Python
    github_calls_tracking[request.url].append(comment)
    return (200, {}, json.dumps({}))

def delete_comment_callback(request):
    if request.url not in github_calls_tracking:
        github_calls_tracking[request.url] = []
    github_calls_tracking[request.url].append({})
    return (200, {}, json.dumps({}))

def get_comment_callback(request):
    print('debug github get comment', request.url, request.path_url, request.params, request.body)
    comments = github_calls_tracking[request.url]
    return (200, {}, json.dumps(comments))

def post_status_callback(request):
    print('debug github post status', request.body)
    payload = json.loads(request.body)
    if request.url not in github_calls_tracking :
        github_calls_tracking[request.url] = {}
    if payload['context'] not in github_calls_tracking[request.url]:
        github_calls_tracking[request.url][payload['context']] = []
    github_calls_tracking[request.url][payload['context']].append(request.body)
    return (200, {}, json.dumps({}))

def mock_github_calls(repo_name):
    github_calls_tracking.clear()
    if repo_name == 'oam':
        payload_head = {
            'version': REPO_PACKAGE_VERSION,
            'devDependencies': {
                'ukh-web-addon-parent-dependencies': 'github:ConnectedHoMes/{}'.format(UKH_WEB_ADDON_PARENT_DEPENDENCIES_VERSION)
            }
        }
        for engine_repo_name in ENGINE_REPO_NAMES:
            payload_head['devDependencies'][engine_repo_name] = 'github:ConnectedHomEs/{}#{}'.format(engine_repo_name, ENGINES_VERSION)
        encoded_payload_head = base64.b64encode(json.dumps(payload_head).encode('utf8')).decode('utf8')
        responses.add(
            responses.GET,
            f'{BASE_GITHUB_URL}/oam/contents/package.json?ref=foo_sha_head',
            json={'content': encoded_payload_head},
            status=200
        )
        responses.add(
            responses.GET,
            f'{BASE_GITHUB_URL}/oam/contents/package.json?ref=foo_sha_base', #doesnt matter as of now if base has another version
            json = {'content': encoded_payload_head},
            status=200
        )

    responses.add_callback(
        responses.POST,
        f'{BASE_GITHUB_URL}/{repo_name}/issues/{PR_NUMBER}/comments',
        callback=post_comment_callback,
        content_type='application/json'
    )
    responses.add_callback(
        responses.GET,
        f'{BASE_GITHUB_URL}/{repo_name}/issues/{PR_NUMBER}/comments',
        callback=get_comment_callback,
        content_type='application/json'
    )
    responses.add_callback(
        responses.DELETE,
        f'{BASE_GITHUB_URL}/{repo_name}/issues/comments/{PENDING_COMMENT_ID}',
        callback=delete_comment_callback,
        content_type='application/json'
    )
    payload_base = {
        'version': REPO_PACKAGE_VERSION
    }
    encoded_payload_base = base64.b64encode(json.dumps(payload_base).encode('utf8')).decode('utf8')
    responses.add(
        responses.GET,
        f'{BASE_GITHUB_URL}/{repo_name}/contents/package.json?ref=foo_sha_base',
        json = {'content': encoded_payload_base},
        status=200
    )

    responses.add_callback(
        responses.POST,
        f'{BASE_GITHUB_URL}/{repo_name}/statuses/foo_sha_head',
        callback=post_status_callback,
        content_type='application/json'
    )

    encoded_payload_makefile = base64.b64encode(json.dumps(PAYLOAD_MAKEFILE).encode('utf8')).decode('utf8')
    responses.add(
        responses.GET,
        f'{BASE_GITHUB_URL}/{repo_name}/contents/Makefile?ref=foo_sha_head',
        json = {'content': encoded_payload_makefile},
        status=200
    )

    #for MS
    responses.add(
        responses.GET,
        f'{BASE_GITHUB_URL}/{repo_name}/topics',
        json = PAYLOAD_TOPICS,
        content_type='application/json'
    )
