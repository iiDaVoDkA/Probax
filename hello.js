<pre
  style={{
    color: 'red',
    background: '#fff',
    padding: 12,
    fontSize: 14,
    whiteSpace: 'pre-wrap',
  }}
>
  {JSON.stringify(
    {
      canEditAsTeamAssessor,
      isDisabledFieldForRatingComment,
      isTeamAssigned: ratingEditValues?.isTeamAssigned,
      teamId: ratingEditValues?.teamId,
      mainAssessorId,
      accountantId,
      userTeamIds: user.teamIds,
      userRoles: user.roles,
      taskStatus: ratingEditValues?.status,
      taskType: ratingEditValues?.type,
      isFinalStatus,
    },
    (_, value) => value === undefined ? 'undefined' : value,
    2,
  )}
</pre>