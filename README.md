# Git from Scratch

## Overview

This project showcases various Git commands designed to streamline version control and enhance our development workflow. Each command serves a specific purpose, contributing to efficient codebase management.

## Project Structure

```
├── ualg # An executable file.
├── Models
│ ├── helper.py # Contains helper functions.
│ └── models.py # Includes model implementations.
└── Commands
    ├── cat_file.py
    ├── initialize.py
    ├── ls_tree.py
    ├── show_ref.py
    ├── hash_object.py
    └── log.py
```

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

## Running Commands 

**Initialization (init command)** : To initialize a new repository

```$ ./ualg init <directory> ``` 

**File Information (cat-file command)** : To retrieve detailed commit information

```$ ./ualg cat-file -commit <commit-hash>```

**Object Hashing (hash-object command)** : To generate unique identifiers for files

```$ ./ualg hash-object <file>```

**Listing Files (ls-tree command)** : To view files and directories in the repository

``` $ ./ualg ls-tree -r <branch>```

**List References (show-ref command)** : To display repository references and their commit hashes

``` $ ./ualg show-ref```

**Commit History (log command)** : To generate a visual commit history representation

- Generate the log file: ```$ ./ualg log > log.dot ```
- Convert the log file to PDF using Graphviz: ```$ dot -O -Tpdf log.dot```