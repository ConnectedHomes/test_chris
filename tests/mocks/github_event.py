from string import Template
import json
from digital_Web_CI_Stack.python_lambdas.lib.logger import configure_logger

LOGGER = configure_logger(__name__)
HEAD_REF = "foo_ref_head"
BASE_REF = "foo_ref_base"
PR_NUMBER = "dummy_pr_number"
PR_URL = "dummy_pr_url"

GITHUB_EVENT_TEMPLATE = Template(
    """{
    "pull_request": {
        "issue_url": "$url",
        "number": "$pr_number",
        "state": "$state",
        "head": {
            "sha": "foo_sha_head",
            "ref": "$head_ref"
        },
        "base": {
            "sha": "foo_sha_base",
            "ref": "$base_ref"
        },
        "labels": [],
        "user": {
            "login": "dummy_github_user"
        },
        "html_url": "$pr_url",
        "merge_commit_sha": "dummy_merge_commit_sha",
        "merged_by": {
            "login": "dummy_login"
        },
        "ts": "dummy_timestamp"
    },
    "action": "$action",
    "label": {
        "name": "$label"
    },
    "repository": {
        "full_name": "$full_repo_name",
        "name": "$repo_name"
    },
    "release": {
        "tag_name": "foo_tag_name"
    }
}"""
)

def create_github_event(options):
    event = json.loads(GITHUB_EVENT_TEMPLATE.substitute(options))
    event['pull_request']['labels'] = options['labels']
    event['pull_request']['merged'] = options['merged']
    return event

def create_github_event_from_params(test_params):
    repo_name = test_params.get('repo_name', 'rewards')
    full_repo_name = f'ConnectedHomes/{repo_name}'
    label = test_params.get('pr_label', 'Quality&TestCheck')
    pr_labels = test_params.get('pr_labels')
    base_ref = test_params.get('base_ref', BASE_REF)
    labels = []
    if pr_labels:
        for pr_label in test_params.get('pr_labels'):
            labels.append({
                'name': pr_label
            })
    else:
        labels.append({
            'name': label
        })
    merged = test_params.get('merged', False)
    options = {
        'state': test_params.get('pr_state', 'open'),
        'action': test_params.get('pr_action', 'labeled'),
        'label': label,
        'labels': labels,
        'repo_name': repo_name,
        'full_repo_name': full_repo_name,
        'head_ref': HEAD_REF,
        'base_ref': base_ref,
        'pr_number': PR_NUMBER,
        'pr_url': PR_URL,
        'merged': merged
    }
    if test_params.get('pr_action') == 'opened':
        issue_url = f'https://api.github.com/repos/{full_repo_name}/pulls/{PR_NUMBER}'
        options['url'] = issue_url
    else:
        options['url'] = 'https://'
    event = create_github_event(options)
    print('debug github event', event, test_params, flush=True)
    return event
