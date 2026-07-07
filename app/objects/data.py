import json
from PySide6.QtCore import QObject, Signal, Property
from .task import TaskObject

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

    def add_or_edit_task(self, task: TaskObject):
        self._data[task.id] = {
            "title": task.title,
            "description": task.description,
            "progress": task.progress,
            "location": task.location
        }

        self.save_data()

    def delete_task(self, id: str):
        del self._data[id]
        self.save_data()

    data = Property(dict, load_data, save_data, notify=dataChanged)
