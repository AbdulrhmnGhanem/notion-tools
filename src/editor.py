from dataclasses import dataclass
import typing

from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.containers import Float, FloatContainer, HSplit, Window
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.application import Application


@dataclass
class CapturedText:
    save: bool
    text: typing.Optional[str] = None


def _make_buffer_with_autocompletion(completion_words: typing.List[str]) -> Buffer:
    completer = WordCompleter(completion_words, ignore_case=True)
    return Buffer(completer=completer, complete_while_typing=True)


def setup_editor(completion_words: typing.List[str]):
    buffer = _make_buffer_with_autocompletion(completion_words)

    body = FloatContainer(
        content=HSplit(
            [
                Window(
                    FormattedTextControl(
                        'Press "Ctrl+s" to submit or "Ctrl+q" to quit.'
                    ),
                    height=1,
                    style="reverse",
                ),
                Window(BufferControl(buffer=buffer)),
            ]
        ),
        floats=[
            Float(
                xcursor=True,
                ycursor=True,
                content=CompletionsMenu(max_height=16, scroll_offset=1),
            )
        ],
    )

    kb = KeyBindings()

    @kb.add(Keys.ControlQ)
    def _(event):
        "Quit application."
        event.app.exit(result=CapturedText(False))

    @kb.add(Keys.ControlS)
    def _(event):
        "Save and quit."
        event.app.exit(result=CapturedText(True, buffer.text))

    return Application(layout=Layout(body), key_bindings=kb, full_screen=True)
