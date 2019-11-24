# -*- coding: utf-8 -*-
import click
import logging
import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import requests
import subprocess
import tarfile
from tqdm import tqdm


URL = 'https://static.openfoodfacts.org/data/'
DUMP_URL = URL + 'openfoodfacts-mongodbdump.tar.gz'
CSV_URL = URL + 'en.openfoodfacts.org.products.csv'

def download_database(url, output_filepath):
    """This will download the database dump from openfoodfacts."""
    logging.info('Start download, this can take a while...')
    response = requests.get(url, stream=True,
                            headers={"User-Agent": "Mozilla/5.0",
                                     'Accept-Encoding' : None})
    content_length = int(response.headers.get('content-length'))
    with open(output_filepath, 'wb') as file:
        chunk_size = 1024 * 1024
        for data in tqdm(response.iter_content(chunk_size=chunk_size),
                         total=content_length // chunk_size,
                         desc='Download data',
                         unit='Mo'):
            file.write(data)

def extract(filepath, purge=True):
    """extract dataset."""
    logging.info("extract the dataset. %s", filepath)
    output_path = '/'.join(filepath.split('/')[:-1])
    logging.info("output_path : %s", output_path)
    with tarfile.open(filepath, 'r:gz') as tar:
        tar.extractall(output_path)
    if purge:
        os.remove(filepath)
    logging.info("Extraction finished. ")

def init_data_dir(filepath):
    """Create empty dir if they not exists"""
    logging.info("Init data directories")
    root_dir = '/'.join(filepath.split('/')[:-1])
    data_dirs = ['external',
                 'interim',
                 'processed',
                 'raw']
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)
        for dir in data_dirs:
            os.mkdir(os.path.join(root_dir, dir))
    else:
        print('already exists')

def start_mongo_docker_instance(dump_location, name='mongodb'):
    ports = '27017-27019:27017-27019'
    volume = dump_location + ':/var/dump'
    cmd = f'docker run -d -p {ports} -v {volume} --name {name} mongo'
    logging.info('Executing : %s', cmd)
    with subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE) as proc:
        for line in iter(proc.stdout.readline, b''):
            logging.info(line.decode('ascii'))
        for line in iter(proc.stderr.readline, b''):
            logging.error(line.decode('ascii'))


def load_dumb_in_mongo(container_name='mongodb'):
    db = 'foodfacts'
    collection = 'products'
    dump_location = '/var/dump/off/products.bson'
    mongo_cmd = f'mongorestore -d {db} -c {collection} {dump_location}'
    cmd = f'docker exec {container_name} {mongo_cmd}'
    logging.info('Executing : %s', cmd)
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as proc:
        for line in iter(proc.stdout.readline, b''):
            logging.info(line.decode('ascii'))
        for line in iter(proc.stderr.readline, b''):
            logging.error(line.decode('ascii'))


@click.command()
@click.argument('input_filepath', type=click.Path())
@click.argument('output_filepath', type=click.Path())
@click.option('--data-type', type=click.Choice(['csv', 'mongo'], case_sensitive=False))
def main(input_filepath, output_filepath, data_type):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making data set.')
    if not os.path.exists(os.path.join(input_filepath, 'dump')):
        logger.info("Dataset not already downloaded.")
        init_data_dir(input_filepath)
        if data_type == "csv":
            download_database(CSV_URL, os.path.join(input_filepath,
                                                    'products.csv'))
        else:
            tar_filepath = os.path.join(input_filepath,
                                        'mongodbdump.tar.gz')
            download_database(URL, tar_filepath)
            extract(tar_filepath)
            dump_location = os.path.join(os.path.abspath(input_filepath), 'dump')
            start_mongo_docker_instance(dump_location)
            load_dumb_in_mongo()
    else:
        logger.info('Dataset is already in raw data dir')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
