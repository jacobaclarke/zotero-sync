import click
from dataclasses import dataclass
from zotero_sync.api import ApiClient
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(filename='.zoterosync'))


@click.group()
def cli():
    """A command line tool for cleaning up zotfile directory.

    Paramaters can be passed as arguments or in a .zoterosync file.
    """
    pass


@dataclass
class pathsObj:
    computer_paths: list
    cloud_paths: list


def get_paths(file_dir: Path, client: ApiClient) -> pathsObj:
    """Returns both computer and cloud paths

    Args:
        file_dir (Path): location of zotfile directory
        client (ApiClient)

    Returns:
        pathsObj: A paths object
    """
    r = client.get_all_pages('items')
    cloud_paths = [path["data"]["path"]
                   for path in r if "path" in path["data"]]
    computer_paths = [path for path in file_dir.glob(
        "**/*.pdf") if "trash" not in str(path)]
    return pathsObj(cloud_paths=cloud_paths, computer_paths=computer_paths)


@cli.command()
@click.option('--file_dir',
              default=os.getenv('ZOTFILE_DIR'),
              type=click.Path(exists=True))
@click.option('--api_key',
              default=os.getenv('API_KEY'))
@click.option('--user_id',
              default=os.getenv('USER_ID'))
def trash(file_dir: click.Path, api_key: str, user_id: str):
    """Trash all files existing on system but not on cloud

    Args:
        file_dir (click.Path): location of zotfile directory
        api_key (str): zotero api key
        user_id (str): zotero user id
    """
    dotfile_explanation = (
        "This can be provided as an option or "
        "in a .zoterozync file as ZOTFILE_DIR")
    assert(file_dir is not None), (
        "No zotfile path was given. " + dotfile_explanation)
    assert(api_key is not None), (
        "No api key was given. " + dotfile_explanation)
    assert(user_id is not None), (
        "No user id was given. " + dotfile_explanation)
    client = ApiClient(api_key, user_id)
    file_dir = Path(file_dir)
    paths = get_paths(file_dir, client)
    computer_unique = [path for path in paths.computer_paths if str(
        path.absolute()) not in paths.cloud_paths]
    if click.confirm(
         f"Are you sure you want to trash {len(computer_unique)} variables?"):
        for path in computer_unique:
            trash = file_dir / 'trash'
            trash.mkdir(parents=True, exist_ok=True)
            path.rename(trash / path.name)


if __name__ == "__main__":
    cli()
