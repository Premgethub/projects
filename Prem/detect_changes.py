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
        return subfolders, files_paths


class detect_changes_class:
    @staticmethod
    def save_previous(handler, data):
        handler.previous_structure = data

    @staticmethod
    def changes(subfolders1, files_paths1, subfolders2, files_paths2):
        added_subfolders = set(subfolders2) - set(subfolders1)
        removed_subfolders = set(subfolders1) - set(subfolders2)

        added_files = {}
        deleted_files = {}

        for folder in subfolders2:
            added_files[folder] = [os.path.abspath(file) for file in list(set(files_paths2[folder]) - set(files_paths1.get(folder, [])))]
            deleted_files[folder] = [os.path.abspath(file) for file in list(set(files_paths1.get(folder, [])) - set(files_paths2[folder]))] 
        return list(added_subfolders), list(removed_subfolders), added_files, deleted_files 

    @staticmethod
    def confirm():
        user_input = input("Changes detected. Overwrite the external JSON file? (yes/no): ").lower()
        return user_input == 'yes'

    @staticmethod
    def get_folder_data(handler, json_data):
        subfolders, files_paths = handler.extract_subfolder_and_files(json_data['data'])
        return subfolders, files_paths
    
if __name__ == "__main__":
    # Initialize handler
    folder_structure_object = folder_structure_class()

    # Read previous folder structure
    prev_json_data = folder_structure_object.read_json_file(STRUCTURE_DIRECTORY)

    # Read current folder structure
    current_data = folder_structure_object.create_folder_structure_json(SOURCE_DIRECTORY)

    # Save current structure as the previous one within the script
    detect_changes_class.save_previous(folder_structure_object, current_data)

    # Get subfolders and files paths for previous and current data
    subfolders_prev, files_paths_prev = detect_changes_class.get_folder_data(folder_structure_object, prev_json_data)
    subfolders_curr, files_paths_curr = detect_changes_class.get_folder_data(folder_structure_object, current_data)

    # Detect changes
    added_subfolders, removed_subfolders, added_files, deleted_files = detect_changes_class.changes(
        subfolders_prev, files_paths_prev, subfolders_curr, files_paths_curr
    )

    print("Added Subfolders:", added_subfolders)
    print("Removed Subfolders:", removed_subfolders)

    print("\nAdded Files:")
    for folder, files in added_files.items():
        print(f"{folder}: {files}")

    print("\nDeleted Files:")
    for folder, files in deleted_files.items():
        print(f"{folder}: {files}")

    # Ask user for confirmation to overwrite the external JSON file
    if added_subfolders or removed_subfolders or added_files or deleted_files:
        if detect_changes_class.confirm():
            folder_structure_object.write_json_file(current_data, STRUCTURE_DIRECTORY)
            print("External JSON file overwritten.")
        else:
            print("Changes not saved.")
