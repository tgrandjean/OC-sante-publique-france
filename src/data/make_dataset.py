# -*- coding: utf-8 -*-
"""make_dataset: script to run to download data.

:usage:
    $ src/data/make_dataset.py ./data/raw/
"""
import click
import logging
from pathlib import Path

from src.data.data_downloader import DataDownloader

@click.command()
@click.argument('input_filepath', type=click.Path())
@click.option('-f', '--format', type=click.Choice(['csv', 'mongodb']),
              default='csv')
def main(input_filepath, format):
    """Download data."""
    logger = logging.getLogger(__name__)
    logger.info('making data set.')
    input_filepath = Path(input_filepath).resolve().parents[0]
    data_downloader = DataDownloader(input_filepath, frmt=format)
    data_downloader.run()


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    main()
