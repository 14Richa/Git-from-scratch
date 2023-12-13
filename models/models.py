import os
import configparser
from .helpers import ensure_repo_directory, get_repo_file, get_repo_path
import argparse 
import hashlib
import zlib
import re
import collections



class GitRepository(object):
    def __init__(self, path, force=False):
        self.work_tree = path
        self.git_dir = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.git_dir)):
            raise Exception("Not a Git repository %s" % path)

        self.config = configparser.ConfigParser()
        config_file = get_repo_file(self, "config")

        if config_file and os.path.exists(config_file):
            self.config.read([config_file])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            version = int(self.config.get("core", "repositoryformatversion"))
            if version != 0:
                raise Exception("Unsupported repositoryformatversion %s" % version)


def repo_create(path):
    repository = GitRepository(path, True)
    if os.path.exists(repository.work_tree):
        if not os.path.isdir(repository.work_tree):
            raise Exception ("%s is not a directory!" % path)
        if os.path.exists(repository.git_dir) and os.listdir(repository.git_dir):
            raise Exception("%s is not empty!" % path)
    else:
        os.makedirs(repository.work_tree)

    # Create necessary directories for the repository
    assert ensure_repo_directory(repository, "branches", mkdir=True)
    assert ensure_repo_directory(repository, "objects", mkdir=True)
    assert ensure_repo_directory(repository, "refs", "tags", mkdir=True)
    assert ensure_repo_directory(repository, "refs", "heads", mkdir=True)

    with open(get_repo_file(repository, "description"), "w") as f:
        f.write("Unnamed repository; edit this file 'description' to file_name the repository.\n")

    with open(get_repo_file(repository, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    with open(get_repo_file(repository, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repository

def repo_default_config():
    serialized_data = configparser.ConfigParser()

    serialized_data.add_section("core")
    serialized_data.set("core", "repositoryformatversion", "0")
    serialized_data.set("core", "filemode", "false")
    serialized_data.set("core", "bare", "false")

    return serialized_data

def repo_find(path=".", required=True):
    path = os.path.realpath(path)
    # check if the .git directory exists within the path
    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path)

    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        if required:
            raise Exception("No git directory.")
        else:
            return None
    return repo_find(parent, required)

class GitObject (object):
    def __init__(self, data=None):
        if data != None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self, repository):
        raise Exception("Unimplemented!")

    def deserialize(self, data):
        raise Exception("Unimplemented!")

    def init(self):
        pass

# KVLM to mean Key-Value List with Message
def kvlm_parse(raw, start_index=0, dictionary=None):
    if not dictionary:
        dictionary = collections.OrderedDict()

    space_index = raw.find(b' ', start_index)
    newline_index = raw.find(b'\n', start_index)

    # check for end of line or no space found
    if (space_index < 0) or (newline_index < space_index):
        assert newline_index == start_index
        dictionary[None] = raw[start_index+1:]
        return dictionary

    # extract the key until the space character
    key = raw[start_index:space_index]

    # locate the end of the current line
    end = start_index
    while True:
        end = raw.find(b'\n', end+1)
        if raw[end+1] != ord(' '): break
    # extract the value and replace newline space with newline character
    value = raw[space_index+1:end].replace(b'\n ', b'\n')

    if key in dictionary:
        if type(dictionary[key]) == list:
            dictionary[key].append(value)
        else:
            dictionary[key] = [ dictionary[key], value ]
    else:
        dictionary[key]=value

    return kvlm_parse(raw, start_index=end+1, dictionary=dictionary)

def kvlm_serialize(kvlm):
    serialized_data = b''
    # Output fields
    for k in kvlm.keys():
        # Skip the message itself
        if k == None: continue
        val = kvlm[k]
        # Normalize to a list
        if type(val) != list:
            val = [ val ]

        for v in val:
            serialized_data += k + b' ' + (v.replace(b'\n', b'\n ')) + b'\n'
    # Append message
    serialized_data += b'\n' + kvlm[None] + b'\n'
    return serialized_data

class GitCommit(GitObject):
    object_type=b'commit'

    def deserialize(self, data):
        self.kvlm = kvlm_parse(data)

    def serialize(self):
        return kvlm_serialize(self.kvlm)

    def init(self):
        self.kvlm = dict()


class GitTreeLeaf (object):
    def __init__(self, mode, path, sha):
        self.mode = mode
        self.path = path
        self.sha = sha

def tree_parse_one(raw, start=0):
    # find the position where the mode ends in the raw data
    mode_end = raw.find(b' ', start)
    # ensure the mode length is either 5 or 6 characters
    assert mode_end - start in (5, 6)

    mode = raw[start:mode_end]
    if len(mode) == 5:
        mode = b" " + mode

    # find the position where the path ends
    path_start = mode_end + 1
    path_end = raw.find(b'\x00', mode_end)
    # Read the path
    path = raw[path_start:path_end]

    # find the position where the SHA-1 hash ends
    sha_start = path_end + 1
    sha_end = sha_start + 20
    # extract the SHA-1 bytes from the raw data
    sha_bytes = raw[sha_start:sha_end]
    # convert the SHA-1 bytes to a hexadecimal string
    sha_hex = sha_bytes.hex()

    return sha_end, GitTreeLeaf(mode, path.decode("utf8"), sha_hex)

def tree_parse(raw_data):
    current_position = 0
    max_position = len(raw_data)
    parsed_data = list()

    while current_position < max_position:
        current_position, parsed_entry = tree_parse_one(raw_data, current_position)
        parsed_data.append(parsed_entry)

    return parsed_data

def tree_leaf_sort_key(leaf):
    if leaf.mode.startswith(b"10"):
        return leaf.path
    else:
        return leaf.path + "/"

def tree_serialize(tree_object):
    tree_object.items.sort(key=tree_leaf_sort_key)
    serialized_tree = b''
    for item in tree_object.items:
        serialized_tree += item.mode
        serialized_tree += b' '
        serialized_tree += item.path.encode("utf8")
        serialized_tree += b'\x00'
        sha_int = int(item.sha, 16)
        serialized_tree += sha_int.to_bytes(20, byteorder="big")
    return serialized_tree

class GitTree(GitObject):
    object_type=b'tree'

    def deserialize(self, data):
        self.items = tree_parse(data)

    def serialize(self):
        return tree_serialize(self)

    def init(self):
        self.items = list()

def object_read(repository, commit_id):
    path = get_repo_file(repository, "objects", commit_id[0:2], commit_id[2:])

    if not os.path.isfile(path):
        return None

    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

        # Read object type
        x = raw.find(b' ')
        object_type = raw[0:x]

        y = raw.find(b'\x00', x)
        size = int(raw[x:y].decode("ascii"))
        if size != len(raw) - y - 1:
            raise Exception("Malformed object {0}: bad length".format(commit_id))

        if object_type == b'blob':
            c = GitBlob
        elif object_type == b'commit':
            c = GitCommit
        elif object_type == b'tree':
            c = GitTree
        else:
            raise Exception("Unknown type {0} for object {1}".format(object_type.decode("ascii"), commit_id))

        return c(raw[y + 1:])


def object_write(obj, repository=None):
    # Serialize object data
    data = obj.serialize()
    # Add header
    result = obj.object_type + b' ' + str(len(data)).encode() + b'\x00' + data
    # Compute hash
    commit_id = hashlib.sha1(result).hexdigest() # This can be done manually using any markov chain algorithm

    if repository:
        # Compute path
        path=get_repo_file(repository, "objects", commit_id[0:2], commit_id[2:], mkdir=True)

        if not os.path.exists(path):
            with open(path, 'wb') as f:
                # Compress and write
                f.write(zlib.compress(result))
    return commit_id

# a class GitBlob inheriting from GitObject
class GitBlob(GitObject):
    object_type = b'blob'

    def serialize(self):
        return self.blob_data

    def deserialize(self, data):
        self.blob_data = data


def ref_resolve(repository, ref):
    path = get_repo_file(repository, ref)

    if not os.path.isfile(path):
        return None

    with open(path, 'r') as fp:
        data = fp.read()[:-1]

    if data.startswith("ref: "):
        return ref_resolve(repository, data[5:])
    else:
        return data

def object_resolve(repository, object_name):
    object_candidates = []
    hash_regex = re.compile(r"^[0-9A-Fa-f]{4,40}$")

    if not object_name.strip():
        return None

    if object_name == "HEAD":
        return [ ref_resolve(repository, "HEAD") ]

    if hash_regex.match(object_name):

        object_name = object_name.lower()
        prefix = object_name[0:2]
        path = ensure_repo_directory(repository, "objects", prefix, mkdir=False)
        if path:
            remaining = object_name[2:]
            for file in os.listdir(path):
                if file.startswith(remaining):
                    object_candidates.append(prefix + file)

    as_tag = ref_resolve(repository, "refs/tags/" + object_name)
    if as_tag:
        object_candidates.append(as_tag)

    as_branch = ref_resolve(repository, "refs/heads/" + object_name)
    if as_branch:
        object_candidates.append(as_branch)

    return object_candidates


def object_find(repository, object_name, object_type=None, follow=True):
      resolved_id = object_resolve(repository, object_name)

      if not resolved_id:
        raise Exception(f"No matching reference found for: '{object_name}'")

      if len(resolved_id) > 1:
        raise Exception(f"Ambiguous reference '{object_name}': Multiple candidates found:\n - {candidates_list}")

      resolved_id = resolved_id[0]

      if not object_type:
          return resolved_id

      while True:
          obj = object_read(repository, resolved_id)
          if obj.object_type == object_type:
              return resolved_id

          if not follow:
              return None

          if obj.object_type == b'tag':
                resolved_id = obj.kvlm[b'object'].decode("ascii")
          elif obj.object_type == b'commit' and object_type == b'tree':
                resolved_id = obj.kvlm[b'tree'].decode("ascii")
          else:
              return None
          


def object_hash(fd, object_type, repository=None):
    data = fd.read()
    obj = None

    if object_type == b'commit':
        obj = GitCommit(data)
    elif object_type == b'tree':
        obj = GitTree(data)
    elif object_type == b'blob':
        obj = GitBlob(data)
    else:
        raise Exception("Unknown type %s!" % object_type)

    return object_write(obj, repository)

def log_graphviz(repository, commit_id, seen_commits):
    if commit_id in seen_commits:
        return
    seen_commits.add(commit_id)

    commit = object_read(repository, commit_id)
    commit_msg = commit.kvlm[None].decode("utf8").strip()
    commit_msg = commit_msg.replace("\\", "\\\\")
    commit_msg = commit_msg.replace("\"", "\\\"")

    if "\n" in commit_msg: 
        commit_msg = commit_msg[:commit_msg.index("\n")]

    print("  c_" + commit_id + " [label=\"" + commit_id[0:7] + ": " + commit_msg + "\"]")
    assert commit.object_type==b'commit'

    if not b'parent' in commit.kvlm.keys():
        return

    parents = commit.kvlm[b'parent']

    if type(parents) != list:
        parents = [ parents ]

    for parent_commit in parents:
        parent_commit = parent_commit.decode("ascii")
        print ("  c_{0} -> c_{1};".format(commit_id, parent_commit))
        log_graphviz(repository, parent_commit, seen_commits)

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

