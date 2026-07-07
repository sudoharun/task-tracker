from PySide6.QtCore import QObject, Signal, Property

class TaskObject(QObject):
    titleChanged = Signal(str)
    descriptionChanged = Signal(str)
    locationChanged = Signal(str)
    progressChanged = Signal(int)

    def __init__(self, id="0", title=None, description=None, location=None, progress=None):
        super().__init__()

        self.id = id
        self._title = title or ""
        self._description = description or ""
        self._location = location or ""
        self._progress = progress or 0

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

    title = Property(str, get_title, set_title, notify=titleChanged)
    description = Property(str, get_description, set_description, notify=descriptionChanged)
    location = Property(str, get_location, set_location, notify=locationChanged)
    progress = Property(int, get_progress, set_progress, notify=progressChanged)
