assessor_id = payload.get("main_assessor")

if assessor_id is None and not payload.get("is_team_assigned", False):
    assessor_id = team_relationship.accountant_id

if assessor_id is not None:
    plm_user = get_users_by_user_id([assessor_id])

    if plm_user and plm_user[0].get("email"):
        try:
            send_email_task_assessor_assigned(
                task_name=payload["task_name"],
                recipients=plm_user[0]["email"],
                initiative_name=initiative.name,
                initiative_id=initiative.id,
                initiative_type=initiative.initiative_type,
                initiative_link=(
                    f"{config.REMOTE_URL.rstrip('/')}/initiative/{initiative.id}"
                ),
                tasks=[{
                    "task_type": payload["task_type"],
                    "task_name": payload["task_name"],
                    "expected_for": (
                        payload.get("expected_for") or "Not scheduled yet"
                    ),
                }],
            )
        except Exception:
            logging.exception("Failed to send task assignment email")