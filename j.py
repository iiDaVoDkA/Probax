"""
Regression tests for FLOWR bug 272026.

Exercises:
- Actual patch_task implementation.
- Actual manual main-assessor reassignment loop.
- Task PATCH authorization through Flask.
- Initiative-list filtering through Flask.

Limitations:
- Database queries, transactions, identity provider and email are mocked.
- Team-selection unit tests unwrap decorators: they test the reassignment
  logic, not authorization of the team-selection endpoint.
- Does not test database commits, frontend rendering or XLS exports.
"""

from contextlib import contextmanager
from copy import deepcopy
from inspect import signature, unwrap
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from config import APPLICATION_ROOT
from constants.roles import InitiativeRoleEnum
from server import server

from repositories import task as task_repository
from resources.task import task as task_api
from resources.initiative import initiative as initiative_api
from resources.initiative_team_members import (
    initiative_team_members as members_api,
)


ASSESSOR = InitiativeRoleEnum.INITIATIVE_ASSESSOR.value
OWNER = InitiativeRoleEnum.INITIATIVE_OWNER.value
COORDINATOR = InitiativeRoleEnum.INITIATIVE_COORDINATOR.value
OBSERVER = InitiativeRoleEnum.INITIATIVE_OBSERVER.value

A = 1803
B = 1783

ALPHA = 209
BETA = 347

ROOT = APPLICATION_ROOT.rstrip("/")
REPOSITORY = task_repository.InitiativeTaskRepository


class Record(SimpleNamespace):
    def to_json(self):
        result = deepcopy(vars(self))
        status = result.get("task_status")
        if hasattr(status, "value"):
            result["task_status"] = status.value
        return result


def make_task(task_id=1, relationship_id=11, main=None, shared=True):
    return Record(
        id=task_id,
        relationship_id=relationship_id,
        main_assessor=main,
        is_team_assigned=shared,
        task_name="Regression task",
        task_type="ASSESSMENT",
        task_status=task_repository.TaskStatus.ON_GOING,
        task_rating="LOW",
        comets_task_rating="Original comment",
        last_assessor=None,
        expected_for=None,
        parent_task_id=None,
    )


@contextmanager
def fake_transaction(*args, **kwargs):
    # Deliberately provides no database-persistence coverage.
    yield


