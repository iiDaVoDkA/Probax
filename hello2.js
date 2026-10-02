The Validate ✔ and Cancel × buttons have separate permission checks in columns.js. Add the same team-assessor permission there.

1. Pass the original tasks into columns.js.

In InitiativePipelineTasksTab.js, append this.props.assessorTasks as the last argument of your existing getTasksTableColumns(...) call.

In columns.js, add the matching last parameter, immediately after openNotAnsweredTaskModal:

openNotAnsweredTaskModal: (task: Object) => void,
assessorTasks: ?(TaskType[]) = [],
) => {

2. Inside getTasksTableColumns, immediately after isUserAssessorOfInitiative, add:

const canEditAsTeamAssessor = original => {
  if (original?.id == null) return false;
  const task = (assessorTasks || []).find(
    item => String(item.id) === String(original.id),
  );
  return (
    task?.isTeamAssigned === true &&
    task.mainAssessor == null &&
    original.mainAssessorId == null &&
    original.accountantId == null &&
    original.teamId != null &&
    (user.roles || []).includes(USER_ROLE_INITIATIVE_ASSESSOR) &&
    (user.teamIds || []).some(
      teamId => String(teamId) === String(original.teamId),
    )
  );
};

This reads the flag from the original task list—the displayed row previously had isTeamAssigned: undefined.

3. Update the two buttons that call:

openDoneTaskModal(original)
openCancelTaskModal(original)

In each button’s disabled expression, replace this permission part:

!(
  isUserAllowedToUpdateTask ||
  isUserAssessorOfInitiative(original.accountantId, original.mainAssessorId)
)

with:

!(
  isUserAllowedToUpdateTask ||
  isUserAssessorOfInitiative(original.accountantId, original.mainAssessorId) ||
  canEditAsTeamAssessor(original)
)

Keep the rest of each expression, including the DONE, CANCELED, ON_HOLD, and final-initiative restrictions.

4. For “VALIDATE TASK” inside the rating modal, include your existing canEditAsTeamAssessor boolean in its permission group too:

(
  isUserAllowedToUpdateTask ||
  isUserAssessorOfInitiative(accountantId, mainAssessorId) ||
  canEditAsTeamAssessor
)

Keep its existing status and required-field checks.

Then validate one eligible task and cancel another; refresh to confirm both changes persisted. Check that another team’s assessor still cannot perform either action.

This fixes the UI permissions shown. The screenshots don’t show the submission handlers: if saving returns 403, we need to check the endpoint called by that action.