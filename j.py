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



FLOWR — task creation and reassignment emails

These are focused edits for src/resources/task/task.py in flowr-initiative-pipeline, based on the POST, PATCH and repository screenshots supplied on 8 October 2026. This is a patch guide, not a replacement for the entire resource file. The corporate repository has not been edited or run here.

What the repository confirms

• create_tasks() saves main_assessor and is_team_assigned from each payload. The shown method does not select a manager or send an email.
• Its return value is a list of task dictionaries, grouped into global-risk tasks and other tasks. Do not pair these dictionaries with the original payloads by position.
• patch_task() already sets task.is_team_assigned = False when a non-null main_assessor is supplied. Keep that behavior.
• The shown PATCH repository code flushes and returns the updated dictionary; it does not send an assignment email. The notification condition must compare the previous and new assessor, independently of the new team flag.

1. Add one shared notification function in the resource file

Place this above class InitiativeTaskResource. It uses the repository classes, PLM user functions and send_email_task_assessor_assigned already used by your POST.

initiative_base_url must be your existing environment-specific initiative base URL. The caller examples use the illustrative constant name INITIATIVE_BASE_URL: substitute your actual configuration variable, or define/import it before running. It must contain the base route before /<initiative_id>. Do not pass the literal string "initiative_link".

Keep the working email helper, including its explicit game_name="_".

import logging


def _notify_task_assignment(task, initiative_base_url):
    """Send one assignment notification for this saved task."""
    task_id = task.get("id")

    try:
        relationship = (
            InitiativeTeamRelationshipRepository.get_by_relationship_ids(
                [task["relationship_id"]]
            )[0]
        )

        # A task-level assessor takes priority over the relationship assessor.
        assessor_id = task.get("main_assessor")
        if assessor_id is None:
            assessor_id = relationship.accountant_id

        recipients = set()
        recipient_kind = "unassigned"

        if assessor_id is not None:
            recipient_kind = "individual"
            recipients = {
                member["email"].strip()
                for member in (get_users_by_user_id([assessor_id]) or [])
                if (member.get("email") or "").strip()
            }

        elif task.get("is_team_assigned") and relationship.team_id is not None:
            recipient_kind = "team"
            recipients = {
                member["email"].strip()
                for member in (get_users() or [])
                if member.get("is_team") is True
                and (member.get("email") or "").strip()
                and any(
                    team["id"] == relationship.team_id
                    for team in (member.get("teams") or [])
                )
            }

            # Preserve the mailbox preference from your existing POST.
            if len(recipients) > 1:
                preferred = {
                    email
                    for email in recipients
                    if email.split("@", 1)[0].lower().endswith("-team")
                }
                recipients = preferred or {sorted(recipients)[0]}

        if not recipients:
            logging.warning(
                "[TASK-MAIL] skipped task_id=%r relationship_id=%r "
                "kind=%s assessor_id=%r team_id=%r is_team_assigned=%r: "
                "no recipient resolved",
                task_id,
                task["relationship_id"],
                recipient_kind,
                assessor_id,
                relationship.team_id,
                task.get("is_team_assigned"),
            )
            return None

        if not initiative_base_url:
            raise ValueError("The initiative base URL is not configured")

        initiative = InitiativeRepository.get_by_ids(
            [relationship.initiative_id], False
        )[0]
        initiative_type = getattr(
            initiative.initiative_type, "value", initiative.initiative_type
        )
        expected_for = task.get("expected_for") or "Not scheduled yet"
        if hasattr(expected_for, "isoformat"):
            expected_for = expected_for.isoformat()

        logging.info(
            "[TASK-MAIL] requesting task_id=%r initiative_id=%r "
            "kind=%s recipient_count=%d",
            task_id,
            initiative.id,
            recipient_kind,
            len(recipients),
        )

        result = send_email_task_assessor_assigned(
            task_name=task["task_name"],
            recipients=sorted(recipients),
            initiative_name=initiative.name,
            initiative_id=initiative.id,
            initiative_type=initiative_type,
            initiative_link=(
                f"{initiative_base_url.rstrip('/')}/{initiative.id}"
            ),
            tasks=[
                {
                    "task_type": task["task_type"],
                    "task_name": task["task_name"],
                    "expected_for": expected_for,
                }
            ],
        )
        logging.info(
            "[TASK-MAIL] helper returned task_id=%r result=%r", task_id, result
        )
        return result

    except Exception:
        # Preserve the existing nonfatal notification behavior.
        logging.exception(
            "[TASK-MAIL] assignment notification failed task_id=%r", task_id
        )
        return None

This keeps your existing team-directory filters. If the log says kind=team and no recipient resolved, inspect whether the team mailbox record actually has is_team=True, a nonempty email, and the relevant team in teams. Do not replace the mailbox with an arbitrary person’s email.

