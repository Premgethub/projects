import os
from dotenv import load_dotenv
import chromadb
from folder_structure import folder_structure_class
from detect_changes import detect_changes_class
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
SOURCE_DIRECTORY = os.getenv("SOURCE_DIRECTORY")
STRUCTURE_DIRECTORY = os.getenv("STRUCTURE_DIRECTORY")
VECTOR_PERSIST_DIRECTORY = os.getenv("VECTOR_PERSIST_DIRECTORY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
TAG_NAME = os.getenv("TAG_NAME")

root_directory = os.path.basename(os.path.normpath(SOURCE_DIRECTORY))

def create_json_structure(folder_structure_object, detect_changes_object):
    folder_structure = folder_structure_object.create_folder_structure_json(SOURCE_DIRECTORY)
    folder_structure_object.write_json_file(folder_structure, STRUCTURE_DIRECTORY)
    folder_json_data = folder_structure_object.read_json_file(STRUCTURE_DIRECTORY)
    subfolders, files_paths = folder_structure_object.extract_subfolder_and_files(folder_json_data[root_directory])
    vector_db_file_creation(subfolders, files_paths)
    print("Json structure is created with necessary files")
    return None

def update_json_structure(folder_structure_object, detect_changes_object):
    if not os.path.exists(STRUCTURE_DIRECTORY):
        create_json_structure(folder_structure_object, detect_changes_object)
    else:
        previous_json_structure = folder_structure_object.read_json_file(STRUCTURE_DIRECTORY)
        current_json_structure = folder_structure_object.create_folder_structure_json(SOURCE_DIRECTORY)

        if previous_json_structure != current_json_structure:
            creation_subfolders = []
            creation_files_count = 0
            print("1111111",folder_structure_object, previous_json_structure)
            subfolders_prev, files_paths_prev = detect_changes_object.get_folder_data(folder_structure_object, previous_json_structure)
            subfolders_curr, files_paths_curr = detect_changes_object.get_folder_data(folder_structure_object, current_json_structure)
            added_subfolders, removed_subfolders, added_files, deleted_files = detect_changes_object.changes(
                subfolders_prev, files_paths_prev, subfolders_curr, files_paths_curr)

            if added_subfolders:
                creation_subfolders += added_subfolders
            for key, value in added_files.items():
                if value:
                    creation_files_count += 1
                    creation_subfolders.append(key)
            
            creation_subfolders = list(set(creation_subfolders))

            if creation_subfolders:
                vector_db_file_creation(creation_subfolders, added_files, creation_files_count)
            if removed_subfolders:
                vector_db_deletion(removed_subfolders)
    
            folder_structure_object.write_json_file(current_json_structure, STRUCTURE_DIRECTORY)
            print("The json folder structure has been updated !!!")
        else:
            print("No changes detected in folder structure !!!")
        return None

def vector_db_file_creation(subfolders, files_paths, count=1):
    client = chromadb.PersistentClient(path=VECTOR_PERSIST_DIRECTORY)
    embeddings = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
    if count:
        for subfolder in subfolders:
            document_contents = SimpleDirectoryReader(os.path.join(SOURCE_DIRECTORY, 'prem')).load_data()
            db_collection_name = client.get_or_create_collection(TAG_NAME)
            vector_store = ChromaVectorStore(chroma_collection=db_collection_name)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            service_context = ServiceContext.from_defaults(llm=None, embed_model=embeddings)
            index = VectorStoreIndex.from_documents(document_contents, storage_context=storage_context, service_context=service_context)
            collection = db_collection_name.get()
            files_added = [metadata['file_name'] for metadata in collection['metadatas']]
            print(list(set(files_added)))
    else:
        for subfolder in subfolders:
            db_collection_name = client.get_or_create_collection(TAG_NAME)
            print(f'collection "{subfolder}" is created !!!')

def vector_db_deletion(subfolders):
    client = chromadb.PersistentClient(path=VECTOR_PERSIST_DIRECTORY)
    for subfolder in subfolders:
        client.delete_collection(subfolder)
        print(f'{subfolder} collection has been deleted !!!')

if __name__ == "__main__":
    client = chromadb.PersistentClient(path=VECTOR_PERSIST_DIRECTORY)

    folder_structure_object = folder_structure_class()
    detect_changes_object = detect_changes_class()

    update_json_structure(folder_structure_object, detect_changes_object)

    # collection = client.list_collections()
    # print(collection)
