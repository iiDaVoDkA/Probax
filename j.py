Yes—these screenshots confirm exactly two edits, both inside InitiativeTaskResource.patch in src/resources/task/task.py.

1. Replace is_selected_assessor = ... around line 160 with:

is_selected_assessor = (
    user["id"] == initiative_team_relationship.accountant_id
    or user["id"] == task.get("main_assessor")
)

This lets the person assigned to the task continue editing after it stops being team-shared. Your existing is_assessor check still applies.

2. Replace the block starting with this comment:

# Team editing must not change assignment through this endpoint.

Replace everything from that comment up to—but excluding—task_updated = ... with:

if can_edit_as_team_member:
    # Keep the task attached to its current team.
    # The repository controls the sharing flag.
    protected_fields = ("relationship_id", "is_team_assigned")
    if any(
        field in payload and payload[field] != task.get(field)
        for field in protected_fields
    ):
        raise InitiativeTaskNotEditableByUserError(user["id"])
    new_assessor_id = payload.get("main_assessor")
    if new_assessor_id is not None:
        if task.get("task_status") in ("DONE", "CANCELED", "ON_HOLD"):
            raise InitiativeTaskNotEditableByUserError(user["id"])
        assessor_ids = {
            assessor["user_id"]
            for assessor in get_users_by_role(
                InitiativeRoleEnum.INITIATIVE_ASSESSOR.value
            )
        }
        selected_member = next(
            (
                member
                for member in get_users()
                if member["id"] == new_assessor_id
            ),
            None,
        )
        if (
            selected_member is None
            or selected_member.get("is_team", False)
            or new_assessor_id not in assessor_ids
            or not any(
                team["id"] == initiative_team_relationship.team_id
                for team in (selected_member.get("teams") or [])
            )
        ):
            raise InitiativeTaskNotEditableByUserError(user["id"])

The existing task_updated = ..., audit code and return follow this block.

Why this remains guarded: your preceding code already checks the caller’s role, team membership and whether the task is shared without a main assessor. The replacement additionally checks that the chosen person exists, has the assessor role, belongs to the same team and is not a team mailbox.

Keep the repository change you already added:

if payload.get("main_assessor") is not None:
    task.is_team_assigned = False

Then test Save → reload → edit again as the selected assessor. Also verify that a different ordinary teammate loses shared editing access. These are proposed changes based on your code; I have not run them in your application.