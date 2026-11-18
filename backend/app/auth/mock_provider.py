from .provider import AuthProvider, AuthenticatedUser


DEMO_USERS = {
    "teacher": AuthenticatedUser(
        user_id="demo-teacher",
        display_name="Demo Teacher",
        email="teacher@example.test",
        role="teacher",
        school="Millard North High School"
    ),

    "secretary": AuthenticatedUser(
        user_id="demo-secretary",
        display_name="Demo Secretary",
        email="secretary@example.test",
        role="secretary",
        school="Millard North High School"
    ),

    "administrator": AuthenticatedUser(
        user_id="demo-administrator",
        display_name="Demo Administrator",
        email="administrator@example.test",
        role="administrator",
        school="Millard North High School"
    ),

    "district_staff": AuthenticatedUser(
        user_id="demo-district-staff",
        display_name="Demo District Staff",
        email="district@example.test",
        role="district_staff",
        school=None
    )
}


class MockAuthProvider(AuthProvider):
    """
    Development-only authentication provider.

    This does not validate real MPS credentials.
    """

    def authenticate(
        self,
        user_identifier: str
    ) -> AuthenticatedUser | None:

        return DEMO_USERS.get(user_identifier)