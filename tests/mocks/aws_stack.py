import json
import io
import zipfile
import subprocess

from string import Template

import shutil
import yaml
import boto3



from .lambda_context import LAMBDA_REGION, AWS_ACCOUNT_NUMBER

SLACK_MESSAGES_BUCKET_NAME = 'dummy_slack_messages_bucket_name'
BUILD_BUCKET_NAME = 'dummy_build_bucket_name'
CF_SHARED_BUCKET_NAME = 'digital-nested-web-prod-apps'
QA_REGRESSION_APP_NAMES = 'identity,dummy_qa_app_name2'
ENGINE_REPO_NAMES = [
    'ukh-web-engine-rewards',
    'ukh-web-engine-payments',
    'ukh-web-engine-existing-home-care',
    'ukh-web-engine-smart-installation',
    'ukh-web-engine-meter-read'
]

def _process_lambda(func_str):
    zip_output = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED)
    zip_file.writestr("lambda_function.py", func_str)
    zip_file.close()
    zip_output.seek(0)
    return zip_output.read()

LAMBA_FUNC_DEFAULT = '''
def lambda_handler(event, context):
    res = []
    return res
'''

def get_lambda_zip_file(pfunc = LAMBA_FUNC_DEFAULT):
    return _process_lambda(pfunc)

class Stack():
    def __init__(self, options) -> None:
        region_name = options['region_name']

        self.client_s3 = boto3.client('s3', **options)
        self.client_s3.create_bucket(
            Bucket=BUILD_BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': region_name},
        )
        self.client_ec2 = boto3.client('ec2',
            **options
        )

        self.client_ssm = boto3.client('ssm',
            **options
        )
        self.client_ssm.put_parameter(
            Name='dev-github_token',
            Description='Github access token for test',
            Value='dummy_github_token',
            Type='String'
        )
        self.client_ssm.put_parameter(
            Name='dev-slack_token',
            Description='Slack access token for test',
            Value='dummy_slack_token',
            Type='String'
        )
        self.client_ssm.put_parameter(
            Name='dev-webslack_channel',
            Description='Slack channel for test',
            Value='dummy_slack_channel',
            Type='String'
        )
        self.client_ssm.put_parameter(
            Name='dev-web_oam_engine_names',
            Description='Dynamic list retrieval for OAM Engine',
            Value=','.join(ENGINE_REPO_NAMES),
            Type='StringList'
        )
        #TODO: dev-regression_fe_webapp_name is not a good name, doesnt convey that it's qa / automation job
        self.client_ssm.put_parameter(
            Name='dev-regression_fe_webapp_name',
            Description='FE app names for which Automated Regression test will start',
            Value=f'{QA_REGRESSION_APP_NAMES}', Type='StringList'
        )
        self.client_ssm.put_parameter(
            Name='dev-testauto-slack_channel',
            Description='Slack channel for automation',
            Value='dummy_automation_slack_channel',
            Type='String'
        )
        self.client_s3.create_bucket(
            Bucket=SLACK_MESSAGES_BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': region_name},
        )
        # MS
        self.client_ssm.put_parameter(
            Name='dev-slack_channel',
            Description='Slack channel for test',
            Value='dummy_slack_channel',
            Type='String'
        )

        self.client_cf = boto3.client('cloudformation', **options)

        self.client_s3.create_bucket(
            Bucket=CF_SHARED_BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': region_name},
        )

        self.client_iam = boto3.client('iam', **options)

        self.client_lambda = boto3.client('lambda',
            endpoint_url='http://localhost:3001',
            region_name=region_name
        )
