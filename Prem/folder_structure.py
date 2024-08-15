import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
SOURCE_DIRECTORY = os.getenv("SOURCE_DIRECTORY")
STRUCTURE_DIRECTORY = os.getenv("STRUCTURE_DIRECTORY")

class folder_structure_class:
    @staticmethod
    def create_folder_structure_json(source_directory):
        folder_structure = {}
        root_directory = os.path.basename(os.path.normpath(source_directory))
        folder_structure[root_directory] = {}

        for root, dirs, files in os.walk(source_directory):
            current_folder = folder_structure[root_directory]
            path = os.path.relpath(root, source_directory).split(os.sep)

            for folder in path:
                current_folder = current_folder.setdefault(folder, {})

            current_folder['files'] = [os.path.join(root, file) for file in files]

        return folder_structure

    @staticmethod
    def write_json_file(data, output_file=STRUCTURE_DIRECTORY):
        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4, sort_keys=True)

    @staticmethod
    def read_json_file(file_path):
        try:
            with open(file_path, 'r') as json_file:
                json_data = json.load(json_file)
            return json_data
        except FileNotFoundError:
            print(f"Error: File not found at path '{file_path}'.")
        except json.JSONDecodeError:
            print(f"Error: Unable to decode JSON in file at path '{file_path}'. Please check if the file contains valid JSON.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def extract_subfolder_and_files(json_data):
        subfolders = []
        files_paths = {}

        for folder_name, folder_data in json_data.items():
            if folder_name != '.':
                subfolders.append(folder_name)
                files_paths[folder_name] = folder_data.get('files', [])
        # print("subfolders : ",subfolders)
        # print("files : ",files_paths)
        return subfolders, files_paths


if __name__ == "__main__":
    folder_handler = folder_structure_class()

    # Create folder structure in JSON
    folder_structure_data = folder_handler.create_folder_structure_json(SOURCE_DIRECTORY)

    # Write JSON to a file
    folder_handler.write_json_file(folder_structure_data)

    # Read JSON from a file
    json_data = folder_handler.read_json_file(STRUCTURE_DIRECTORY)

    if json_data is not None:
        # Extract subfolders and files
        subfolders, files_paths = folder_handler.extract_subfolder_and_files(json_data['data'])
        print("subfolders : ",subfolders)
        for folder, files in files_paths.items():
            print(f"{folder}: {files}")
