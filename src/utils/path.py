from pathlib import Path
from typing import List

_DESIRED_EXT = 'pdf'


def find_all_files(root_folder: Path) -> List[Path]:
    """
    Recursively find all PDF files in the given folder and its subfolders.
    
    Args:
        root_folder (Path): The root folder to start searching from
        
    Returns:
        List[Path]: List of paths to all PDF files found
    """
    all_files = []
    
    # Use rglob to recursively search for PDF files
    for file in root_folder.rglob(f'*.{_DESIRED_EXT}'):
        if file.is_file():  # Ensure we only get files, not directories
            all_files.append(file)
    
    return sorted(all_files)  # Sort files for consistent processing order
