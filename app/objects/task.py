from PySide6.QtCore import QObject, Signal, Property

class TaskObject(QObject):
    titleChanged = Signal(str)
    descriptionChanged = Signal(str)
    locationChanged = Signal(str)
    progressChanged = Signal(int)
    subtasksChanged = Signal(dict)
    subtaskAdded = Signal(str, dict)
    subtaskRemoved = Signal(str, dict)

    def __init__(self, id="0", title=None, description=None, location=None, progress=None, subtasks=None):
        super().__init__()

        self.id = id
        self._title = title or ""
        self._description = description or ""
        self._location = location or ""
        self._progress = progress or 0
        self._subtasks = subtasks or {}

    def get_title(self):
        return self._title

    def set_title(self, new_title):
        self._title = new_title
        self.titleChanged.emit(self._title)

    def get_description(self):
        return self._description

    def set_description(self, new_description):
        self._description = new_description
        self.descriptionChanged.emit(self._description)

    def get_location(self):
        return self._location

    def set_location(self, new_location):
        self._location = new_location
        self.locationChanged.emit(new_location)

    def get_progress(self):
        return self._progress

    def set_progress(self, new_progress):
        self._progress = new_progress
        self.progressChanged.emit(self._progress)

    def get_subtasks(self):
        return self._subtasks

    def set_subtasks(self, new_subtasks_list: dict):
        self._subtasks = new_subtasks_list
        self.subtasksChanged.emit(self._subtasks)

    def add_subtask(self, id: str, subtask: dict):
        self._subtasks[id] = subtask
        self.subtaskAdded.emit(id, subtask)

    def remove_subtask(self, id: int):
        subtask_to_remove = self._subtasks[id] or None
        if subtask_to_remove is not None:
            del self._subtasks[id]
            self.subtaskRemoved.emit(id, subtask_to_remove)

    title = Property(str, get_title, set_title, notify=titleChanged)
    description = Property(str, get_description, set_description, notify=descriptionChanged)
    location = Property(str, get_location, set_location, notify=locationChanged)
    progress = Property(int, get_progress, set_progress, notify=progressChanged)
    subtasks = Property(dict, get_subtasks, set_subtasks, notify=subtasksChanged)
