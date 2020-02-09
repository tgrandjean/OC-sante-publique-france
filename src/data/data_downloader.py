# -*- coding: utf-8 -*-
"""DataDownloader: module used for data downloading."""

import logging
import os
import requests
import subprocess
import tarfile
from tqdm import tqdm

logger = logging.getLogger(__file__)


class DataDownloader(object):
    """DataDownloader. This class is used to fetch the data from the
    openfoodfacts's website.

    :usage:
        >>> data_downloader = DataDownloader('path/to/data_dir')
        >>> data_downloader.run()

    :args:
        data_path (str, path like) : destination folder for downloaded files
        frmt (str) : should be one of "csv" or "mongodb". Format of downloaded
        file. Optional, default=csv
    """

    BASE_URL = 'https://static.openfoodfacts.org/data/'
    MONGO_URL = BASE_URL + 'openfoodfacts-mongodbdump.tar.gz'
    CSV_URL = BASE_URL + 'en.openfoodfacts.org.products.csv'

    def __init__(self, data_path, frmt='csv', **kwargs):
        logger.debug('Init DataDownloader object with arg : %s, %s, %s',
                     data_path, frmt, kwargs)
        self.data_format = frmt.lower()
        self.data_path = os.path.join(data_path, 'raw')
        if self.data_format == 'csv':
            self.output_filepath = os.path.join(self.data_path, 'products.csv')
        elif self.data_format == 'mongodb':
            self.output_filepath = os.path.join(self.data_path,
                                                'mongodbdump.tar.gz')
            self.container_name = kwargs.get('container_name')
            if not self.container_name:
                self.container_name = 'openfoodfacts'
            self.dump_location =  os.path.join(data_path, 'dump')

    @property
    def _headers(self):
        """Return a dict with options for requests's headers."""
        return {"User-Agent": "Mozilla/5.0",'Accept-Encoding' : None}

    def init_data_dir(self):
        """Initialize empty directories for data."""
        logger.info("Init data directories.")
        data_dirs = [
                     'interim',
                     'processed',
                     'raw'
                     ]
        if not os.path.exists(self.data_path):
            logger.info('Creating directories.')
            os.mkdir(self.data_path)
            for dir in data_dirs:
                os.mkdir(os.path.join(self.data_path, dir))
        else:
            logger.info('Data directories already exists.')

    def _fetch_data(self):
        """Method used to fetch the data on the website using requests."""
        logger.info('Start download, this can take a while...')
        if self.data_format == 'csv':
            response = requests.get(self.CSV_URL, stream=True,
                                    headers=self._headers)
        elif self.data_format == 'mongodb':
            response = requests.get(self.MONGO_URL, stream=True,
                                    headers=self._headers)
        else:
            raise ValueError("Wrong format argument.")
        content_length = int(response.headers.get('content-length'))
        # Use tqdm to monitore the progress of the downloading progress
        with open(self.output_filepath, 'wb') as file:
            chunk_size = 1024 * 1024
            for data in tqdm(response.iter_content(chunk_size=chunk_size),
                             total=content_length // chunk_size,
                             desc='Download data',
                             unit='Mo'):
                file.write(data)
        logger.info('Download finished.')

    def _extract_mongo_dump(self, purge=True):
        """Method to extract the content of the tarfile.

        Used only for mongodb dump.
        """
        logger.info("Extracting the dump from the tar archive.")
        with tarfile.open(self.output_filepath, 'r:gz') as tar:
            tar.extractall(self.data_path)
        if purge:
            os.remove(self.output_filepath)
        logger.info("Extraction done.")

    def _start_mongo_docker_instance(self):
        """Wrapper method to start a docker container.

        This will start a new docker container using mongodb image.
        This imply that you have docker installed.
        """
        logger.info("Start a docker instance.")
        ports = '27017-27019:27017-27019'
        volume = self.dump_location + ':/var/dump'
        cmd = f'docker run -d -p {ports} -v {volume} \
        --name {self.container_name} mongo'
        logging.info('Executing : %s', cmd)
        with subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE) as proc:
            for line in iter(proc.stdout.readline, b''):
                logger.info(line.decode('ascii'))
            for line in iter(proc.stderr.readline, b''):
                logger.error(line.decode('ascii'))

    def _load_dumb_in_mongo(self):
        """Wrapper method to restore the database.

        This will reload the database's dump in the docker instance.
        """
        logger.info("Restoring data in mongodb. This will take a while.")
        db = "foodfacts"
        collection = "products"
        dump_location = '/var/dump/off/products.bson'
        mongo_cmd = f'mongorestore -d {db} -c {collection} {dump_location}'
        cmd = f'docker exec {self.container_name} {mongo_cmd}'
        logging.info('Executing : %s', cmd)
        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as proc:
            for line in iter(proc.stdout.readline, b''):
                logging.info(line.decode('ascii'))
            for line in iter(proc.stderr.readline, b''):
                logging.error(line.decode('ascii'))
        logger.info("Database successfully restored.")

    def run(self):
        """Lauch the full process."""
        self.init_data_dir()
        self._fetch_data()
        if self.data_format == 'mongodb':
            self._extract_mongo_dump()
            self._start_mongo_docker_instance()
            self._load_dumb_in_mongo()
