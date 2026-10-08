Email delivery now works. The remaining issue is the data passed from task.py. The screenshot shows the ID being used as the name, and literal placeholders for the ID and type.

The values should map like this:

Email field	Value
Clickable title	Actual initiative name
Initiative ID	team_relationship.initiative_id
Initiative type	Actual initiative type label
Link	Base URL + / + initiative ID
Expected for	Formatted date, or “Not scheduled yet”

For the ID and link:

initiative_id = team_relationship.initiative_id
initiative_link = f"{base_url.rstrip('/')}/{initiative_id}"

For each task’s missing date, pass this into the email data:

"expected_for": formatted_date or "Not scheduled yet",

Here, formatted_date means the actual date formatted for display, or None when unset. The strange characters in the screenshot look like an incorrectly encoded dash; supplying this text avoids that fallback.

Send me the base URL, your current email-calling block in task.py, and the initiative model/repository getter. Then I can give you the exact replacement using your real name/type fields, without guessing their names.




    
    Yes, understood. Only change patch() in src/resources/task/task.py. Your two creation cases already work.

1. Immediately after fetching the original task:

task = InitiativeTaskRepository.get_task_by_id(id)

Add:

was_team_assigned = task.get("is_team_assigned", False)
previous_main_assessor = task.get("main_assessor")

This remembers its state before the repository changes the flag.

2. After your existing update, timeline and audit code, just before return task_updated, add:

new_main_assessor = task_updated.get("main_assessor")
if (
    was_team_assigned
    and previous_main_assessor is None
    and new_main_assessor is not None
):
    try:
        assigned_users = get_users_by_user_id([new_main_assessor])
        if assigned_users and assigned_users[0].get("email"):
            initiative = InitiativeRepository.get_by_ids(
                [initiative_team_relationship.initiative_id],
                False,
            )[0]
            send_email_task_assessor_assigned(
                task_name=task_updated["task_name"],
                recipients=assigned_users[0]["email"],
                initiative_name=initiative.name,
                initiative_id=initiative.id,
                initiative_type=initiative.initiative_type,
                initiative_link=(
                    f"{INITIATIVE_BASE_URL.rstrip('/')}/{initiative.id}"
                ),
                tasks=[
                    {
                        "task_type": task_updated["task_type"],
                        "task_name": task_updated["task_name"],
                        "expected_for": (
                            task_updated.get("expected_for")
                            or "Not scheduled yet"
                        ),
                    }
                ],
            )
    except Exception:
        logging.exception(
            "Failed to send task assignment email for task %s",
            id,
        )
return task_updated

Replace INITIATIVE_BASE_URL with the actual configuration variable you already use for the working email link.

Keep this block at the same indentation as your existing return task_updated, outside if can_edit_as_team_member and if "task_status" in payload.

That adds exactly your case: previously team-assigned + no assessor → now an assessor selected → email that person. Saving again won’t trigger this condition.
