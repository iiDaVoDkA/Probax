# ============================================================
# 1) PROJECT STATUS TEST
# FILE:
# test/api/project/test_update_project_status.py
# ============================================================

# ---- ADD THESE TO THE EXISTING IMPORTS ----
from models import UserRole, UserRoleEnum


# ---- ADD THIS TEST INSIDE class TestUpdateProjectStatus ----

@patch(
    "resources.project.project_status.is_project_status_transition_valid",
    return_value=False,
)
@patch(
    "resources.project.project_status.is_user_authorized_to_modify_project",
    return_value=False,
)
def test_super_admin_can_force_project_status(
    self,
    is_user_authorized_to_modify_project,
    is_project_status_transition_valid,
):
    # Give the existing test user the SUPER_ADMIN role
    UserRole(
        user_id=1,
        role=UserRoleEnum.SUPER_ADMIN,
    ).save()

    # Number of audit entries before the update
    previous_changes = ProjectDataChange.query.count()

    # Try a transition that would normally be rejected
    response = self.client.patch(
        "{}/{}/status".format(self.url, 1),
        data=json.dumps(
            {
                "status": ProjectStatus.COMPLETED.value,
            }
        ),
        content_type="application/json",
    )

    # SUPER_ADMIN must be allowed
    self.assertEqual(response.status_code, 200)

    # Reload project from DB
    project = db.session.get(Project, 1)

    # Status must really have changed
    self.assertEqual(
        project.status,
        ProjectStatus.COMPLETED,
    )

    # A ProjectDataChange must have been created
    self.assertEqual(
        ProjectDataChange.query.count(),
        previous_changes + 1,
    )


# ============================================================
# WHAT THIS PROJECT TEST PROVES
# ============================================================

# SUPER_ADMIN exists on the user
#
# normal authorization = False
# normal transition validation = False
#
# BUT:
#
# PATCH /projects/1/status
#               ↓
# SUPER_ADMIN branch
#               ↓
# status changes anyway
#               ↓
# ProjectDataChange created
#               ↓
# HTTP 200
#
# So this proves the bypass really works.


# ============================================================
# 2) TASK VALIDATION TEST
# FILE:
# test/api/task/test_validate_task.py
# ============================================================

# ---- ADD THESE TO THE EXISTING IMPORTS ----
from models import UserRole, UserRoleEnum


# ---- ADD THIS TEST INSIDE THE EXISTING ValidateTask test class ----
#
# IMPORTANT:
# Use a task id that ALREADY EXISTS in this test file's setUp().
# If the existing task is id=1, keep task_id = 1.
# Otherwise replace 1 with that task id.

def test_super_admin_can_validate_task(self):
    task_id = 1

    # Give existing test user SUPER_ADMIN
    UserRole(
        user_id=1,
        role=UserRoleEnum.SUPER_ADMIN,
    ).save()

    task_before = db.session.get(Task, task_id)

    # Make sure we know the starting status
    self.assertNotEqual(
        task_before.status,
        TaskStatus.DONE,
    )

    # Call the existing validate endpoint
    response = self.client.patch(
        "{}/{}/validate".format(self.url, task_id),
        content_type="application/json",
    )

    # SUPER_ADMIN validation must work
    self.assertEqual(response.status_code, 200)

    # Reload from DB
    task = db.session.get(Task, task_id)

    # Task must now be DONE
    self.assertEqual(
        task.status,
        TaskStatus.DONE,
    )

    # Repository.validate() should also set these
    self.assertIsNotNone(task.ending_date)


# ============================================================
# WHAT THIS TASK TEST PROVES
# ============================================================

# Normal user normally does:
#
# can_modify_task(...)
#       ↓
# validate_task(task, user)
#       ↓
# full business workflow
#
#
# SUPER_ADMIN does:
#
# UserRoleEnum.SUPER_ADMIN found
#       ↓
# TaskRepository.validate(task, user_id)
#       ↓
# task.status = DONE
# ending_date set
# flush
#
# So the normal validation workflow is bypassed.


# ============================================================
# 3) OPTIONAL SIMPLE ROLE TEST
# FILE:
# test/api/user_role/test_user_role.py
# ============================================================

# You already have tests using USER / OBSERVER etc.
# Add this inside class TestUserRole if you want to explicitly
# test that SUPER_ADMIN can be stored.

def test_super_admin_role(self):
    user_role = UserRole(
        user_id=1,
        role=UserRoleEnum.SUPER_ADMIN,
    )

    user_role.save()

    saved_role = UserRoleRepository.get(
        1,
        UserRoleEnum.SUPER_ADMIN.value,
    )

    self.assertEqual(
        saved_role.role,
        UserRoleEnum.SUPER_ADMIN,
    )


# ============================================================
# 4) RUN ONLY THE NEW PROJECT TEST
# ============================================================

# Terminal:

pytest test/api/project/test_update_project_status.py::TestUpdateProjectStatus::test_super_admin_can_force_project_status -vv -s


# ============================================================
# 5) RUN ONLY THE NEW TASK TEST
# ============================================================

# Replace the class name below with the exact class name
# already present in test_validate_task.py if different.

pytest test/api/task/test_validate_task.py -k "super_admin" -vv -s


# ============================================================
# 6) RUN ALL SUPER_ADMIN TESTS
# ============================================================

pytest test/api -k "super_admin" -vv -s


# ============================================================
# EXPECTED RESULTS
# ============================================================

# PROJECT:
# 200
# project.status == COMPLETED
# ProjectDataChange +1
#
# TASK:
# 200
# task.status == DONE
# ending_date != None
#
# EXISTING NORMAL USER TESTS:
# must continue passing unchanged