import boto3

from ..mocks.github_event import HEAD_REF
from ..mocks.github_event import BASE_REF

from ..mocks.github import UKH_WEB_ADDON_PARENT_DEPENDENCIES_VERSION
from ..mocks.github import ENGINES_VERSION

from ..mocks.codebuild import codebuild_calls_tracking

from ..mocks.aws_stack import QA_REGRESSION_APP_NAMES
from ..mocks.aws_stack import ENGINE_REPO_NAMES

def assert_codebuild_calls(self, test_params):
    repo_name = test_params.get('repo_name', 'rewards')
    full_repo_name = f'ConnectedHomes/{repo_name}'
    pr_label = test_params.get('pr_label', 'Quality&TestCheck')
    is_merged = test_params.get('merged', False)
    base_ref = test_params.get('base_ref', BASE_REF)
    keys = codebuild_calls_tracking.keys()
    self.assertNotIn(
        'CreateProject',
        keys,
        'don"t create a new codebuild project as it already exists'
    )
    self.assertIn('GetObject', keys)
    self.assertIn('GetParameter', keys)
    if is_merged:
        self.assertNotIn('ListProjects', keys)
    else:
        self.assertIn('ListProjects', keys)

    self.assertIn('StartBuild', keys)
    is_parent_app = repo_name == 'oam'
    is_qa_app = 'dummy'
    is_ms = repo_name[0:7] == 'bg-core'
    should_start_kiuwan_job = not is_merged
    if is_ms:
        nb_of_codebuild_jobs = 1
    elif is_parent_app:
        nb_of_codebuild_jobs = 1 + len(ENGINE_REPO_NAMES) + (1 if should_start_kiuwan_job else 0)
    else:
        is_qa_app = repo_name in QA_REGRESSION_APP_NAMES
        should_start_qa_jobs_after_merge = is_qa_app and is_merged
        nb_of_codebuild_jobs = 1 + (2 if should_start_qa_jobs_after_merge else 0) + (1 if should_start_kiuwan_job else 0)

    self.assertEqual(
        len(codebuild_calls_tracking['StartBuild']),
        nb_of_codebuild_jobs,
        'starts {} codebuild jobs'.format(nb_of_codebuild_jobs)
    )
    print('debug StartBuild', codebuild_calls_tracking['StartBuild'], flush=True)


    for start_build in codebuild_calls_tracking['StartBuild']:
        current_repo_name = start_build['projectName']
        is_parent_repo = current_repo_name.replace('_kiuwan', '') == repo_name
        environment_variables = start_build['environmentVariablesOverride']
        bg_initiator = next((item for item in environment_variables if item['name'] == 'bg_initiator'), False)
        is_qa_job = bg_initiator and bg_initiator['value'] == 'qa_automation'
        is_kiuwan_job = is_parent_repo and bg_initiator['value'] == 'web_kiuwan'
        if not (is_qa_job or is_ms):
            print('start_build debug',  start_build)

            print('debug current_repo_name', current_repo_name)

            _projectname = next(
                item for item in environment_variables if item['name'] == '_projectname'
            )['value']
            self.assertEqual(_projectname + ('_kiuwan' if is_kiuwan_job else ''), current_repo_name)

            if is_merged:
                merged = next(
                    item for item in environment_variables if item['name'] == 'merged'
                )['value']
                self.assertEqual(merged, 'true')
            else:
                pr_label_env = next(
                    item for item in environment_variables if item['name'] == 'PR_Label'
                )['value']
                self.assertEqual(pr_label_env, test_params.get('pr_label', pr_label))

            github_payload_event = next(
                item for item in environment_variables if item['name'] == '_GITHUB_PAYLOAD_EVENT'
            )['value']
            self.assertEqual(github_payload_event, test_params.get('pr_state', 'open'))

            github_payload_s3_path = next(
                item for item in environment_variables if item['name'] == '_GITHUB_PAYLOAD_S3_PATH'
            )['value']
            print('debug github_payload_s3_path', github_payload_s3_path)
            self.assertIn(
                full_repo_name,
                github_payload_s3_path,
                'reference to the parent app PR'
            )
            print('debug environment vars', environment_variables)
            source_version = start_build['sourceVersion']
            print('debug stuff', is_parent_repo, is_kiuwan_job, current_repo_name, repo_name)
            if is_parent_repo:
                self.assertEqual(len(environment_variables), 12)
                self.assertEqual(source_version, base_ref if is_merged else HEAD_REF)
            elif is_kiuwan_job:
                self.assertEqual(len(environment_variables), 11)
            else:
                self.assertEqual(len(environment_variables), 13)
                addon_version = next(
                    item for item in environment_variables if item['name'] == 'UKH_WEB_ADDON_PARENT_DEPENDENCIES_VERSION'
                )['value']
                self.assertEqual(addon_version, UKH_WEB_ADDON_PARENT_DEPENDENCIES_VERSION)
                self.assertEqual(source_version, ENGINES_VERSION)

        #else:
            #TODO @BIPLAVGHOSAL
