from objects import DataObject, TaskObject
from widgets import TaskWidget, TaskArea
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

# To Do:
# - Add label when task area is empty, more visually pleasing
# - Add progress bar for in-progress and cancelled tasks
# - Add (potentially colour-coded) priorities

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

        self.task_areas = {
            "planned": TaskArea("Planned tasks"),
            "in_progress": TaskArea("Tasks in progress"),
            "completed": TaskArea("Completed tasks"),
            "cancelled": TaskArea("Cancelled tasks")
        }

        for _, area in self.task_areas.items():
            area.tasksChanged.connect(lambda *_: self.on_area_tasks_changed())
            area.taskDeleted.connect(lambda task: self.on_area_task_widget_delete_request(task))
            root_layout.addWidget(area)

        self.update_tasks_based_on_data()

        # Menu bar
        menu_bar = self.menuBar()

        # Add task button for menu bar
        add_task_menu = menu_bar.addMenu("Add Task...")
        add_task_menu.addAction("Add planned task", lambda: self.add_task("planned"))
        add_task_menu.addAction("Add task in progress", lambda: self.add_task("in_progress"))
        add_task_menu.addAction("Add completed task", lambda: self.add_task("completed"))
        add_task_menu.addAction("Add cancelled task", lambda: self.add_task("cancelled"))

        # Force data refresh button
        menu_bar.addAction("Force update", lambda: self.update_tasks_based_on_data())

        # Window base configuration
        self.setWindowTitle("Task Tracker")
        self.setMinimumSize(QSize(800, 600))

    def on_area_tasks_changed(self):
        self.data_object.save_data()

    def on_area_task_widget_delete_request(self, task_widget: TaskWidget):
        self.data_object.delete_task(task_widget.task_obj.id)

    def update_tasks_based_on_data(self):
        # Disabling updates then re-enabling them at the end when all widgets have been added and removed allows for one smooth transition
        self.setUpdatesEnabled(False)

        for _, task_area in self.task_areas.items():
            task_area.reset_self(delete_data=False)

        for id, task in self.data_object.data.items():
            new_task = TaskWidget(
                id=id,
                title=task["title"],
                description=task["description"],
                location=task["location"]
            )
            new_task.locationChangeRequest.connect(self.answer_task_location_change_request)
            new_task.editSubmitRequest.connect(self.answer_edit_submit_request)
            self.task_areas[task["location"]].add_task(new_task)

        self.setUpdatesEnabled(True)

    def answer_task_location_change_request(self, widget, old_location, new_location):
        self.task_areas[old_location].remove_task(widget, delete_widget=False, delete_data=False)
        self.task_areas[new_location].add_task(widget, emit_signal=True)
        self.data_object.add_or_edit_task(widget.task_obj)

    def answer_edit_submit_request(self, task_object: TaskObject):
        self.data_object.add_or_edit_task(task_object)

    def add_task(self, location: str):
        all_ids = [key for key in self.data_object.data.keys()]
        if len(all_ids) == 0:
            new_id = str(0)
        else:
            new_id = str(int(all_ids[-1])+1)
        new_task = TaskWidget(id=new_id, location=location)
        new_task.locationChangeRequest.connect(self.answer_task_location_change_request)
        new_task.editSubmitRequest.connect(self.answer_edit_submit_request)
        self.task_areas[location].add_task(new_task, emit_signal=True)
        new_task.edit_task()

if __name__ == "__main__":
    app = QApplication()

    window = MainWindow()
    window.show()

    app.exec()
