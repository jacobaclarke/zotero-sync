"""
Module for filesystem processing
"""

import click
import subprocess
import os
from pathlib import Path
from shutil import copy


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
