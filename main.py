from typing import Final
import keyring


def read_auth():
    """Read the notion access token and the Reading list notion DB from keyring."""
    access_token: Final = keyring.get_password("notion", "weekly-articles-selector")
    reading_list_id: Final = keyring.get_password("notion", "reading-list")

    if access_token == None:
        raise ValueError("Access token not found!")

    if reading_list_id == None:
        raise ValueError('"Reading List" database id not found!')

    return access_token, reading_list_id


def main(access_token, reading_list_id):
    print(access_token, reading_list_id)


if __name__ == "__main__":
    access_token, db_id = read_auth()
    main(access_token, db_id)
