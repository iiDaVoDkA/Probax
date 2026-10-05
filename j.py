Avec ce modèle, on peut filtrer directement via InitiativeTeamRelationship.team_id.

Cette version applique la règle stricte : une équipe de l’utilisateur doit être rattachée à l’initiative. Ses propres initiatives sans équipe commune seront donc également masquées.

1. Dans src/repositories/initiative.py, ajoute aux imports :

from sqlalchemy import or_, select
from models import InitiativeTeamRelationship

Puis ajoute cette méthode dans InitiativeRepository :

@staticmethod
def get_by_team_ids_or_by_ids(
    team_ids, initiative_ids, is_active_only=False
):
    linked_initiative_ids = select(
        InitiativeTeamRelationship.initiative_id
    ).where(
        InitiativeTeamRelationship.team_id.in_(team_ids)
    )
    query = Initiative.query.filter(
        or_(
            Initiative.id.in_(linked_initiative_ids),
            Initiative.id.in_(initiative_ids),
        )
    )
    if is_active_only:
        query = query.filter(Initiative.is_active.is_(True))
    return query.all()

Cette méthode renvoie [] si aucune initiative ne correspond et évite les doublons liés à plusieurs équipes.

2. Dans la branche Owner seul, remplace son contenu par :

team_ids = [
    user_team["team_id"]
    for user_team in get_user_teams_by_user_id(user)
]
initiatives = InitiativeRepository.get_by_team_ids_or_by_ids(
    team_ids=team_ids,
    initiative_ids=[],
    is_active_only=is_active_only,
)
return [initiative.to_json() for initiative in initiatives]

3. Dans la branche Owner + Assessor, remplace la collecte des membres et l’appel à get_by_created_by_id_or_by_ids par :

team_ids = [
    user_team["team_id"]
    for user_team in get_user_teams_by_user_id(user)
]
initiatives = InitiativeRepository.get_by_team_ids_or_by_ids(
    team_ids=team_ids,
    initiative_ids=[
        relationship.initiative_id
        for relationship in assessor_initiative_relationships
    ],
    is_active_only=is_active_only,
)
return [initiative.to_json() for initiative in initiatives]

Cette branche conserve les accès supplémentaires accordés comme Assessor.

Les 14 tests précédents vérifiaient l’ancienne règle. Pour un Owner seul, les nouvelles attentes sont :

Situation	Résultat attendu
Initiative liée à l’une de ses équipes	Visible, quel que soit le créateur
Initiative d’un collègue, sans équipe commune avec l’utilisateur	Masquée
Initiative créée par lui, sans équipe commune	Masquée avec cette version stricte
Initiative inactive et is_active_only=True	Masquée

Le correctif reste à exécuter et vérifier dans ton projet.