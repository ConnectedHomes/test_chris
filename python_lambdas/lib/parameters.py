"""Used for all AWS Systems Manager Parameter Store operations"""

import boto3
import json

from .logger import configure_logger
from botocore.exceptions import ClientError

LOGGER = configure_logger(__name__)

class Parameters(object):
    """Class used for modeling Parameters"""

    def __init__(self) -> None:
        LOGGER.info(
            'Creating a new SSM boto3 client'
        )
        self.client = boto3.client('ssm', region_name='eu-west-1')

    """Gets a Parameter from Parameter Store"""
    def get_parameter(self, name: str, decryption: bool=False) -> str:
        LOGGER.info(
            "Retrieving parameter '{}' from SSM Parameter Store".format(
                name
            )
        )

        try:
            response = self.client.get_parameter(
                Name=name,
                WithDecryption=decryption
            )
            return response['Parameter']['Value']

        except ClientError as error:
            raise error
