Oui, on réutilise bien InitiativeRepository.get_status_data(id). Tes captures confirment un détail : son élément [1] est un dictionnaire :

{"name": "ON_HOLD", "is_final_status": False}

On va donc comparer uniquement name.

get_all_status_data() filtre les initiatives actives : il ne convient pas ici, puisque ton PATCH rend les initiatives On Hold/Canceled inactives.

La fonction _get_initiative_status_recipients() proposée sert à rassembler et dédupliquer les emails. Les fonctions de ces captures récupèrent des statuts ; elles ne remplacent pas cette collecte.

Dans mon code précédent, fais seulement ces ajustements.

Avant le with, remplace le bloc de mémorisation par :

check_status_notification = bool(kwargs.get("timeline_status_to_update"))
previous_status = None
if check_status_notification:
    previous_status = (
        InitiativeRepository.get_status_data(id)[1] or {}
    ).get("name")

Après le with, dans le try, remplace le calcul de current_status et event par :

current_status = (
    InitiativeRepository.get_status_data(id)[1] or {}
).get("name")
updated_initiative = InitiativeRepository.get(id)
event = None
if previous_status is None or current_status is None:
    logging.warning(
        "Cannot determine status transition for initiative %s: %s -> %s",
        id,
        previous_status,
        current_status,
    )
elif previous_status != current_status:
    if current_status == "ON_HOLD":
        event = "on_hold"
    elif current_status == "CANCELED":
        event = "canceled"
    elif (
        previous_status in ("ON_HOLD", "CANCELED")
        and updated_initiative.is_active
    ):
        event = "reactivated"

Garde ensuite le bloc if event: avec les destinataires et l’envoi. La variable was_active n’est plus nécessaire : la réactivation est maintenant détectée à partir de l’ancien statut et de l’état actif après modification.