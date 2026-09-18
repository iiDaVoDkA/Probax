
Object.values(members.byId || {})
  .filter(member => member.teamIds.includes(selectedTeamId))
  .filter(member =>
    (member.firstname + ' ' + member.lastname).includes(filter)
  )
  .filter(member => member.roles?.includes(INITIATIVE_ASSESSOR))
  .map(member => (
    ...
  ))
  
  
  .filter(
  member =>
    Array.isArray(member.roles) &&
    member.roles.includes('INITIATIVE_ASSESSOR')
)