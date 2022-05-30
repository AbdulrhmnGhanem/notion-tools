from pathlib import Path
import subprocess
from collections import namedtuple
import tempfile
from typing import Final

import click
import notion_client

from auth_store import AuthStore


Quote: Final = "quote"
Text: Final = "text"
PlainText: Final = "plain_text"
MultiSelect: Final = "multi_select"
Name: Final = "name"
PageName: Final = "Name"
Title: Final = "title"

TwitterThread: Final = "twitter"
PDF: Final = "pdf"
Markdown = "md"


Page = namedtuple("Page", "title, authors, blocks")


def get_page_info(page_id: str):
    access_token = AuthStore().notion.weekly_articles_selector_integration
    notion = notion_client.Client(auth=access_token)

    blocks = notion.blocks.children.list(page_id)["results"]
    page_properties = notion.pages.retrieve(page_id)["properties"]

    return Page(
        title=get_page_title(page_properties),
        authors=get_page_authors(page_properties),
        blocks=blocks,
    )


def get_page_authors(page_properties: dict) -> list[str]:
    return [author[Name] for author in page_properties["Authors"][MultiSelect]]


def get_page_title(page_properties: dict) -> str:
    return page_properties[PageName][Title][0][PlainText]


def get_quotes_plain_text(page_blocks: list[dict]) -> list[str]:
    text_blocks = [block[Quote][Text] for block in page_blocks if Quote in block]
    return [
        "".join(sub_block[PlainText] for sub_block in block) for block in text_blocks
    ]


def write_quotes_md(
    title: str,
    authors: list[str],
    quotes_plain_text: list[str],
    file_path: str,
    is_temp=False,
):
    with open(file_path, mode="w", encoding="utf-8") as fp:
        fp.write(f"# {title}\n")
        fp.write(f'_{", ".join(authors)}_\n')

        for quote in quotes_plain_text:
            for quote_line in quote.split("\n"):
                fp.write(f"\n> {quote_line}")
            fp.write("\n")
        if is_temp:
            fp.flush()


def write_quotes_pdf(
    title: str, authors: list[str], quotes_plain_text: list[str], file_path: str
):
    head_file_path = str(
        Path(__file__).parents[2].joinpath("assets").joinpath("head.tex")
    )

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as fp:
        write_quotes_md(title, authors, quotes_plain_text, fp.name, True)
        subprocess.check_call(
            [
                "pandoc",
                "-H",
                head_file_path,
                "-f",
                "markdown",
                fp.name,
                "-o",
                file_path,
            ]
        )


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
    info = get_page_info(page_id)
    quotes_plain_text = get_quotes_plain_text(info.blocks)

    if export_format == TwitterThread:
        print("t")
    elif export_format == PDF:
        write_quotes_pdf(info.title, info.authors, quotes_plain_text, export_dest)
    elif export_format == Markdown:
        write_quotes_md(info.title, info.authors, quotes_plain_text, export_dest)
    else:
        raise ValueError("Unsupported export formant!")
