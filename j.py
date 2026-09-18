@patch(
    "util.required_plm_authentication._me",
    return_value=make_fake_me_response(),
)
@patch(
    "clients.oidc.validate_token",
    return_value={"uid": "mySpecialuid"},
)
class TestInitiativeTeamMembers(unittest.TestCase):
    ...