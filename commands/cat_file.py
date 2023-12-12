from models import models
import sys
import argparse



def add_cat_file_subparser(subparsers):
    argsp = subparsers.add_parser("cat-file", help="Provide content of repository objects")
    argsp.add_argument("type", metavar="type", choices=["blob", "commit", "tag", "tree"],
                       help="Specify the type")
    argsp.add_argument("object", metavar="object", help="The object to display")


# function to execute the cat-file command
def cmd_cat_file(args):
    repository = models.repo_find()
    # print("hi from cat command")
    cat_file(repository, args.object, object_type=args.type.encode())

# function to display the content of an object
def cat_file(repository, obj, object_type=None):
    obj = models.object_read(repository, models.object_find(repository, obj, object_type=object_type))
    sys.stdout.buffer.write(obj.serialize())


    


