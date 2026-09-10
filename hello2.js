if UserRoleEnum.SUPER_ADMIN.value in user.get("roles", []):
    new_project_status = ProjectStatus(status)

    with SessionCriticalActionManager(...):  # mêmes paramètres que le bloc existant plus bas
        ProjectRepository.update(
            project=project,
            status=new_project_status,
        )

    return project.to_json(for_project_card=True)