
if plm_user and plm_user[0].get("email"):
    initiative = InitiativeRepository.get_by_ids(
        [initiative_id], False
    )[0]

    send_email_assessor_changed(
        initiative_id=initiative.id,
        recipients=plm_user[0]["email"],
        initiative_name=initiative.name,
        initiative_type=initiative.initiative_type,
        initiative_link=(
            f"{config.REMOTE_URL.rstrip('/')}/initiative/{initiative.id}"
        ),
        tasks=[
            {
                "task_type": task.to_json()["task_type"],
                "task_name": task.task_name,
                "expected_for": task.to_json().get("expected_for")
                or "Not scheduled yet",
            }
            for task in tasks_to_update
        ],
    )