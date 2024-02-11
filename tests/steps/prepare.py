import os
from unittest.mock import patch

from moto import (
    mock_lambda,
    mock_s3,
    mock_ssm,
    mock_cloudformation
)

from ..mocks.aws_stack import SLACK_MESSAGES_BUCKET_NAME
from ..mocks.aws_stack import BUILD_BUCKET_NAME
from ..mocks.aws_stack import Stack

from ..mocks.lambda_context import LAMBDA_REGION
from ..mocks.github import mock_github_calls
#from ..mocks.slack import mock_slack_calls

OS_ENVIRON_MOCK = {
    'dev-github_token': 'foo_token',
    'BUILD_BUCKET_NAME': BUILD_BUCKET_NAME,
    'TEST_BUCKET_NAME':	'bar',
    'AWS_DEFAULT_REGION': 'eu-west-1',
    'SLACK_MESSAGES_BUCKET_NAME': SLACK_MESSAGES_BUCKET_NAME,
    'GITHUB_SLACK_DYNAMODB_TABLE_NAME': 'dummy_slack_dynamodb_table',
    'root_url': 'dummy_root_url',
    'STAGE_NAME': 'prod',
    'FILTER_JOB_OUTPUT': 'digital-web-prod-app_pr',
    'SECONDARY_SOURCE': 'dummy_github',
    'CODEBUILD_SOURCE_IDENTIFIER': 'dummy_identifier',
    'ARTIFACT_BUCKET_NAME': 'dummy_artifact_bucket_name',
    'CACHE_BUCKET_NAME': 'dummy_cache_bucket_name',
    'CODEBUILD_ROLE': 'dummy_role',
    'AWS_ACCESS_KEY_ID': 'dummy-access-key',
    'AWS_SECRET_ACCESS_KEY': 'dummy-access-key-secret',
    'AWS_DEFAULT_REGION': 'eu-west-1'
}

def decorator_for_tests(func):
    def decorated_func(*args, **kwargs):
        with patch.dict(os.environ, OS_ENVIRON_MOCK):
            mock_ssm(
                mock_s3(
                    mock_lambda(mock_cloudformation(func))
                )
            )(*args, **kwargs)
    return decorated_func


def prepare_mocks(test_params, seed_func = False):
    repo_name = test_params.get('repo_name', 'rewards')
    print('debug test_params', test_params)
    options = {
        'region_name': LAMBDA_REGION
    }
    stack = Stack(options)
    s3 = stack.client_s3
    if seed_func:
        seed_func(s3)
    mock_github_calls(repo_name)
    #mock_slack_calls(repo_name)
    os.s3_client = s3
    return stack
