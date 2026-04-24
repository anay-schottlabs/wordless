from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, TextArea, Markdown, Tabs
from textual.containers import Horizontal
import json

def load_files():
    with open("files.json", "r") as files_json:
        loaded_files = json.load(files_json)
    return loaded_files

def save_files():
    with open("files.json", "w") as files_json:
        json.dump(files, files_json, indent=4)

files = load_files()

class Wordless(App):

    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        Binding("ctrl+1", "italicize", "italicize"),
        Binding("ctrl+2", "highlight", "highlight"),
        Binding("ctrl+3", "condense", "condense"),
        Binding("ctrl+s", "save", "save"),
        Binding("ctrl+l", "load", "load")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Tabs(list(files.keys())[0])
        yield Footer()
        self.textarea = TextArea()
        self.markdown = Markdown()
        yield Horizontal(self.textarea, self.markdown)

    def on_mount(self) -> None:
        tabs = self.query_one(Tabs)
        tabs.focus()
        tabs.add_tab(list(files.keys())[1])

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        self.textarea.focus()
        self.current_filename = event.tab.label
        loaded_content = files[self.current_filename]
        self.textarea.text = loaded_content
        self.past_text = loaded_content
        self.markdown.update(loaded_content)

    def on_text_area_changed(self) -> None:
        files[self.current_filename] = self.textarea.text
        md_text = self.textarea.text.replace("\n", "  \n")
        self.markdown.update(md_text)

    def action_italicize(self) -> None:
        pass

    def action_highlight(self) -> None:
        pass

    def action_condense(self) -> None:
        start = self.textarea.selection.start
        end = self.textarea.selection.end
        self.textarea.replace(
            self.textarea.text.replace("\n", " "),
            start, end
        )

    def action_load(self) -> None:
        self.textarea.text = load_files()[self.current_filename]

    def action_save(self) -> None:
        save_files()

if __name__ == "__main__":
    app = Wordless()
    app.run()
