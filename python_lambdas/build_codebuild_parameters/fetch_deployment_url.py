from ..lib.logger import configure_logger

ENV_LIST = {
    # dont use just 'staging', or it will be found in lots of Makefiles when
    # computing deployment_env
    'STAGING_ENVIRONMENT': 'www1',
    'QA1': 'www2',
    'QA2': 'www3',
    'QA3': 'www4',
    'INT1': 'www5',
    'INT2': 'www6',
    'INT3': 'www7',
    'INT4': 'www9',
    'QA_TARIFF': 'www8',
    'PROD': 'www'
}

LOGGER = configure_logger(__name__)

def fetch_deployment_url(event, parameters_dict, github):
    full_repo_name = event['repository']['full_name']
    pr_payload = event['pull_request']
    commit_id = pr_payload['head']['sha']
    deployment_env = parameters_dict['_Environment']
    root_url = parameters_dict['root_url']
    release = pr_payload.get('release')
    print('>>> fetch_deployment_url', full_repo_name, commit_id, deployment_env, release)
    '''compute deployment environment and corresponding host name'''
    hostname = None
    if not deployment_env:
        try:
            makefile_content = github.get_file_content(full_repo_name, commit_id, 'Makefile')
            envs = ENV_LIST.keys()
            #look for QA1 QA2 INT1 etc. string in the Makefile
            deployment_env = next((x for x in envs if x in makefile_content), 'INT1')
        except:
            print('>> trying to fetch deployment_env from github failed')
            deployment_env = 'INT1'
    try:
        prefix = ENV_LIST[deployment_env.upper()]
        if release:
            hostname = 'https://www.britishgas.co.uk'
        else:
            hostname = f'https://{prefix}.bgo.bgdigitaltest.co.uk'

    except:
        print('>>> error in trying to compute prefix', flush=True)
        LOGGER.error('>>> error in trying to compute prefix', exc_info=True)

    print('>>> root_url', root_url, flush=True)
    print('>>> hostname', hostname, flush=True)
    if root_url and hostname:
        base_url = f'{hostname}/{root_url}'
        if 'nucleus' in full_repo_name:
            return f'{base_url}/{commit_id}/demo/index.html'
        if deployment_env == 'Staging_Environment':
            return base_url
        if release:
            return base_url
        return f'{base_url}/?branch={commit_id}'
    return None
