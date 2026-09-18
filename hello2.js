else:
    users = get_users()

    assessor_users = get_users_by_role(
        InitiativeRoleEnum.INITIATIVE_ASSESSOR.value
    )

    assessor_ids = {
        user["id"]
        for user in assessor_users
    }

    team_to_managers = {
        team_id: next(
            (
                u
                for u in users
                if (
                    u["is_initiative_manager"]
                    and u["id"] in assessor_ids
                    and any(
                        user_team["id"] == team_id
                        for user_team in u["teams"]
                    )
                )
            ),
            None,
        )
        for team_id in team_ids
    }

    for team_id in team_ids:
        if team_to_managers[team_id]:
            new_initiative_team_member = (
                InitiativeTeamMembersRepository.add_team_member(
                    initiative_id,
                    team_id,
                    team_to_managers[team_id].get("id", None),
                )
            )

            members_to_return.append(
                new_initiative_team_member.to_json()
            )

            InitiativeTeamRelationshipRepository.modify_team(
                initiative_id,
                team_id,
                team_to_managers[team_id].get("id", None),
            )