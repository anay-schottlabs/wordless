from textual.app import App, ComposeResult, Widget
from textual.binding import Binding
from textual import work  # for async network tasks
from textual.widgets import (
    TextArea,
    Markdown,
    Tabs,
    Button,
    Input,
    Label,
    Tab,
    Static,
)
from textual.containers import Horizontal, Vertical, VerticalScroll


def _word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0


class WordlessFooter(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("", id="footer-share")
        yield Static("", id="footer-left")
        yield Static("", id="footer-right")

    def on_mount(self) -> None:
        self.set_share_status(False)

    def set_share_status(self, is_sharing: bool, filename: str = "") -> None:
        share = self.query_one("#footer-share", Static)
        if is_sharing:
            share.update(f"⬤  sharing: {filename}")
            self.add_class("-sharing")
        else:
            share.update("◌  not sharing")
            self.remove_class("-sharing")

    def show_editor_stats(self, full_text: str, selected_text: str) -> None:
        total_words = _word_count(full_text)
        total_chars = len(full_text)
        right = self.query_one("#footer-right", Static)
        left = self.query_one("#footer-left", Static)
        if selected_text:
            sel_words = _word_count(selected_text)
            sel_chars = len(selected_text)
            left.update(f"◈  {sel_words}w · {sel_chars}c  selected")
            right.update(f"doc  {total_words}w · {total_chars}c")
            self.add_class("-selecting")
        else:
            left.update("")
            right.update(f"{total_words}w · {total_chars}c")
            self.remove_class("-selecting")

    def clear(self) -> None:
        self.query_one("#footer-left", Static).update("")
        self.query_one("#footer-right", Static).update("")
        self.remove_class("-selecting")


import socket
from enum import Enum, auto
import re
import file_manager
import network

# large banner for the homepage
ASCII_ART = """
 ██╗    ██╗ ██████╗ ██████╗ ██████╗ ██╗     ███████╗███████╗███████╗
 ██║    ██║██╔═══██╗██╔══██╗██╔══██╗██║     ██╔════╝██╔════╝██╔════╝
 ██║ █╗ ██║██║   ██║██████╔╝██║  ██║██║     █████╗  ███████╗███████╗
 ██║███╗██║██║   ██║██╔══██╗██║  ██║██║     ██╔══╝  ╚════██║╚════██║
 ╚███╔███╔╝╚██████╔╝██║  ██║██████╔╝███████╗███████╗███████║███████║
  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝"""


# a class for the home screen
class Home(Widget):
    def __init__(self):
        super().__init__()
        self.save_button = Button("Save", id="save")
        self.load_button = Button("Load", id="load")
        self.new_button = Button("New File", id="new")
        self.rename_button = Button("Rename File", id="rename")
        self.delete_button = Button("Delete File", id="delete")
        self.buttons = [
            self.save_button,
            self.load_button,
            self.new_button,
            self.rename_button,
            self.delete_button,
        ]
        self.event_button_state = EventButtonState.NONE

    def hide_all_buttons(self) -> None:
        for button in self.buttons:
            button.display = False
        self.io_header.display = False
        self.io_row.display = False
        self.mgmt_header.display = False
        self.mgmt_row.display = False

    def reset_buttons(self) -> None:
        for button in self.buttons:
            button.display = True
        self.io_header.display = True
        self.io_row.display = True
        self.mgmt_header.display = True
        self.mgmt_row.display = True

    def compose(self) -> ComposeResult:
        yield Static(ASCII_ART, id="ascii-art")
        yield Static("// a minimalist text editor //", id="subtitle")

        self.io_header = Static(
            "─── FILE I/O ───────────────────────────────────────────────────────────",
            classes="section-label",
        )
        yield self.io_header
        self.io_row = Horizontal(self.save_button, self.load_button, id="io-buttons")
        yield self.io_row

        self.mgmt_header = Static(
            "─── FILE MANAGEMENT ────────────────────────────────────────────────────",
            classes="section-label",
        )
        yield self.mgmt_header
        self.mgmt_row = Horizontal(
            self.new_button,
            self.rename_button,
            self.delete_button,
            id="mgmt-buttons",
        )
        yield self.mgmt_row

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

        yield Horizontal(self.cancel_button, self.event_button, id="action-buttons")


# big banner for the network page
NETWORK_BANNER = """\
   ┌──────────┐                                          ┌──────────┐
   │   HOST   │ ════════════════════════════════════════ │   JOIN   │
   └──────────┘         WORDLESS  //  NETWORK            └──────────┘"""


class Network(Widget):
    def __init__(self):
        super().__init__()
        self.event_button_state = NetworkEventButtonState.NONE

    def compose(self) -> ComposeResult:
        yield Static(NETWORK_BANNER, id="network-banner")
        yield Static(
            "// share files across your local network in real time //",
            id="network-tagline",
        )

        self.host_button = Button("Host a File", id="host")
        self.join_button = Button("Join a Session", id="join")

        self.mode_row = Horizontal(
            Vertical(
                Static("HOST", classes="mode-label"),
                Static(
                    "Share a local file with\nanother machine on your network",
                    classes="mode-desc",
                ),
                self.host_button,
                id="host-card",
            ),
            Vertical(
                Static("JOIN", classes="mode-label"),
                Static(
                    "Connect to a file hosted\nby another machine on your network",
                    classes="mode-desc",
                ),
                self.join_button,
                id="join-card",
            ),
            id="mode-row",
        )
        yield self.mode_row

        self.conn_input = Input()
        self.conn_input.display = False
        yield self.conn_input

        self.status_label = Label()
        self.status_label.display = False
        yield self.status_label

        self.cancel_button = Button("Cancel", id="network_cancel")
        self.cancel_button.display = False

        self.event_button = Button(id="network_event")
        self.event_button.display = False

        self.disconnect_button = Button("Disconnect", id="network_disconnect")
        self.disconnect_button.display = False
        yield self.disconnect_button

        self.done_button = Button("Done", id="network_done")
        self.done_button.display = False
        yield self.done_button

        yield Horizontal(
            self.cancel_button, self.event_button, id="network-action-buttons"
        )

        self.received_header = Static(
            "─── RECEIVED CONTENT ───────────────────────────────────────────────────",
            id="received-header",
        )
        self.received_header.display = False
        yield self.received_header

        self.markdown = Markdown()
        self.markdown.display = False
        yield self.markdown


# both the network and the home pages have event buttons
# event buttons are able to change their function based on the state of the app
# instead of having multiple different buttons, we simply relabel and rerender the event button
# the enums manage the states of the event buttons so that their different functions can be called


# this enum manages the state of the home page's event button
class EventButtonState(Enum):
    NONE = auto()
    CREATE = auto()
    SELECT_RENAME = auto()
    RENAME = auto()
    DELETE = auto()
    SUCCESS = auto()


# this enum manages the state of the network page's event button
class NetworkEventButtonState(Enum):
    NONE = auto()
    HOST_FILE = auto()
    HOST_CONN = auto()
    CLOSE_HOST = auto()
    JOIN = auto()
    CONN_CLOSED = auto()


# this manages the state of the app's tabs
# all files are condensed down to the EDITOR state
# this is because all of them are rendered with the same widgets
# for each unique file, the contents are simply loaded into the widgets
class ActiveTab(Enum):
    HOME = auto()
    NETWORK = auto()
    EDITOR = auto()


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
    ENABLE_COMMAND_PALETTE = False  # this app doesn't use the command palette
    CSS_PATH = "styles.tcss"
    TITLE = "WORDLESS"
    SUB_TITLE = "// a text editor //"

    # creates the layout of the app
    def compose(self) -> ComposeResult:
        # creates a new tab for the home page and network page
        self.tabs = Tabs(Tab("HOME", id="home"), Tab("NETWORK", id="network"))
        yield self.tabs

        # creates the home screen
        self.home = Home()
        yield self.home

        # creates the network screen
        self.network = Network()
        yield self.network

        # creates the text editor
        self.editor = Editor()
        self.editor.display = False
        self.textarea = self.editor.textarea
        self.markdown = self.editor.markdown
        yield self.editor

        # custom footer — docked at the bottom
        self.footer_bar = WordlessFooter(id="wordless-footer")
        yield self.footer_bar

    # called when the app is created
    def on_mount(self) -> None:
        self._disconnecting = False
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
        if event.tab.id == "home":
            self.active_tab = ActiveTab.HOME
            self.home.display = True
            self.network.display = False
            self.editor.display = False
            self.footer_bar.clear()
        # if the user switched to the network tab
        # display the network screen
        elif event.tab.id == "network":
            self.active_tab = ActiveTab.NETWORK
            self.network.display = True
            self.home.display = False
            self.editor.display = False
            self.footer_bar.clear()
        # if the user switched to a file tab
        # load the contents of the file
        # open editor view
        else:
            self.active_tab = ActiveTab.EDITOR
            self.editor.display = True
            self.network.display = False
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
            self.footer_bar.show_editor_stats(loaded_content, "")

    # called whenever the textarea's value changes
    def on_text_area_changed(self) -> None:
        self.files[self.current_filename] = self.textarea.text  # update files dict
        md_text = self.textarea.text.replace("\n", "  \n")  # handle new lines
        self.markdown.update(md_text)
        # if hosting a file, send the updated content to the client
        if self.network.event_button_state == NetworkEventButtonState.CLOSE_HOST:
            network.send_data(self.host_conn, self.files[self.host_file])
        self.footer_bar.show_editor_stats(
            self.textarea.text, self.textarea.selected_text
        )

    # called whenever the textarea's selection changes
    def on_text_area_selection_changed(self, event: TextArea.SelectionChanged) -> None:
        if hasattr(self, "active_tab") and self.active_tab == ActiveTab.EDITOR:
            self.footer_bar.show_editor_stats(
                self.textarea.text, self.textarea.selected_text
            )

    # method to reset to the home screen
    # the UI state is changed often
    # this method entirely changes it back to the home screen's state
    def return_home(self) -> None:
        self.home.text_input.display = False
        self.home.text_input.value = ""
        self.home.event_button.display = False
        self.home.status_label.display = False
        self.home.files_label.display = False
        self.home.cancel_button.display = False
        self.home.event_button_state = EventButtonState.NONE
        self.home.reset_buttons()

    # method to reset to the network page
    # the UI state is changed often
    # this method entirely changes it back to the network page's state
    def return_network_page(self) -> None:
        self.network.mode_row.display = True
        self.network.conn_input.display = False
        self.network.conn_input.value = ""
        self.network.status_label.display = False
        self.network.cancel_button.display = False
        self.network.event_button.display = False
        self.network.disconnect_button.display = False
        self.network.done_button.display = False
        self.network.received_header.display = False
        self.network.markdown.display = False
        self.network.event_button_state = NetworkEventButtonState.NONE
        self.footer_bar.set_share_status(False)

    def _on_conn_closed(self, message: str) -> None:
        self.network.status_label.update(message)
        self.network.status_label.display = True
        self.network.event_button.display = False
        self.network.disconnect_button.display = False
        self.network.done_button.display = True
        self.footer_bar.set_share_status(False)

    @work(thread=True)
    def _connect_client(self, input_host: str, input_port: int) -> None:
        # --- connection phase ---
        self._disconnecting = False
        try:
            self.client = network.Client(input_host, input_port)
            self.client_conn = self.client.run()
        except Exception:
            if not self._disconnecting:
                self.call_from_thread(
                    self.network.status_label.update,
                    f"Could not connect to host on {input_host}:{input_port}",
                )
                self.call_from_thread(
                    setattr, self.network.status_label, "display", True
                )
            return

        # update UI on successful connection
        self.call_from_thread(self.network.status_label.update, "Connected to host")
        self.call_from_thread(setattr, self.network.status_label, "display", True)
        self.call_from_thread(setattr, self.network.conn_input, "display", False)
        self.call_from_thread(setattr, self.network.cancel_button, "display", False)
        self.call_from_thread(setattr, self.network.event_button, "display", False)
        self.call_from_thread(setattr, self.network.received_header, "display", True)
        self.call_from_thread(setattr, self.network.markdown, "display", True)
        self.call_from_thread(setattr, self.network.disconnect_button, "display", True)

        # --- receive phase ---
        try:
            while True:
                self.data = network.get_data(self.client_conn)
                if self.data == "":
                    # empty recv means the host closed the connection
                    if not self._disconnecting:
                        self.call_from_thread(
                            self._on_conn_closed, "Connection closed by host"
                        )
                    break
                self.call_from_thread(self.network.markdown.update, self.data)
        except Exception:
            # any socket error during receive means the host dropped the connection
            if not self._disconnecting:
                self.call_from_thread(self._on_conn_closed, "Connection closed by host")
        finally:
            if hasattr(self, "client") and self.client:
                self.client.close()

    @work(thread=True)
    def _monitor_host_conn(self) -> None:
        try:
            while True:
                data = network.get_data(self.host_conn)
                if data == "":
                    # empty recv means the client closed the connection
                    if not self._disconnecting:
                        self.call_from_thread(
                            self._on_conn_closed, "Connection closed by client"
                        )
                    break
        except Exception:
            if not self._disconnecting:
                self.call_from_thread(
                    self._on_conn_closed, "Connection closed by client"
                )

    # called when a button is pressed
    def on_button_pressed(self, event: Button.Pressed) -> None:
        # button functions for the home tab

        if self.active_tab == ActiveTab.HOME:
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

                # the previous condition checks for an empty input box
                # if it is passed, the input box contains text
                # the content of this text is not validated, that is handled by individual methods

                if state == EventButtonState.CREATE:
                    # if the file already exists
                    if self.home.text_input.value in list(self.files.keys()):
                        self.home.status_label.display = True
                        self.home.status_label.update(
                            "File with this name already exists"
                        )
                        return
                    # if the file name is invalid
                    if (
                        re.search(r"[^A-Za-z0-9 ]", self.home.text_input.value)
                        or self.home.text_input.value == "home"
                        or self.home.text_input.value == "network"
                    ):
                        self.home.status_label.display = True
                        self.home.status_label.update("Invalid file name")
                        return
                    # nothing is wrong, create the file
                    else:
                        self.files[self.home.text_input.value] = ""
                        file_manager.save_files(self.files)  # save the new file
                        # add a new tab to the tab bar
                        self.tabs.add_tab(
                            Tab(
                                self.home.text_input.value,
                                id=self.home.text_input.value.replace(" ", "-"),
                            )
                        )
                        success = True
                elif state == EventButtonState.SELECT_RENAME:
                    if self.home.text_input.value not in list(self.files.keys()):
                        self.home.status_label.display = True
                        self.home.status_label.update(
                            "File with this name doesn't exist"
                        )
                        return
                    self.rename_from = self.home.text_input.value
                    self.home.text_input.value = ""
                    self.home.text_input.placeholder = "New file name"
                    self.home.event_button.label = "Rename"
                    self.home.event_button_state = EventButtonState.RENAME
                    self.home.status_label.display = False
                elif state == EventButtonState.RENAME:
                    new_name = self.home.text_input.value
                    if new_name in list(self.files.keys()):
                        self.home.status_label.display = True
                        self.home.status_label.update(
                            "File with this name already exists"
                        )
                        return
                    if (
                        # use regex to check for invalid characters
                        # if there are characters that aren't letters or numbers, the file name is invalid
                        re.search(r"[^A-Za-z0-9 ]", new_name)
                        or new_name == "home"
                        or new_name == "network"
                    ):
                        self.home.status_label.display = True
                        self.home.status_label.update("Invalid file name")
                        return
                    self.files[new_name] = self.files.pop(self.rename_from)
                    file_manager.save_files(
                        self.files
                    )  # save the file with the new name
                    # change the name of the tab
                    self.tabs.remove_tab(self.rename_from.replace(" ", "-"))
                    self.tabs.add_tab(Tab(new_name, id=new_name.replace(" ", "-")))
                    success = True
                elif state == EventButtonState.DELETE:
                    # if the file doesn't exist
                    if self.home.text_input.value not in list(self.files.keys()):
                        self.home.status_label.display = True
                        self.home.status_label.update(
                            "File with this name doesn't exist"
                        )
                        return
                    # nothing is wrong, delete the file
                    else:
                        del self.files[self.home.text_input.value]
                        file_manager.save_files(self.files)
                        self.tabs.remove_tab(
                            self.home.text_input.value.replace(" ", "-")
                        )
                        success = True
                elif state == EventButtonState.SUCCESS:
                    self.return_home()

                # if the operation was successful, change the UI state
                # once the button is pressed again,
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
                self.home.files_label.update(
                    "Files: " + ", ".join(list(self.files.keys()))
                )
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
                    self.home.event_button_state = EventButtonState.SELECT_RENAME
                elif event.button.id == "delete":
                    self.home.text_input.placeholder = "Name of file to delete"
                    self.home.event_button.label = "Delete"
                    self.home.event_button_state = EventButtonState.DELETE

        # button functions for the network tab

        elif self.active_tab == ActiveTab.NETWORK:
            if event.button.id == "network_event":
                state = self.network.event_button_state

                # checks if input box is empty or just whitespace
                if self.network.conn_input.value.strip() == "":
                    self.network.status_label.display = True
                    self.network.status_label.update("Please enter a value")
                    return

                # the previous condition checks for an empty input box
                # if it is passed, the input box contains text
                # the content of this text is not validated, that is handled by individual methods

                if state == NetworkEventButtonState.HOST_FILE:
                    # the user first must choose a file to host
                    if self.network.conn_input.value not in list(self.files.keys()):
                        self.network.status_label.display = True
                        self.network.status_label.update("File doesn't exist")
                        return
                    # store the file to be hosted in a variable so it can be accessed by other methods
                    self.host_file = self.network.conn_input.value
                    # change UI state
                    self.network.event_button_state = NetworkEventButtonState.HOST_CONN
                    self.network.conn_input.value = ""
                    self.network.conn_input.placeholder = "Port Number"
                    self.network.event_button.label = "Host"

                elif state == NetworkEventButtonState.HOST_CONN:
                    # check if port number is an int
                    self._disconnecting = False
                    try:
                        # host file
                        port = int(self.network.conn_input.value)
                        self.network.status_label.display = True
                        self.network.status_label.update(
                            f"Hosting {self.host_file} on {network.HOST}:{port}"
                        )
                        self.host = network.Host(network.HOST, port)
                        self.host_conn = self.host.run()
                        # change UI state
                        # changes buttons so that user can close connection
                        self.network.event_button_state = (
                            NetworkEventButtonState.CLOSE_HOST
                        )
                        self.network.conn_input.display = False
                        self.network.cancel_button.display = False
                        self.network.event_button.label = "Close Connection"
                        # send data
                        network.send_data(self.host_conn, self.files[self.host_file])
                        self.footer_bar.set_share_status(True, self.host_file)
                        # monitor connection for client disconnect
                        self._monitor_host_conn()
                    except ValueError:
                        self.network.status_label.display = True
                        self.network.status_label.update("Port must be a number")
                        return
                    except OSError as e:
                        # error 98: port already in use
                        if e.errno == 98:
                            self.network.status_label.display = True
                            self.network.status_label.update("Port already in use")

                elif state == NetworkEventButtonState.CLOSE_HOST:
                    self._disconnecting = True
                    try:
                        self.host_conn.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    self.host_conn.close()
                    self.host.close()
                    self.return_network_page()

                elif state == NetworkEventButtonState.JOIN:
                    if ":" not in self.network.conn_input.value:
                        self.network.status_label.display = True
                        self.network.status_label.update("Invalid format, needs a ':'")
                        return
                    input_host, input_port = self.network.conn_input.value.split(":")
                    self._client_worker = self._connect_client(
                        input_host, int(input_port)
                    )

            elif event.button.id == "network_disconnect":
                self._disconnecting = True
                if hasattr(self, "_client_worker"):
                    self._client_worker.cancel()
                if hasattr(self, "client") and self.client:
                    self.client.close()
                self.return_network_page()

            elif event.button.id == "network_done":
                self.return_network_page()

            elif event.button.id == "network_cancel":
                self.return_network_page()

            else:
                self.network.mode_row.display = False
                self.network.conn_input.display = True
                self.network.conn_input.focus()
                self.network.cancel_button.display = True
                self.network.event_button.display = True
                if event.button.id == "host":
                    self.network.conn_input.placeholder = "Name of file to host"
                    self.network.event_button.label = "Choose File"
                    self.network.event_button_state = NetworkEventButtonState.HOST_FILE
                elif event.button.id == "join":
                    self.network.conn_input.placeholder = "IP Address : Port Number"
                    self.network.event_button.label = "Join"
                    self.network.event_button_state = NetworkEventButtonState.JOIN

        self.set_focus(None)


# runs the app
if __name__ == "__main__":
    app = Wordless()
    app.run()
