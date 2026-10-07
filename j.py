response = s.post(
    url,
    data=payload_send,
    files=files,
    headers=headers,
    verify=False,
)

logging.warning(
    "MAILER status=%s | body=%s",
    response.status_code,
    response.text,
)

response.raise_for_status()
return "OK"