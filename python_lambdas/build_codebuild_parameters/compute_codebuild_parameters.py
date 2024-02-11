from ..lib.parameters import Parameters
from ..lib.github import Github

from .fetch_root_url import fetch_root_url

parameters = Parameters()

'''Builds env variables to be used in codebuild jobs'''
def compute(event, is_secondary_build = False):
    pr_payload = event['pull_request']
    commit_id =  pr_payload['head']['sha']
    base_branch = pr_payload['base']['ref']
    head_branch = pr_payload['head']['ref']
    action = event['action']
    repo_name = event['repository']['name']
    full_repo_name = event['repository']['full_name']
    github_token = parameters.get_parameter(
        name = 'dev-github_token'
    )
    github = Github(github_token)
    root_url = fetch_root_url(full_repo_name, repo_name, github, commit_id)

    env_vars = []

    is_merged = pr_payload['merged']
    if is_merged:
        env_vars.append({
            'Name': 'merged',
            'Value': 'true',
            'Type': 'PLAINTEXT'
        })

        is_base_branch_master = (base_branch in ['main', 'master'])
        if is_base_branch_master:
            env_vars.append({
                'Name': 'ROOT_DEPLOY',
                'Value': 'true',
                'Type': 'PLAINTEXT'
            })
    else:
        head_branch = pr_payload['head']['ref']
        env_vars.append({
            'Name': 'PR_BRANCH',
            'Value': head_branch,
            'Type': 'PLAINTEXT'
        })

    deployment_env = 'INT1'

    if is_merged:
        if is_base_branch_master:
            deployment_env = 'Staging_Environment'
    elif len(pr_payload['labels']) > 0:
        if action == 'labeled':
            pr_label = pr_payload['NewLabel']['Name']
            if 'DEPLOY_TO_' in pr_label:
                deployment_env = pr_label.replace('DEPLOY_TO_', '').upper()
        else:
            pr_label = pr_payload['labels']
            for label in pr_label:
                if 'DEPLOY_TO_' in label['name']:
                    deployment_env = label['name'].replace('DEPLOY_TO_', '').upper()
                    break

    print(f'Final deployment_env after on {action} github action :', deployment_env)

    env = 'devtest'
    if action == 'published':
        env = 'production'

    env_vars.extend([{
        'Name': '_projectname',
        'Value': repo_name,
        'Type': 'PLAINTEXT'
    }, {
        'Name': '_Environment',
        'Value': deployment_env,
        'Type': 'PLAINTEXT'
    }, {
        'Name': 'ENV',
        'Value': env,
        'Type': 'PLAINTEXT'
    }])

    if is_secondary_build:
        env_vars.append({
            'Name': 'IS_SECONDARY_BUILD',
            'Value': 'true',
            'Type': 'PLAINTEXT'
        })
    else:
        env_vars.extend([ {
            'Name': 'COMMIT_ID',
            'Value': commit_id,
            'Type': 'PLAINTEXT'
        }, {
            'Name': 'root_url',
            'Value': root_url,
            'Type': 'PLAINTEXT'
        }])

    if action == 'published' and pr_payload['release']['prerelease']: #release gas bene artificially put under pr_payload in parent state machine TODO: do it better
        env_vars.append({
            'Name': '_Release', # See https://playbook.digital/en/product-engineering/canary
            'Value': 'prerelease',
            'Type': 'PLAINTEXT'
        })

    if action == 'published':
        source_version = pr_payload['release']['tag_name']
    elif is_merged:
        source_version = base_branch
    else:
        source_version = head_branch
    return {
        'EnvironmentVariablesOverride': env_vars,
        'SourceVersion': source_version,
        'Buildspec': ''
    }
