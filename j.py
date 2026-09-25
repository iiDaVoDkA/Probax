
roles = user.get("roles") or []

has_privileged_role = any(
    role in roles
    for role in [
        InitiativeRoleEnum.INITIATIVE_OWNER.value,
        InitiativeRoleEnum.INITIATIVE_COORDINATOR.value,
        "ADMIN",
    ]
)

is_assessor = (
    InitiativeRoleEnum.INITIATIVE_ASSESSOR.value in roles
)

is_selected_assessor = (
    user["id"] == initiative_team_relationship.accountant_id
)

can_edit_as_team_member = False

if (
    not has_privileged_role
    and is_assessor
    and task.get("is_team_assigned", False)
    and task.get("main_assessor") is None
    and initiative_team_relationship.accountant_id is None
    and initiative_team_relationship.team_id is not None
):
    current_member = next(
        (
            member
            for member in get_users()
            if member["id"] == user["id"]
        ),
        None,
    )

    if current_member is not None:
        can_edit_as_team_member = any(
            team["id"] == initiative_team_relationship.team_id
            for team in current_member["teams"]
        )

if not (
    has_privileged_role
    or (
        is_assessor
        and (is_selected_assessor or can_edit_as_team_member)
    )
):
    raise InitiativeTaskNotEditableByUserError(user["id"])

# Team editing must not change assignment through this endpoint.
if can_edit_as_team_member:
    protected_fields = (
        "relationship_id",
        "main_assessor",
        "is_team_assigned",
    )

    if any(
        field in payload and payload[field] != task.get(field)
        for field in protected_fields
    ):
        raise InitiativeTaskNotEditableByUserError(user["id"])








users = get_users()
assessor_users = get_users_by_role(
    InitiativeRoleEnum.INITIATIVE_ASSESSOR.value
)
assessor_ids = {
    assessor["user_id"] for assessor in assessor_users
}

for payload in payloads:
    team_relationship = (
        InitiativeTeamRelationshipRepository
        .get_by_relationship_ids(
            [payload["relationship_id"]]
        )[0]
    )

    # Preserve an individual assignment and require a real team.
    payload["is_team_assigned"] = False

    if (
        team_relationship.team_id is not None
        and team_relationship.accountant_id is None
        and payload.get("main_assessor") is None
    ):
        has_eligible_manager = any(
            member["is_initiative_manager"]
            and member["id"] in assessor_ids
            and any(
                team["id"] == team_relationship.team_id
                for team in member["teams"]
            )
            for member in users
        )

        payload["is_team_assigned"] = not has_eligible_manager

# Keep the existing first-task individual notification.
relationship_id = payloads[0]["relationship_id"]
team_relationship = (
    InitiativeTeamRelationshipRepository
    .get_by_relationship_ids([relationship_id])[0]
)

if team_relationship.accountant_id is not None:
    plm_user = get_users_by_user_id(
        [team_relationship.accountant_id]
    )
    if plm_user:
        send_email_task_assessor_assigned(
            payloads[0]["task_name"],
            plm_user[0].get("email"),
        )

return InitiativeTaskRepository.create_tasks(payloads)