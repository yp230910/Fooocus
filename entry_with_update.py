import os
import sys

root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root)
os.chdir(root)

update_successful = False

try:
    import pygit2

    pygit2.option(pygit2.GIT_OPT_SET_OWNER_VALIDATION, 0)
    repo = pygit2.Repository(root)

    # Detached HEAD check
    if repo.head_is_detached:
        raise RuntimeError("HEAD is detached. Cannot pull updates automatically.")

    branch_name = repo.head.shorthand
    remote_name = "origin"
    remote = repo.remotes[remote_name]
    remote.fetch()

    local_branch_ref = f"refs/heads/{branch_name}"
    local_branch = repo.lookup_reference(local_branch_ref)

    remote_reference = f"refs/remotes/{remote_name}/{branch_name}"
    remote_commit = repo.revparse_single(remote_reference)

    merge_result, _ = repo.merge_analysis(remote_commit.id)

    if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
        print("Already up-to-date.")
        update_successful = True
    elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
        local_branch.set_target(remote_commit.id)
        repo.checkout_tree(repo.get(remote_commit.id))
        repo.reset(remote_commit.id, pygit2.GIT_RESET_HARD)
        print("Fast-forward merge complete.")
        update_successful = True
    elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
        print("Update skipped: non-fast-forward merge detected (local changes exist).")
    else:
        print("Update skipped: no automatic merge path found.")

except Exception as e:
    print(f"Update check failed: {e}")

if update_successful:
    print("Update succeeded.")

from launch import *
