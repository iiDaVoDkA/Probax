Get the initiative through team_relationship, which you already load. The variables in my earlier example need to be assigned from that initiative.

1. Load the initiative immediately after loading the relationship

Import the repository:

from repositories.initiative import InitiativeRepository

Inside your existing loop:

for payload in payloads:
    team_relationship = (
        InitiativeTeamRelationshipRepository.get_by_relationship_ids(
            [payload["relationship_id"]]
        )[0]
    )
    # The relationship connects this task to its initiative.
    initiative_id = team_relationship.initiative_id
    initiative = InitiativeRepository.get_by_ids(
        [initiative_id],
        False,
    )[0]
    # Your existing assignment logic continues here.

Your earlier initiative resource uses get_by_ids with an ID list and the is_active_only flag; False disables that filtering for this lookup.

2. Where each email value comes from

Email value	Source
initiative_id	team_relationship.initiative_id
initiative_name	The name field on the loaded initiative
initiative_type_label	The initiative’s type, converted to its display label if necessary
initiative_link	The configured frontend URL plus the initiative route
Task details	The current payload

I still need to see the actual initiative model to give you the exact name/type expressions. Don’t assume they are initiative.name or initiative.type.

You already have models/initiative.py open. Show me its fields and to_json() method. For the link, your task_reminder_notifications.py tab should show how the existing reminder builds plm_url; we can reuse that construction.

3. Fix the second email block’s task reference

In your second screenshot, the individual email is outside the loop. At that point, payload refers to the last task, while you load the relationship from payloads[0].

Start that block with:

first_payload = payloads[0]
team_relationship = (
    InitiativeTeamRelationshipRepository.get_by_relationship_ids(
        [first_payload["relationship_id"]]
    )[0]
)
initiative_id = team_relationship.initiative_id
initiative = InitiativeRepository.get_by_ids(
    [initiative_id],
    False,
)[0]

Then use first_payload throughout that individual email:

task_name=first_payload["task_name"],
tasks=[
    {
        "task_type": first_payload["task_type"],
        "task_name": first_payload["task_name"],
        "expected_for": first_payload.get("expected_for"),
    }
],

Also derive its initiative name, type and link from this newly loaded initiative, rather than reusing values left over from the loop.