from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown, Tabs
from json import load, dump

def load_files():
    with open("files.json", "r") as files_json:
        loaded_files = load(files_json)
    return loaded_files

def save_files():
    with open("files.json", "w") as files_json:
        dump(files, files_json, indent=4)

files = load_files()

class Wordless(App):

    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        ("^1", "underline", "Underline"),
        ("^2", "highlight", "Highlight"),
        ("^3", "condense", "Condense")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Tabs(list(files.keys())[0])
        yield Footer()
        self.viewer = Markdown()
        yield self.viewer

    def on_mount(self) -> None:
        tabs = self.query_one(Tabs)
        tabs.focus()
        tabs.add_tab(list(files.keys())[1])

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        self.viewer.update(files[event.tab.label])

    def action_underline(self) -> None:
        pass

    def action_highlight(self) -> None:
        pass

    def action_condense(self) -> None:
        pass

if __name__ == "__main__":
    app = Wordless()
    app.run()
