import json
import unittest
from unittest.mock import MagicMock, patch

from config import APPLICATION_ROOT
from constants.roles import InitiativeRoleEnum
from server import server


BASE_URL = f"{APPLICATION_ROOT}/initiative-add-team-members"


def make_fake_me_response():
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "uid": "owner@flowr.com",
        "roles": [
            InitiativeRoleEnum.INITIATIVE_ASSESSOR.value,
            "ADMIN",
        ],
    }
    return fake_response


@patch(
    "util.required_plm_authentication.me",
    return_value=make_fake_me_response(),
)
@patch(
    "clients.oidc.validate_token",
    return_value={"uid": "mySpecialuid"},
)
class TestInitiativeTeamMembers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = server.test_client()
        cls.url = BASE_URL

    @patch(
        "resources.initiative_team_members.initiative_team_members."
        "SessionCriticalActionManager"
    )
    @patch(
        "resources.initiative_team_members.initiative_team_members."
        "InitiativeTeamRelationshipRepository.modify_team"
    )
    @patch(
        "resources.initiative_team_members.initiative_team_members."
        "InitiativeTeamMembersRepository.add_team_member"
    )
    @patch(
        "resources.initiative_team_members.initiative_team_members."
        "get_users_by_role"
    )
    @patch(
        "resources.initiative_team_members.initiative_team_members."
        "get_users"
    )
    def test_auto_assign_initiative_manager_if_assessor(
        self,
        mock_get_users,
        mock_get_users_by_role,
        mock_add_team_member,
        mock_modify_team,
        mock_session_manager,
        mock_validate,
        mock_me,
    ):
        # User is Initiative Manager and belongs to team 209
        mock_get_users.return_value = [
            {
                "id": 1783,
                "is_initiative_manager": True,
                "teams": [{"id": 209}],
            }
        ]

        # Same user has INITIATIVE_ASSESSOR role
        mock_get_users_by_role.return_value = [
            {
                "user_id": 1783,
            }
        ]

        member = MagicMock()
        member.to_json.return_value = {
            "id": 13,
            "relationship_id": 24,
            "user_id": 1783,
        }

        mock_add_team_member.return_value = member

        payload = {
            "initiative_id": "I7",
            "team_ids": [209],
            "automatic_assessor": True,
        }

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        mock_add_team_member.assert_called_once_with(
            "I7",
            209,
            1783,
        )

        mock_modify_team.assert_called_once_with(
            "I7",
            209,
            1783,
        )

    @patch(
        "resources.initiative_team_members.initiative_team_members."
        "SessionCriticalActionManager"
    )
    @patch(
        "resources.initiative_team_members.initiative_team_members."
        "InitiativeTeamRelationshipRepository.modify_team"
    )
    @patch(
        "resources.initiative_team_members.initiative_team_members."
        "InitiativeTeamMembersRepository.add_team_member"
    )
    @patch(
        "resources.initiative_team_members.initiative_team_members."
        "get_users_by_role"
    )
    @patch(
        "resources.initiative_team_members.initiative_team_members."
        "get_users"
    )
    def test_do_not_auto_assign_manager_without_assessor_role(
        self,
        mock_get_users,
        mock_get_users_by_role,
        mock_add_team_member,
        mock_modify_team,
        mock_session_manager,
        mock_validate,
        mock_me,
    ):
        # User is Initiative Manager
        mock_get_users.return_value = [
            {
                "id": 1783,
                "is_initiative_manager": True,
                "teams": [{"id": 209}],
            }
        ]

        # But 1783 is NOT an Initiative Assessor
        mock_get_users_by_role.return_value = [
            {
                "user_id": 9999,
            }
        ]

        payload = {
            "initiative_id": "I7",
            "team_ids": [209],
            "automatic_assessor": True,
        }

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        mock_add_team_member.assert_not_called()
        mock_modify_team.assert_not_called()
        
        test/api/initiative/test_initiative_team_members.py
        