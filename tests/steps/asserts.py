from ..assertions.github_calls import assert_github_calls
from ..assertions.slack_calls import assert_slack_calls
from ..assertions.s3_objects import assert_s3_objects
from ..assertions.codebuild_calls import assert_codebuild_calls

def do_all_assertions(self, test_params, s3_codebuild_keys):
    assert_codebuild_calls(self, test_params)
    assert_github_calls(self, test_params)
    assert_slack_calls(self, test_params)
    assert_s3_objects(self, test_params, s3_codebuild_keys)
