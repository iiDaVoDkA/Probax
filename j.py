That could be a loading-order crash. Your saga stores tasks before fetching teams, but the selector accesses teams.byId immediately.

In selectors.combined.js, inside selectInitiativeTasksByUserId, make these two changes:

1. Replace:

team: teams.byId[task.teamId]?.name,

with:

team: teams?.byId?.[task.teamId]?.name ?? '',

The original ?.name doesn’t protect against byId being undefined.

2. Immediately before the existing .map(task => ({, insert:

.filter(task => relById[task.teamInitiativeRelationshipId] != null)

The beginning becomes:

const tasksForUser = myInitiativeTasks
  .filter(task => relById[task.teamInitiativeRelationshipId] != null)
  .map(task => ({

This waits to include a task until its relationship is available, protecting the direct .initiativeId accesses inside that mapping.

Save and try a normal reload. These changes address two visible crash risks. If the error page still appears, send the first red error message from Chrome’s Console so we can identify the actual remaining failure.