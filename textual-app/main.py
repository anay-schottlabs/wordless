from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, TextArea, Markdown, Tabs
from textual.containers import Horizontal
import file_manager

# load files on app startup
files = file_manager.load_files()


# creating the app class
class Wordless(App):
    # hides one of the default bindings
    # hiding it saves screen space
    ENABLE_COMMAND_PALETTE = False

    # path to the CSS file
    CSS_PATH = "styles.tcss"

    # bindings that are visible in the footer
    # each has a keybaord shortcut that maps to a method
    BINDINGS = [
        Binding("ctrl+1", "italicize", "italicize"),
        Binding("ctrl+2", "highlight", "highlight"),
        Binding("ctrl+3", "condense", "condense"),
        Binding("ctrl+s", "save", "save"),
        Binding("ctrl+l", "load", "load"),
    ]

    # creates the layout of the app
    def compose(self) -> ComposeResult:
        yield Header()
        # creates a new tab for the first file in the files dictionary
        yield Tabs(list(files.keys())[0])
        yield Footer()
        # the textarea is where users type
        self.textarea = TextArea()
        # the markdown is where the result is displayed with formatting
        self.markdown = Markdown()
        # place them side by side
        yield Horizontal(self.textarea, self.markdown)

    # called when the app is created
    def on_mount(self) -> None:
        tabs = self.query_one(Tabs)
        # opens the first tab by default
        tabs.focus()
        # creates tabs, naming them whatever the name of the file is
        # ignores the first file because it was created in the compose() method
        for file in list(files.keys())[1:]:
            tabs.add_tab(file)

    # called when the user switches tabs
    # this is also called when the first tab is loaded by default
    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        # focuses the textarea so that users can start typing without having to click on it manually
        self.textarea.focus()
        # gets the name of the file so that the file contents can be accessed from the dictionary
        self.current_filename = event.tab.label
        # loads the file from the dictionary with the filename
        loaded_content = files[self.current_filename]
        # sets the default content of the newly opened tab to the saved content
        self.textarea.text = loaded_content
        self.markdown.update(loaded_content)

    # called whenever the textarea's value changes
    def on_text_area_changed(self) -> None:
        # updates the dictionary content
        files[self.current_filename] = self.textarea.text
        # makes sure that new lines are handled properly
        md_text = self.textarea.text.replace("\n", "  \n")
        # updates the markdown view
        self.markdown.update(md_text)

    # mapped to a binding
    def action_italicize(self) -> None:
        pass

    # mapped to a binding
    def action_highlight(self) -> None:
        pass

    # mapped to a binding
    # condenses several paragraphs into one
    def action_condense(self) -> None:
        start = self.textarea.selection.start
        end = self.textarea.selection.end
        self.textarea.replace(self.textarea.text.replace("\n", " "), start, end)

    # loads the files and replaces the current tab's text with the new content
    def action_load(self) -> None:
        self.textarea.text = file_manager.load_files()[self.current_filename]

    # saves all files
    def action_save(self) -> None:
        file_manager.save_files(files)


# runs the app
if __name__ == "__main__":
    app = Wordless()
    app.run()
