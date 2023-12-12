from models import models


def add_init_subparser(subparsers):
    argsp = subparsers.add_parser("init", help="Initialize a new, empty repository.")
    argsp.add_argument("path", metavar="directory", nargs="?", default=".", help="Where to create the repository.")

def initialize_command(args):
    models.repo_create(args.path)