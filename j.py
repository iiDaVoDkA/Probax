
LOWR 271870 — initiative hold, cancel and reactivation emails

Prepared from the ticket screenshot. This covers the template and email helper; the initiative status endpoint has not been supplied, so the sending trigger is not yet wired into the application.

Required behavior

|Initiative event|Subject                                                   |Main message                                      |
|----------------|----------------------------------------------------------|--------------------------------------------------|
|Put on hold     |FLOWR - The initiative you’ve been assigned to is on hold |The initiative you’ve been assigned to is on hold |
|Canceled        |FLOWR - The initiative you’ve been assigned to is canceled|The initiative you’ve been assigned to is canceled|
|Reactivated     |FLOWR - Reactivation of the initiative 131                |The initiative 131 has been reactivated           |

131 is illustrative; use the real initiative ID. Each message also contains the linked initiative name, initiative ID and initiative type. Use the same green styling as the assignment email, with no logo. The ticket does not request a task table.

The event is a change to the initiative, not an individual task’s status. Notify the assessors in charge of its tasks. An unchanged status must not trigger another status email. Use one notification per assessor for the initiative event even if that assessor has several tasks.

Step 1 — add the template through a new migration

In flowr-mailer-api, create a new Alembic revision using your normal project workflow. Keep its generated revision metadata and dependency. Paste the following imports and function bodies into that new migration; do not replace an already applied migration.

This adds one template row. Subjects and introductory messages are supplied by the helper in Step 2. The HTML is an ordinary triple-quoted string; SQL parameters are bound separately.

import sqlalchemy as sa
from alembic import op


def upgrade():
    body = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>FLOWR - Initiative update</title>
</head>
<body style="margin:0; padding:0; background-color:#ffffff;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
         border="0" style="border-collapse:collapse; background-color:#ffffff;">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <!--[if mso]>
        <table role="presentation" width="600" cellpadding="0" cellspacing="0"
               border="0"><tr><td>
        <![endif]-->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
               border="0" style="max-width:600px; border-collapse:collapse;
               font-family:Arial,Helvetica,sans-serif; color:#333333;">
          <tr>
            <td style="border-top:4px solid #00965e; padding:24px 0 20px;">
              <h1 style="margin:0; font-size:23px; line-height:32px;
                         font-weight:700; color:#252525;">
                {{ notification_message | e }}
              </h1>
            </td>
          </tr>
          <tr>
            <td style="padding:0 0 18px; font-size:20px; line-height:28px;
                       font-weight:700;">
              <a href="{{ initiative_url | e }}"
                 style="color:#008653; text-decoration:underline;">
                {{ initiative_name | e }}
              </a>
            </td>
          </tr>
          <tr>
            <td style="padding:0 0 10px; font-size:14px; line-height:22px;">
              <strong>Initiative ID:</strong> {{ initiative_id | e }}
            </td>
          </tr>
          <tr>
            <td style="padding:0 0 28px; font-size:14px; line-height:22px;">
              <strong>Initiative type:</strong> {{ initiative_type | e }}
            </td>
          </tr>
          <tr>
            <td style="border-top:1px solid #dce5df; padding:16px 0 0;
                       color:#666666; font-size:12px; line-height:18px;">
              FLOWR - Initiative Pipeline
            </td>
          </tr>
        </table>
        <!--[if mso]>
        </td></tr></table>
        <![endif]-->
      </td>
    </tr>
  </table>
</body>
</html>"""

    op.execute(
        sa.text(
            """
            INSERT INTO template
                (locale, template_type, game_name, body, subject, description)
            VALUES
                (:locale, :template_type, :game_name, :body, :subject, :description)
            """
        ).bindparams(
            locale="en_US",
            template_type="initiative_status_changed_v1",
            game_name="_",
            body=body,
            subject="{{ notification_subject }}",
            description="Initiative hold, cancellation and reactivation notification",
        )
    )


def downgrade():
    op.execute(
        sa.text(
            """
            DELETE FROM template
            WHERE template_type = :template_type
              AND locale = :locale
              AND game_name = :game_name
            """
        ).bindparams(
            template_type="initiative_status_changed_v1",
            locale="en_US",
            game_name="_",
        )
    )

Apply that new migration to the database used by the target mailer environment before testing the new mail type. The runtime mailer code does not need a new rendering path.

Step 2 — add a helper to the pipeline

Add this function to src/util/email_helpers.py in flowr-initiative-pipeline. Reuse the existing mailer import used by send_email_task_assessor_assigned.

The strings on_hold, canceled and reactivated below are notification events, not assumptions about the names of the initiative’s stored status values.

def send_email_initiative_status_changed(
    recipients,
    *,
    event,
    initiative_name,
    initiative_id,
    initiative_type,
    initiative_link,
):
    if event == "on_hold":
        message = "The initiative you've been assigned to is on hold"
        subject = "FLOWR - " + message
    elif event == "canceled":
        message = "The initiative you've been assigned to is canceled"
        subject = "FLOWR - " + message
    elif event == "reactivated":
        message = f"The initiative {initiative_id} has been reactivated"
        subject = f"FLOWR - Reactivation of the initiative {initiative_id}"
    else:
        raise ValueError(f"Unsupported initiative notification event: {event!r}")

    if not recipients:
        raise ValueError("At least one assessor recipient is required")

    return mailer.send_mail_template(
        recipients,
        "initiative_status_changed_v1",
        locale="en_US",
        game_name="_",
        injections={
            "notification_subject": subject,
            "notification_message": message,
            "initiative_name": initiative_name,
            "initiative_id": initiative_id,
            "initiative_type": getattr(initiative_type, "value", initiative_type),
            "initiative_url": initiative_link,
        },
    )

The explicit game_name="_" preserves the working template lookup convention from the assignment-email fix.

Step 3 — connect it to the initiative change

Next, inspect the resource and repository methods called by On Hold, Cancel and Reactivate for an initiative. That source is needed to identify the stored state fields, the transaction boundary and the existing task/assessor queries. Do not insert this notification into the individual task-status PATCH simply because it also contains ON_HOLD and CANCELED values.

At that integration point:

1. Capture the previous initiative state before saving.
2. Detect a real hold/cancel transition or a valid reactivation through the existing business logic.
3. Resolve the assessors responsible for the initiative’s tasks using the actual assignment fields. Deduplicate recipients for this initiative event.
4. After a successful state change, call the helper for each intended assessor using the appropriate event and current initiative details.
5. For the link, reuse the working REMOTE_URL expression from the assignment email. If that setting contains only the frontend base address, the expression is f"{REMOTE_URL.rstrip('/')}/initiative/{initiative.id}".

The ticket does not specify the recipient for a task that still has only a team assignment. Keep that as a business-rule question when wiring the recipient selection; do not silently treat the team mailbox as an individually assigned assessor.

Validation and remaining work

Python syntax, the three subject/message mappings, rejection of unsupported events, injection keys and the template lookup tuple were checked locally with mocks. No email was sent and no database was modified. Jinja rendering and Outlook appearance have not been tested here because the rendering dependency is unavailable in this workspace.

The new migration still needs its project-generated revision header, the initiative endpoint still needs its trigger, and the end-to-end checks must be run in INT: hold, cancel, reactivation, unchanged-state save and an assessor with multiple tasks.