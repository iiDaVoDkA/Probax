
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