import json
import botocore

from .aws_stack import BUILD_BUCKET_NAME
from .lambda_context import Context
context = Context()

codebuild_calls_tracking = {}
codebuild_keys_tracking = []
cloudwatch_payloads_tracking = []
DUMMY_COMMIT_ID_SHOULD_BE_DIFFERENT_FOR_EACH_REPO = '1234'
env_vars_for_codebuild_batch_get_builds = {}
PREVIOUS_ATTEMPT_NUMBER = 5


def mock_codebuild_api_call(s3, project_name):
    orig = botocore.client.BaseClient._make_api_call  #pylint: disable=protected-access
    codebuild_calls_tracking.clear()
    codebuild_keys_tracking.clear()
    cloudwatch_payloads_tracking.clear()

    def make_api_call(self, operation_name, kwarg):
        #print('debug codebuild api operation_name', operation_name, kwarg)
        #tried to use mock.create_autospec(so etc.), but no cigar
        codebuild_calls_tracking[operation_name] = codebuild_calls_tracking.get(operation_name) or []
        codebuild_calls_tracking[operation_name].append(kwarg)
        if operation_name == 'ListProjects':
            return {
                'projects': [
                    project_name,
                    project_name+'_kiuwan'
                ],
            }
        if operation_name == 'BatchGetBuilds':
            print(
                'debug env_vars_for_codebuild_batch_get_builds',
                env_vars_for_codebuild_batch_get_builds
            )
            return {
                'builds': [{
                    'environment': env_vars_for_codebuild_batch_get_builds
                }]
            }
        if operation_name == 'StartBuild':
            current_project_name = kwarg['projectName']
            key = '{}:{}'.format(
                current_project_name,
                DUMMY_COMMIT_ID_SHOULD_BE_DIFFERENT_FOR_EACH_REPO
            )
            codebuild_keys_tracking.append(key)

            payload = {
                'detail': {
                    'project-name': current_project_name,
                    'build-status': 'SUCCEEDED',
                    'build-id': DUMMY_COMMIT_ID_SHOULD_BE_DIFFERENT_FOR_EACH_REPO,
                    'additional-information': {
                        'environment': {
                            'environment-variables': kwarg['environmentVariablesOverride']
                        }
                    }
                }
            }
            cloudwatch_payloads_tracking.append(payload)
            s3.put_object(
                Bucket=BUILD_BUCKET_NAME,
                Key=key,
                Body=json.dumps(payload)
            )
            return {
                'build': {
                    'buildStatus': 'IN_PROGRESS',
                    'id': key,
                    'arn': context.invoked_function_arn,
                    'projectName': current_project_name,
                    'source': {
                        'location': f'https://github.com/ConnectedHomes/{current_project_name}',
                    },
                    'environment': {
                        'environmentVariables': cloudwatch_payloads_tracking[0]['detail']['additional-information']['environment']['environment-variables']
                    }
                }
            }

        myorig = orig(self, operation_name, kwarg)
        return myorig
    return make_api_call
