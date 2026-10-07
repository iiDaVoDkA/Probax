Paste this implementation into your NEW generated migration.
# Preserve its generated docstring and revision identifiers.
# Replace the existing imports and upgrade/downgrade functions.
# This file alone is not an Alembic revision.

import sqlalchemy as sa
from alembic import op


def upgrade():
    # Plain string: keep Jinja placeholders intact for the mailer.
    body = r"""{#
  Expected template data:
  initiative_name, initiative_id, initiative_type, initiative_url,
  tasks: [{task_type, task_name, expected_for}]
  Supply expected_for as an already formatted date string, or None.
  Pass ordinary unescaped strings; the template escapes dynamic values.
#}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>FLOWR - You've been assigned to a new initiative</title>
  </head>
  <body style="margin:0; padding:0; background-color:#ffffff;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="border-collapse:collapse; background-color:#ffffff;">
      <tr>
        <td align="center" style="padding:32px 16px;">
          <!--[if mso]>
          <table role="presentation" width="628" cellpadding="0" cellspacing="0" border="0"><tr><td>
          <![endif]-->
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="max-width:628px; border-collapse:collapse;
                        font-family:BNPPSans,Helvetica,Arial,sans-serif; color:#333333;">
            <tr>
              <td style="padding:24px 0; border-top:3px solid #00915a;
                         font-family:BNPPSans-Light,Helvetica,Arial,sans-serif;
                         font-size:28px; line-height:36px; font-weight:normal;">
                You have been assigned to the following initiative:
              </td>
            </tr>
            <tr>
              <td style="padding:0 0 12px; font-size:20px; line-height:28px;
                         font-family:BNPPSans-Bold,Helvetica,Arial,sans-serif;
                         font-weight:bold; word-wrap:break-word;">
                <a href="{{ initiative_url | e }}"
                   style="color:#00915a; text-decoration:underline;">
                  {{ initiative_name | e }}
                </a>
              </td>
            </tr>
            <tr>
              <td style="padding:0 0 6px; font-size:14px; line-height:22px;">
                <strong>Initiative ID:</strong> {{ initiative_id | e }}
              </td>
            </tr>
            <tr>
              <td style="padding:0 0 28px; font-size:14px; line-height:22px;">
                <strong>Initiative type:</strong>
                {{ initiative_type | default('â', true) | e }}
              </td>
            </tr>
            {% if tasks %}
            <tr>
              <td>
                <table width="100%" cellpadding="0" cellspacing="0" border="0"
                       style="border-collapse:collapse; table-layout:fixed;
                              font-family:BNPPSans,Helvetica,Arial,sans-serif;
                              font-size:14px; line-height:22px; color:#333333;">
                  <thead>
                    <tr bgcolor="#00915a" style="background-color:#00915a; color:#ffffff;">
                      <th scope="col" width="28%" align="left"
                          style="padding:12px; border-right:1px solid #ffffff;
                                 font-size:12px; line-height:18px; font-weight:bold;">
                        TASK TYPE
                      </th>
                      <th scope="col" width="46%" align="left"
                          style="padding:12px; border-right:1px solid #ffffff;
                                 font-size:12px; line-height:18px; font-weight:bold;">
                        TASK NAME
                      </th>
                      <th scope="col" width="26%" align="left"
                          style="padding:12px; font-size:12px; line-height:18px;
                                 font-weight:bold;">
                        EXPECTED FOR
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {% for task in tasks %}
                    <tr bgcolor="#f2f3f2" style="background-color:#f2f3f2;">
                      <td valign="top"
                          style="padding:14px 12px; border:1px solid #ffffff;
                                 word-wrap:break-word;">
                        {{ task.task_type | default('â', true) | e }}
                      </td>
                      <td valign="top"
                          style="padding:14px 12px; border:1px solid #ffffff;
                                 word-wrap:break-word;">
                        {{ task.task_name | e }}
                      </td>
                      <td valign="top"
                          style="padding:14px 12px; border:1px solid #ffffff;
                                 word-wrap:break-word;">
                        {{ task.expected_for | default('â', true) | e }}
                      </td>
                    </tr>
                    {% endfor %}
                  </tbody>
                </table>
              </td>
            </tr>
            {% endif %}
            <tr>
              <td style="padding:28px 0 0;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                       style="border-collapse:collapse;">
                  <tr>
                    <td style="border-top:1px solid #dce5df; padding:16px 0 0;
                               font-size:12px; line-height:18px; color:#66736b;">
                      FLOWR &middot; Initiative Pipeline
                    </td>
                  </tr>
                </table>
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
            template_type="task_assessor_assigned_v1",
            game_name="_",
            body=body,
            subject="FLOWR - You've been assigned to a new initiative",
            description="Initiative task assignment notification",
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
            template_type="task_assessor_assigned_v1",
            locale="en_US",
            game_name="_",
        )
    )
