import os
import tarfile

from tqdm import tqdm
from urllib.request import urlretrieve


class DLProgress(tqdm):
    last_block = 0

    def hook(self, block_num=1, block_size=1, total_size=None):
        self.total = total_size
        self.update((block_num - self.last_block) * block_size)
        self.last_block = block_num


def download_dataset_and_uncompress(dataset_dir: str,
                                    url: str,
                                    filename: str=None):
    """Downloads and uncompresses dataset from url, expects tar.gz file

    """
    filename = filename or url.split('/')[-1]

    if not os.path.isfile(filename):
        with DLProgress(unit='B',
                        unit_scale=True,
                        miniters=1,
                        desc='download dataset') as pbar:
            urlretrieve(
                url,
                filename,
                pbar.hook)

    if not os.path.exists(dataset_dir):
        os.mkdir(dataset_dir)

    with tarfile.open(filename, 'r:gz') as tar:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, dataset_dir)
        tar.close()

    statinfo = os.stat(filename)
    print('Successfully downloaded', filename, statinfo.st_size, 'bytes.')


def create_checkpoints_dir(checkpoints_dir: str='checkpoints/'):
    """Creates the checkpoints directory if it does not exist

   """
    if not os.path.exists(checkpoints_dir):
        os.makedirs(checkpoints_dir)
