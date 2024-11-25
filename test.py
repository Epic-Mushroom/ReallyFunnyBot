import json
from pathlib import Path

test_path = Path('trackers\\test.json')

if __name__ == '__main__':
    with open(test_path, 'r+') as file:
        dick = json.load(file)
        del dick['b']
        file.seek(0)
        json.dump(dick, file, indent=4)
        file.truncate()