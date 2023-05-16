import os

def create_missing_folder(path_file):
    directory = os.path.dirname(path_file)
    if directory == '':
        return
    if not os.path.exists(directory):
        os.makedirs(directory)