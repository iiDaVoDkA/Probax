Your helper needs two fixes: send initiative_url to match the HTML, and put the task name inside the tasks list.

1. Replace these two functions in src/util/email_helpers.py

Downloadable version: email_assignment_helpers.py⁠￼.

from clients import mailer
def send_email_task_assessor_assigned(
    task_name,
    recipients,
    *,
    initiative_name,
    initiative_id,
    initiative_type,
    initiative_link,
    tasks=None,
):
    if tasks is None:
        tasks = [
            {
                "task_type": None,
                "task_name": task_name,
                "expected_for": None,
            }
        ]
    injections = {
        "initiative_name": initiative_name,
        "initiative_id": initiative_id,
        "initiative_type": initiative_type,
        # Must match {{ initiative_url }} in the HTML:
        "initiative_url": initiative_link,
        "tasks": tasks,
    }
    return mailer.send_mail_template(
        recipients,
        "task_assessor_assigned_v1",
        injections=injections,
    )
def send_email_assessor_changed(
    initiative_id,
    recipients,
    *,
    initiative_name,
    initiative_type,
    initiative_link,
    tasks,
):
    return send_email_task_assessor_assigned(
        task_name="",
        recipients=recipients,
        initiative_name=initiative_name,
        initiative_id=initiative_id,
        initiative_type=initiative_type,
        initiative_link=initiative_link,
        tasks=tasks,
    )

The initiative details are now required. Update every call to both functions, otherwise old two-argument calls will raise a TypeError.

2. Call it where your existing notification is sent

For this ticket, replace the existing call in the resource or repository where it already exists. If the repository sends the notification, adding another send in the resource would duplicate it.

For the team-assignment branch, the call would have this structure:

send_email_task_assessor_assigned(
    task_name=payload["task_name"],
    recipients=team_email,
    initiative_name=initiative_name,
    initiative_id=initiative_id,
    initiative_type=initiative_type_label,
    initiative_link=initiative_link,
    tasks=[
        {
            "task_type": task_type_label,
            "task_name": payload["task_name"],
            "expected_for": expected_for_display,
        }
    ],
)

The variables for the initiative, type labels, link and date above must come from your actual handler. Their field names aren’t visible in your screenshot, so this is the call structure, not a complete repository patch.

For an individual assignment, use the assessor recipient already selected by that branch instead of team_email.

Pass a readable type label and an already formatted date, for example:

{
    "task_type": "Assessment",
    "task_name": "Review the initiative",
    "expected_for": "15/10/2026",
}

3. When changing the main assessor

Collect the rows for the tasks actually reassigned to that person, then call:

send_email_assessor_changed(
    initiative_id=initiative_id,
    recipients=assessor_email,
    initiative_name=initiative_name,
    initiative_type=initiative_type_label,
    initiative_link=initiative_link,
    tasks=reassigned_task_rows,
)

For several tasks on the same initiative going to the same recipient, make this call once after the reassignment loop succeeds, using the existing transaction/send timing.

One separate issue: your terminal shows ModuleNotFoundError: No module named 'clients'. That happens before the email helper runs. The standalone script still needs the API’s working interpreter and import setup; these helper changes won’t resolve that import error.

Send me the existing email call in your task resource/repository, with roughly 20 lines around it. Then I can replace the illustrative variables above with your actual fields.