from models import models

def add_hash_object_subparser(subparsers):
    argsp = subparsers.add_parser(
        "hash-object",
        help="Compute object ID and optionally creates a blob from a file"
    )

    argsp.add_argument("-t",
                       metavar="type",
                       dest="type",
                       choices=["blob", "commit", "tag", "tree"],
                       default="blob",
                       help="Specify the type")

    argsp.add_argument("-w",
                       dest="write",
                       action="store_true",
                       help="Actually write the object into the database")

    argsp.add_argument("path",
                       help="Read object from <file>")

def hash_object_command(args):
    print(f"File path: {args.path}")
    if args.write:
        repository = models.repo_find()
    else:
        repository = None

    with open(args.path, "rb") as fd:
        commit_id = models.object_hash(fd, args.type.encode(), repository)
        print("SHA:", commit_id)

def object_hash(fd, object_type, repository=None):
    data = fd.read()
    obj = None

    if object_type == b'commit':
        obj = models.GitCommit(data)
    elif object_type == b'tree':
        obj = models.GitTree(data)
    elif object_type == b'blob':
        obj = models.GitBlob(data)
    else:
        raise Exception("Unknown type %s!" % object_type)

    return models.object_write(obj, repository)