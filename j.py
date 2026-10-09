Oui, c’est le bon PATCH dans src/resources/initiative/initiative.py. On peut ajouter l’envoi après le bloc with, juste avant return [initiative_json].

Voici les quatre ajouts.

1. Ajoute ces imports

logging et les repositories sont déjà importés dans ta capture.

from client.plm import get_users
from config import REMOTE_URL
from util.email_helpers import send_email_initiative_status_changed

2. Après les imports, avant class InitiativesResource, ajoute cette fonction

Elle récupère les destinataires de toutes les tâches, sans filtrer leurs statuts. Le fallback accountant_id couvre les tâches dont l’assessor est porté par la relation d’équipe.

def _get_initiative_status_recipients(initiative_id):
    relationships = {
        rel.id: rel
        for rel in InitiativeTeamRelationshipRepository.get_by_initiative_id(
            initiative_id
        )
    }
    if not relationships:
        return []
    tasks = InitiativeTaskRepository.get_by_relationship_id_no_errors(
        list(relationships)
    )
    assessor_ids = set()
    team_ids = set()
    for task in tasks:
        relationship = relationships[task.relationship_id]
        if task.main_assessor is not None:
            assessor_ids.add(task.main_assessor)
        elif task.is_team_assigned:
            if relationship.team_id is not None:
                team_ids.add(relationship.team_id)
        elif relationship.accountant_id is not None:
            assessor_ids.add(relationship.accountant_id)
    users = get_users() or []
    recipients = {
        member["email"].strip().lower()
        for member in users
        if member["id"] in assessor_ids
        and (member.get("email") or "").strip()
    }
    for team_id in team_ids:
        team_emails = {
            member["email"].strip().lower()
            for member in users
            if member.get("is_team") is True
            and (member.get("email") or "").strip()
            and any(
                team["id"] == team_id
                for team in (member.get("teams") or [])
            )
        }
        if team_emails:
            # Même sélection de boîte d'équipe que dans ton POST.
            preferred = {
                email
                for email in team_emails
                if email.split("@", 1)[0].endswith("-team")
            }
            recipients.update(preferred or {sorted(team_emails)[0]})
    return sorted(recipients)

3. Dans InitiativeByIdResource.patch(), juste avant le with vers la ligne 430

Cela mémorise l’état avant toute modification. J’utilise get_status_data(id)[1], que ton endpoint GET expose déjà comme current_status.

check_status_notification = bool(kwargs.get("timeline_status_to_update"))
was_active = initiative.is_active
previous_status = (
    InitiativeRepository.get_status_data(id)[1]
    if check_status_notification
    else None
)
# Ton bloc existant commence ici :
with SessionCriticalActionManager(
    "Modify an initiative", db.session, DEV_TEAM_EMAILS
):
    # ... ton code existant ...

4. Tout en bas du même PATCH, remplace le dernier return [initiative_json] par ceci

Aligne le premier if avec le with : l’envoi se fait après sa sortie, une fois les mises à jour terminées.

if check_status_notification:
    try:
        current_status = InitiativeRepository.get_status_data(id)[1]
        updated_initiative = InitiativeRepository.get(id)
        event = None
        if previous_status != current_status:
            requested_status = kwargs.get(
                "initiative_status_not_matching_comitee_status"
            )
            if requested_status == "ON_HOLD":
                event = "on_hold"
            elif requested_status == "CANCELED":
                event = "canceled"
            elif not was_active and updated_initiative.is_active:
                event = "reactivated"
        if event:
            recipients = _get_initiative_status_recipients(id)
            if not recipients:
                logging.warning(
                    "No recipients for initiative %s, event %s",
                    id,
                    event,
                )
            for email in recipients:
                try:
                    send_email_initiative_status_changed(
                        recipients=email,
                        event=event,
                        initiative_name=updated_initiative.name,
                        initiative_id=updated_initiative.id,
                        initiative_type=getattr(
                            updated_initiative.initiative_type,
                            "value",
                            updated_initiative.initiative_type,
                        ),
                        initiative_link=(
                            f"{REMOTE_URL.rstrip('/')}"
                            f"/initiative/{updated_initiative.id}"
                        ),
                    )
                except Exception:
                    logging.exception(
                        "Failed to send initiative notification: id=%s event=%s",
                        id,
                        event,
                    )
    except Exception:
        logging.exception(
            "Failed to prepare status notifications for initiative %s",
            id,
        )
return [initiative_json]

La sélection des destinataires et les transitions ont été vérifiées avec des données simulées. À tester dans INT : passage en On Hold, annulation, réactivation, puis un nouvel enregistrement sans changement de statut. Un assessor ayant plusieurs tâches doit recevoir un seul email par transition.