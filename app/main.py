import json
from PySide6.QtCore import Property, QObject, Qt, QSize, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QLineEdit,
    QMainWindow,
    QMenu,
    QTextEdit,
    QToolButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QScrollArea,
    QLabel
)

app = QApplication()

# To Do:
# - Add label when task area is empty, more visually pleasing
# - Add progress bar for in-progress and cancelled tasks
# - Add (potentially colour-coded) priorities

class DataObject(QObject):
    dataChanged = Signal(dict)

    def __init__(self, data=None):
        super().__init__()

        self._data = data or {}

    def load_data(self):
        with open("tasks.json", "r") as f:
            try:
                data = json.load(f)
            except:
                data = {}

        self._data = data
        return self._data

    def save_data(self, new_dataset=None):
        try:
            if new_dataset is not None:
                self._data = new_dataset
            self.dataChanged.emit(self._data)
            with open("tasks.json", "w") as f:
                json.dump(self._data, f)
            return self._data
        except Exception as e:
            print(e)
            raise SystemExit()

    def add_or_edit_task(self, id: str, task: dict):
        self._data[id] = task
        self.save_data()

    def delete_task(self, id: str):
        del self._data[id]
        self.save_data()

    data = Property(dict, load_data, save_data, notify=dataChanged)

class Task(QFrame):
    # Name and description kwargs, self-explanatory
    # task_widgets kwarg as a dictionary for move to functionality, gives actual widget and names for those widgets that the task can move itself into
    # parent_widget passed in due to no parent being assigned for whatever reason upon task creation
    def __init__(self, id="-1", name="", description="", task_widgets={}, parent_widget=None, location=None):
        super().__init__()

        # QFrame props
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        self.id = id
        self._name = ""
        self._description = ""
        self.task_widgets = task_widgets
        self.parent_widget = parent_widget or self.getParent() # No parent when it is created for some reason, breaks custom "move to" functionality
        self.setParent(self.parent_widget)
        self.location = location or "planned" # Makes it easier when saving data
        self.data_object = DataObject()
        self.data_object.load_data()

        # Task name and description labels setup
        self.name_widget = QLabel(name)
        self.name_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) # Sharing space with button, so give it as much space as possible
        self.name_widget.setWordWrap(True) # Prevents overflowing and creating a horizontal scroll, which isn't nice
        self.name_widget.setStyleSheet(" * { font-weight: bold;  } ")
        self.description_widget = QLabel(description)
        self.description_widget.setWordWrap(True)
        self.description_widget.setStyleSheet(" * { font-style: italic;  } ")

        self.set_name(name)
        self.set_description(description)

        # Container for name widget and button wih dropdown menu
        self.name_box = QWidget()
        self.name_box.layout = QHBoxLayout()
        self.name_box.setLayout(self.name_box.layout)
        self.name_box.layout.setContentsMargins(0, 0, 0, 0)
        self.name_box.layout.setSpacing(4)

        self.name_box.layout.addWidget(self.name_widget)

        # UI and Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.name_box)
        self.layout.addWidget(self.description_widget)

        # Button that opens menu which modifies the task
        menu_button = QToolButton()
        menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu_button.setArrowType(Qt.ArrowType.DownArrow)
        menu_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        menu_button.setStyleSheet("QToolButton::menu-indicator { image: none; }") # Removes redundant built-in dropdown icon
        self.popup_menu = QMenu(self)
        self.populate_menu()
        menu_button.setMenu(self.popup_menu)

        self.name_box.layout.addWidget(menu_button)

    def set_name(self, new_name: str): # Custom functionality, deletes task if no name nor description assigned
        self._name = new_name.strip()
        if len(self._name) <= 0 and len(self._description) <= 0:
            self.delete_self()
            self.data_object.delete_task(self.id)
        elif len(self._name) <= 0:
            self._name = "Default"

        self.name_widget.setText(self._name)

    def set_description(self, new_description: str): # Custom functionality, removes ugly space that's present when there is no text in description label
        self._description = new_description
        self.description_widget.setText(self._description)
        if len(self._description) <= 0:
            self.description_widget.setVisible(False)
        else:
            self.description_widget.setVisible(True)

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def delete_self(self, *_):
        self.deleteLater()
        self.data_object.delete_task(self.id)

    def edit_task(self, *_): # Opens separate window dialog, in which user can edit task name and description
        dialog = QDialog()
        dialog_layout = QVBoxLayout()
        dialog.setLayout(dialog_layout)

        dialog_layout.addWidget(QLabel("Task Title:"))
        title_edit = QLineEdit()
        title_edit.setPlaceholderText("Enter the title of the task here...")
        title_edit.setText(self._name)
        dialog_layout.addWidget(title_edit)

        dialog_layout.addWidget(QLabel("Task Description:"))
        description_edit = QTextEdit()
        description_edit.setPlaceholderText("Enter the description of the task here...")
        description_edit.setText(self._description)
        dialog_layout.addWidget(description_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        def button_apply(*_):
            self.set_name(title_edit.text().strip())
            self.set_description(description_edit.toPlainText())
            self.data_object.add_or_edit_task(self.id, {"name": self.name, "description": self.description, "location": self.location})
            dialog.close()

        def button_cancel(*_):
            dialog.close()

        button_box.accepted.connect(button_apply)
        button_box.rejected.connect(button_cancel)

        dialog_layout.addWidget(button_box)

        dialog.exec()

    def populate_menu(self):
        def populate_move_to_menu():
            move_to_menu.clear()
            for k,v in self.task_widgets.items():
                if v is not self.parentWidget():
                    move_to_menu.addAction(k, lambda widget=v: move_to_different_widget(widget)) # Why does reassigning v before it's passed into lambda work? *shrugs*

        def move_to_different_widget(widget):
            if widget is not None and widget is not self.parentWidget():
                self.window().setUpdatesEnabled(False) # Disable updates temporarily so all updates happen simultaneously and instantly, avoids awkward stutter caused by multiple redraws
                self.parentWidget().layout().removeWidget(self)
                widget.layout().addWidget(self)
                populate_move_to_menu()
                self.window().setUpdatesEnabled(True)

        self.popup_menu.addAction("Edit", lambda: self.edit_task())
        self.popup_menu.addAction("Delete", lambda: self.delete_self())
        move_to_menu = QMenu("Move to...")
        populate_move_to_menu()
        self.popup_menu.addMenu(move_to_menu)

    def __str__(self):
        return self._name

    name = Property(str, get_name, set_name)
    description = Property(str, get_description, set_description)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load data as object
        self.data_object = DataObject()
        self.data_object.load_data()

        # Layout: Window -> Root Widget -> 4 task sections -> Section title + (Scrollable area -> tasks area)
        root = QWidget()
        root_layout = QHBoxLayout(root)
        self.setCentralWidget(root)

        self.planned_tasks = QWidget()
        self.planned_tasks.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.planned_tasks_scroll_area = QScrollArea()
        self.planned_tasks_scroll_area.setWidget(self.planned_tasks)
        self.planned_tasks_scroll_area.setWidgetResizable(True)
        self.planned_tasks_layout = QVBoxLayout(self.planned_tasks)
        self.planned_tasks_column = QVBoxLayout()
        self.planned_tasks_column.addWidget(QLabel("Planned Tasks"))
        self.planned_tasks_column.addWidget(self.planned_tasks_scroll_area)
        root_layout.addLayout(self.planned_tasks_column)

        self.in_progress_tasks = QWidget()
        self.in_progress_tasks.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.in_progress_tasks_scroll_area = QScrollArea()
        self.in_progress_tasks_scroll_area.setWidget(self.in_progress_tasks)
        self.in_progress_tasks_scroll_area.setWidgetResizable(True)
        self.in_progress_tasks_layout = QVBoxLayout(self.in_progress_tasks)
        self.in_progress_tasks_column = QVBoxLayout()
        self.in_progress_tasks_column.addWidget(QLabel("Tasks In Progress"))
        self.in_progress_tasks_column.addWidget(self.in_progress_tasks_scroll_area)
        root_layout.addLayout(self.in_progress_tasks_column)

        self.completed_tasks = QWidget()
        self.completed_tasks.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.completed_tasks_scroll_area = QScrollArea()
        self.completed_tasks_scroll_area.setWidget(self.completed_tasks)
        self.completed_tasks_scroll_area.setWidgetResizable(True)
        self.completed_tasks_layout = QVBoxLayout(self.completed_tasks)
        self.completed_tasks_column = QVBoxLayout()
        self.completed_tasks_column.addWidget(QLabel("Completed Tasks"))
        self.completed_tasks_column.addWidget(self.completed_tasks_scroll_area)
        root_layout.addLayout(self.completed_tasks_column)

        self.cancelled_tasks = QWidget()
        self.cancelled_tasks.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.cancelled_tasks_scroll_area = QScrollArea()
        self.cancelled_tasks_scroll_area.setWidget(self.cancelled_tasks)
        self.cancelled_tasks_scroll_area.setWidgetResizable(True)
        self.cancelled_tasks_layout = QVBoxLayout(self.cancelled_tasks)
        self.cancelled_tasks_column = QVBoxLayout()
        self.cancelled_tasks_column.addWidget(QLabel("Cancelled Tasks"))
        self.cancelled_tasks_column.addWidget(self.cancelled_tasks_scroll_area)
        root_layout.addLayout(self.cancelled_tasks_column)

        # Dictionary of widgets and their names as keys to pass into Task widgets
        self.task_widgets = {
            "Planned": self.planned_tasks,
            "In progress": self.in_progress_tasks,
            "Completed": self.completed_tasks,
            "Cancelled": self.cancelled_tasks
        }

        # Update data in-app everytime database changes + initial setup
        self.data_object.dataChanged.connect(lambda *_: self.update_tasks_based_on_data())
        self.update_tasks_based_on_data()

        # Menu bar
        menu_bar = self.menuBar()

        # Add task menu
        def add_task(widget, location):
            all_ids = [key for key in self.data_object.data.keys()]
            new_task = Task(id=str(int(all_ids[-1])+1), name="Change Me!", task_widgets=self.task_widgets, parent_widget=widget)
            location.addWidget(new_task)
            new_task.edit_task()

        add_task_menu = menu_bar.addMenu("Add Task...")
        add_task_menu.addAction("Add planned task", lambda: add_task(self.planned_tasks, self.planned_tasks_layout))
        add_task_menu.addAction("Add task in progress", lambda: add_task(self.in_progress_tasks, self.in_progress_tasks_layout))
        add_task_menu.addAction("Add completed task", lambda: add_task(self.completed_tasks, self.completed_tasks_layout))
        add_task_menu.addAction("Add cancelled task", lambda: add_task(self.cancelled_tasks, self.cancelled_tasks_layout))

        # Window base configuration
        self.setWindowTitle("Task Tracker")
        self.setMinimumSize(QSize(800, 600))

    def update_tasks_based_on_data(self):
        self.setUpdatesEnabled(False) # Disable updates so we can have one complete smooth redraw

        # Firstly remove all existing tasks
        for i in range(self.planned_tasks_layout.count()):
            self.planned_tasks_layout.removeWidget(self.planned_tasks_layout.itemAt(i))
        for i in range(self.in_progress_tasks_layout.count()):
            self.in_progress_tasks_layout.removeWidget(self.in_progress_tasks_layout.itemAt(i))
        for i in range(self.completed_tasks_layout.count()):
            self.completed_tasks_layout.removeWidget(self.completed_tasks_layout.itemAt(i))
        for i in range(self.cancelled_tasks_layout.count()):
            self.cancelled_tasks_layout.removeWidget(self.cancelled_tasks_layout.itemAt(i))

        # Then all add tasks from data object
        for id, task in self.data_object.data.items():
            if task["location"] == "planned":
                self.planned_tasks_layout.addWidget(Task(
                    id=id,
                    name=task["name"],
                    description=task["description"],
                    task_widgets=self.task_widgets,
                    parent_widget=self.planned_tasks,
                    location="planned"
                ))
            elif task["location"] == "in_progress":
                self.in_progress_tasks_layout.addWidget(Task(
                    id=id,
                    name=task["name"],
                    description=task["description"],
                    task_widgets=self.task_widgets,
                    parent_widget=self.in_progress_tasks,
                    location="in_progress"
                ))
            elif task["location"] == "completed":
                self.completed_tasks_layout.addWidget(Task(
                    id=id,
                    name=task["name"],
                    description=task["description"],
                    task_widgets=self.task_widgets,
                    parent_widget=self.completed_tasks,
                    location="completed"
                ))
            elif task["location"] == "cancelled":
                self.cancelled_tasks_layout.addWidget(Task(
                    id=id,
                    name=task["name"],
                    description=task["description"],
                    task_widgets=self.task_widgets,
                    parent_widget=self.cancelled_tasks,
                    location="cancelled"
                ))

        self.setUpdatesEnabled(True)

window = MainWindow()
window.show()

app.exec()
