from ..mocks.github import github_calls_tracking
from ..mocks.github import ADDON_VERSION
from ..mocks.github import BASE_GITHUB_URL
from ..mocks.github import PENDING_COMMENT_ID
from ..mocks.github import PAYLOAD_MAKEFILE
from ..mocks.github_event import PR_NUMBER
from ..mocks.codebuild import DUMMY_COMMIT_ID_SHOULD_BE_DIFFERENT_FOR_EACH_REPO
from ..mocks.aws_stack import QA_REGRESSION_APP_NAMES
from ..mocks.aws_stack import ENGINE_REPO_NAMES

def assert_github_calls(self, test_params):
    print('debug github_calls_tracking', github_calls_tracking)
    is_merged = test_params.get('merged', False)
    repo_name = test_params.get('repo_name', 'rewards')

    pr_post_comments_url = '{}/{}/issues/{}/comments'.format(BASE_GITHUB_URL, repo_name, PR_NUMBER)
    pr_post_comments_tracking = github_calls_tracking[pr_post_comments_url]
    is_qa_app = repo_name in QA_REGRESSION_APP_NAMES
    is_ms = repo_name[0:7] == 'bg-core'

    if is_qa_app and is_merged:
        self.assertEqual(
            len(pr_post_comments_tracking),
            4,
            'two more comments on github than usual, for qa jobs'
        )
    else:
        self.assertEqual(
            len(pr_post_comments_tracking),
            2,
            'only two calls to comments, even for OAM'
        )

    pending_build_comment = pr_post_comments_tracking[0]['body']
    finished_build_comment = pr_post_comments_tracking[1]['body']
    print('finished_build_comment', finished_build_comment)

    # from digital_Web_CI_Stack.python_lambdas.on_build_completed import ENV_LIST
    # envs = ENV_LIST.keys()
    # #look for QA1 QA2 INT1 etc. string in the Makefile
    # www_env = next((x for x in envs if x in PAYLOAD_MAKEFILE), False)
    www_env = False

    if www_env and not is_ms:
        link_to_deployment_part = finished_build_comment.split('Link to deployment')[1]
        self.assertNotIn('ConnectedHomes', link_to_deployment_part)
    #else: TODO

    if is_merged:
        self.assertIn('Awesome! Your Merge build has started', pending_build_comment)
        self.assertIn('CodeBuild project build status after merging', finished_build_comment)
        if not is_ms:
            self.assertNotIn('?', link_to_deployment_part, 'deployment to root')
    else:
        self.assertIn('Awesome! Your PR build has started', pending_build_comment)
        self.assertIn('CodeBuild project build status before merging', finished_build_comment)
        if not is_ms:
            self.assertIn('?', link_to_deployment_part, 'deployment to branch')

    if not is_merged: #TODO: should remove previous "pending" comment too for on_merged_pull_request lambda

        #TODO: the same for MS
        if not is_ms:
            pr_delete_comments_url = '{}/{}/issues/comments/{}'.format(BASE_GITHUB_URL, repo_name, PENDING_COMMENT_ID)
            pr_delete_comments_tracking = github_calls_tracking[pr_delete_comments_url]
            self.assertEqual(len(pr_delete_comments_tracking), 1, 'deleting one pending comment')

        pr_status_url = '{}/{}/statuses/foo_sha_head'.format(BASE_GITHUB_URL, repo_name)
        pr_status_tracking = github_calls_tracking[pr_status_url]

        print('debug pr_status_tracking', pr_status_tracking)
        contexts_hash = {}
        contexts_hash[repo_name] = 'CodeBuild PR Bot'
        if repo_name == 'oam':
            for engine_repo_name in ENGINE_REPO_NAMES:
                contexts_hash[engine_repo_name] = f'{engine_repo_name} ukh-web-addon-child-dependencies#{ADDON_VERSION}'

        statuses_for_repo = github_calls_tracking[pr_status_url]
        self.assertEqual(len(statuses_for_repo), len(contexts_hash.keys()))
        for current_repo_name in contexts_hash.keys():
            context = contexts_hash[current_repo_name]
            statuses = statuses_for_repo[context]
            if is_ms and context == 'CodeBuild PR Bot':
                self.assertEqual(len(statuses), 1, 'one status only for MS stack on CodeBuild PR Bot which needs to be fixed')
            else:
                self.assertIn('Please wait...', statuses[0])
                self.assertEqual(len(statuses), 2, 'two statuses per context have been printed in github')
                #TODO: fix MS
                if not is_ms:
                    codebuild_log_url =  'https://eu-west-1.console.aws.amazon.com/codesuite/codebuild/projects/{}/build/{}:{}/log'.format(
                        current_repo_name, current_repo_name, DUMMY_COMMIT_ID_SHOULD_BE_DIFFERENT_FOR_EACH_REPO
                    )
                    self.assertIn(codebuild_log_url, statuses[0])


    #else: TODO: @BIPLAVGHOSAL
