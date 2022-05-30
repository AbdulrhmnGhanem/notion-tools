from typing import Final

import click
import notion_client

from auth_store import AuthStore


Quote: Final = "quote"
Text: Final = "text"
PlainText: Final = "plain_text"

TwitterThread: Final = "twitter"
PDF: Final = "pdf"
Markdown = "md"


def get_page_blocks(page_id: str) -> list[dict]:
    access_token = AuthStore().notion.weekly_articles_selector_integration
    notion = notion_client.Client(auth=access_token)
    return notion.blocks.children.list(page_id)["results"]


def get_quotes_plain_text(page_blocks: list[dict]) -> list[str]:
    text_blocks = [block[Quote][Text] for block in page_blocks if Quote in block]
    return [
        "".join(sub_block[PlainText] for sub_block in block) for block in text_blocks
    ]


def write_quotes_md(quotes_plain_text: list[str], file_path: str):
    with open(file_path, mode="w", encoding="utf-8") as fp:
        for quote in quotes_plain_text:
            for quote_line in quote.split("\n"):
                fp.write(f"\n> {quote_line}")
            fp.write("\n")


@click.command()
@click.option(
    "--page-id",
    required=True,
    help="Notion page ID",
)
@click.option("--export-format", type=click.Choice([TwitterThread, PDF, Markdown]))
@click.option(
    "--export-dest", type=click.Path(dir_okay=False, writable=True), default=None
)
def cli(page_id, export_format, export_dest):
    "Collect quotes from a notion page and export it in the desired format."
    blocks = get_page_blocks(page_id)
    quotes_plain_text = get_quotes_plain_text(blocks)

    if export_format == TwitterThread:
        print("t")
    elif export_format == PDF:
        print("p")
    elif export_format == Markdown:
        write_quotes_md(quotes_plain_text, export_dest)
    else:
        raise ValueError("Unsupported export formant!")
