Yes—this is the correct wrapper. We can now connect the team’s Initiative Assessors to this dropdown.

1. In InitiativePipelineTasksTab.wrap.js

Replace the existing fetchUsers import with:

import {
  fetchUsers,
  fetchUsersByTeam,
} from '@app/redux/entities/users/actions';

Add these imports:

import { selectUsers } from '@app/redux/entities/users/selectors';
import { selectTasks } from '@app/redux/entities/initiativeTasks/selectors';

Add inside the existing mapStateToProps object:

assessorUsers: selectUsers(state),
assessorTasks: selectTasks(state),

Add inside the existing mapDispatchToProps object:

fetchTeamUsers: (teamId: number) =>
  dispatch(fetchUsersByTeam(teamId)),

2. In InitiativePipelineTasksTab.js

Add this import:

import { getUsersByTeamId } from '@app/redux/entities/users/selectors';

Add these fields to its existing MapStateToPropsType:

assessorUsers: UsersStateType,
assessorTasks: Object[],

Add this field to its existing MapDispatchToPropsType:

fetchTeamUsers: (teamId: number) => void,

3. Immediately after the existing teamIdToTeamMembers block, around line 825

Add:

const assessorTeamId = ratingEditValues.teamId;
const taskForAssessorOptions = this.props.assessorTasks.find(
  task => String(task.id) === String(this.state.ratingEditingTaskId),
);
const useTeamAssessorOptions =
  taskForAssessorOptions != null &&
  taskForAssessorOptions.isTeamAssigned === true &&
  taskForAssessorOptions.mainAssessor == null;
const taskMainAssessorOptions =
  useTeamAssessorOptions && assessorTeamId != null
    ? getUsersByTeamId(this.props.assessorUsers, assessorTeamId)
        .filter(
          member =>
            member &&
            !member.isTeam &&
            (member.roles || []).includes(
              USER_ROLE_INITIATIVE_ASSESSOR,
            ),
        )
        .map(member => ({
          value: member.id,
          label: [
            member.firstName || member.firstname || '',
            member.lastName || member.lastname || '',
          ]
            .filter(Boolean)
            .join(' '),
        }))
    : teamIdToTeamMembers[assessorTeamId] || [];

This uses the task’s saved shared-assignment flag. Ordinary tasks continue using their existing options.

4. Replace only the editable Main Assessor <Field> around line 965

Keep its surrounding permission conditions and replace the field with:

<Field
  name="mainAssessor"
  component={Select}
  options={taskMainAssessorOptions}
  value={ratingEditValues.mainAssessor}
  onMenuOpen={() => {
    if (useTeamAssessorOptions && assessorTeamId != null) {
      this.props.fetchTeamUsers(assessorTeamId);
    }
  }}
  onChange={option => this.setMainAssessor(option)}
  isClearable
/>

Opening the dropdown now requests that team’s users. When the response arrives, the options update to show its human Initiative Assessors, including those without the manager flag.

Remove the temporary alert, reload I2, open Task 3, and click MAIN ASSESSOR. Check that the team-user request runs and the names appear. Also check one ordinary assigned task to confirm its existing list remains available.