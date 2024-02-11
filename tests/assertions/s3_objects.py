import json
import boto3

from ..mocks.aws_stack import BUILD_BUCKET_NAME
from ..mocks.aws_stack import SLACK_MESSAGES_BUCKET_NAME
from ..mocks.aws_stack import QA_REGRESSION_APP_NAMES
from ..mocks.aws_stack import ENGINE_REPO_NAMES

from ..mocks.github_event import PR_NUMBER

from ..mocks.github import UKH_WEB_ADDON_PARENT_DEPENDENCIES_VERSION

from ..mocks.codebuild import PREVIOUS_ATTEMPT_NUMBER

def assert_s3_objects(self, test_params, s3_codebuild_keys):
    s3 = boto3.client('s3')
    repo_name = test_params.get('repo_name', 'rewards')
    full_repo_name = f'ConnectedHomes/{repo_name}'
    is_oam = repo_name == 'oam'
    pr_action = test_params.get('pr_action', 'labeled')
    pr_label = test_params.get('pr_label', 'Quality&TestCheck')
    pr_labels = test_params.get('pr_labels', [pr_label])
    is_merged = test_params.get('merged', False)
    is_qa_app = repo_name in QA_REGRESSION_APP_NAMES
    is_ms = repo_name[0:7] == 'bg-core'

    # BUILD_BUCKET_NAME objects
    base_codebuild_prefix = '{}/{}/attempt_{}'.format(
        full_repo_name, PR_NUMBER,
        PREVIOUS_ATTEMPT_NUMBER + 1 if 'previous_attempt' in test_params else 1
    )
    list_s3_objects_pr_action_plus_codebuild = s3.list_objects_v2(
        Bucket=BUILD_BUCKET_NAME,
        Prefix=base_codebuild_prefix
    )['Contents']
    print('debug list_s3_objects_for_pr_action', list_s3_objects_pr_action_plus_codebuild)

    if is_merged:
        self.assertEqual(
            len(list_s3_objects_pr_action_plus_codebuild),
            4
        )
        self.assertIn('_labeled', list_s3_objects_pr_action_plus_codebuild[0]['Key'])
        self.assertIn('_featureBuildCompleted', list_s3_objects_pr_action_plus_codebuild[1]['Key'])
        self.assertIn('_merged', list_s3_objects_pr_action_plus_codebuild[2]['Key'])
        self.assertIn('_mergedBuildCompleted', list_s3_objects_pr_action_plus_codebuild[3]['Key'])
    else:
        self.assertEqual(
            len(list_s3_objects_pr_action_plus_codebuild),
            2 + len(ENGINE_REPO_NAMES) if is_oam else 2
        )
        self.assertIn(pr_action, list_s3_objects_pr_action_plus_codebuild[0]['Key'])

    if is_ms:
        self.assertEqual(
            len(s3_codebuild_keys),
            1,
            'created 1 codebuild jobfor ms'
        )
    elif is_qa_app and is_merged:
        self.assertEqual(
            len(s3_codebuild_keys),
            3,
            'created 2 codebuild jobs for QA plus normal one'
        )
    elif is_merged:
        self.assertEqual(
            len(s3_codebuild_keys),
            1 + (len(ENGINE_REPO_NAMES) if is_oam else 0),
            'create 1 codebuild job for merged PRs plus engine jobs when relevant'
        )
    else:
        self.assertEqual(
            len(s3_codebuild_keys),
            2 + (len(ENGINE_REPO_NAMES) if is_oam else 0),
            'create 2 codebuild job for normal PRs (including Kiuwan) plus engine jobs when relevant'

        )
    for key in s3_codebuild_keys:
        list_s3_objects_for_codebuild_artifacts = s3.list_objects_v2(
            Bucket=BUILD_BUCKET_NAME,
            Prefix=key
        )['Contents']
        self.assertEqual(
            len(list_s3_objects_for_codebuild_artifacts),
            1
        )

    list_all_objects = s3.list_objects_v2(
        Bucket=BUILD_BUCKET_NAME
    )['Contents']
    previous_attempt_length = 0
    if 'previous_green_build' in test_params:
        previous_attempt_length = 2
    elif 'previous_attempt' in test_params:
        previous_attempt_length = 1
    kiuwan_job_first_for_merged_prs = 1 if is_merged else 0
    self.assertEqual(
        len(list_all_objects),
        len(list_s3_objects_pr_action_plus_codebuild) + len(s3_codebuild_keys) + previous_attempt_length + kiuwan_job_first_for_merged_prs,
        'no other S3 objects created'
    )

    def map_func(content):
        key = content['Key']
        obj = s3.get_object(
            Bucket=BUILD_BUCKET_NAME,
            Key=key
        )
        payload = json.loads(obj['Body'].read().decode('utf-8'))
        return payload
    complete_objects = list(map(map_func, list_s3_objects_pr_action_plus_codebuild))

    if is_merged:
        self.assertEqual(complete_objects[-2]['action'], pr_action)
    elif pr_action == 'labeled':
        s3_object_pr_action = complete_objects[0]
        self.assertEqual(s3_object_pr_action['action'], pr_action)
        self.assertEqual(s3_object_pr_action['label']['name'], pr_label)
        self.assertIn(
            {'name': pr_label},
            s3_object_pr_action['pull_request']['labels']
        )
        self.assertEqual(s3_object_pr_action['pull_request']['state'], 'open')
        self.assertEqual(s3_object_pr_action['repository']['name'], repo_name)

        complete_objects.pop(0)
        for index, obj in enumerate(complete_objects, start=0):

            current_repo_name = repo_name if index == 0 else ENGINE_REPO_NAMES[index-1]
            self.assertEqual(obj['detail']['project-name'], current_repo_name)

            env_vars = obj['detail']['additional-information']['environment']['environment-variables']
            _GITHUB_PAYLOAD_S3_PATH = next(item for item in env_vars if item['name'] == '_GITHUB_PAYLOAD_S3_PATH')['value']
            self.assertIn(base_codebuild_prefix, _GITHUB_PAYLOAD_S3_PATH)

            if not is_ms:
                _projectname = next(item for item in env_vars if item['name'] == '_projectname')['value']
                self.assertEqual(_projectname, current_repo_name)

                PR_Label = next(item for item in env_vars if item['name'] == 'PR_Label')['value']
                self.assertEqual(PR_Label, pr_label)
                
                ENV = next(item for item in env_vars if item['name'] == 'ENV')['value']
                self.assertEqual(ENV, 'devtest')

            # else: TODO

            _GITHUB_PAYLOAD_EVENT = next(item for item in env_vars if item['name'] == '_GITHUB_PAYLOAD_EVENT')['value']
            self.assertEqual(_GITHUB_PAYLOAD_EVENT, 'open')#name is confusing

            parent_deps_version = next(
                (item for item in env_vars if item['name'] == 'UKH_WEB_ADDON_PARENT_DEPENDENCIES_VERSION'),
                None
            )
            print('debug parent_deps_version', is_oam, current_repo_name, env_vars)
            if is_oam and current_repo_name != 'oam':
                self.assertEqual(
                    parent_deps_version['value'],
                    UKH_WEB_ADDON_PARENT_DEPENDENCIES_VERSION
                )
            else:
                self.assertEqual(parent_deps_version, None)


    # SLACK_MESSAGES_BUCKET_NAME objects
    list_s3_objects_slack_wrapper = s3.list_objects_v2(
        Bucket=SLACK_MESSAGES_BUCKET_NAME
    )
    print('debug list_s3_objects_slack_wrapper', list_s3_objects_slack_wrapper)
    if is_merged:
        self.assertEqual(list_s3_objects_slack_wrapper['KeyCount'], 2)
        list_s3_objects_slack = list_s3_objects_slack_wrapper['Contents']
        self.assertIn(
            '_featureBuildSuccess.json',
            list_s3_objects_slack[0]['Key'],
            'success message sent to Slack'
        )
        self.assertIn(
            '_mergedBuild.json',
            list_s3_objects_slack[1]['Key'],
            'merged build message sent to Slack'
        )
    elif 'READY_FOR_MERGE' in pr_labels:
        list_s3_objects_slack = list_s3_objects_slack_wrapper['Contents']
        self.assertEqual(
            len(list_s3_objects_slack),
            1
        )
        key = list_s3_objects_slack[0]['Key']
        self.assertIn(base_codebuild_prefix, key)
        self.assertIn('_featureBuildSuccess.json', key, 'success message sent to Slack')
    else:
        self.assertEqual(list_s3_objects_slack_wrapper['KeyCount'], 0)
