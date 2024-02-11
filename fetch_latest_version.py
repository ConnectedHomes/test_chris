import os
import json
from semver.version import Version
import semver

if __name__ == '__main__':
    # https://python-semver.readthedocs.io/en/latest/usage.html
    # need to start patches with two digits to allow sorting in the AWS query
    semantic_versions = json.loads(os.environ['SEMANTIC_VERSIONS'])
    semantic_version = semantic_versions[0]['SemanticVersion'] if semantic_versions else "0.0.1"
    semantic_version = semantic_version.replace('"', '')
    ver = Version.parse(semantic_version)
    for semantic_version in semantic_versions:
        semantic_version = semantic_version['SemanticVersion'].replace('"', '')
        if ver.compare(semantic_version) == -1:
            ver = Version.parse(semantic_version)
    patch = ver[2]
    #new_version = semver.replace(semantic_version, patch=patch+1)
    final_version = semver.replace(semantic_version)
    # don't delete, as it's passed to the parent bash script!! https://stackoverflow.com/a/26767586/1984997
    print(final_version)
