import json
import copy
from ..lib.logger import configure_logger
from ..lib.parameters import Parameters
from ..lib.github import Github

from .compute_codebuild_parameters import compute as compute_codebuild_parameters
from .compute_engine_codebuild_parameters \
    import compute as compute_engine_codebuild_parameters
from .fetch_deployment_url import fetch_deployment_url

LOGGER = configure_logger(__name__)

parameters = Parameters()
github_token = parameters.get_parameter(
    name = 'dev-github_token'
)
github = Github(github_token)
CADET_JOB_NAMES = ['kiuwan', 'gitleaks']

'''Builds env variables to be used in codebuild jobs'''
def handler(event, _):
    print('build_codebuild_parameters debug', event)
    engine_repo_names = parameters.get_parameter(
        name = 'dev-web_oam_engine_names'
    ).split(',')
    repo_name = event['repository']['name']

    #same parameters for all projects for now, but that could change
    codebuild_parameters = compute_codebuild_parameters(event)

    parameters_dict = {} # will be used for lambdas other than codebuild
    for param in codebuild_parameters['EnvironmentVariablesOverride']:
        parameters_dict[param['Name']] = param['Value']

    deployment_url = fetch_deployment_url(
        event,
        parameters_dict,
        github
    )
    parameters_dict['deployment_url'] = deployment_url
    full_repo_name = event['repository']['full_name']
    pr_payload = event['pull_request']
    is_merged = pr_payload['merged']
    base_branch = pr_payload['base']['ref']
    commit_id = pr_payload['head']['sha']
    # make sure this starts with the repo computing the tests
    all_parameters = [{
        'ProjectName': repo_name,
        'CodebuildParameters': copy.deepcopy(codebuild_parameters),
        'ParametersDict': parameters_dict
    }]

    for cadet_job_name in CADET_JOB_NAMES:
        codebuild_parameter = copy.deepcopy(codebuild_parameters)
        codebuild_parameter['EnvironmentVariablesOverride'].append(
            {
                'Name': 'CADET_JOB_NAME',
                'Value': cadet_job_name,
                'Type': 'PLAINTEXT'
            }
        )
        all_parameters.append({
            'ProjectName': f'{repo_name}_cadet',
            'CodebuildParameters': codebuild_parameter
        })

    if repo_name == 'oam':
        for engine_repo_name in engine_repo_names:
            full_repo_name = event['repository']['full_name']
            pr_payload = event['pull_request']
            commit_id =  pr_payload['head']['sha']
            package_json_content_head = github.get_file_content(full_repo_name, commit_id, 'package.json')
            package_json_head = json.loads(package_json_content_head)
            codebuild_engine_parameters = compute_engine_codebuild_parameters(
                event,
                engine_repo_name,
                package_json_head
            )
            all_parameters.append({
                'ProjectName': engine_repo_name,
                'CodebuildParameters': codebuild_engine_parameters
            })

    print('ALL PARAMETERS FINAL DEBUG', all_parameters)
    # so that we can check for presence in the next "choice" Task:
    if is_merged == True and base_branch not in ['master', 'main']:
        all_parameters = []
    else:
        all_parameters = [{
            'ProjectName': repo_name,
            'CodebuildParameters': codebuild_parameters,
            'ParametersDict': parameters_dict
        }, {
            'ProjectName': f'{repo_name}_kiuwan',
            'CodebuildParameters': codebuild_parameters
        }]
        if repo_name == 'oam':
            for engine_repo_name in engine_repo_names:
                
                package_json_content_head = github.get_file_content(full_repo_name, commit_id, 'package.json')
                package_json_head = json.loads(package_json_content_head)
                codebuild_engine_parameters = compute_engine_codebuild_parameters(
                    event,
                    engine_repo_name,
                    package_json_head
                )
                all_parameters.append({
                    'ProjectName': engine_repo_name,
                    'CodebuildParameters': codebuild_engine_parameters
                })
        # so that we can check for presence in the next "choice" Task:
    return all_parameters if len(all_parameters) > 0 else 'false'
