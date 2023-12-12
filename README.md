# Git from Scratch

This project showcases various Git commands designed to streamline version control and enhance our development workflow. Each command serves a specific purpose, contributing to efficient codebase management.

## Project Overview

The project consists of:

- **ualg File**: An executable file.
  
- **models Folder**:
  - `helper.py`: Contains helper functions.
  - `models.py`: Includes model implementations.

- **commands Folder**: Contains Python files implementing Git commands.
   - `cat_file.py`
   - `initialize.py`
   - `ls_tree.py`
   - `show_ref.py`
   - `hash_object.py`
   - `log.py`


## Implemented Commands and Their Functionalities

1. Initialization (init command):
   Sets up a new, empty repository at a specified or default directory location, laying the groundwork for version control and subsequent development activities.
   
2. File Information (cat-file command):
    Retrieves detailed commit information like an associated tree, parent commit, author, committer, timestamp, and commit message without altering the repository.

3. Object Hashing (hash-object command):
    Generates unique identifiers for objects or files, aiding effective change tracking and data integrity verification.

4. Commit History (log command):
    Creates a visual commit history representation using Graphviz, encapsulating project evolution, branches, commits, and merges in a PDF format.

5. Listing Files (ls-tree command):
    Provides a structured view of files and directories within the repository, aiding in efficient file management.

6. List References (show-ref command):
    Displays repository references (branches, tags, etc.) alongside their respective commit hashes, aiding in understanding and tracking the repository's structure.
