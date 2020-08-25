"""
Contains all command line options for zotero_sync
"""
import click
import os
from pathlib import Path
from zotero_sync.api import get_paths
from zotero_sync.fs import process_pdfs
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(filename='.zoterosync'))


@click.group()
def cli():
    pass


@cli.command()
@click.option('--file_dir',
              default=os.getenv('ZOTFILE_DIR'),
              type=click.Path(exists=True))
def optimize(file_dir):
    """
    Optimize file size of all pdfs

    Args:
        file_dir (click.Path): location of zotfile dir
    """
    click.echo(click.style('Optimizing files...', fg='blue'))
    process_pdfs(file_dir, (
        'gs -sDEVICE=pdfwrite'
        ' -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook'
        ' -dNOPAUSE -dQUIET -dBATCH -sOutputFile={output} {input}'))


@cli.command()
@click.option('--file_dir',
              default=os.getenv('ZOTFILE_DIR'),
              type=click.Path(exists=True))
def ocr(file_dir):
    """
    Optimize file size of all pdfs

    Args:
        file_dir (click.Path): location of zotfile dir
    """
    click.echo(click.style('Running OCR on files...', fg='blue'))
    process_pdfs(
        file_dir,
        'python -m ocrmypdf --tesseract-timeout 10 {input} {output}')


@cli.command()
@click.option('--file_dir',
              default=os.getenv('ZOTFILE_DIR'),
              type=click.Path(exists=True))
@click.option('--api_key',
              default=os.getenv('API_KEY'))
@click.option('--user_id',
              default=os.getenv('USER_ID'))
def trash(file_dir: click.Path, api_key: str, user_id: str):
    """
    Trash all files existing on system but not on cloud

    Args:
        file_dir (click.Path): location of zotfile dir
        api_key (str): zotero api key
        user_id (str): zotero user id
    """
    computer_unique, _ = get_paths(file_dir, api_key, user_id)
    if click.confirm(
        f"Are you sure you want to trash {len(computer_unique)} files?",
        default=True,
            abort=True):
        for path in computer_unique:
            trash = file_dir / 'trash'
            trash.mkdir(parents=True, exist_ok=True)
            path.rename(trash.absolute() / path.name)
        click.echo(click.style('Successfully deleted files!', fg='green'))


@cli.command()
@click.option('--file_dir',
              default=os.getenv('ZOTFILE_DIR'),
              type=click.Path(exists=True))
@click.option('--api_key',
              default=os.getenv('API_KEY'))
@click.option('--user_id',
              default=os.getenv('USER_ID'))
def upload(file_dir: click.Path, api_key: str, user_id: str):
    """
    Adds all files from local folders to zotero.

    Args:
        file_dir (click.Path): location of zotfile dir
        api_key (str): zotero api key
        user_id (str): zotero user id
    """
    computer_unique, client = get_paths(Path(file_dir), api_key, user_id)
    if click.confirm(
        f"Are you sure you upload {len(computer_unique)} files?",
        abort=True,
            default=True):
        with click.progressbar(computer_unique) as paths:
            for path in paths:
                client.create_item(path)
    click.echo(click.style('Successfully uploaded files!', fg='green'))
