
Object.values(members.byId || {})
  .filter(member => member.teamIds.includes(selectedTeamId))
  .filter(member =>
    (member.firstname + ' ' + member.lastname).includes(filter)
  )
  .filter(member => member.roles?.includes(INITIATIVE_ASSESSOR))
  .map(member => (
    ...
  ))