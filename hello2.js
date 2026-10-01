
Yes — same situation as before. Your new ticket branch contains the old “Allow to assign a task to a team” commit in its history, so Azure DevOps is showing those old files again even though that ticket was already merged.

For this PR you want to keep only:

1321699c  add a template patch

Do this in the flowr-initiative-pipeline repo:

git branch backup/feat271768-before-cleanup
git status --short

If git status --short shows local changes, stash them:

git stash push -u -m "temp before cleaning feat271768"

Then:

git fetch origin
git reset --hard origin/develop
git cherry-pick 1321699c

Now verify:

git log --oneline origin/develop..HEAD

You should see only one commit, your template patch.

Then:

git diff --name-status origin/develop...HEAD

You should now see only the template-ticket file(s), not all the task-assignment files.

If that looks correct:

git push --force-with-lease origin feat271768/allow-to-edit-initiative-template-name

Then refresh the PR. It should go from:

2 commits
8 files

to essentially:

1 commit
only template-related file(s)

If cherry-pick gives any conflict, stop there and send me the screen.