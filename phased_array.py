"""
Module Documentation: phased_array.py

This module provides classes and functionality for representing and interacting
with graphical elements, such as transmitters and receivers, in a phased array
application using PyQt5.

Classes:
--------

1. ArrayBox
   - Purpose: Represents a movable polygon on a graphics scene that symbolizes
     an array composed of transmitters and receivers.
   - Key Methods:
     - itemChange(change, value): Handles the movement of the polygon and
       updates the positions of associated transmitters and receivers.

2. ElementGraphicsPixmapItem
   - Purpose: Provides a graphical representation for individual elements
     (transmitters or receivers) within the phased array.
   - Key Methods:
     - itemChange(change, value): Updates the element's position upon position
       change events.
     - mouseDoubleClickEvent(event): Opens an editing dialog upon double-click.

3. Element
   - Purpose: A logical representation of an element within the phased array,
     such as transmitters or receivers.
   - Key Methods:
     - set_phase_shift(phase): Assigns a new phase shift value to the element.
     - transmit_signal(time): Simulates the signal transmitted by this element.

4. ElementParamsDialog
   - Purpose: Provides a dialog interface allowing users to view and modify
     parameters of a specific element in the array.
   - Key Methods:
     - accept(): Validates and applies new input parameters for transmitters.

Dependencies:
-------------
- PyQt5: Utilized for creating the graphical user interface and handling user
  interactions.
- numpy: Used for performing numerical computations, especially in calculating
  the transmitted signal.

Usage:
------
To use this module, instantiate the classes with the required parameters,
typically within a PyQt5 application context that manages scenes and graphics views.
"""

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QDialogButtonBox, QGraphicsRectItem, \
    QGraphicsItem, QGraphicsPolygonItem
import numpy as np
from PyQt5.QtGui import QPixmap, QPen, QPolygon, QPolygonF
from PyQt5.QtWidgets import QGraphicsPixmapItem


class ArrayBox(QGraphicsPolygonItem):
    def __init__(self, array, app):
        super().__init__()
        self.array = array
        self.app = app
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setPolygon(QPolygonF([QPointF(50, 50), QPointF(150, 50), QPointF(150, 100), QPointF(50, 100)]))
        self.setPen(QPen(Qt.lightGray, 2))
        self.setBrush(Qt.transparent)
        self.setZValue(-1)
        self.previous_position = self.pos()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            dx = value.x() - self.previous_position.x()
            dy = value.y() - self.previous_position.y()

            for transmitter in self.array["transmitters"]:
                tx_x, tx_y = transmitter.position
                transmitter.image.setPos(tx_x + dx, tx_y + dy)
                transmitter.position = (tx_x + dx, tx_y + dy)

            for receiver in self.array["receivers"]:
                rx_x, rx_y = receiver.position
                receiver.image.setPos(rx_x + dx, rx_y + dy)
                receiver.position = (rx_x + dx, rx_y + dy)
            self.array["position_offset_x"] += dx
            self.array["position_offset_y"] += dy
            self.previous_position = value
            self.app.redraw_array(self.array)
        return super().itemChange(change, value)


class ElementGraphicsPixmapItem(QGraphicsPixmapItem):
    def __init__(self, element, app):
        super().__init__()
        self.element = element
        self.app = app

    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.ItemPositionChange:
            self.element.position = (value.x(), value.y())
            self.app.redraw_lines()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            dialog = ElementParamsDialog(self.element, self.app)
            dialog.exec_()


class Element:
    def __init__(self, category, index, app, array_index, frequency=1e9, power=1.0, phase_shift=0):
        self.category = category
        self.image = ElementGraphicsPixmapItem(self, app)
        self.image.setPixmap(QPixmap(f"assets/{category}.png"))
        self.image.setFlags(QGraphicsPixmapItem.ItemIsSelectable)
        self.position = (self.image.x(), self.image.y())
        self.index = index
        self.array_index = array_index
        if category == "Transmitter":
            self.frequency = frequency
            self.power = power
            self.phase_shift = phase_shift
        else:
            self.frequency = None
            self.power = None
            self.phase_shift = None

    def set_phase_shift(self, phase):
        self.phase_shift = phase

    def transmit_signal(self, time):
        signal = self.power * np.sin(2 * np.pi * self.frequency * time + self.phase_shift)
        return signal


class ElementParamsDialog(QDialog):
    def __init__(self, element, parent=None):
        super().__init__(parent)
        self.element = element
        self.setWindowTitle(f"Edit Parameters for {element.category} at Array {element.array_index}, Element {element.index}")
        layout = QFormLayout()

        self.array_index_label = QLabel(str(element.array_index))
        layout.addRow(QLabel("Array Index:"), self.array_index_label)

        self.element_index_label = QLabel(str(element.index))
        layout.addRow(QLabel(f"{element.category} Index:"), self.element_index_label)

        if element.category == "Transmitter":
            self.freq_input = QLineEdit(str(element.frequency))
            layout.addRow(QLabel("Frequency (Hz):"), self.freq_input)

            self.phase_input = QLineEdit(str(element.phase_shift))
            layout.addRow(QLabel("Phase Shift (°):"), self.phase_input)

        self.element_position_x = QLabel(str(element.position[0]))
        layout.addRow(QLabel("Position_X:"), self.element_position_x)

        self.element_position_y = QLabel(str(element.position[1]))
        layout.addRow(QLabel("Position_Y:"), self.element_position_y)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

    def accept(self):
        if self.element.category == "Transmitter":
            try:
                new_frequency = float(self.freq_input.text())
                new_phase_shift = float(self.phase_input.text())

                self.element.frequency = new_frequency
                self.element.phase_shift = new_phase_shift
                print(f"Updated Element {self.element.index} in Array {self.element.array_index}: Frequency = {new_frequency}, Phase Shift = {new_phase_shift}")
                super().accept()
            except ValueError:
                print("Invalid input! Please enter valid numbers.")
        else:
            super().accept()
