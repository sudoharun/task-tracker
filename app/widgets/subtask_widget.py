from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QLineEdit,
    QWidget
)

class SubtaskWidget(QWidget):
    deleteSelfRequest = Signal(QWidget)
    saveRequest = Signal(dict)

    def __init__(self, id="0", text="Change me", completed=False, edit_mode=False, checkable=False):
        super().__init__()

        self.id = id
        self.text = text
        self.completed = completed

        self.wlayout = QHBoxLayout(self)

        self.checkbox = QCheckBox()
        self.checkbox.setCheckState(Qt.CheckState.Checked if self.completed else Qt.CheckState.Unchecked)
        self.checkbox.setVisible(checkable)
        self.checkbox.checkStateChanged.connect(self.on_checkbox_state_changed)
        self.display_widget = QStackedWidget()

        # Stack to show when not in progress
        self.regular_mode = QWidget()
        self.regular_mode_layout = QVBoxLayout(self.regular_mode)

        self.label = QLabel(self.text, wordWrap=True)
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")

        self.regular_buttons = QWidget()
        self.regular_buttons_layout = QHBoxLayout(self.regular_buttons)
        self.regular_buttons_layout.addWidget(self.edit_button)
        self.regular_buttons_layout.addWidget(self.delete_button)

        self.regular_mode_layout.addWidget(self.label)
        self.regular_mode_layout.addWidget(self.regular_buttons)

        # Stack to show when in progress
        self.edit_mode = QWidget()
        self.edit_mode_layout = QVBoxLayout(self.edit_mode)

        self.line_edit = QLineEdit(text=self.text)
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.edit_mode_buttons = QWidget()
        self.edit_mode_buttons_layout = QHBoxLayout(self.edit_mode_buttons)
        self.edit_mode_buttons_layout.addWidget(self.save_button)
        self.edit_mode_buttons_layout.addWidget(self.cancel_button)

        self.edit_mode_layout.addWidget(self.line_edit)
        self.edit_mode_layout.addWidget(self.edit_mode_buttons)

        # All buttons connectors
        self.edit_button.clicked.connect(lambda *_: self.set_edit_mode(True))
        self.delete_button.clicked.connect(lambda *_: self.delete_self())

        self.save_button.clicked.connect(lambda *_: self.save())
        self.cancel_button.clicked.connect(lambda *_: self.set_edit_mode(False))

        # Finally, put it all together
        self.display_widget.addWidget(self.regular_mode)
        self.display_widget.addWidget(self.edit_mode)

        self.wlayout.addWidget(self.checkbox)
        self.wlayout.addWidget(self.display_widget)

        self.set_edit_mode(edit_mode)

    def on_checkbox_state_changed(self, state):
        self.save()

    def set_edit_mode(self, state: bool):
        if state:
            self.display_widget.setCurrentIndex(1)
        else:
            self.display_widget.setCurrentIndex(0)

    def delete_self(self):
        self.setParent(None)
        self.deleteLater()
        self.deleteSelfRequest.emit(self)

    def save(self):
        self.text = self.line_edit.text()

        check_state = self.checkbox.checkState()
        if check_state == Qt.CheckState.Checked:
            self.completed = True
        else:
            self.completed = False

        data = {"id": self.id, "text": self.text, "completed": self.completed}

        self.label.setText(self.text)
        self.line_edit.setText(self.text)

        self.set_edit_mode(False)
        self.saveRequest.emit(data)
