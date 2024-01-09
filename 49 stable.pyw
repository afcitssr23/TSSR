import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton,
    QFileDialog, QDialog, QLineEdit, QLabel, QMenu, QAction, QColorDialog,
    QStyleFactory, QStyle, QInputDialog, QMessageBox)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QSettings, QSize, QPoint, Qt, pyqtSignal, QEvent
import keyboard
import time
import subprocess
import os

class ButtonConfig:
    def __init__(self, program_path="", button_number="", button_name="", hotkey="", color="red"):
        self.program_path = program_path
        self.button_number = button_number
        self.button_name = button_name
        self.hotkey = hotkey
        self.color = color

class ButtonConfigDialog(QDialog):
    def __init__(self, parent=None):
        super(ButtonConfigDialog, self).__init__(parent)

        self.program_path = ""
        self.button_number = ""
        self.button_name = ""
        self.hotkey = ""

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Button Configuration")
        self.setGeometry(100, 100, 400, 200)

        layout = QGridLayout()

        button_number_label = QLabel("Button Number:")
        layout.addWidget(button_number_label, 0, 0)

        button_name_label = QLabel("Button Name:")
        layout.addWidget(button_name_label, 1, 0)

        hotkey_label = QLabel("Hotkey:")
        layout.addWidget(hotkey_label, 2, 0)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_program)
        layout.addWidget(self.browse_button, 3, 0, 1, 2)

        self.button_number_input = QLineEdit()
        layout.addWidget(self.button_number_input, 0, 1)

        self.button_name_input = QLineEdit()
        layout.addWidget(self.button_name_input, 1, 1)

        self.hotkey_input = QLineEdit()
        layout.addWidget(self.hotkey_input, 2, 1)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button, 4, 0, 1, 2)

        self.setLayout(layout)

    def browse_program(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()
            if selected_file:
                self.program_path = selected_file[0]

class RemoveButtonDialog(QDialog):
    def __init__(self, parent=None):
        super(RemoveButtonDialog, self).__init__(parent)

        self.button_number = ""

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Remove Button Data")
        self.setGeometry(100, 100, 400, 150)

        layout = QVBoxLayout()

        button_number_label = QLabel("Button Number:")
        layout.addWidget(button_number_label)

        self.button_number_input = QLineEdit()
        layout.addWidget(self.button_number_input)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_button_number(self):
        return self.button_number_input.text()

class EditButtonDialog(QDialog):
    def __init__(self, config, parent=None):
        super(EditButtonDialog, self).__init__(parent)

        self.config = config
        self.program_path = config.program_path
        self.button_number = config.button_number
        self.button_name = config.button_name
        self.hotkey = config.hotkey

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Edit Button {self.button_number}")
        self.setGeometry(100, 100, 400, 200)

        layout = QGridLayout()

        button_number_label = QLabel(f"Button Number: {self.button_number}")
        layout.addWidget(button_number_label, 0, 0, 1, 2)

        button_name_label = QLabel("Button Name:")
        layout.addWidget(button_name_label, 1, 0)

        hotkey_label = QLabel("Hotkey:")
        layout.addWidget(hotkey_label, 2, 0)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_program)
        layout.addWidget(self.browse_button, 3, 0, 1, 2)

        self.button_name_input = QLineEdit()
        self.button_name_input.setText(self.button_name)
        layout.addWidget(self.button_name_input, 1, 1)

        self.hotkey_input = QLineEdit()
        self.hotkey_input.setText(self.hotkey)
        layout.addWidget(self.hotkey_input, 2, 1)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button, 4, 0, 1, 2)

        self.setLayout(layout)

    def browse_program(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()
            if selected_file:
                self.program_path = selected_file[0]

class ButtonManager(QWidget):
    hotkeyPressed = pyqtSignal(str)
    windowStateChanged = pyqtSignal(Qt.WindowStates)

    def __init__(self):
        super(ButtonManager, self).__init__()

        self.button_configs = {}

        self.init_ui()
        self.load_config()

        self.last_hotkey_press_time = 0

    def init_ui(self):
        self.setWindowTitle('Button Manager')
        self.setGeometry(100, 100, 800, 400)

        self.button_layout = QGridLayout()

        for i in range(1, 49):  # Modified this line to create 48 buttons
            self.create_button(i, buttons_per_row=6)

        add_modify_button = QPushButton("Add/Modify Button")
        remove_button = QPushButton("Remove Button")
        open_computer_button = QPushButton("Open Computer")
        open_computer_button.clicked.connect(self.open_computer)
        open_explorer_button = QPushButton("Open File Explorer")
        open_explorer_button.clicked.connect(self.open_file_explorer)

        add_modify_button.clicked.connect(self.show_add_button_dialog)
        remove_button.clicked.connect(self.show_remove_button_dialog)

        layout = QVBoxLayout()
        layout.addLayout(self.button_layout)
        layout.addWidget(add_modify_button)
        layout.addWidget(remove_button)
        layout.addWidget(open_computer_button)
        layout.addWidget(open_explorer_button)

        menu = QMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        customize_main_window_action = QAction("Customize Main Window Color", self)
        customize_main_window_action.triggered.connect(self.show_customize_main_window_dialog)
        menu.addAction(customize_main_window_action)

        self.setLayout(layout)

        self.keyboard_hook = keyboard.hook(self.handle_hotkey)
        self.hotkeyPressed.connect(self.handle_hotkey_press)
        self.windowStateChanged.connect(self.handle_window_state_changed)

    def create_button(self, i, buttons_per_row):
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)

        number_label = QLabel(f"{i}")
        number_label.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(number_label)

        button = QPushButton(f"Button {i}")
        button.clicked.connect(lambda _, num=i: self.show_button_config(num))
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(lambda point, num=i: self.show_context_menu(point, num))

        button_layout.addWidget(button)

        row, col = divmod(i - 1, buttons_per_row)
        self.button_layout.addWidget(button_widget, row, col)

    def show_context_menu(self, point, button_number):
        menu = QMenu(self)
        config = self.button_configs.get(button_number)

        if config:
            edit_action = QAction("Edit", self)
            customize_action = QAction("Customize", self)
            remove_action = QAction("Remove", self)
            customize_main_window_action = QAction("Customize Main Window", self)
            set_button_action = QAction("Set Button", self)
            copy_path_action = QAction("Copy Path", self)

            edit_action.triggered.connect(lambda _, cfg=config: self.show_edit_dialog(cfg))
            customize_action.triggered.connect(lambda _, cfg=config: self.show_customize_dialog(cfg))
            remove_action.triggered.connect(lambda _, num=button_number: self.remove_button_data(num))
            customize_main_window_action.triggered.connect(self.show_customize_main_window_dialog)
            set_button_action.triggered.connect(lambda _, num=button_number: self.show_set_button_dialog(num))
            copy_path_action.triggered.connect(lambda _, cfg=config: self.copy_path_to_clipboard(cfg))

            menu.addAction(edit_action)
            menu.addAction(customize_action)
            menu.addAction(remove_action)
            menu.addSeparator()
            menu.addAction(customize_main_window_action)
            menu.addAction(set_button_action)
            menu.addAction(copy_path_action)

        else:
            add_action = QAction("Add Button", self)
            set_button_action = QAction("Set Button", self)

            add_action.triggered.connect(self.show_add_button_dialog)

            # Disable the "Set Button" action for unconfigured buttons
            set_button_action.setEnabled(False)

            menu.addAction(add_action)
            menu.addAction(set_button_action)

        # Adjust the point to be above the right-clicked button
        row, col = divmod(button_number - 1, 6)  # Adjusted for 6 buttons per row
        button_widget = self.button_layout.itemAtPosition(row, col).widget()
        adjusted_point = button_widget.mapToGlobal(button_widget.rect().topRight())

        menu.exec_(adjusted_point)

    def set_button_text(self, button_number):
        row, col = divmod(button_number - 1, 6)  # Adjusted for 6 buttons per row
        button_widget = self.button_layout.itemAtPosition(row, col).widget()

        if button_widget:
            button = button_widget.findChild(QPushButton)
            if button_number in self.button_configs:
                config = self.button_configs[button_number]
                button.setText(config.button_name if config.button_name else f"Button {button_number}")
                button.setStyleSheet(f"background-color: {config.color};")
            else:
                button.setText(f"Button {button_number}")

    def show_button_config(self, button_number):
        if button_number in self.button_configs:
            config = self.button_configs[button_number]
            self.execute_program(config.program_path)
        else:
            print(f"No configuration for button {button_number}")

    def show_add_button_dialog(self):
        keyboard.unhook_all()

        dialog = ButtonConfigDialog(self)
        result = dialog.exec_()

        self.keyboard_hook = keyboard.hook(self.handle_hotkey)

        if result == QDialog.Accepted:
            button_number_text = dialog.button_number_input.text()
            try:
                button_number = int(button_number_text)
            except ValueError:
                print(f"Invalid button number: {button_number_text}")
                return

            config = ButtonConfig(
                program_path=dialog.program_path,
                button_number=button_number,
                button_name=dialog.button_name_input.text(),
                hotkey=dialog.hotkey_input.text()
            )

            self.button_configs[int(config.button_number)] = config
            self.save_config()
            self.set_button_text(int(config.button_number))

    def show_remove_button_dialog(self):
        keyboard.unhook_all()

        dialog = RemoveButtonDialog(self)
        result = dialog.exec_()

        self.keyboard_hook = keyboard.hook(self.handle_hotkey)

        if result == QDialog.Accepted:
            button_number = dialog.get_button_number()
            if button_number:
                button_number = int(button_number)
                if button_number in self.button_configs:
                    del self.button_configs[button_number]
                    self.set_button_text(button_number)
                    self.save_config()

    def show_edit_dialog(self, config):
        keyboard.unhook_all()

        dialog = EditButtonDialog(config, self)
        result = dialog.exec_()

        self.keyboard_hook = keyboard.hook(self.handle_hotkey)

        if result == QDialog.Accepted:
            config.button_name = dialog.button_name_input.text()
            config.hotkey = dialog.hotkey_input.text()
            config.program_path = dialog.program_path
            self.save_config()
            self.set_button_text(int(config.button_number))

    def show_customize_dialog(self, config):
        color_dialog = QColorDialog.getColor(QColor(config.color), self)
        if color_dialog.isValid():
            config.color = color_dialog.name()
            self.save_config()
            self.set_button_text(int(config.button_number))

    def show_customize_main_window_dialog(self):
        color_dialog = QColorDialog.getColor(self.palette().color(QPalette.Window), self)
        if color_dialog.isValid():
            self.setStyleSheet(f"background-color: {color_dialog.name()};")
            self.save_main_window_config()

    def show_set_button_dialog(self, button_number=None):
        if button_number is None:
            button_number, ok = QInputDialog.getInt(self, "Set Button", "Enter button number:")
            if not ok or not (1 <= button_number <= 60):  # Adjusted for 60 buttons
                return

        config = self.button_configs.get(button_number, ButtonConfig())
        dialog = EditButtonDialog(config, self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            config.button_name = dialog.button_name_input.text()
            config.hotkey = dialog.hotkey_input.text()
            config.program_path = dialog.program_path
            self.save_config()
            self.set_button_text(int(config.button_number))

    def remove_button_data(self, button_number):
        if button_number in self.button_configs:
            del self.button_configs[button_number]
            self.set_button_text(button_number)
            self.save_config()

    def copy_path_to_clipboard(self, config):
        clipboard = QApplication.clipboard()
        clipboard.setText(config.program_path)

    def open_computer(self):
        try:
            os.startfile("::{20D04FE0-3AEA-1069-A2D8-08002B30309D}")  # This opens Computer
        except Exception as e:
            print(f"Error opening Computer: {e}")

    def open_file_explorer(self):
        try:
            os.startfile(os.path.expanduser("~"))  # This opens File Explorer
        except Exception as e:
            print(f"Error opening File Explorer: {e}")

    def save_config(self):
        settings = QSettings("config.ini", QSettings.IniFormat)

        settings.clear()

        for button_number, config in self.button_configs.items():
            settings.beginGroup(f"Button{button_number}")
            settings.setValue("ProgramPath", config.program_path)
            settings.setValue("ButtonName", config.button_name)
            settings.setValue("Hotkey", config.hotkey)
            settings.setValue("Color", config.color)
            settings.endGroup()

        settings.beginGroup("MainWindow")
        settings.setValue("Size", self.size())
        settings.setValue("Position", self.pos())
        main_window_color = self.palette().color(QPalette.Window)
        settings.setValue("MainWindowColor", main_window_color.name())
        settings.endGroup()

    def load_config(self):
        settings = QSettings("config.ini", QSettings.IniFormat)

        for button_number in range(1, 61):  # Adjusted for 60 buttons
            settings.beginGroup(f"Button{button_number}")
            program_path = settings.value("ProgramPath", "")
            button_name = settings.value("ButtonName", "")
            hotkey = settings.value("Hotkey", "")
            color = settings.value("Color", "red")
            settings.endGroup()

            if program_path and button_name and hotkey:
                config = ButtonConfig(program_path, str(button_number), button_name, hotkey, color)
                self.button_configs[int(button_number)] = config
                self.set_button_text(int(button_number))
            else:
                self.button_configs.pop(int(button_number), None)

        self.load_main_window_config()

    def save_main_window_config(self):
        settings = QSettings("config.ini", QSettings.IniFormat)
        settings.beginGroup("MainWindow")
        settings.setValue("Size", self.size())
        settings.setValue("Position", self.pos())
        main_window_color = self.palette().color(QPalette.Window)
        settings.setValue("MainWindowColor", main_window_color.name())
        settings.endGroup()

    def load_main_window_config(self):
        settings = QSettings("config.ini", QSettings.IniFormat)
        settings.beginGroup("MainWindow")

        size = settings.value("Size", QSize(800, 400))
        position = settings.value("Position", QPoint(100, 100))
        main_window_color = QColor(settings.value("MainWindowColor", "#ffffff"))  # Default to white

        self.resize(size)
        self.move(position)
        self.setStyleSheet(f"background-color: {main_window_color.name()};")

        settings.endGroup()

    def handle_hotkey(self, event):
        current_time = time.time()
        if current_time - self.last_hotkey_press_time < 0.5:
            return

        if not self.isActiveWindow():
            return

        self.last_hotkey_press_time = current_time

        for config in self.button_configs.values():
            if event.name == config.hotkey:
                self.hotkeyPressed.emit(config.program_path)

    def handle_hotkey_press(self, program_path):
        self.execute_program(program_path)

    def execute_program(self, file_path):
        try:
            os.startfile(file_path)
        except Exception as e:
            print(f"Error opening file: {e}")

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            self.windowStateChanged.emit(self.windowState())
        super().changeEvent(event)

    def handle_window_state_changed(self, state):
        if state == Qt.WindowMinimized:
            keyboard.unhook_all()
        elif state == Qt.WindowNoState:
            self.keyboard_hook = keyboard.hook(self.handle_hotkey)

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = ButtonManager()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
