
new_main_assessor = task_updated.get("main_assessor")

logging.warning(
    "[ASSIGN-MAIL] task=%s old_team=%s old_assessor=%s "
    "requested_assessor=%s saved_assessor=%s",
    id,
    was_team_assigned,
    previous_main_assessor,
    payload.get("main_assessor"),
    new_main_assessor,
)

base_plm_url = config.PLM_URL.replace("/plm", "")