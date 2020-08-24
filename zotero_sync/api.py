"""
Model with helper functions for making api calls
"""
import requests
import json
import click
from pathlib import Path

version = '3'


class ApiClient:
    """
    Client for making calls to the zotero api

    Args:
        api_key (str): a user generated api string
        user_id (str): the zotero user id to use as part of the base url

    Attributes:
        api_key (str): see api key arg
        base (str): base url string used for http requests
        headers (dict): Headers for making requests to zotero api
    """

    def __init__(self, api_key: str, user_id: str):
        self.api_key = api_key
        self.base = f'https://api.zotero.org/users/{user_id}/'
        self.headers = {
            "Zotero-API-Version": version,
            "Authorization": f"Bearer   {self.api_key}"
        }

    def get_page(self, index: int, path: str) -> []:
        """
        Gets a single page of API response

        Args:
            index (int): The starting index for results. 
            path (str): The api path to make a request to

        Returns:
            list: JSON parsed text attribute of the response
        """
        return json.loads(
            requests.get(
                self.base + path,
                headers=self.headers,
                params={
                    'limit': '100',
                    'start': index,
                    'itemType':'attachment'
                }).text)

    def get_all_pages(self, path: str = ''):
        """
        Gets all available pages from zotero

        Args:
            path (str): The zotero api path to make a request to

        Returns:
            list: The JSON parsed text attribute of all pages of the reponse.
        """
        click.echo(click.style('Loading zotero web data...', fg='red'))
        index = 0
        final = []
        res = self.get_page(index, path)
        while len(res) != 0:
            final += res
            index += 100
            res = self.get_page(index, path)
            click.echo(click.style(
                f"Retrieved {index} online files so far...\r", fg="blue"),
                nl=False)
        click.echo(click.style(
            f"Retrieved {len(final)} online files in total.    ", fg="green"))
        return final

    def create_item(self, path: Path):
        template = [
            {
                "itemType": "book",
                "title": str(path.stem),
                "tags": [
                    {"tag": "folder_upload"}
                ]
            }
        ]
        res = requests.post(self.base + 'items',
                            headers=self.headers,
                            data=json.dumps(template))
        
        assert (res.status_code == 200), 'Received an error html response'
        parentItem = json.loads(res.text)["success"]["0"]
        template = [
            {
                "itemType": "attachment",
                "linkMode": "linked_file",
                "title": str(path.stem),
                "parentItem": parentItem,
                "path": str(path),
                "tags": [
                    {"tag": "folder_upload"}
                ],
                "contentType": "application/pdf"
            }
        ]
        res = requests.post(self.base + 'items',
                            headers=self.headers,
                            data=json.dumps(template))
        assert (res.status_code == 200), 'Received an error html response'
