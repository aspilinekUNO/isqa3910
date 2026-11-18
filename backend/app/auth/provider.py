from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AuthenticatedUser:
    """
    User information made available to the MPS application
    after authentication.

    The authentication provider is responsible for converting
    its own user information into this common format.
    """

    user_id: str
    display_name: str
    email: str
    role: str
    school: str | None = None


class AuthProvider(ABC):
    """
    Base interface for authentication providers.

    Development currently uses MockAuthProvider.
    MPS can later implement this interface using its approved
    identity provider, such as Microsoft Entra ID or ClassLink.
    """

    @abstractmethod
    def authenticate(self, user_identifier: str) -> AuthenticatedUser | None:
        pass