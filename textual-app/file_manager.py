import json

FILENAME = "files.json"

# loading all files
def load_files():
    with open(FILENAME, "r") as files_json:
        # parse the file content into a dictionary
        loaded_files = json.load(files_json)
    return loaded_files


# saving all files
def save_files(files):
    with open(FILENAME, "w") as files_json:
        # dump the files dictionary as JSON
        json.dump(files, files_json, indent=4)
