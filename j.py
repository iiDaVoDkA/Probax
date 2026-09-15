change = (
    ProjectDataChange.query
    .order_by(ProjectDataChange.id.desc())
    .first()
)

self.assertEqual(change.project_id, 1)
self.assertEqual(change.data_name, ProjectDataNames.PROJECT_STATUS)
self.assertEqual(change.old_value, ProjectStatus.ONHOLD.value)
self.assertEqual(change.new_value, ProjectStatus.COMPLETED.value)
self.assertEqual(change.user_id, 1)
self.assertIsNone(change.task_id)


change = (
    ProjectDataChange.query
    .order_by(ProjectDataChange.id.desc())
    .first()
)

self.assertEqual(change.project_id, self.normal_task.project_id)
self.assertEqual(change.task_id, self.normal_task.id)
self.assertEqual(change.data_name, ProjectDataNames.TASK_STATUS)
self.assertEqual(change.old_value, TaskStatus.ONGOING.value)
self.assertEqual(change.new_value, TaskStatus.DONE.value)
self.assertEqual(change.user_id, 1)