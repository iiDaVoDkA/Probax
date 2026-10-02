const canEditAsTeamAssessor =
  ratingEditValues?.isTeamAssigned === true &&
  mainAssessorId == null &&
  accountantId == null &&
  ratingEditValues?.teamId != null &&
  (user.roles ?? []).includes(USER_ROLE_INITIATIVE_ASSESSOR) &&
  (user.teamIds ?? []).includes(ratingEditValues.teamId);