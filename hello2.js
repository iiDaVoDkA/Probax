Your screenshot still contains the old Main Assessor reset at lines 123–141. Replace it while adding team-user loading.

This assumes you added users and fetchTeamUsers to the wrapper as described earlier.

1. In TaskEdition.js, replace componentDidMount with:

componentDidMount() {
  const { getAssessmentCategory, fetchTeamUsers, values } = this.props;
  getAssessmentCategory();
  const teamId = values.teams?.value;
  if (teamId != null) {
    fetchTeamUsers(teamId);
  }
}

2. Change the componentDidUpdate signature to:

componentDidUpdate(prevProps: PropsType) {

Keep the category/subcategory code above line 123. Replace only the final team/Main Assessor block, including its commented-out code, with:

const {
  values,
  editedTask,
  teamOptions,
  teamIdToTeamMembers,
  fetchTeamUsers,
  setFieldValue,
} = this.props;
const teamId = values.teams?.value ?? null;
const previousTeamId = prevProps.values.teams?.value ?? null;
const teamChanged = teamId !== previousTeamId;
if (teamChanged && teamId != null) {
  fetchTeamUsers(teamId);
}
const members = teamIdToTeamMembers[teamId] ?? [];
const currentId = values.mainAssessor?.value ?? null;
const isTaskTeam =
  editedTask?.teamId != null &&
  teamId != null &&
  String(editedTask.teamId) === String(teamId);
const savedAssessorId = isTaskTeam
  ? editedTask.mainAssessor
  : null;
const savedAssessor = savedAssessorId != null
  ? members.find(
      member => String(member.value) === String(savedAssessorId),
    )
  : null;
const teamDefault = teamOptions.find(
  team => team.value === teamId,
)?.mainAssessor;
const defaultAssessor = editedTask
  ? savedAssessor ?? null
  : teamDefault ?? null;
const currentIsValid = members.some(
  member => String(member.value) === String(currentId),
);
const currentIsSavedAssessor =
  savedAssessorId != null &&
  currentId != null &&
  String(currentId) === String(savedAssessorId);
const shouldUpdateAssessor = teamChanged
  ? !currentIsValid && !currentIsSavedAssessor
  : currentId == null && defaultAssessor != null;
if (
  shouldUpdateAssessor &&
  currentId !== (defaultAssessor?.value ?? null)
) {
  setFieldValue('mainAssessor', defaultAssessor, false);
}

Keep the closing brace of componentDidUpdate.

This fetches users when the team changes, preserves a selection while users load, and only updates the assessor when its value actually changes.

3. In InitiativeTasksEdition/utils.js, add this import:

import { getUsersByTeamId } from '@app/redux/entities/users/selectors';

Inside getAdditionalProps, replace the whole const teamIdToTeamMembers = ... block with:

const toAssessorOption = member => ({
  value: member.id,
  label: [
    member.firstName ?? member.firstname ?? '',
    member.lastName ?? member.lastname ?? '',
  ].join(' ').trim(),
});
const teamIdToTeamMembers = Object.fromEntries(
  props.initiative.teams.map(team => {
    const registeredOptions = (team.team_members ?? [])
      .map(toAssessorOption);
    const { editedTask, users } = props;
    const isTaskTeam =
      editedTask?.teamId != null &&
      String(editedTask.teamId) === String(team.team_id);
    const includeTeamCandidates = editedTask
      ? isTaskTeam && editedTask.isTeamAssigned === true
      : team.accountant_id == null;
    const teamUsers = users?.byTeamId && users?.byId
      ? getUsersByTeamId(users, team.team_id).filter(Boolean)
      : [];
    const additionalOptions = includeTeamCandidates
      ? teamUsers
          .filter(member =>
            !member.isTeam &&
            (member.roles ?? []).includes('INITIATIVE_ASSESSOR')
          )
          .map(toAssessorOption)
      : [];
    const savedAssessor = isTaskTeam
      ? users?.byId?.[editedTask.mainAssessor]
      : null;
    const options = [
      ...registeredOptions,
      ...additionalOptions,
      ...(savedAssessor ? [toAssessorOption(savedAssessor)] : []),
    ];
    return [
      team.team_id,
      Array.from(
        new Map(
          options.map(option => [String(option.value), option]),
        ).values(),
      ),
    ];
  }),
);

The name mapping handles the existing initiative members’ firstname/lastname fields and the users directory’s camelCase fields.

For existing tasks, additional candidates are restricted to team-assigned tasks. For creation without a relationship Main Assessor, it offers eligible team members; the backend still decides the assignment mode.

Then check these three cases:

* I2: selecting team 209 loads its users and populates Main Assessor with eligible human assessors.
* I2: leaving Main Assessor empty does not automatically select the first person.
* I1: user 1803 and the existing assignment remain available.

Send the dropdown result after selecting team 209. That will verify the loading and options before we check saving and reopening.