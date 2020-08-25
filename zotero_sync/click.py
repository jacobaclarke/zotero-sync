import click
import subprocess
import os
from pathlib import Path
from zotero_sync.api import ApiClient
from dotenv import load_dotenv, find_dotenv
from shutil import copy
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
    """
    click.echo(click.style('Optimizing files...', fg='blue'))
    process_pdfs(file_dir, (
        'gs -sDEVICE=pdfwrite'
        ' -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook'
        ' -dNOPAUSE -dQUIET -dBATCH -sOutputFile={output} {input}'))


def process_pdfs(file_dir: click.Path, command: str):
    """
    Run a script on all pdf files in subfolders

    Args:
        file_dir (click.Path): Path of pdf files
        command (str): A string containing command to
            be exected with {input} and {output} files.
    """
    infile = 'infile.pdf'
    temp = "temppdf.pdf"
    count = 0
    for path in Path(file_dir).rglob('*.pdf'):
        if path.name == "infile.pdf":
            continue
        count += 1
        click.echo(click.style(f"Processed {count} so far\r", fg="blue"),
                   nl=False)
        click.echo(click.style(f"Processing {path.name}", fg="red"))
        os.chdir(path.resolve().parent)
        copy(path.resolve(), infile)
        try:
            subprocess.check_call(
                [item.format(input=infile, output=temp)
                 for item in command.split(' ')])
        except subprocess.CalledProcessError:
            continue
            # if e.returncode not in [6, 8, 10]:
        (path.resolve().parent / temp).rename(path.resolve())
        Path(infile).unlink()
    click.echo(click.style(f'Finished Processing {count} files!', fg='green'))


@cli.command()
@click.option('--file_dir',
              default=os.getenv('ZOTFILE_DIR'),
              type=click.Path(exists=True))
def ocr(file_dir):
    """
    Optimize file size of all pdfs
    """
    click.echo(click.style('Running OCR on files...', fg='blue'))
    process_pdfs(
        file_dir,
        'python -m ocrmypdf --tesseract-timeout 10 {input} {output}')


def get_paths(file_dir: Path, api_key: str, user_id: str) -> (list, ApiClient):
    """Returns both computer and cloud paths

    Args:
        file_dir (Path): location of zotfile directory
        client (ApiClient)

    Returns:
        list: A list of uniqe paths on the computer.
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
    r = client.get_all_pages('items')
    cloud_paths = [path["data"]["path"]
                   for path in r if "path" in path["data"]]
    computer_paths = [path for path in file_dir.glob(
        "**/*.pdf") if "trash" not in str(path)]
    computer_unique = [path for path in computer_paths if str(
        path.absolute()) not in cloud_paths]
    return computer_unique, client


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
        ctx: click context
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
        ctx: click context
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