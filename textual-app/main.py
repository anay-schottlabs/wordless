from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class Wordless(App):

    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        ("^1", "underline", "Underline"),
        ("^2", "highlight", "Highlight"),
        ("^3", "condense", "Condense")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_underline(self) -> None:
        pass

    def action_highlight(self) -> None:
        pass

    def action_condense(self) -> None:
        pass

if __name__ == "__main__":
    app = Wordless()
    app.run()
