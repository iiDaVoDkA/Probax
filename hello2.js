if (
    u["is_initiative_manager"]
    and InitiativeRoleEnum.INITIATIVE_ASSESSOR.value in u["roles"]
    and any(user_team["id"] == team_id for user_team in u["teams"])
)