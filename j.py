def get_users_by_role(role):
    """Calls the PLM API to get users by role"""
    logging.debug("[PLM] Getting users by role ...")
    session = get_new_requests_session()

    url = f"{config.PLM_URL}/user_role?role={role}"
    headers = {"Authorization": request.headers.get("Authorization")}

    response = session.get(url, headers=headers, verify=False)
    handle_http_error(response)

    logging.debug("[PLM] users by role loaded.")
    return response.json()