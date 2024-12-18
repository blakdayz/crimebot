import os
import click

from crimebot.obfuscator.wam_builder import WAMBuilder
from crimebot.obfuscator.wam_provider import WamProvider

@click.group()
def cli():
    pass

@cli.command('build')
@click.option('--output-dir', default='dist', help='The output directory for the final files.')
def build(output_dir: os.PathLike):
    """
    Builds the (not so) Weak Ass Malware Module (WAM) provider and its associated files.

    Args:
        output_dir (os.PathLike, optional): The output directory for the final files. Defaults to 'dist'.
    """
    WamProvider.build(output_dir)

@cli.command('clean')
def clean():
    """
    Cleans up any temporary files generated during the build process.
    """
    WamProvider.clean()

if __name__ == '__main__':
    cli()
