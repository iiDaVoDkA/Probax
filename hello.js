Yes—use taskForAssessorOptions. Your screenshot confirms its lookup already uses the correct ratingEditingTaskId. The helper below it still reads the missing flag from ratingEditValues.

Replace only your existing canEditAsTeamAssessor block with:

const canEditAsTeamAssessor =
  taskForAssessorOptions?.isTeamAssigned === true &&
  mainAssessorId == null &&
  accountantId == null &&
  ratingEditValues?.teamId != null &&
  (user.roles ?? []).includes(USER_ROLE_INITIATIVE_ASSESSOR) &&
  (user.teamIds ?? []).includes(ratingEditValues.teamId);

Keep it in its current position, after taskForAssessorOptions. This reads the flag from the selected Redux task while retaining the role, team and assessor checks.

Also update the red debug output, otherwise it will keep showing the old missing value. Replace its isTeamAssigned entry with:

isTeamAssigned: taskForAssessorOptions?.isTeamAssigned,
selectedTaskFound: taskForAssessorOptions != null,

Save and reopen the rating modal. The rating/comment/Save conditions must still include || canEditAsTeamAssessor as previously shown. No further constructor or close-handler changes are needed for this correction.