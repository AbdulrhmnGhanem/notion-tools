from typing import Final, List
import random

import notion_client
from todoist_api_python.api import TodoistAPI

from ..auth_store import AuthManager


def get_articles_names(articles: List[dict]) -> List[str]:
    """Extract the `Name` property form the records

    The `Name` property is a [rich-text block](https://developers.notion.com/reference/rich-text).
    """
    return [
        article["properties"]["Name"]["title"][0]["plain_text"] for article in articles
    ]


def select_articles(article_names: List[str], select: int) -> List[str]:
    return random.choices(article_names, k=select)


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
    next_cursor: str = None

    while has_more:
        response = notion.databases.query(
            **query, **{"start_cursor": next_cursor} if next_cursor else {}
        )

        all_articles += response["results"]
        has_more = response["has_more"]
        next_cursor = response["next_cursor"]

    return all_articles


def select_articles_of_week(select: int):
    notion_auth_manager = AuthManager().notion
    access_token = notion_auth_manager.weekly_articles_selector_integration
    reading_list_id = notion_auth_manager.reading_list

    notion = notion_client.Client(auth=access_token)

    not_read_articles = get_not_read_articles(notion, reading_list_id)
    not_read_articles_numbers = get_articles_names(not_read_articles)
    return select_articles(not_read_articles_numbers, select)


def add_articles_to_todoist(selected_articles: List[str]):
    todoist_auth_manager = AuthManager().todoist
    todoist_api = TodoistAPI(todoist_auth_manager.api_token)

    reading_list_project_id = todoist_auth_manager.reading_list_id

    try:
        for article in selected_articles:
            # FIXME handle failure, though I don't know what to do if it fails
            todoist_api.add_task(
                content=article,
                due_string="7 days from now",
                project_id=reading_list_project_id,
            )

        return True
    except Exception as e:
        print(e)

        return False


if __name__ == "__main__":
    import sys

    try:
        select = int(sys.argv[1])
    except IndexError:
        select = 7

    selected_articles = select_articles_of_week(select)
    add_articles_to_todoist(selected_articles)
    print(selected_articles)
