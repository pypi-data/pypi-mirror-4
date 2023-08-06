import os
from cubes.vcsfile.hooks import repo_cache_dir

sync_schema_props_perms(('Repository', 'title', 'String'), syncperms=False)


cacheroot = repo_cache_dir(repo.config)
for repo in rql('Any X, XLC WHERE X local_cache XLC, NOT X local_cache NULL,'
                'X is Repository').entities():
    if repo.local_cache.startswith(cacheroot):
        repo.set_attributes(local_cache=repo.local_cache.replace(cacheroot, '').lstrip(os.sep))

