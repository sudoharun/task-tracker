from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QSizePolicy, QProgressBar, QLabel, QToolButton, QMenu, QVBoxLayout, QDialog, QDialogButtonBox, QLineEdit, QTextEdit
from objects import TaskObject, DataObject

class TaskWidget(QFrame):
    editSubmitRequest = Signal(TaskObject)
    locationChangeRequest = Signal(QFrame, str, str)
    deleteSelfRequest = Signal(QFrame, str)

    def __init__(self, **task_data):
        super().__init__(frameShape=QFrame.Shape.StyledPanel, frameShadow=QFrame.Shadow.Raised)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # Setup task object and connectors, location change is handled by parent to move between other layouts
        self.task_obj = TaskObject(**task_data)
        self.task_obj.titleChanged.connect(self.on_title_updated)
        self.task_obj.descriptionChanged.connect(self.on_description_updated)
        self.task_obj.locationChanged.connect(self.on_location_updated)
        self.task_obj.progressChanged.connect(self.on_progress_updated)

        # Widgets
        self.title_label = QLabel(wordWrap=True, text=self.task_obj.title)
        self.description_label = QLabel(wordWrap=True, text=self.task_obj.description)
        self.progress_bar = QProgressBar(value=self.task_obj.progress)

        # Action menu
        self.action_button = QToolButton(
            popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
            arrowType=Qt.ArrowType.DownArrow,
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        self.action_button.setStyleSheet("QToolButton::menu-indicator { image: none; }") # Removes redundant built-in dropdown icon
        self.action_menu = QMenu(self)
        self.action_button.setMenu(self.action_menu)
        self.populate_action_menu()

        # Putting all the widgets together
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.addWidget(self.title_label)
        self.widget_layout.addWidget(self.description_label)
        self.widget_layout.addWidget(self.progress_bar)
        self.widget_layout.addWidget(self.action_button)

        # Widget styling
        self.title_label.setStyleSheet(" * { font-weight: bold; } ")
        self.description_label.setStyleSheet(" * { font-style: italic; } ")

        # self.setStyleSheet(" QLabel { background-color: green; } ")

        # Initial widgets visibility setup
        if len(self.task_obj.description) == 0:
            self.description_label.setVisible(False)
        if self.task_obj.location != "in_progress":
            self.progress_bar.setVisible(False)

    def on_title_updated(self, new_title: str):
        self.title_label.setText(new_title)

    def on_description_updated(self, new_description: str):
        self.description_label.setText(new_description)
        if len(new_description) == 0:
            self.description_label.setVisible(False)
        else:
            self.description_label.setVisible(True)

    def on_location_updated(self, new_location: str):
        self.populate_action_menu()
        if new_location != "in_progress":
            self.progress_bar.setVisible(False)
        else:
            self.progress_bar.setVisible(True)

    def on_progress_updated(self, new_progress: int):
        self.progress_bar.setValue(new_progress)

    def populate_action_menu(self):
        self.action_menu.clear()

        def on_delete_request():
            self.deleteSelfRequest.emit(self, self.task_obj.location)

        self.action_menu.addAction("Edit task...", self.edit_task)
        self.action_menu.addAction("Delete task", on_delete_request)

        locations = {
            "Planned": "planned",
            "In Progress": "in_progress",
            "Completed": "completed",
            "Cancelled": "cancelled"
        }
        locations_menu = QMenu("Move task to...")

        def update_location(new_location: str):
            old_location = self.task_obj.location
            self.task_obj.location = new_location
            self.locationChangeRequest.emit(self, old_location, new_location)

        for title, location in locations.items():
            if location != self.task_obj.location:
                locations_menu.addAction(title, lambda location=location: update_location(location))

        self.action_menu.addMenu(locations_menu)

    def edit_task(self):
        dialog = QDialog()
        dialog_layout = QVBoxLayout(dialog)

        title_field = QLineEdit(text=self.task_obj.get_title(), placeholderText="Enter new title here...")
        description_field = QTextEdit(text=self.task_obj.get_description(), placeholderText="Enter new description here...")

        dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        def on_apply():
            self.task_obj.title = title_field.text().strip()
            self.task_obj.description = description_field.toPlainText()
            self.editSubmitRequest.emit(self.task_obj)
            dialog.close()

        def on_cancel():
            dialog.close()

        dialog_buttons.accepted.connect(on_apply)
        dialog_buttons.rejected.connect(on_cancel)

        dialog_layout.addWidget(QLabel("Title:"))
        dialog_layout.addWidget(title_field)
        dialog_layout.addWidget(QLabel("Description:"))
        dialog_layout.addWidget(description_field)
        dialog_layout.addWidget(dialog_buttons)

        dialog.exec()
