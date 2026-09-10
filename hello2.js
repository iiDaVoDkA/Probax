task = TaskRepository.get(task_id)

if UserRoleEnum.SUPER_ADMIN.value in user.get("roles", []):
    task = TaskRepository.validate(task, user.get("id"))
else:
    if not can_modify_task(user, task):
        raise PermissionError

    task = validate_task(task, user)

return task.to_json(load_task_details=True)