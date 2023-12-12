from models import models

def add_show_ref_subparser(subparsers):
    argsp = subparsers.add_parser("show-ref", help="List references.")

def display_references(args):
    repository = models.repo_find()
    refs = models.ref_list(repository)
    display_repository_refs(repository, refs, prefix="refs")

def display_repository_refs(repository, refs, with_hash=True, prefix=""):
    for key, value in refs.items():
        if isinstance(value, str):
            hash_prefix = value + " " if with_hash else ""
            path_prefix = prefix + "/" if prefix else ""
            print(f"{hash_prefix}{path_prefix}{key}")
        else:
            new_prefix = f"{prefix}/{key}" if prefix else key
            display_repository_refs(repository, value, with_hash=with_hash, prefix=new_prefix)


