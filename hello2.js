const teamOptions = useMemo(() => {
  if (!Array.isArray(teams)) return [];

  return teams
    .map(team => ({
      value: team.id,
      label: team.name,
    }))
    .sort((a, b) =>
      String(a.label ?? "").localeCompare(String(b.label ?? ""))
    );
}, [teams]);