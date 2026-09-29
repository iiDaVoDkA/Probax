The creation form is calling fetchTeamUsers, but its own wrapper doesn’t supply that function. We wired it into InitiativePipelineTasksTab.wrap.js; Add a Task uses a separate wrapper.

In InitiativeTasksEdition/TaskEdition.wrap.js, add these two pieces:

1. Import the existing action:

import { fetchUsersByTeam } from '@app/redux/entities/users/actions';

2. Inside the existing mapDispatchToProps object, add:

fetchTeamUsers: (teamId: number) =>
  dispatch(fetchUsersByTeam(teamId)),

Keep the existing createTasks, closeInitiativeTaskForm, and getAssessmentCategory mappings.

This supplies the function that TaskEdition.componentDidUpdate is already calling. Save, fully reload the browser, then retry Add a Task and select the team. This addresses the missing-function error in your screenshot.