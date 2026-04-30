from textual.app import App, ComposeResult, Widget
from textual.binding import Binding
from textual.widgets import (
    Footer,
    Header,
    TextArea,
    Markdown,
    Tabs,
    Button,
    Input,
    Label,
    Tab
)
from textual.containers import Horizontal
import file_manager
from enum import Enum, auto


# a class for the home screen
class Home(Widget):
    def __init__(self):
        super().__init__()
        self.buttons = [
            Button("Save", id="save"),
            Button("Load", id="load"),
            Button("New File", id="new"),
            Button("Rename File", id="rename"),
            Button("Delete File", id="delete"),
        ]
        self.event_button_state = EventButtonState.NONE

    def hide_all_buttons(self) -> None:
        for button in self.buttons:
            button.display = False

    def reset_buttons(self) -> None:
        for button in self.buttons:
            button.display = True

    def compose(self) -> ComposeResult:
        for button in self.buttons:
            yield button

        self.files_label = Label()
        self.files_label.display = False
        yield self.files_label

        self.text_input = Input()
        self.text_input.display = False
        yield self.text_input

        self.status_label = Label()
        self.status_label.display = False
        yield self.status_label

        self.cancel_button = Button("Cancel", id="cancel")
        self.cancel_button.display = False

        self.event_button = Button(id="event")
        self.event_button.display = False

        yield Horizontal(self.cancel_button, self.event_button)


class EventButtonState(Enum):
    NONE = auto()
    CREATE = auto()
    SELECT_RENAME = auto()
    RENAME = auto()
    DELETE = auto()
    SUCCESS = auto()


# a class for the text editor
class Editor(Widget):
    def __init__(self):
        super().__init__()
        # the textarea is where users type
        self.textarea = TextArea()
        # the markdown is where the result is displayed with formatting
        self.markdown = Markdown()

    def compose(self) -> ComposeResult:
        # place both elements side by side
        yield Horizontal(self.textarea, self.markdown)


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
    ]

    # creates the layout of the app
    def compose(self) -> ComposeResult:
        # the top of the page with the title
        yield Header()
        yield Footer()

        # creates a new tab for the first file in the files dictionary
        self.tabs = Tabs("Home")
        yield self.tabs

        # creates the home screen
        self.home = Home()
        yield self.home

        # creates the text editor
        self.editor = Editor()
        self.editor.display = False
        self.textarea = self.editor.textarea
        self.markdown = self.editor.markdown
        yield self.editor

    # called when the app is created
    def on_mount(self) -> None:
        self.files = file_manager.load_files()
        # goes through every file
        # creates tabs, naming them the filename
        for file in list(self.files.keys()):
            self.tabs.add_tab(Tab(file, id=file.replace(" ", "-")))

    # called when the user switches tabs
    # this is also called when the first tab is loaded by default
    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        # if the user switched to the home tab
        # display the home screen
        if str(event.tab.label).lower() == "home":
            self.home.display = True
            self.editor.display = False
        # if the user switched to a file tab
        # load the contents of the file
        # open editor view
        else:
            self.editor.display = True
            self.home.display = False
            # focuses the textarea so that users can start typing without having to click on it manually
            self.textarea.focus()
            # gets the name of the file so that the file contents can be accessed from the dictionary
            self.current_filename = event.tab.label
            # loads the file from the dictionary with the filename
            loaded_content = self.files[self.current_filename]
            # sets the default content of the newly opened tab to the saved content
            self.textarea.text = loaded_content
            self.markdown.update(loaded_content)

    # called whenever the textarea's value changes
    def on_text_area_changed(self) -> None:
        self.files[self.current_filename] = self.textarea.text  # update files dict
        md_text = self.textarea.text.replace("\n", "  \n")  # handle new lines
        self.markdown.update(md_text)

    def return_home(self) -> None:
        self.home.text_input.display = False
        self.home.text_input.value = ""
        self.home.event_button.display = False
        self.home.status_label.display = False
        self.home.files_label.display = False
        self.home.cancel_button.display = False
        self.home.event_button_state = EventButtonState.NONE
        self.home.reset_buttons()

    # called when a button is pressed
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save" or event.button.id == "load":
            if event.button.id == "save":
                file_manager.save_files(self.files)
            elif event.button.id == "load":
                self.files = file_manager.load_files()
        elif (
            event.button.id == "event"
            and self.home.event_button_state != EventButtonState.NONE
        ):
            state = self.home.event_button_state
            success = False


            # if the file name is empty or just whitespace
            if self.home.text_input.value.strip() == "":
                self.home.status_label.display = True
                self.home.status_label.update("Please enter a file name")
                return

            # if the previous condition checks for an empty input box
            # if it is passed, the input box contains text
            # the content of this text is not validated, that is handled by individual methods
            
            if state == EventButtonState.CREATE:
                # if the file already exists
                if self.home.text_input.value in list(self.files.keys()):
                    self.home.status_label.display = True
                    self.home.status_label.update("File with this name already exists")
                    return
                # nothing is wrong, create the file
                else:
                    self.files[self.home.text_input.value] = ""
                    file_manager.save_files(self.files)
                    self.tabs.add_tab(Tab(self.home.text_input.value, id=self.home.text_input.value.replace(" ", "-")))
                    success = True
            elif state == EventButtonState.SELECT_RENAME:
                pass
            elif state == EventButtonState.RENAME:
                pass
            elif state == EventButtonState.DELETE:
                # if the file doesn't exist
                if self.home.text_input.value not in list(self.files.keys()):
                    self.home.status_label.display = True
                    self.home.status_label.update("File with this name doesn't exist")
                    return
                # nothing is wrong, delete the file
                else:
                    del self.files[self.home.text_input.value]
                    file_manager.save_files(self.files)
                    self.tabs.remove_tab(self.home.text_input.value.replace(" ", "-"))
                    success = True
            elif state == EventButtonState.SUCCESS:
                self.return_home()

            if success == True:
                self.home.text_input.display = False
                self.home.status_label.display = True
                self.home.event_button_state = EventButtonState.SUCCESS
                self.home.files_label.display = False
                self.home.event_button.label = "Continue"
                self.home.cancel_button.display = False
                self.home.status_label.update("Success!")

        elif event.button.id == "cancel":
            self.return_home()

        else:
            self.home.hide_all_buttons()
            self.home.files_label.display = True
            self.home.files_label.update("Files: " + ", ".join(list(self.files.keys())))
            self.home.text_input.display = True
            self.home.text_input.focus()
            self.home.cancel_button.display = True
            self.home.event_button.display = True
            if event.button.id == "new":
                self.home.text_input.placeholder = "New file name"
                self.home.event_button.label = "Create"
                self.home.event_button_state = EventButtonState.CREATE
            elif event.button.id == "rename":
                self.home.text_input.placeholder = "Name of file to rename"
                self.home.event_button.label = "Select"
            elif event.button.id == "delete":
                self.home.text_input.placeholder = "Name of file to delete"
                self.home.event_button.label = "Delete"
                self.home.event_button_state = EventButtonState.DELETE

        self.set_focus(None)

    # mapped to a binding
    def action_italicize(self) -> None:
        pass

    # mapped to a binding
    def action_highlight(self) -> None:
        pass

    # mapped to a binding
    # condenses several paragraphs into one
    def action_condense(self) -> None:
        # FIX: bug -> when nothing is selected, it duplicates all text
        start = self.textarea.selection.start
        end = self.textarea.selection.end
        self.textarea.replace(self.textarea.text.replace("\n", " "), start, end)


# runs the app
if __name__ == "__main__":
    app = Wordless()
    app.run()
