"""

Unit tests for Initiative Owner visibility.

Run:

    python test_initiative_owner_visibility.py -v

Default source:

    src/resources/initiative/initiative.py

These tests read the actual InitiativesResource.get method.

They mock repositories and team lookups, and skip authentication decorators.

They do NOT test actual SQL queries, authentication, or live team data.

The Admin/Coordinator/Observer tests document the CURRENT role precedence

shown in your screenshots.

With user_ids = [] in both Owner branches, the no-team cases should fail.

"""

import ast

import copy

import os

import unittest

from dataclasses import asdict, dataclass

from enum import Enum

from pathlib import Path

from types import SimpleNamespace

from unittest.mock import Mock

class _Roles(Enum):

    INITIATIVE_OWNER = "INITIATIVE_OWNER"

    INITIATIVE_ASSESSOR = "INITIATIVE_ASSESSOR"

    INITIATIVE_COORDINATOR = "INITIATIVE_COORDINATOR"

    INITIATIVE_OBSERVER = "INITIATIVE_OBSERVER"

@dataclass(frozen=True)

class _Initiative:

    id: str

    created_by_id: int

    is_active: bool = True

    def to_json(self):

        return asdict(self)

def _source_file():

    override = os.environ.get("FLOWR_INITIATIVE_RESOURCE_FILE")

    if override:

        candidates = [Path(override).expanduser()]

    else:

        relative = Path("src/resources/initiative/initiative.py")

        candidates = [

            Path.cwd() / relative,

            Path(__file__).resolve().parent / relative,

        ]

    for candidate in candidates:

        if candidate.is_file():

            return candidate.resolve()

    raise FileNotFoundError(

        "Cannot find the Initiative resource. "

        "Put this test next to src/ and run it from the repository root, "

        "or set FLOWR_INITIATIVE_RESOURCE_FILE to the resource's full path. "

        "Tried: " + ", ".join(str(path) for path in candidates)

    )

def _load_real_get(namespace):

    path = _source_file()

    tree = ast.parse(

        path.read_text(encoding="utf-8"),

        filename=str(path),

    )

    resource = next(

        (

            node

            for node in tree.body

            if isinstance(node, ast.ClassDef)

            and node.name == "InitiativesResource"

        ),

        None,

    )

    if resource is None:

        raise AssertionError(

            "InitiativesResource was not found in " + str(path)

        )

    method = next(

        (

            node

            for node in resource.body

            if isinstance(node, ast.FunctionDef)

            and node.name == "get"

        ),

        None,

    )

    if method is None:

        raise AssertionError(

            "InitiativesResource.get was not found in " + str(path)

        )

    # Extract the real method without importing the whole application.

    # This does not modify your source file.

    method = copy.deepcopy(method)

    method.decorator_list = []

    method.returns = None

    arguments = (

        method.args.posonlyargs

        + method.args.args

        + method.args.kwonlyargs

    )

    for argument in arguments:

        argument.annotation = None

    for argument in (method.args.vararg, method.args.kwarg):

        if argument is not None:

            argument.annotation = None

    code = ast.fix_missing_locations(

        ast.Module(body=[method], type_ignores=[])

    )

    exec(compile(code, str(path), "exec"), namespace)

    return namespace["get"]

