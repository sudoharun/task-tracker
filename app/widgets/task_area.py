from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QSpacerItem, QStackedWidget, QWidget, QVBoxLayout
from . import TaskWidget

class TaskArea(QWidget):
    tasksChanged = Signal()
    taskDeleted = Signal(TaskWidget)

    def __init__(self, title=""):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(title))

        scroll_area = QScrollArea(widgetResizable=True)

        tasks_area = QWidget()
        self.tasks_layout = QVBoxLayout(tasks_area)
        self.tasks_layout.addStretch()

        self.tasks_stack = QStackedWidget()
        self.tasks_stack.addWidget(tasks_area)
        self.tasks_stack.addWidget(QLabel("Nothing to see here!", alignment=Qt.AlignmentFlag.AlignCenter))
        self.tasks_stack.setCurrentIndex(1) # By default there is nothing inside anyway

        scroll_area.setWidget(self.tasks_stack)
        layout.addWidget(scroll_area)

    def add_task(self, task_widget: TaskWidget, emit_signal=False):
        task_added = False
        index = self.tasks_layout.count()
        while index >= 0:
            if type(self.tasks_layout.itemAt(index)) is QSpacerItem:
                self.tasks_layout.insertWidget(index, task_widget)
                task_added = True
                break
            index-=1

        if not task_added:
            self.tasks_layout.insertWidget(index, task_widget)
        else:
            self.tasks_stack.setCurrentIndex(0)

        task_widget.deleteSelfRequest.connect(lambda task=task_widget: self.answer_widget_delete_self_request(task_widget))

        if emit_signal:
            self.tasksChanged.emit()

    def answer_widget_delete_self_request(self, task: TaskWidget):
        self.remove_task(task, emit_signal=True)

    def remove_task(self, task_widget: TaskWidget, delete_widget=True, delete_data=True, emit_signal=False):
        self.tasks_layout.removeWidget(task_widget)

        if delete_data:
            self.taskDeleted.emit(task_widget)

        if delete_widget:
            task_widget.deleteLater()

        if emit_signal:
            self.tasksChanged.emit()

        if self.tasks_layout.count() == 1: # So only the QSpacerItem
            self.tasks_stack.setCurrentIndex(1)

    def reset_self(self, delete_widget=True, delete_data=True):
        for index in reversed(range(self.tasks_layout.count())):
            item_to_remove = self.tasks_layout.itemAt(index)
            if item_to_remove is not None:
                widget = item_to_remove.widget()
                if isinstance(widget, TaskWidget):
                    self.remove_task(widget, delete_widget=delete_widget, delete_data=delete_data)
