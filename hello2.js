if UserRoleEnum.SUPER_ADMIN.value in user.get("roles", []):
    new_project_status = ProjectStatus(status)

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