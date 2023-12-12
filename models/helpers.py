import os
import collections


def get_repo_path(repository, *path):
    return os.path.join(repository.git_dir, *path)

def get_repo_file(repository, *path, mkdir=False):
    if ensure_repo_directory(repository, *path[:-1], mkdir=mkdir):
        return get_repo_path(repository, *path)

def ensure_repo_directory(repository, *path, mkdir=False):
    path = get_repo_path(repository, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception("Not a directory %s" % path)
    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None
        
def ref_resolve(repository, ref):
    # path associated with the reference in the repository
    path = get_repo_path(repository, ref)
    if os.path.isfile(path):
        with open(path, 'r') as file:
            data = file.read().rstrip('\n')
            if data.startswith("ref: "):
                return ref_resolve(repository, data[5:])
            else:
                return data
    return None

def ref_list(repository, path=None):
    # no path provided, set it to the default repository reference directory
    if path is None:
        path = ensure_repo_directory(repository, "refs")
    # an ordered dictionary to store references
    references = collections.OrderedDict()

    for filename in sorted(os.listdir(path)):
        full_path = os.path.join(path, filename)
        
        if os.path.isdir(full_path):
            references[filename] = ref_list(repository, full_path)
        else:
            references[filename] = ref_resolve(repository, full_path)

    return references