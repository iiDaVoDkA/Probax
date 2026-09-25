We’ll implement one shared task, accessible to eligible team assessors, which returns to the existing individual workflow when someone takes ownership.

I’m taking your confirmation to include My Tasks and shared assessment editing before ownership. Completion and validation still follow their specific workflow rules.

I’ve prepared the full reference, including code examples, searches and test scenarios: FLOWR-271432-implementation-guide.md⁠￼.

Below is the implementation map. The confirmed locations come from your screenshots; where we haven’t seen the actual handler, I give you the symbol to find. These are implementation instructions, not a patch tested against your repository.

flowchart TD
    FRONT["Frontend: add team or assign"] --> API["Existing assignment handler"]
    USERS["FLOWR API: users, roles and teams"] --> API
    API --> TASK["Task and initiative-team relationship"]
    API --> MAIL["Notification recipient selection"]
    MAIL --> BOX["Generic team mailbox"]
    TASK --> RIGHTS["Assignment access rule"]
    USERS --> RIGHTS
    RIGHTS --> LIST["My Tasks and counters"]
    RIGHTS --> WORK["Read, edit and take ownership"]
    WORK --> CLAIM["Set Main Assessor and clear team flag"]
    CLAIM --> TASK

1. First, identify the scope of the existing assignment action.
    Where: search around initiative_team_members.py, main_assessor, accountant_id and teamAccountantId.
    An earlier excerpt showed a loop updating several tasks belonging to an initiative/team relationship. Therefore, establish whether the existing Main Assessor action assigns one task or the team’s assessment as a whole.
    What to connect: the displayed Main Assessor, the relationship’s stored owner if applicable, and every task already covered by that action.
    Why: updating one task while the Community still shows another Main Assessor would create inconsistent ownership.

rg -n 'main_assessor|accountant_id|teamAccountantId' src
rg -n 'get_by_initiative_id_and_team_id|get_by_relationship_id_no_errors' src

    Keep the existing scope when extending the action. A task-level action must not unexpectedly claim another team’s work.
2. Add the new field to InitiativeTask.
    Where confirmed: flowr-initiative-pipeline → src/models/task.py, beside main_assessor.

from sqlalchemy import false
is_team_assigned = db.Column(
    db.Boolean,
    nullable=False,
    default=False,
    server_default=false(),
)

    Because your model has a custom constructor, append an optional is_team_assigned=False parameter and initialize it:

self.is_team_assigned = is_team_assigned

    Why: the application needs to distinguish these states:

State	main_assessor	is_team_assigned
Ordinary unassigned task	None	False
Task available to the team	None	True
Task assigned to Alice	Alice’s ID	False

    Enforce this rule wherever assignment changes: team-assigned requires a valid team relationship and no individual Main Assessor.
3. Create the Python migration.
    Where: the migration history that owns this particular task table. Check its existing schema and latest revision.
    The migration body should look like:

