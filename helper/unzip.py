import zipfile
import os

def unzip_file(zip_file, destination_folder):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)

if __name__ == "__main__":
    # Specify the path to the zip file and the destination folder
    zip_file_path = '../common_voice.zip'
    destination_folder = '../common_voice'

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    unzip_file(zip_file_path, destination_folder)
