import random
from typing import Final, List
from collections import namedtuple

import click
import notion_client
from todoist_api_python.api import TodoistAPI

from auth_store import AuthManager
import click_validators


"""
! note: the `notion_url` is the url to the notion page of the article not the article itself.
"""
NotionArticle = namedtuple("NotionArticle", "title, notion_url")


def get_articles_info(articles: List[dict]) -> List[NotionArticle]:
    """Extract the `Name` property form the records

    The `Name` property is a [rich-text block](https://developers.notion.com/reference/rich-text).
    """
    return [
        NotionArticle(
            article["properties"]["Name"]["title"][0]["plain_text"], article["url"]
        )
        for article in articles
    ]


def select_articles(articles: List[NotionArticle], select: int):
    return random.choices(articles, k=select)


def get_not_read_articles(
    notion: notion_client.Client, reading_list_id: str
) -> List[dict]:
    """Fetch all the unread articles from the `Reading List` DB."""
    query: Final = {
        "database_id": reading_list_id,
        "filter": {
            "and": [
                {"property": "Done", "checkbox": {"equals": False}},
                {"property": "Name", "title": {"is_not_empty": True}},
            ]
        },
        "page_size": 100,
    }

    all_articles = []

    has_more = True
    next_cursor: str = ""

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
    not_read_articles_info = get_articles_info(not_read_articles)
    return select_articles(not_read_articles_info, select)


def add_articles_to_todoist(selected_articles: List[NotionArticle], due: int):
    todoist_auth_manager = AuthManager().todoist
    todoist_api = TodoistAPI(todoist_auth_manager.api_token)

    reading_list_project_id = todoist_auth_manager.reading_list_id

    try:
        for article in selected_articles:
            # FIXME handle failure, though I don't know what to do if it fails
            todoist_api.add_task(
                content=article.title,
                due_string=f"{due} days from now",
                project_id=reading_list_project_id,
            )

        return True
    except Exception as e:
        print(e)

        return False


def make_checklist(selected_articles: List[NotionArticle]):
    return "\n".join(
        f"- [ ] [{article.title}]({article.notion_url})"
        for article in selected_articles
    )


@click.command()
@click.option(
    "--count",
    default=7,
    show_default=True,
    callback=click_validators.positive_num,
    help="Number of articles to select",
)
@click.option(
    "--add-to-todoist",
    "-t",
    is_flag=True,
    show_default=True,
    help="Add articles to Todoist",
)
@click.option("--due", default=7, show_default=True, help="Due after how many days.")
@click.option(
    "--checklist",
    "-c",
    default=True,
    is_flag=True,
    show_default=True,
    help="Print formatted checklist which is pastbale into notion with backlinks.",
)
def cli(count, add_to_todoist, due, checklist):
    selected_articles = select_articles_of_week(count)

    if add_to_todoist:
        add_articles_to_todoist(selected_articles, due)

    if checklist:
        selected_articles_checklist = make_checklist(selected_articles)
        click.echo(selected_articles_checklist)
