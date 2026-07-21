from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QSizePolicy,
    QProgressBar,
    QLabel,
    QSpinBox,
    QToolButton,
    QMenu,
    QVBoxLayout,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QTextEdit,
    QWidget
)
from objects import TaskObject
from . import SubtaskWidget

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
        self.task_obj.subtasksChanged.connect(self.on_subtasks_changed)
        self.task_obj.subtaskAdded.connect(self.on_subtask_added)
        self.task_obj.subtaskRemoved.connect(self.on_subtask_removed)

        # Widgets
        self.title_label = QLabel(wordWrap=True, text=self.task_obj.title)
        self.description_label = QLabel(wordWrap=True, text=self.task_obj.description)
        self.progress_bar = QProgressBar(value=self.task_obj.progress)

        # Action menu
        # self.action_button = QToolButton(
        #     popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
        #     arrowType=Qt.ArrowType.DownArrow,
        #     toolButtonStyle=Qt.ToolButtonStyle.ToolButtonIconOnly
        # )
        # self.action_button.setStyleSheet("QToolButton::menu-indicator { image: none; }") # Removes redundant built-in dropdown icon
        self.action_button = QPushButton("Actions")
        self.action_menu = QMenu(self)
        self.action_button.setMenu(self.action_menu)
        self.populate_action_menu()

        # Subtasks section
        self.subtasks = QWidget(visible=False)
        self.subtasks_layout = QVBoxLayout(self.subtasks)

        self.subtasks_button = QPushButton("Subtasks")
        self.subtasks_button.clicked.connect(lambda *_: self.show_or_hide_subtasks())

        self.add_subtask_button = QPushButton("Add subtask")
        self.add_subtask_button.clicked.connect(lambda *_: self.add_subtask())
        self.subtasks_layout.addWidget(self.add_subtask_button)
        self.populate_subtasks()

        # Putting all the widgets together
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.addWidget(self.title_label)
        self.widget_layout.addWidget(self.description_label)
        self.widget_layout.addWidget(self.progress_bar)
        self.widget_layout.addWidget(self.action_button)
        self.widget_layout.addWidget(self.subtasks_button)
        self.widget_layout.addWidget(self.subtasks)

        # Widget styling
        self.title_label.setStyleSheet(" * { font-weight: bold; } ")
        self.description_label.setStyleSheet(" * { font-style: italic; } ")

        # self.setStyleSheet(" QLabel { background-color: green; } ")

        # Initial widgets visibility setup
        if len(self.task_obj.description) == 0:
            self.description_label.setVisible(False)
        if self.task_obj.location != "in_progress":
            self.progress_bar.setVisible(False)
            self.set_subtasks_checkable(False)

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
            self.set_subtasks_checkable(False)
        else:
            self.progress_bar.setVisible(True)
            self.set_subtasks_checkable(True)

    def on_progress_updated(self, new_progress: int):
        self.progress_bar.setValue(new_progress)

    def on_subtasks_changed(self, subtasks):
        self.populate_subtasks()

    def on_subtask_added(self, id, data):
        # self.add_subtask(subtask_id=id, subtask_data=data, populate=True)
        # Adds it again so redundant ^^^
        pass

    def on_subtask_removed(self, subtask_data):
        pass

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

    def on_subtask_delete_self_request(self, subtask: SubtaskWidget):
        del self.task_obj.subtasks[subtask.id]
        self.editSubmitRequest.emit(self.task_obj)

    def on_subtask_save_request(self, subtask: dict):
        self.task_obj.subtasks[subtask["id"]] = {"text": subtask["text"], "completed": subtask["completed"]}
        self.editSubmitRequest.emit(self.task_obj)

    def edit_task(self):
        dialog = QDialog()
        dialog_layout = QVBoxLayout(dialog)

        title_field = QLineEdit(text=self.task_obj.get_title(), placeholderText="Enter new title here...")
        progress_field = QSpinBox(value=self.task_obj.progress, minimum=0, maximum=100)
        description_field = QTextEdit(text=self.task_obj.get_description(), placeholderText="Enter new description here...")

        dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        def on_apply():
            self.task_obj.title = title_field.text().strip()
            self.task_obj.progress = progress_field.value()
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
        dialog_layout.addWidget(QLabel("Progress:"))
        dialog_layout.addWidget(progress_field)
        dialog_layout.addWidget(dialog_buttons)

        dialog.exec()

    def show_or_hide_subtasks(self):
        self.subtasks.setVisible(not self.subtasks.isVisible())

    def add_subtask(self, subtask_id=None, subtask_data=None, populate=False):
        checkable = False
        if self.task_obj.location == "in_progress":
            checkable = True

        all_subtask_ids = list(self.task_obj.subtasks.keys())

        if len(all_subtask_ids) > 0:
            last_id = all_subtask_ids[-1]
        else:
            last_id = -1

        if last_id != subtask_id or (last_id == subtask_id and populate):
            new_id = "0"
            if subtask_id is not None and type(subtask_id) is str:
                new_id = subtask_id
            elif len(self.task_obj.subtasks.keys()) > 0:
                new_id = str(int(last_id)+1)

            subtask_widget = SubtaskWidget(
                id=new_id if subtask_id is None else subtask_id,
                text="Change me" if subtask_data is None else subtask_data["text"],
                completed=False if subtask_data is None else subtask_data["completed"],
                edit_mode=not populate,
                checkable=checkable
            )

            subtask_widget.deleteSelfRequest.connect(self.on_subtask_delete_self_request)
            subtask_widget.saveRequest.connect(self.on_subtask_save_request)

            if subtask_data is None:
                subtask_data = {
                    "text": subtask_widget.text,
                    "completed": subtask_widget.completed
                }

            subtask_added = False
            index = self.subtasks_layout.count()
            while index >= 0:
                if type(self.subtasks_layout.itemAt(index)) is QPushButton:
                    self.subtasks_layout.insertWidget(index, subtask_widget)
                    subtask_added = True
                    break
                index-=1

            if not subtask_added:
                self.subtasks_layout.insertWidget(index, subtask_widget)

            if not populate:
                self.task_obj.add_subtask(new_id, subtask_data)

    def reset_subtasks(self):
        for index in reversed(range(self.subtasks_layout.count())):
            item_to_remove = self.subtasks_layout.itemAt(index)
            if item_to_remove is not None:
                widget = item_to_remove.widget()
                if isinstance(widget, SubtaskWidget):
                    self.subtasks_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()

    def populate_subtasks(self):
        self.reset_subtasks()
        for id in list(self.task_obj.subtasks.keys()):
            self.add_subtask(id, self.task_obj.subtasks[id], populate=True)

    def set_subtasks_checkable(self, arg: bool):
        for index in reversed(range(self.subtasks_layout.count())):
            item_to_remove = self.subtasks_layout.itemAt(index)
            if item_to_remove is not None:
                widget = item_to_remove.widget()
                if isinstance(widget, SubtaskWidget):
                    widget.checkbox.setVisible(arg)
