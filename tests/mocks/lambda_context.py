from digital_Web_CI_Stack.python_lambdas.lib.logger import configure_logger

LOGGER = configure_logger(__name__)
LAMBDA_REGION = 'eu-west-1'
AWS_ACCOUNT_NUMBER = 'foo_account_number'

class Context():

    def __init__(self) -> None:
        LOGGER.info(
            'Creating a new {} mock context'.format(
                __class__.__name__
            )
        )
        self.invoked_function_arn = "{}:{}:{}:{}:{}".format(
            'foo_context_0',
            'foo_context_1',
            'foo_context_2',
            LAMBDA_REGION,
            AWS_ACCOUNT_NUMBER
        )
