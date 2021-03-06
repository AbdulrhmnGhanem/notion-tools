import io
from textwrap import dedent
import typing
import uuid

import click
from rich.console import Console
from editor import CapturedText, setup_editor
import notion_client

from auth_store import AuthStore


COMPLETION_WORDS: typing.Final = ["Todo: ", "Idea: ", "Backlog: "]
console = Console(log_path=False)


def make_checkbox_block(checkbox_text: str):
    return {
        "object": "block",
        "id": uuid.uuid4(),
        "children": [
            {
                "to_do": {
                    "text": [
                        {
                            "type": "text",
                            "text": {"content": checkbox_text},
                        }
                    ],
                    "checked": False,
                }
            }
        ],
    }


def append_block(
    block: dict,
) -> typing.Tuple[
    typing.Optional[dict], typing.Optional[notion_client.APIResponseError]
]:
    notion_auth_manager = AuthStore().notion
    access_token = notion_auth_manager.weekly_articles_selector_integration
    capture_page_id = notion_auth_manager.capture_page
    notion = notion_client.Client(auth=access_token)

    try:
        return notion.blocks.children.append(capture_page_id, **block), None
    except notion_client.APIResponseError as e:
        return None, e


def save(text: str) -> None:
    if len(text) == 0:
        console.log("[red]Empty capture, didn't add it :person_shrugging:")
        return

    block = make_checkbox_block(text)
    _, err = append_block(block)

    if err is None:
        console.log("[green]Captured successfully :heavy_check_mark:")
    else:
        console.log("[red]Capture failed :x:")


@click.command()
def cli():
    """Capture a todo/idea quickly into notion"""
    application = setup_editor(COMPLETION_WORDS)
    result: CapturedText = application.run()

    if result.save:
        save(result.text)
        return
    console.log("[red]Quited without saving :x:")
