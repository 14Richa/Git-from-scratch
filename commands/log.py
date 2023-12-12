from models import models


def add_log_subparser(subparsers):
    argsp = subparsers.add_parser("log", help="Display history of a given commit.")
    
    argsp.add_argument("commit",
                       default="HEAD",
                       nargs="?",
                       help="Commit to start at.")


def log_command(args):
    repository = models.repo_find()

    print("digraph wyaglog{")
    models.log_graphviz(repository, models.object_find(repository, args.commit), set())
    print("}")
