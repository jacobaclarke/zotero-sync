"""
Model with helper functions for making api calls
"""
import requests
import json
import click

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
    """

    def __init__(self, api_key: str, user_id: str):
        self.api_key = api_key
        self.base = f'https://api.zotero.org/users/{user_id}/'

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
                headers={
                    "Zotero-API-Version": version,
                    "Authorization": f"Bearer   {self.api_key}"
                },
                params={
                    'limit': '100',
                    'start': index
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
        click.echo(click.style('Data Loaded.', fg='green'))
        return final
