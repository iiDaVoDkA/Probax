This caller controls which initiatives an assessor can see. It filters relationships twice, so we must include team assignment in both places.

We can reuse get_user_teams_by_user_id(user), which already appears in this file, to get the logged-in user’s actual teams.

Make these changes:

1. In src/repositories/task.py, add this new method below get_by_main_assessor().
    Add the model import if it is absent:

from models.initiative_team_relationship import InitiativeTeamRelationship

    Then add:

@staticmethod
def get_team_assigned_relationship_ids(team_ids):
    """Get relationship IDs containing unclaimed team-assigned tasks."""
    if not team_ids:
        return []
    relationship_ids = (
        db.session.query(InitiativeTask.relationship_id)
        .join(
            InitiativeTeamRelationship,
            InitiativeTask.relationship_id
            == InitiativeTeamRelationship.id,
        )
        .filter(
            InitiativeTask.is_team_assigned.is_(True),
            InitiativeTask.main_assessor.is_(None),
            InitiativeTeamRelationship.accountant_id.is_(None),
            InitiativeTeamRelationship.team_id.in_(team_ids),
        )
        .distinct()
        .all()
    )
    return [rel_id[0] for rel_id in relationship_ids]

    Why: this finds team-assigned tasks belonging to the user’s teams. Checking both individual-assignment fields prevents the fallback from granting access after someone takes ownership.
2. In src/resources/initiative/initiative.py, inside the existing Initiative Assessor branch, find:

relationships_id_linked_to_main_assessor = (
    InitiativeTaskRepository.get_by_main_assessor(user.get("id"))
)

    Your existing line may be formatted on one line. Immediately after it, add:

team_ids = [
    user_team.get("team_id")
    for user_team in get_user_teams_by_user_id(user)
]
team_assigned_relationship_ids = (
    InitiativeTaskRepository.get_team_assigned_relationship_ids(
        team_ids
    )
)

    Why: the surrounding branch already checks the Initiative Assessor role; this adds their team membership.
3. Replace the following initiative_relationships = ... block with:

initiative_relationships = (
    InitiativeTeamRelationshipRepository.get_by_relationship_ids(
        list(
            set(
                relationship_ids
                + relationships_id_linked_to_main_assessor
                + team_assigned_relationship_ids
            )
        )
    )
)

    Why: an eligible team member might have no individual entry in InitiativeTeamMembers. Their team-assigned relationships must be included independently.
4. Replace the following assessor_initiative_relationships = [...] block with:

assessor_initiative_relationships = [
    assessor_initiative_relationship
    for assessor_initiative_relationship in initiative_relationships
    if (
        assessor_initiative_relationship.accountant_id
        == user.get("id")
        or assessor_initiative_relationship.id
        in relationships_id_linked_to_main_assessor
        or assessor_initiative_relationship.id
        in team_assigned_relationship_ids
    )
]

    Why: without that final or, this second filter would remove the team-assigned relationships we just added.

This covers initiative-list visibility. We still need to trace the actual My Tasks fetch and its task-level filtering.

After these edits, send the saga handling fetchTasksByUserId under src/redux/entities/initiativeTasks. That will show the request used for Initiative My Tasks.