import datetime, os, shutil, fish_utils, subprocess
from pathlib import Path

DATA_PATHS = [
    Path('trackers', 'fishing.json'),
    Path('trackers', 'specials.json'),
    Path('trackers', 'total_triggers.txt'),
    Path('trackers', 'user_triggers.json'),
]

def shell_command(input: str) -> None:
    try:
        command = input.strip().split(' ')
        output = subprocess.run(command, capture_output=True, text=True, shell=True)
        print(output.stdout)

    except Exception as err:
        print(f'exception: {err}')

def make_backup() -> None:
    folder_name = str(datetime.datetime.now().strftime("%m-%d-%Y %I.%M.%S %p"))
    if not json_utils.FISHING_ENABLED:
        folder_name = f'TESTDATA {folder_name}'

    os.mkdir(Path("trackers_backup", folder_name))

    for path in DATA_PATHS:
        shutil.copy(path, Path("trackers_backup", folder_name, path.name))

def commit_and_push_backups() -> None:
    shell_command('git add trackers_backup/')
    shell_command('git commit -m Backup')
    shell_command('git push')