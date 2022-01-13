from typing import Literal

import keyring
from typeguard import check_literal

Services = Literal["notion", "todoist"]


class _KeyringService:
    """Keyring service record (username)"""

    def __init__(self, service: Services):
        self.service = service

    def __getattr__(self, name: str):
        password = keyring.get_password(self.service, name)

        if password is None:
            raise ValueError(f"Service {self.service} has no record {name}!")

        return password


class AuthManager:
    """Manages accessing tokens from keyring

    >>> manager = AuthManager()
    >>> print(manager.notion.reading_list)
    """

    def __getattr__(self, service: Services):
        check_literal("service", service, Services, None)
        return _KeyringService(service)
