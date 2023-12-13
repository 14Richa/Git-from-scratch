from models import models
import os


def add_ls_tree_subparser(subparsers):
    argsp = subparsers.add_parser("ls-tree", help="Pretty-print a tree object.")
    
    argsp.add_argument("-r", dest="recursive", action="store_true", help="Recurse into sub-trees")
    argsp.add_argument("tree", help="A tree-ish object.")


def list_files_in_tree(args):
    repository = models.repo_find()
    list_tree_contents(repository, args.tree, args.recursive)

def list_tree_contents(repository, reference, is_recursive=None, path_prefix=""):
    tree_sha = models.object_find(repository, reference, object_type=b"tree")
    tree_object = models.object_read(repository, tree_sha)

    for tree_item in tree_object.items:
        mode_prefix = "0" * (6 - len(tree_item.mode)) + tree_item.mode.decode("ascii")
        item_type = get_item_type(tree_item.mode)

        if not (is_recursive and item_type == 'tree'):
            print(f"{mode_prefix} {item_type} {tree_item.sha}\t{os.path.join(path_prefix, tree_item.path)}")
        else:
            list_tree_contents(repository, tree_item.sha, is_recursive, os.path.join(path_prefix, tree_item.path))

def get_item_type(mode):
    type_code = mode[0:1] if len(mode) == 5 else mode[0:2]

    if type_code == b'04':
        return "tree"
    elif type_code == b'10':
        return "blob"
    elif type_code == b'12':
        return "blob"  
    elif type_code == b'16':
        return "commit" 
    
