SELECT
    i.id,
    i.created_by_id,
    i.is_active,
    r.team_id
FROM initiative i
LEFT JOIN initiative_team_relationship r
    ON r.initiative_id = i.id
ORDER BY i.id, r.team_id;