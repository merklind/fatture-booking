from pathlib import Path
from typing import List

_DESIRED_EXT = 'pdf'


def find_all_files(root_folder: Path) -> List[Path]:
    all_files = []

    for file in root_folder.glob(f'*/*.{_DESIRED_EXT}'):
        all_files.append(file)

    return all_files
