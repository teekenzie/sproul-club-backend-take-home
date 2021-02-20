import json

# read textbook.json and return it
def get_texbooks():
    with open('textbooks.json') as f:
        return json.load(f)