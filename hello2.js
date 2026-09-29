Yes—the last three screenshots show the correct files. We now have the existing functions:

fetchUsersByTeam(teamId)
selectUsers(state)
getUsersByTeamId(users, teamId)

First, connect them in TaskEdition.wrap.js.

1. Add these imports:

import { selectUsers } from '@app/redux/entities/users/selectors';
import { fetchUsersByTeam } from '@app/redux/entities/users/actions';

2. Add users inside the existing mapStateToProps:

const mapStateToProps = (state: StateType, props: OwnPropsType): MapStateToPropsType => ({
  assessmentCategories: selectAssessmentCategoryInitiative(state),
  user: selectUserState(state),
  users: selectUsers(state),
});

3. Add this entry inside the existing mapDispatchToProps, alongside createTasks:

fetchTeamUsers: (teamId: number) =>
  dispatch(fetchUsersByTeam(teamId)),

4. In TaskEdition.js, update the props types:

Add to MapStateToPropsType:

users: UsersStateType,

Add alongside the existing dispatch-function props, such as createTasks:

fetchTeamUsers: (teamId: number) => void,

This connects the users data and the action that loads a selected team.

Next, send the current componentDidMount and componentDidUpdate from TaskEdition.js. We need to place that loading call correctly and update the dropdown when users arrive, while preserving the selected assessor and avoiding the repeated setFieldValue loop we fixed earlier.