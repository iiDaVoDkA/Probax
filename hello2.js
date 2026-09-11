if UserRoleEnum.SUPER_ADMIN.value in user.get("roles", []):
    new_project_status = ProjectStatus(status)

    with SessionCriticalActionManager(
        "Update project {} status".format(project_id), db.session, DEV_TEAM_EMAILS
    ):
        ProjectDataChangeRepository.create(
            project_id=project.id,
            data_name=ProjectDataNames.PROJECT_STATUS,
            old_value=project.status.value,
            new_value=new_project_status.value,
            user_id=user["id"],
        )

        project.status = new_project_status
        project.flush()

    return project.to_json(for_project_card=True)
    
    
    if UserRoleEnum.SUPER_ADMIN.value in user.get("roles", []):
    ProjectDataChangeRepository.create(
        project_id=task.project_id,
        data_name=ProjectDataNames.TASK_STATUS,
        old_value=task.status.value,
        new_value=TaskStatus.DONE.value,
        user_id=user["id"],
    )

    task = TaskRepository.validate(task, user.get("id"))

else:
    if not can_modify_task(user, task):
        raise PermissionError

    task = validate_task(task, user)
    
    