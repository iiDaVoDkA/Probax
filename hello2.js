payload["is_team_assigned"] = not has_eligible_manager

if payload["is_team_assigned"]:
    team_emails = {
        member["email"].strip()
        for member in users
        if member.get("is_team") is True
        and (member.get("email") or "").strip()
        and any(
            team["id"] == team_relationship.team_id
            for team in (member.get("teams") or [])
        )
    }

    for team_email in sorted(team_emails):
        send_email_task_assessor_assigned(
            payload["task_name"],
            team_email,
        )