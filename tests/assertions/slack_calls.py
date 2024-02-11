from ..mocks.slack import POST_MESSAGE_URL
from ..mocks.slack import UPDATE_MESSAGE_URL

from ..mocks.slack import slack_calls_tracking

from ..mocks.github_event import PR_URL

def assert_slack_calls(self, test_params):
    pr_label = test_params.get('pr_label', 'Quality&TestCheck')
    pr_labels = test_params.get('pr_labels', [pr_label])
    is_merged = test_params.get('merged', False)
    print('debug slack_calls_tracking', slack_calls_tracking)

    if is_merged:
        self.assertEqual(len(slack_calls_tracking.keys()), 1)
        update_slack_calls_tracking = slack_calls_tracking[UPDATE_MESSAGE_URL]
        self.assertEqual(
            len(update_slack_calls_tracking),
            1
        )
        self.assertIn('has been `merged`', update_slack_calls_tracking[0]['text'])
    elif 'READY_FOR_MERGE' in pr_labels:
        post_slack_calls_tracking = slack_calls_tracking[POST_MESSAGE_URL]
        print('debug post_slack_calls_tracking', post_slack_calls_tracking)
        self.assertEqual(
            len(post_slack_calls_tracking),
            1
        )
        slack_actions = post_slack_calls_tracking[0]['attachments'][0]['actions']
        self.assertEqual(len(slack_actions), 2)
        self.assertEqual(
            slack_actions[0]['url'],
            PR_URL
        )
    else:
        self.assertEqual(len(slack_calls_tracking.keys()), 0)