class RepositoryFixture(unittest.TestCase):
    def start_patch(self, target, attribute, **kwargs):
        patcher = patch.object(target, attribute, **kwargs)
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    def start_named_patch(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    def setUp(self):
        super().setUp()

        # Fail if a test accidentally makes an external HTTP request.
        self.start_named_patch(
            "requests.sessions.Session.request",
            side_effect=AssertionError(
                "Unexpected external HTTP request in regression test"
            ),
        )

        self.rows = {}
        self.db = self.start_patch(task_repository, "db")

        model = self.start_patch(task_repository, "InitiativeTask")
        model.query.filter_by.side_effect = self.lookup_task

    def lookup_task(self, **filters):
        # Calls to the real repository must target a specific task.
        self.assertEqual(set(filters), {"id"})
        return SimpleNamespace(
            first=lambda: self.rows.get(filters["id"])
        )

    def snapshot(self):
        return {
            task_id: task.to_json()
            for task_id, task in self.rows.items()
        }

    def patch_real_task(self, task_id, payload):
        # The method under test is NOT mocked.
        return REPOSITORY.patch_task(task_id, payload, A)


class TestRepositoryAssignmentFlag(RepositoryFixture):
    def test_assigning_a_person_clears_flag_for_all_initial_states(self):
        for previous_main in (None, A, B):
            for previous_flag in (False, True):
                with self.subTest(
                    previous_main=previous_main,
                    previous_flag=previous_flag,
                ):
                    task = make_task(
                        main=previous_main,
                        shared=previous_flag,
                    )
                    self.rows = {1: task}
                    self.db.session.flush.reset_mock()

                    result = self.patch_real_task(
                        1, {"main_assessor": A}
                    )

                    self.assertEqual(task.main_assessor, A)
                    self.assertIs(task.is_team_assigned, False)
                    self.assertIs(result["is_team_assigned"], False)
                    self.db.session.flush.assert_called_once()

    def test_rating_and_comment_do_not_change_assignment(self):
        for main in (None, A):
            for shared in (False, True):
                with self.subTest(main=main, shared=shared):
                    task = make_task(main=main, shared=shared)
                    self.rows = {1: task}

                    self.patch_real_task(
                        1,
                        {
                            "task_rating": "HIGH",
                            "comets_task_rating": "Updated comment",
                        },
                    )

                    self.assertEqual(task.task_rating, "HIGH")
                    self.assertEqual(
                        task.comets_task_rating, "Updated comment"
                    )
                    self.assertEqual(task.main_assessor, main)
                    self.assertIs(task.is_team_assigned, shared)

    def test_removing_person_does_not_automatically_enable_team_flag(self):
        for shared in (False, True):
            with self.subTest(shared=shared):
                task = make_task(main=A, shared=shared)
                self.rows = {1: task}

                self.patch_real_task(1, {"main_assessor": None})

                self.assertIsNone(task.main_assessor)
                self.assertIs(task.is_team_assigned, shared)

    def test_assignment_preserves_status_rating_comment_and_last_assessor(self):
        for status in task_repository.TaskStatus:
            with self.subTest(status=status):
                task = make_task(main=B, shared=True)
                task.task_status = status
                task.last_assessor = B
                self.rows = {1: task}

                expected = task.to_json()
                expected["main_assessor"] = A
                expected["is_team_assigned"] = False

                self.patch_real_task(1, {"main_assessor": A})

                self.assertEqual(task.to_json(), expected)

    def test_updating_one_task_does_not_change_another_task(self):
        self.rows = {
            1: make_task(1, 11, None, True),
            2: make_task(2, 22, B, True),
        }
        other_before = self.rows[2].to_json()

        self.patch_real_task(1, {"main_assessor": A})

        self.assertEqual(self.rows[2].to_json(), other_before)

    def test_unknown_task_raises_without_flushing(self):
        with self.assertRaises(task_repository.EntityNotFound):
            self.patch_real_task(99999, {"main_assessor": A})

        self.db.session.flush.assert_not_called()


class TestManualTeamReassignment(RepositoryFixture):
    def setUp(self):
        super().setUp()

        self.links = {
            11: Record(
                id=11,
                initiative_id="I1",
                team_id=ALPHA,
                accountant_id=None,
            ),
            22: Record(
                id=22,
                initiative_id="I2",
                team_id=ALPHA,
                accountant_id=None,
            ),
            33: Record(
                id=33,
                initiative_id="I1",
                team_id=BETA,
                accountant_id=None,
            ),
            44: Record(
                id=44,
                initiative_id="I3",
                team_id=BETA,
                accountant_id=None,
            ),
        }

        self.start_patch(members_api, "db")
        self.start_patch(
            members_api,
            "SessionCriticalActionManager",
            new=fake_transaction,
        )

        self.start_patch(
            members_api.InitiativeTeamMembersRepository,
            "add_team_member",
            return_value=Record(id=100, relationship_id=11, user_id=A),
        )

        self.scope_query = self.start_patch(
            members_api.InitiativeTeamRelationshipRepository,
            "get_by_initiative_id_and_team_id",
            side_effect=lambda initiative_id, team_id: [
                link
                for link in self.links.values()
                if link.initiative_id == initiative_id
                and link.team_id == team_id
            ],
        )

        self.start_patch(
            members_api.InitiativeTeamRelationshipRepository,
            "modify_team",
            side_effect=self.modify_team,
        )

        self.start_patch(
            REPOSITORY,
            "get_by_relationship_id_no_errors",
            side_effect=lambda relationship_ids: [
                task
                for task in self.rows.values()
                if task.relationship_id in relationship_ids
            ],
        )

        self.start_patch(
            members_api,
            "get_users_by_user_id",
            side_effect=lambda user_ids: [
                {
                    "id": user_id,
                    "email": f"user{user_id}@example.test",
                }
                for user_id in user_ids
            ],
        )
        self.start_patch(members_api, "send_email_assessor_changed")

        self.selection = unwrap(
            members_api.InitiativeAddTeamMembersResource.post
        )

        required_parameters = {
            "user",
            "initiative_id",
            "team_ids",
            "user_id",
            "automatic_assessor",
            "is_main_assessor",
        }

        actual_parameters = set(
            signature(self.selection, follow_wrapped=False).parameters
        )

        if not required_parameters.issubset(actual_parameters):
            raise RuntimeError(
                "Cannot unwrap the selection method with this decorator "
                "implementation. This is a test setup issue: provide the "
                "current decorators/resource source before adapting it."
            )

    def modify_team(self, initiative_id, team_id, user_id):
        for link in self.links.values():
            if (
                link.initiative_id == initiative_id
                and link.team_id == team_id
            ):
                link.accountant_id = user_id

    def select_main(self, user_id=A, is_main=True):
        # Unit test of the selection body. Its decorators are not tested here.
        with server.test_request_context():
            return self.selection(
                user={"id": 9001, "roles": ["ADMIN"]},
                initiative_id="I1",
                team_ids=[ALPHA],
                user_id=user_id,
                automatic_assessor=False,
                is_main_assessor=is_main,
            )

    def test_all_target_tasks_reassigned_and_other_scopes_unchanged(self):
        states = [
            (None, True),
            (B, False),
            (B, True),
            (A, True),   # Critical: same person, stale True flag.
            (A, False),
            (None, False),
        ]

        self.rows = {
            task_id: make_task(task_id, 11, main, shared)
            for task_id, (main, shared) in enumerate(states, start=1)
        }

        # Same team/different initiative; different team/same initiative;
        # different team/different initiative.
        for task_id, relationship_id in ((101, 22), (102, 33), (103, 44)):
            self.rows[task_id] = make_task(
                task_id, relationship_id, B, True
            )

        before = self.snapshot()

        self.select_main(A)

        self.scope_query.assert_called_once_with("I1", ALPHA)
        self.assertEqual(self.links[11].accountant_id, A)

        for task_id in range(1, 7):
            expected = deepcopy(before[task_id])
            expected["main_assessor"] = A
            expected["is_team_assigned"] = False
            self.assertEqual(self.rows[task_id].to_json(), expected)

        for task_id in (101, 102, 103):
            self.assertEqual(self.rows[task_id].to_json(), before[task_id])

        for relationship_id in (22, 33, 44):
            self.assertIsNone(self.links[relationship_id].accountant_id)

    def test_same_assessor_with_stale_flag_is_not_skipped(self):
        self.rows = {1: make_task(main=A, shared=True)}

        self.select_main(A)

        self.assertEqual(self.rows[1].main_assessor, A)
        self.assertIs(self.rows[1].is_team_assigned, False)
        self.db.session.flush.assert_called_once()

    def test_reselection_preserves_assignment_state(self):
        self.rows = {1: make_task(main=None, shared=True)}

        self.select_main(A)
        after_first_selection = self.snapshot()

        self.select_main(A)

        self.assertEqual(self.snapshot(), after_first_selection)

    def test_selecting_a_different_person_reassigns_again(self):
        self.rows = {1: make_task(main=None, shared=True)}

        self.select_main(A)
        self.select_main(B)

        self.assertEqual(self.rows[1].main_assessor, B)
        self.assertIs(self.rows[1].is_team_assigned, False)

    def test_adding_member_without_main_selection_does_not_reassign(self):
        self.rows = {1: make_task(main=None, shared=True)}
        before = self.snapshot()

        self.select_main(A, is_main=False)

        self.assertEqual(self.snapshot(), before)
        self.scope_query.assert_not_called()
        self.db.session.flush.assert_not_called()

    def test_team_without_tasks_does_not_modify_other_team_tasks(self):
        self.rows = {2: make_task(2, 33, B, True)}
        before = self.snapshot()

        self.select_main(A)

        self.assertEqual(self.snapshot(), before)
        self.db.session.flush.assert_not_called()


class AuthenticatedApiFixture(RepositoryFixture):
    def setUp(self):
        super().setUp()

        self.client = server.test_client()
        self.actor = {
            "id": A,
            "uid": "SuperUser",
            "roles": [ASSESSOR],
            "teams": [{"id": ALPHA}],
        }

        # Stub identity-provider boundaries, not application role decorators.
        self.start_named_patch(
            "client.oidc.validate_token",
            return_value={"uid": "SuperUser"},
        )
        self.start_named_patch(
            "util.required_plm_authentication._me",
            side_effect=self.me_response,
        )

    def me_response(self, *args, **kwargs):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = deepcopy(self.actor)
        return response

    def assert_route_exists(self, url, method):
        # Prevent a missing route from falsely passing a "denied" test.
        try:
            server.url_map.bind("localhost").match(url, method=method)
        except Exception as error:
            raise AssertionError(
                f"Check the registered {method} route: {url}"
            ) from error


class TestTaskPatchPermissions(AuthenticatedApiFixture):
    def setUp(self):
        super().setUp()

        self.url = f"{ROOT}/tasks/1"
        self.assert_route_exists(self.url, "PATCH")

        self.rows = {1: make_task()}
        self.link = Record(
            id=11,
            initiative_id="I1",
            team_id=ALPHA,
            accountant_id=None,
        )

        self.start_patch(task_api, "db")
        self.start_patch(
            task_api,
            "SessionCriticalActionManager",
            new=fake_transaction,
        )
        self.start_patch(
            REPOSITORY,
            "get_task_by_id",
            side_effect=lambda task_id: self.rows[int(task_id)].to_json(),
        )
        self.start_patch(
            task_api.InitiativeTeamRelationshipRepository,
            "get_by_relationship_ids",
            side_effect=lambda ids: [self.link] if ids == [11] else [],
        )
        self.start_patch(
            task_api,
            "get_users",
            side_effect=lambda: [deepcopy(self.actor)],
        )

        error_class = task_api.InitiativeTaskNotEditableByUserError
        self.permission_error = self.start_patch(
            task_api,
            "InitiativeTaskNotEditableByUserError",
            wraps=error_class,
        )

    def send_patch(self, payload):
        return self.client.patch(
            self.url,
            json={"payload": payload},
        )

    def assert_allowed(self, response):
        self.assertEqual(
            response.status_code,
            200,
            response.get_data(as_text=True),
        )

    def assert_denied(self, response, check_inner_guard=True):
        self.assertTrue(
            400 <= response.status_code < 500,
            response.get_data(as_text=True),
        )
        if check_inner_guard:
            # Prove the resource permission guard rejected the request.
            # A parser error or broken route is not enough.
            self.permission_error.assert_called_once()
        self.db.session.flush.assert_not_called()

    def test_rating_access_matrix(self):
        cases = [
            # name, roles, teams, task main, team main, flag, allowed
            ("shared_member", [ASSESSOR], [ALPHA], None, None, True, True),
            ("shared_other_team", [ASSESSOR], [BETA], None, None, True, False),
            ("shared_no_team", [ASSESSOR], [], None, None, True, False),
            ("shared_multiple_teams", [ASSESSOR], [ALPHA, BETA],
             None, None, True, True),
            ("unassigned_not_shared", [ASSESSOR], [ALPHA],
             None, None, False, False),
            ("assigned_to_other_person", [ASSESSOR], [ALPHA],
             B, None, True, False),
            ("other_team_main_selected", [ASSESSOR], [ALPHA],
             B, B, False, False),
            ("selected_main_assessor", [ASSESSOR], [ALPHA],
             A, A, False, True),
            ("observer", [OBSERVER], [ALPHA], None, None, True, False),
            ("no_role", [], [ALPHA], None, None, True, False),
            ("owner_existing_workflow", [OWNER], [ALPHA],
             None, None, False, True),
            ("coordinator_existing_workflow", [COORDINATOR], [ALPHA],
             None, None, False, True),
            ("admin_existing_workflow", ["ADMIN"], [ALPHA],
             None, None, False, True),
            ("assessor_and_owner", [ASSESSOR, OWNER], [ALPHA],
             None, None, False, True),
        ]

        for name, roles, teams, main, team_main, shared, allowed in cases:
            with self.subTest(case=name):
                self.actor["roles"] = roles
                self.actor["teams"] = [{"id": team} for team in teams]
                self.rows = {1: make_task(main=main, shared=shared)}
                self.link.accountant_id = team_main
                self.db.session.flush.reset_mock()
                self.permission_error.reset_mock()
                before = self.snapshot()

                response = self.send_patch(
                    {
                        "task_rating": "HIGH",
                        "comets_task_rating": "Regression comment",
                    }
                )

                if allowed:
                    self.assert_allowed(response)
                    self.assertEqual(self.rows[1].task_rating, "HIGH")
                    self.assertEqual(
                        self.rows[1].comets_task_rating,
                        "Regression comment",
                    )
                    self.assertEqual(self.rows[1].main_assessor, main)
                    self.assertIs(self.rows[1].is_team_assigned, shared)
                else:
                    self.assert_denied(
                        response,
                        check_inner_guard=(ASSESSOR in roles),
                    )
                    self.assertEqual(self.snapshot(), before)

    def test_personal_assessor_can_edit_before_team_main_is_selected(self):
        # Ticket requirement. Do not change this expected success to denial
        # simply to make the current implementation pass.
        self.rows = {1: make_task(main=A, shared=False)}
        self.link.accountant_id = None

        response = self.send_patch(
            {
                "task_rating": "HIGH",
                "comets_task_rating": "Personal assessor comment",
            }
        )

        self.assert_allowed(response)
        self.assertEqual(self.rows[1].task_rating, "HIGH")
        self.assertEqual(
            self.rows[1].comets_task_rating,
            "Personal assessor comment",
        )

    def test_shared_member_cannot_change_protected_fields(self):
        changes = [
            {"relationship_id": 22},
            {"main_assessor": B},
            {"is_team_assigned": False},
        ]

        for changeset in changes:
            with self.subTest(changes=changeset):
                self.rows = {1: make_task(main=None, shared=True)}
                self.db.session.flush.reset_mock()
                self.permission_error.reset_mock()
                before = self.snapshot()

                response = self.send_patch(changeset)

                self.assert_denied(response)
                self.assertEqual(self.snapshot(), before)

    def test_unchanged_protected_values_do_not_block_comment_update(self):
        response = self.send_patch(
            {
                "relationship_id": 11,
                "main_assessor": None,
                "is_team_assigned": True,
                "comets_task_rating": "Allowed comment",
            }
        )

        self.assert_allowed(response)
        self.assertEqual(
            self.rows[1].comets_task_rating,
            "Allowed comment",
        )
        self.assertIs(self.rows[1].is_team_assigned, True)

    def test_former_team_member_cannot_write_after_reassignment(self):
        # Represents a fresh request from B after A was selected.
        self.actor["id"] = B
        self.rows = {1: make_task(main=A, shared=False)}
        self.link.accountant_id = A
        before = self.snapshot()

        response = self.send_patch(
            {"comets_task_rating": "Must not be saved"}
        )

        self.assert_denied(response)
        self.assertEqual(self.snapshot(), before)


class TestInitiativeListFiltering(AuthenticatedApiFixture):
    def setUp(self):
        super().setUp()

        self.url = f"{ROOT}/initiatives"
        self.assert_route_exists(self.url, "GET")

        self.links = {
            11: Record(id=11, initiative_id="I1", accountant_id=None),
            22: Record(id=22, initiative_id="I2", accountant_id=None),
            33: Record(id=33, initiative_id="I3", accountant_id=B),
        }
        self.initiatives = {
            key: Record(id=key, name=f"Initiative {key}")
            for key in ("I1", "I2", "I3")
        }

        self.memberships = []
        self.personal_candidates = []
        self.team_candidates = []

        self.start_patch(
            initiative_api.InitiativeTeamMembersRepository,
            "get_by_user_id",
            side_effect=lambda user_id: [
                Record(relationship_id=relationship_id)
                for relationship_id in self.memberships
            ],
        )
        self.start_patch(
            REPOSITORY,
            "get_by_main_assessor",
            side_effect=lambda user_id: list(self.personal_candidates),
        )
        self.team_lookup = self.start_patch(
            REPOSITORY,
            "get_team_assigned_relationship_ids",
            side_effect=lambda team_ids: list(self.team_candidates),
        )
        self.start_patch(
            initiative_api.InitiativeTeamRelationshipRepository,
            "get_by_relationship_ids",
            side_effect=lambda ids: [self.links[key] for key in ids],
        )
        self.start_patch(
            initiative_api.InitiativeRepository,
            "get_by_ids",
            side_effect=lambda ids, *args, **kwargs: [
                self.initiatives[key] for key in dict.fromkeys(ids)
            ],
        )
        self.start_patch(
            initiative_api.InitiativeRepository,
            "get_all",
            side_effect=AssertionError(
                "Assessor-only account took the unfiltered initiative path"
            ),
        )

        # Original failure: assessor-only account must not need this
        # extra PLM user-team request when authenticated teams are available.
        self.start_patch(
            initiative_api,
            "get_user_teams_by_user_id",
            side_effect=AssertionError(
                "Unexpected PLM user-team lookup in assessor list path"
            ),
        )

    def returned_ids(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
            response.get_data(as_text=True),
        )
        data = response.get_json()
        self.assertIsInstance(data, list)

        ids = [item["id"] for item in data]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate initiatives")
        return set(ids)

    def test_personally_assigned_initiative_is_visible(self):
        self.personal_candidates = [22]

        self.assertEqual(self.returned_ids(), {"I2"})

    def test_team_assigned_initiative_is_visible(self):
        self.team_candidates = [11]

        self.assertEqual(self.returned_ids(), {"I1"})
        self.team_lookup.assert_called_once_with([ALPHA])

    def test_two_valid_reasons_do_not_expose_unrelated_initiative(self):
        self.personal_candidates = [22]
        self.team_candidates = [11]

        self.assertEqual(self.returned_ids(), {"I1", "I2"})

    def test_multiple_reasons_do_not_duplicate_an_initiative(self):
        self.personal_candidates = [11]
        self.team_candidates = [11]

        self.assertEqual(self.returned_ids(), {"I1"})

    def test_no_eligible_assignment_returns_no_initiatives(self):
        self.assertEqual(self.returned_ids(), set())

    def test_old_membership_does_not_keep_access_after_reassignment(self):
        # After reassignment there are no shared-task candidates.
        # An old membership row alone must not preserve team-only access.
        self.memberships = [11]
        self.links[11].accountant_id = B

        self.assertEqual(self.returned_ids(), set())

    def test_selected_main_assessor_retains_initiative_access(self):
        self.memberships = [11]
        self.links[11].accountant_id = A

        self.assertEqual(self.returned_ids(), {"I1"})

    def test_independent_personal_assignment_survives_other_revocation(self):
        self.memberships = [11]
        self.links[11].accountant_id = B
        self.personal_candidates = [22]

        self.assertEqual(self.returned_ids(), {"I2"})


if __name__ == "__main__":
    unittest.main(verbosity=2)