from alembic import op
import sqlalchemy as sa
def upgrade():
    op.add_column(
        "task",
        sa.Column(
            "is_team_assigned",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
def downgrade():
    op.drop_column("task", "is_team_assigned")

    Match the existing schema configuration in both operations. Generate the revision header using the project’s established process.
    Why: existing tasks receive False. Historical tasks without an assignee must not suddenly become accessible to a team.
    server_default supplies a database default; the model’s default supplies an insertion default on the Python/SQLAlchemy side. 
    From our previous migration work: use the current migration head, not an old revision ID remembered from the manager or SUPER_ADMIN tickets.
4. Expose the field through the task API.
    Where: InitiativeTask.to_json(), then any task response schema or intermediary mapper that explicitly lists fields.
    Add:

"is_team_assigned": self.is_team_assigned,

    Why: the frontend must receive the saved assignment state.
    Keep the existing relationship_id and main_assessor. In the frontend task mapper, follow the existing naming convention:

isTeamAssigned: apiTask.is_team_assigned === true,

    apiTask here is an example argument name.
    Returning the flag does not make it freely editable. The backend should set it through authorized assignment actions.
5. Reuse the role, manager flag and membership mechanisms.
    Where: the FLOWR API provider already supplying team users and assessor candidates, plus its existing initiative-service client.
    Keep two separate eligibility rules:

Purpose	Required conditions
Automatically select a manager	Team membership + Initiative Manager flag + Initiative Assessor role
Access a team-assigned task	Team membership + Initiative Assessor role

    Why: requiring the manager flag for team access would recreate the original problem.
    This preserves what we implemented in the previous ticket:
    * Automatic selection requires both the manager flag and role.
    * Manual candidates require the Initiative Assessor role, without requiring the manager flag.
    * The Main Assessor badge reflects actual assignment, not manager eligibility.
    Use the actual field spelling in your code. One supplied SQL excerpt uses is_initiative_manager, while earlier frontend work discussed isManagerInitiative; verify their existing mapping.
    Also, do not assume InitiativeTeamMembers contains every organizational team member. It links users to an initiative/team relationship. Reuse the actual membership source used by team-user selection.
6. Add the fallback to task creation and assignment.
    Where: the existing automatic Main Assessor selection and the backend handler that persists it. Search create_tasks, main_assessor, and the relevant team/key-question handlers.
    Apply this decision:

Explicit valid individual assignment:
    keep/apply that person
    is_team_assigned = False
Otherwise, eligible manager found:
    main_assessor = manager ID
    is_team_assigned = False
Otherwise, eligible team fallback applies:
    main_assessor = None
    is_team_assigned = True

    Why: this adds the missing branch while preserving explicit assignments.
    Cover every relevant task creation path: adding a team, templates, key-question changes and regeneration.
    A detail that matters: when Alice already owns the team’s assessment, tasks generated later must inherit the current intended assignment. They must not return to the team merely because Alice lacks the manager flag.
    Also preserve PATCH semantics: a missing main_assessor field means “leave unchanged.” An explicit None follows the existing unassignment rules. This is the same missing/null/value distinction that mattered in the Committee Agenda ticket.
7. Extend backend access checks.
    Where: the code that raises InitiativeTaskNotEditableByUserError, plus the corresponding read and assignment checks. The errors.py declaration itself is not where authorization is decided.
    Conceptually, the new eligibility check is:

# Pseudocode: adapt helper names to your existing code.
def has_team_assignment_access(user, task):
    if not task.is_team_assigned:
        return False
    if task.main_assessor is not None:
        return False
    relation = task.relation_ship
    if relation is None or relation.team_id is None:
        return False
    return (
        has_initiative_assessor_role(user)
        and belongs_to_team(user, relation.team_id)
    )

    Why: My Tasks visibility and backend authorization must agree.
    Integrate this into the assignment eligibility part of authorization. Keep the existing restrictions for the action, status, scope and editable fields.
    Apply it to task reads, assessment edits and claiming. Check the parent initiative endpoint used by the email link too.
    Two regression points:
    * An old unconditional team_members_ids check must not continue granting shared assessor access after ownership changes.
    * Bob’s already-open browser must not let him save after Alice claims the task. The backend must check current ownership again.
    Preserve existing independent admin permissions. The SUPER_ADMIN ticket is a reason to inspect those paths, not to assume the project-task authorization code is also Initiative’s code.
8. Extend the My Tasks query and its counters.
    Where: trace the My Tasks screen’s Saga/network request to its backend endpoint. We haven’t identified that exact module from the screenshots.
    Extend its ownership filter to:

Existing personal-task condition
OR
(
    is_team_assigned = True
    AND main_assessor IS NULL
    AND task's team is one of the user's eligible teams
)

    Why: allowing a task’s detail endpoint does not automatically include it in My Tasks.
    Preserve status, search, date and initiative filters. Apply the ownership condition before pagination, and use it for the corresponding counts.
    Prevent duplicate results from membership/role joins. Resolve eligible teams once per request through the existing trusted source.
    A shared task may appear in Alice’s and Bob’s personal lists, but it is still one task in a global dashboard count.
9. Make taking ownership atomic.
    Where confirmed: src/repositories/task.py contains InitiativeTaskRepository.patch_task. Extend the authorized assignment handler above it.
    The transition changes these together:

task.main_assessor = authenticated_user.id
task.is_team_assigned = False

    Why: Alice and Bob might click at the same time.
    The backend must only claim a task that is still team-assigned and still has no individual owner. Use the existing transaction style with a row lock or a conditional update, and check the result. PostgreSQL rechecks an update’s condition after a competing update commits, which supports this conditional-claim approach. 
    If assignment covers an initiative/team relationship, protect and update that whole intended scope consistently. Do not commit inside a loop.
    The second claimant receives the application’s conflict response and refreshes. A repeated request from the successful claimant must not trigger duplicate emails.
    Do not simply add the flag to an unrestricted PATCH allowlist. Validate assignment-specific fields, including main_assessor and relationship_id.
10. Connect the frontend display and save flow.

These are the relevant components from our previous work:

Location	What to change	Why
Task entity mapper	Preserve isTeamAssigned	Carry the API field into Redux
InitiativeCommunity / CommunityTeam	Handle team responsibility	Display the fallback coherently
CommunityMember	Keep the badge tied to actual assignment	A manager flag does not mean ownership
Assignment modal	Reuse existing selection/claim action	Preserve the familiar workflow
Task detail / My Tasks	Show team state and allowed actions	Explain availability to eligible users
Save Saga	Consume saved response and refresh affected state	Keep detail, list and counters consistent
Existing error UI	Handle another person claiming first	Avoid silent failed saves

Previous context suggests the badge uses teamAccountantId. Trace that mapping before changing it independently of task ownership.

Put the new flag in the task mapper. Our earlier src/redux/entities/users/modelize.js work remains relevant for user flags and roles, but this new field is not a user attribute.

From the Initiative Edit work: refresh the displayed card and edit form from the successful save. Do not display an assignment as successful while the request failed.

11. Change notification recipients.

Where confirmed: src/util/email_helpers.py contains assignment/change/reminder helpers. Locate their callers—the callers select recipients.

State	Recipient
Team-assigned	Generic account matched to that team with is_team=True
Individually assigned	Existing individual notification recipient

Why: notifications and access are separate mechanisms.

Use the existing configured mailbox address. Keep it out of main_assessor.

Send one mailbox notification for the intended event, without looping over all assessors. Check batching and retries for duplicate messages.

Also inspect reminders and daily summaries if they derive recipients from main_assessor.

The literal "generic_email" in your screenshot is a template argument, not the mailbox address. Some shown helpers contain test text, so verify the live caller before reusing them.

12. Preserve assessment state, completion and audit.

Where: assessment write handlers, patch_task callers, status transitions and the existing Initiative history mechanism.

Keep one shared task record. The assignment flag must not itself change task_status.

Check:

* Editing, completion and cancellation retain their action-specific rules.
* Existing parent/child and global-risk behavior remains consistent.
* last_assessor records the real person performing the relevant action.
* Assignment history records the actual claimant and previous ownership.
* Generic mailbox identity is never substituted for the acting user.

Do not confuse the relationship’s accountant_id with the similarly named argument passed to patch_task; trace their callers.

For shared edits, reuse existing conflict handling. A row lock prevents competing assignment writes, but it does not automatically detect that someone submitted an outdated form. Send changed fields and inspect any existing version checks.

13. Test the behaviors that could regress.

Follow the nearby tests and fixtures, as you requested in earlier tickets.

Test	Expected result
Manager flag + assessor role	Existing automatic individual assignment
Manager flag without role	Not automatically selected
Three eligible team assessors	One task visible to all three in My Tasks
Same team, wrong role	No new team access
Correct role, wrong team	No new team access
Old unassigned task	No new access; flag remains False
Alice claims	Individual ownership; shared team access ends
Bob saves an old open form afterward	Backend refuses team-derived access
Two simultaneous claims	One winner
Description-only PATCH	Assignment stays unchanged
New task after ownership	Correct current assignment inherited
Multi-team initiative	Other teams’ ownership remains intact
Pagination and counters	No duplicates; list and counts agree
Existing privileged access and completion	Existing behavior preserved

Add notification and frontend save/conflict checks. Run the concurrent-claim case with independent database transactions.

From the manager ticket: fixtures need the actual manager flag and role explicitly. A database migration does not populate a mocked user dictionary.

14. Implement in these checkpoints.

Order	Deliverable
A	Model + migration + constructor + serialization
B	Creation/fallback decision + existing assignment scope
C	Backend access + My Tasks query/counts
D	Atomic ownership change + audit
E	Frontend mapping/display/save + notifications
F	Focused regression tests + coordinated deployment

Apply the additive migration before code depends on the column. Enable the fallback only when all relevant backend writers and permission checks support it.

Once shared tasks exist, reverting the code or dropping the flag needs care: older code would see only an empty Main Assessor.

Your first coding deliverable is A: the model, migration, constructor and response field. Its acceptance check is simple: existing tasks remain False, a new task can persist True, and the API returns the saved value.