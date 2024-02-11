"""Used for all GitHub operations"""
import json
import base64
import requests

from .logger import configure_logger
LOGGER = configure_logger(__name__, '📘')

"""Class used for modeling GitHub API Calls"""
class Github():

    def __init__(self, token: str) -> None:
        self.request_headers = {
            'Authorization': 'token {}'.format(token)
        }
        self.github_api_url = 'https://api.github.com'

    """Posts a message to a specific GitHub endpoint e.g to a pull request comment endpoint"""
    def post_message(self, endpoint: str, message: str) -> dict:

        full_url = '{}/{}'.format(self.github_api_url, endpoint)
        LOGGER.info(
            "Posting the message '{}' to GitHub endpoint '{}".format(
                message,
                full_url
            )
        )

        try:
            github_message = {
                'body': message
            }

            response = requests.post(
                full_url,
                json.dumps(github_message),
                headers=self.request_headers
            )
            decoded_response = response.content.decode('utf8').replace("'", '"')

            LOGGER.info(
                'Successfully posted message to GitHub endpoint: ' +
                json.dumps(response, default=str)
            )
            LOGGER.info(
                'decoded_response for posted message to GitHub endpoint: ' +
                json.dumps(decoded_response, default=str)
            )
            return response

        except requests.exceptions.ConnectionError as error:
            raise error

    """Posts a label to a specific GitHub endpoint"""
    def add_label(self, endpoint: str, labelName: str) -> dict:
        LOGGER.info(
            "Posting the label '{}' to GitHub endpoint '{}".format(
                labelName,
                endpoint
            )
        )

        try:
            label = {
                'labels': [labelName]
            }

            response = requests.post(
                endpoint,
                json.dumps(label),
                headers=self.request_headers
            )
            decoded_response = response.content.decode('utf8').replace("'", '"')

            LOGGER.info(
                'Successfully posted label to GitHub endpoint: ' +
                json.dumps(response, default=str)
            )
            LOGGER.info(
                'decoded_response for posted message to GitHub endpoint: ' +
                json.dumps(decoded_response, default=str)
            )
            return response

        except requests.exceptions.ConnectionError as error:
            raise error

    """Deletes the message of a specific GitHub endpoint e.g a pull request comment endpoint"""
    def delete_message(self, endpoint: str, message_id: int) -> dict:
        full_url = '{}/{}/{}'.format(self.github_api_url, endpoint, str(message_id))
        LOGGER.info(
            "Deleting message '{}' on GitHub endpoint '{}".format(
                message_id,
                full_url
            )
        )

        try:

            response = requests.delete(
                full_url,
                headers=self.request_headers
            )
            decoded_response = response.content.decode('utf8').replace("'", '"')

            LOGGER.info(
                'Successfully deleted message from GitHub endpoint: ' +
                json.dumps(response, default=str)
            )
            LOGGER.info(
                'decoded_response for deleted message from GitHub endpoint: ' +
                json.dumps(decoded_response, default=str)
            )
            return decoded_response

        except requests.exceptions.ConnectionError as error:
            raise error

    """Retrieves all the messages of a specific GitHub endpoint e.g of a pull request comment endpoint"""
    def get_messages(self, endpoint: str) -> dict:
        full_url = '{}/{}'.format(self.github_api_url, endpoint)
        LOGGER.info(
            "Fetching messages of GitHub endpoint '{}'".format(
                full_url
            )
        )

        try:
            response = requests.get(
                full_url,
                headers=self.request_headers
            )
            decoded_response = response.content.decode('utf8')

            LOGGER.info(
                'Successfully retrieved all messages from GitHub endpoint: ' +
                json.dumps(response, default=str)
            )
            LOGGER.info(
                'decoded_response for retrieved messages of GitHub endpoint: ' +
                json.dumps(decoded_response, default=str)
            )
            return json.loads(decoded_response)

        except requests.exceptions.ConnectionError as error:
            raise error

    """Posts a status check to a GitHub repository given a commit SHA"""
    def post_status_check(self, status: str, github_full_repo_name:  str, github_commit_sha: str, codebuild_logs_url: str, context = 'CodeBuild PR Bot') -> dict:
        full_url = '{}/repos/{}/statuses/{}'.format(self.github_api_url, github_full_repo_name, github_commit_sha)
        LOGGER.info(
            f"Posting status check '{status}' for category '{context}' to GitHub endpoint '{full_url}' logs url is '{codebuild_logs_url}'"
        )
        description = '' if status == 'pending' else 'CodeBuild project has completed'

        try:
            github_status = {
                'state': status,
                'description': 'Please wait...' if status == 'pending' else 'CodeBuild project has completed',
                'context': context
            }
            if codebuild_logs_url:
                github_status['target_url'] = codebuild_logs_url

            response = requests.post(
                full_url,
                json.dumps(github_status),
                headers=self.request_headers
            )

            LOGGER.info(
                'Successfully posted status to GitHub endpoint: ' +
                json.dumps(response, default=str)
            )
            return response

        except requests.exceptions.ConnectionError as error:
            raise error


    """Retrieves file contents of a given GitHub repository"""
    def get_file_content(
        self,
        github_full_repo_name: str,
        github_commit_sha: str,
        file_name: str
    ) -> dict:
        full_url = (
            f'{self.github_api_url}/repos/{github_full_repo_name}/'
            f'contents/{file_name}?ref={github_commit_sha}'
        )
        LOGGER.info(f'Retrieving repository contents(s) from GitHub endpoint "{full_url}"')

        try:
            self.request_headers['Accept'] = 'application/vnd.github.mercy-preview+json'
            response = requests.get(
                full_url,
                headers=self.request_headers
            )
            decoded_response = response.content.decode('utf8')
            LOGGER.info(
                'Successfully retrieved contents(s) from GitHub'
                 f'repository "{github_full_repo_name}": {decoded_response}'
            )
            content = json.loads(decoded_response).get('content')
            if content:
                content = base64.b64decode(content.replace('\n', ''))
                return content.decode('utf8').strip()
            return None

        except requests.exceptions.ConnectionError as error:
            raise error

    """Retrieves the topics of a given GitHub repository"""
    def get_topic(self, github_full_repo_name: str) -> dict:
        full_url = '{}/repos/{}/topics'.format(self.github_api_url, github_full_repo_name)
        LOGGER.info(
            "Retrieving repository topic(s) from GitHub endpoint '{}'".format(
                full_url
            )
        )

        try:
            """https://developer.github.com/v3/repos/#list-all-topics-for-a-repository
            Note: The topics property for repositories on GitHub is currently available for developers to preview.
            Warning: The API may change without advance notice during the preview period."""
            self.request_headers['Accept'] = 'application/vnd.github.mercy-preview+json'
            response = requests.get(
                full_url,
                headers=self.request_headers
            )
            decoded_response = response.content.decode('utf8').replace("'", '"')

            LOGGER.info(
                "Successfully retrieved topic(s) from GitHub repository '{}': ".format(github_full_repo_name) +
                decoded_response
            )
            return decoded_response

        except requests.exceptions.ConnectionError as error:
            raise error

    """Retrieves the statuses of a given GitHub repository"""
    def get_pr_statuses(self, github_full_repo_name: str, sha: str) -> str:
        full_url = f'{self.github_api_url}/repos/{github_full_repo_name}/statuses/{sha}'
        LOGGER.info(f"Checking statuse for GitHub endpoint '{full_url}'")

        try:
            self.request_headers['Accept'] = 'application/vnd.github.mercy-preview+json'
            response = requests.get(
                full_url,
                headers=self.request_headers
            )
            decoded_response = response.content.decode('utf8').replace("'", '"')

            LOGGER.info(
                "Successfully retrieved statuse(s) from GitHub repository '{}': ".format(github_full_repo_name) +
                decoded_response
            )
            return decoded_response

        except requests.exceptions.ConnectionError as error:
            raise error
