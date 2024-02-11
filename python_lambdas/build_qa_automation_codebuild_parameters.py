from .lib.logger import configure_logger
from .lib.parameters import Parameters

parameters = Parameters()
LOGGER = configure_logger(__name__)

'''Builds env variables to be used in codebuild jobs'''
def lambda_handler(event, _):

    print('build_qa_automation_codebuild_parameters debug', event)
    pr_payload = event['pull_request']
    base_branch = pr_payload['base']['ref']
    is_merged = pr_payload['merged']
    repo_name = event['repository']['name']
    automation_fe_webapp_names = parameters.get_parameter(
        name = 'dev-regression_fe_webapp_name'
    )
    print('debug automation_fe_webapp_names', repo_name, automation_fe_webapp_names, repo_name in automation_fe_webapp_names)
    # TODO: add check for build_status succeeded  "and build_status == 'SUCCEEDED'""
    all_parameters = []
    if base_branch in ['master', 'main'] and \
        is_merged and \
        repo_name in automation_fe_webapp_names:

        LOGGER.info(f'Triggering Automation QA Build for {repo_name}')
        full_repo_name = event['repository']['full_name']
        pr_number = pr_payload['number']
        github_endpoint = f'repos/{full_repo_name}/issues/{pr_number}/comments'
        env_vars = [
            {
                'Name': '_INITIATOR',
                'Value': 'Lambda',
                'Type': 'PLAINTEXT'
            },
            {
                'Name': 'folderPath',
                'Value': 'features-Regression',
                'Type': 'PLAINTEXT'
            },
            {
                'Name': 'github_endpoint',
                'Value': f'{github_endpoint}',
                'Type': 'PLAINTEXT'
            },
            {
                'Name': 'bg_initiator',
                'Value': 'qa_automation',
                'Type': 'PLAINTEXT'
            }
        ]

        parameters_dict = {} # will be used for lambdas other than codebuild
        for param in env_vars:
            parameters_dict[param['Name']] = param['Value']

        automation_repo_name = f'{repo_name}-automation'
        all_parameters.append({
            "ProjectName": automation_repo_name,
            "CodebuildParameters": {
                "EnvironmentVariablesOverride": env_vars,
                "SourceVersion": 'master',
                'ParametersDict': parameters_dict
            }
        })
        all_parameters.append({
            "ProjectName": 'ci-cd-automation',
            "CodebuildParameters": {
                "EnvironmentVariablesOverride": env_vars,
                "SourceVersion": 'master'
            }
        })

    # so that we can check for presence in the next "choice" Task:
    return all_parameters if len(all_parameters) > 0 else 'false'
