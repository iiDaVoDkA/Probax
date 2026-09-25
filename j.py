.filter(task => {
  const relationship = relById[task.teamInitiativeRelationshipId];
  const isClosed = ['DONE', 'CANCELED'].includes(task.status);

  // Completed/canceled tasks follow the existing last-assessor rule.
  if (isClosed && task.lastAssessor) {
    return user.id === task.lastAssessor;
  }

  // Individual assignment directly on the task.
  const isMainAssessor = user.id === task.mainAssessor;

  // Existing assignment through the initiative-team relationship.
  const isRelationshipAssessor =
    !task.mainAssessor &&
    teamMembers.some(
      teamMember =>
        teamMember.teamInitiativeRelationshipId ===
          task.teamInitiativeRelationshipId &&
        teamMember.userId === user.id &&
        user.id === relationship?.accountantId,
    );

  // New fallback: an unclaimed task belonging to the user's team.
  const isEligibleTeamAssessor =
    !isClosed &&
    task.isTeamAssigned === true &&
    task.mainAssessor == null &&
    relationship?.accountantId == null &&
    relationship?.teamId != null &&
    (user.roles ?? []).includes('INITIATIVE_ASSESSOR') &&
    (user.teamIds ?? []).includes(relationship.teamId);

  return (
    isMainAssessor ||
    isRelationshipAssessor ||
    isEligibleTeamAssessor
  );
});










const tasksForUser = myInitiativeTasks
  .map(/* your existing mapping */)
  .filter(/* replacement above */);

return tasksForUser;
