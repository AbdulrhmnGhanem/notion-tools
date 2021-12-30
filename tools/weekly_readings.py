from typing import Final, List
import random

import keyring
import notion_client


def read_auth():
    """Read the notion access token and the Reading list notion DB from keyring."""
    access_token: Final = keyring.get_password("notion", "weekly-articles-selector")
    reading_list_id: Final = keyring.get_password("notion", "reading-list")

    if access_token == None:
        raise ValueError("Access token not found!")

    if reading_list_id == None:
        raise ValueError('"Reading List" database id not found!')

    return access_token, reading_list_id


def get_articles_numbers(articles) -> List[int]:
    """Extract the `No` fields form the records"""
    return [article["properties"]["No"]["number"] for article in articles]


def select_articles(article_numbers: List[int], select: int) -> List[int]:
    return random.sample(article_numbers, select)


def get_not_read_articles(
    notion: notion_client.Client, reading_list_id: str
) -> List[dict]:
    """Fetch all the unread articles from the `Reading List` DBs."""
    query: Final = {
        "database_id": reading_list_id,
        "filter": {"property": "Done", "checkbox": {"equals": False}},
        "page_size": 100,
    }

    all_articles = []

    has_more = True
    next_cursor = None

    while has_more:
        response = notion.databases.query(
            **query, **{"start_cursor": next_cursor} if next_cursor else {}
        )

        all_articles += response["results"]
        has_more = response["has_more"]
        next_cursor = response["next_cursor"]

    return all_articles


def select_articles_of_week(select: int):
    access_token, reading_list_id = read_auth()
    notion = notion_client.Client(auth=access_token)

    not_read_articles = get_not_read_articles(notion, reading_list_id)
    not_read_articles_numbers = get_articles_numbers(not_read_articles)
    return select_articles(not_read_articles_numbers, select)


if __name__ == "__main__":
    import sys

    try:
        select = int(sys.argv[1])
    except IndexError:
        select = 7

    print(select_articles_of_week(select))