class TestInitiativeOwnerVisibility(unittest.TestCase):

    def setUp(self):

        # Users:

        # 1810 = current user

        # 1811 = teammate

        # 1812 = unrelated user

        # 1813 = member of another team

        self.rows = [

            _Initiative("112", 1810),

            _Initiative("113", 1811),

            _Initiative("114", 1812),

            _Initiative("115", 1813),

            _Initiative("116", 1811, is_active=False),

        ]

        self.owner = {

            "id": 1810,

            "roles": [_Roles.INITIATIVE_OWNER.value],

            "teams": [{"id": 347}],

        }

        self.team_members = {

            347: [1810, 1811],

            348: [1810, 1813],

        }

        self.memberships = []

        self.relationships = []

        self.main_assessor_ids = []

        self.team_assigned_ids = []

        def select_rows(predicate, is_active_only):

            return [

                row

                for row in self.rows

                if predicate(row)

                and (not is_active_only or row.is_active)

            ]

        # Fake repository reads:

        # test the resource's decisions, not the real SQL implementation.

        self.repository = SimpleNamespace(

            get_by_created_by_id=Mock(

                side_effect=lambda user_ids, is_active_only: select_rows(

                    lambda row: row.created_by_id in user_ids,

                    is_active_only,

                )

            ),

            get_by_created_by_id_or_by_ids=Mock(

                side_effect=lambda user_ids, initiative_ids, is_active_only:

                select_rows(

                    lambda row: (

                        row.created_by_id in user_ids

                        or row.id in initiative_ids

                    ),

                    is_active_only,

                )

            ),

            get_by_ids=Mock(

                side_effect=lambda initiative_ids, is_active_only:

                select_rows(

                    lambda row: row.id in initiative_ids,

                    is_active_only,

                )

            ),

            get_all=Mock(

                side_effect=lambda is_active_only=False: select_rows(

                    lambda row: True,

                    is_active_only,

                )

            ),

        )

        self.get_user_teams = Mock(

            side_effect=lambda user: [

                {

                    "team_id": team["id"],

                    "user_id": user["id"],

                }

                for team in user["teams"]

            ]

        )

        self.get_team_members = Mock(

            side_effect=lambda user, team_id: [

                {

                    "team_id": team_id,

                    "user_id": member_id,

                }

                for member_id in self.team_members.get(team_id, [])

            ]

        )

        self.tasks = SimpleNamespace(

            get_by_main_assessor=Mock(

                side_effect=lambda user_id: list(self.main_assessor_ids)

            ),

            get_team_assigned_relationship_ids=Mock(

                side_effect=lambda team_ids: list(self.team_assigned_ids)

            ),

        )

        namespace = {

            "InitiativeRoleEnum": _Roles,

            "InitiativeRepository": self.repository,

            "get_user_teams_by_user_id": self.get_user_teams,

            "get_user_teams_by_team_id": self.get_team_members,

            "InitiativeTeamMembersRepository": SimpleNamespace(

                get_by_user_id=Mock(

                    side_effect=lambda user_id: list(self.memberships)

                )

            ),

            "InitiativeTaskRepository": self.tasks,

            "InitiativeTeamRelationshipRepository": SimpleNamespace(

                get_by_relationship_ids=Mock(

                    side_effect=lambda ids: [

                        relation

                        for relation in self.relationships

                        if relation.id in ids

                    ]

                )

            ),

        }

        self.get = _load_real_get(namespace)

    def visible_ids(self, is_active_only=False):

        result = self.get(

            user=self.owner,

            is_active_only=is_active_only,

        )

        self.assertIsInstance(

            result,

            list,

            "The GET method should return a list of JSON rows.",

        )

        ids = [str(row["id"]) for row in result]

        self.assertEqual(

            len(ids),

            len(set(ids)),

            "An initiative was returned more than once.",

        )

        return set(ids)

    def add_assessor_role(self):

        self.owner["roles"].append(

            _Roles.INITIATIVE_ASSESSOR.value

        )

    def add_external_relationship(self, relation_id, accountant_id=None):

        self.relationships.append(

            SimpleNamespace(

                id=relation_id,

                initiative_id="114",

                accountant_id=accountant_id,

            )

        )

    def test_owner_sees_own_and_teammates_but_not_other_teams(self):

        self.assertEqual(

            self.visible_ids(),

            {"112", "113", "116"},

        )

        self.repository.get_all.assert_not_called()

        self.repository.get_by_created_by_id.assert_called_once()

        creator_ids, active_only = (

            self.repository.get_by_created_by_id.call_args.args

        )

        self.assertEqual(set(creator_ids), {1810, 1811})

        self.assertIs(active_only, False)

    def test_owner_sees_initiatives_from_each_of_their_teams(self):

        self.owner["teams"].append({"id": 348})

        self.assertEqual(

            self.visible_ids(),

            {"112", "113", "115", "116"},

        )

    def test_owner_without_team_still_sees_own_initiatives(self):

        self.owner["teams"] = []

        self.assertEqual(

            self.visible_ids(),

            {"112"},

            "Own initiatives must remain visible without a team. "

            "Initialize user_ids with [user['id']].",

        )

        self.repository.get_all.assert_not_called()

    def test_owner_keeps_own_initiatives_if_team_lookup_omits_self(self):

        self.team_members[347] = [1811]

        self.assertEqual(

            self.visible_ids(),

            {"112", "113", "116"},

        )

    def test_owner_active_only_is_forwarded(self):

        self.assertEqual(

            self.visible_ids(is_active_only=True),

            {"112", "113"},

        )

        self.assertIs(

            self.repository.get_by_created_by_id.call_args.args[1],

            True,

        )

    def test_owner_assessor_adds_external_main_assessor_initiatives(self):

        self.add_assessor_role()

        self.add_external_relationship(900)

        self.main_assessor_ids.append(900)

        self.assertEqual(

            self.visible_ids(),

            {"112", "113", "114", "116"},

        )

        self.repository.get_all.assert_not_called()

    def test_owner_assessor_adds_team_assigned_initiatives(self):

        self.add_assessor_role()

        self.add_external_relationship(901)

        self.team_assigned_ids.append(901)

        self.assertEqual(

            self.visible_ids(),

            {"112", "113", "114", "116"},

        )

        self.tasks.get_team_assigned_relationship_ids.assert_called_once_with(

            [347]

        )

    def test_owner_assessor_adds_matching_accountant_initiatives(self):

        self.add_assessor_role()

        self.add_external_relationship(

            902,

            accountant_id=1810,

        )

        self.memberships.append(

            SimpleNamespace(relationship_id=902)

        )

        self.assertEqual(

            self.visible_ids(),

            {"112", "113", "114", "116"},

        )

    def test_owner_assessor_membership_alone_does_not_grant_access(self):

        self.add_assessor_role()

        self.add_external_relationship(

            903,

            accountant_id=1812,

        )

        self.memberships.append(

            SimpleNamespace(relationship_id=903)

        )

        self.assertEqual(

            self.visible_ids(),

            {"112", "113", "116"},

        )

    def test_owner_assessor_without_team_still_sees_own_initiatives(self):

        self.add_assessor_role()

        self.owner["teams"] = []

        self.assertEqual(

            self.visible_ids(),

            {"112"},

            "Initialize user_ids with [user['id']] "

            "in the combined Owner + Assessor branch too.",

        )

    def assert_current_full_access(self, extra_role):

        self.owner["roles"].append(extra_role)

        self.assertEqual(

            self.visible_ids(),

            {"112", "113", "114", "115", "116"},

        )

        self.repository.get_all.assert_called_once_with(

            is_active_only=False

        )

        self.get_user_teams.assert_not_called()

    def test_owner_admin_currently_retains_full_access(self):

        self.assert_current_full_access("ADMIN")

    def test_owner_coordinator_currently_retains_full_access(self):

        self.assert_current_full_access(

            _Roles.INITIATIVE_COORDINATOR.value

        )

    def test_owner_observer_currently_retains_full_access(self):

        self.assert_current_full_access(

            _Roles.INITIATIVE_OBSERVER.value

        )

    def test_active_only_is_forwarded_for_full_access_role(self):

        self.owner["roles"].append("ADMIN")

        self.assertEqual(

            self.visible_ids(is_active_only=True),

            {"112", "113", "114", "115"},

        )

        self.repository.get_all.assert_called_once_with(

            is_active_only=True

        )

if __name__ == "__main__":

    unittest.main(verbosity=2)