2. Change POST

1. At the beginning of post, before its with SessionCriticalActionManager(...), add:

created_tasks = None

2. Keep the existing read-only branch, authorization checks, and assignment/flag calculation in the payload loop. Remove both old email sections:
  • The entire if payload["is_team_assigned"]: mailbox-selection/send block. Keep the preceding flag calculation.
  • The entire block starting with # Keep the existing first-task individual notification.
3. Replace the existing final creation return, at its current indentation inside the authorized creation branch:

return InitiativeTaskRepository.create_tasks(payloads)

with:

created_tasks = InitiativeTaskRepository.create_tasks(payloads)

4. Add this at the end of post, outside the with block, at the same indentation as that with:

if created_tasks is not None:
    for created_task in created_tasks:
        _notify_task_assignment(created_task, INITIATIVE_BASE_URL)

return created_tasks

Each email now uses the saved task’s own relationship_id, name, type, date and assessor. Creation happens before notification, and the old two email sections cannot also send duplicates.

Existing manager rule to watch

Your POST sets is_team_assigned = not has_eligible_manager. The shown repository does not fill main_assessor when a manager exists. If both main_assessor and accountant_id remain null but this rule sets the flag false, the saved task has no notification recipient; the new warning will show kind=unassigned.

The code above preserves that assignment policy. Do not remove the manager check just to trigger an email. If that state appears, the assignment flow must either supply the eligible assessor or explicitly keep the task team-assigned, according to the agreed business rule.

3. Change PATCH

Keep all existing role checks, same-team validation, timeline handling and audit records.

1. At the start of patch, before the with block, add:

task_updated = None
notify_new_assessor = False

2. After fetching task and initiative_team_relationship, but before calling patch_task, capture the previous effective recipient:

previous_assessor_id = task.get("main_assessor")
if previous_assessor_id is None:
    previous_assessor_id = initiative_team_relationship.accountant_id

The fallback prevents another assignment email if a person already assigned through the relationship is simply copied into main_assessor.

3. Keep the existing update and all following timeline/audit code:

task_updated = InitiativeTaskRepository.patch_task(id, payload, user["id"])

4. Replace the existing return task_updated inside the with block, after the timeline/audit code, with:

new_assessor_id = task_updated.get("main_assessor")
notify_new_assessor = (
    new_assessor_id is not None
    and new_assessor_id != previous_assessor_id
)

This must be outside if can_edit_as_team_member and outside if "task_status" in payload. It applies to every authorized editor.

5. Add this outside the with block, at the same indentation as that with:

if notify_new_assessor:
    _notify_task_assignment(task_updated, INITIATIVE_BASE_URL)

return task_updated

Do not require task_updated["is_team_assigned"] to be true: the repository correctly makes it false once a person is assigned. Do not add is_team_assigned=False to a team member’s PATCH payload; your existing resource guard protects that field and the repository already updates it.

Transaction boundary

The notification calls above run after normal exit from your existing transaction context. The screenshot’s db.session.flush() alone does not prove a commit. Confirm that SessionCriticalActionManager commits on success and propagates save/commit failures; its implementation was not supplied. Do not add an extra commit() to either repository method. If the context suppresses a failed commit, the success path must be adjusted before relying on these calls.

Checks in INT

|Action                                                           |Expected assignment notification                                |
|-----------------------------------------------------------------|----------------------------------------------------------------|
|Create a team-assigned task with no main/relationship assessor   |One template request to the resolved team mailbox recipient list|
|Set its main assessor to A                                       |A receives the task notification; team receives no new one      |
|Save again with A unchanged                                      |No assignment notification                                      |
|Edit only its date, name or status                               |No assignment notification                                      |
|Change A to B                                                    |B receives the task notification                                |
|Clear the main assessor                                          |No individual assignment notification from this change          |
|Create with a main assessor and a different relationship assessor|Main assessor receives the notification                         |
|Create tasks for multiple initiatives together                   |Each email contains its own task and initiative data            |
|Creation/update fails                                            |No assignment notification for the failed operation             |

This change prevents duplicate assignment notifications from unchanged-assignee edits and duplicate POST code paths. It is not a durable exactly-once delivery mechanism across concurrent requests, retries, process crashes or mail-service failures.

Validation performed here

The helper and insertion snippets were syntax-checked. Local checks used mocked repositories, user-directory lookups and an email recorder to verify team routing, individual priority, per-task initiative data, blank-date fallback, changed-assignee detection and nonfatal mail failures. No connection to the corporate database or mail service was made. Transaction-manager behavior and the actual team mailbox records still require the INT checks above.

