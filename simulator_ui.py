"""
Module Documentation: simulator_ui.py

This module provides functions for managing the user interface of the Beamforming Simulator application.

Functions:
----------

1. add_array(app)
   - Purpose: Adds a new phased array to the application.
   - Parameters:
     - app (QApplication): The application context.

2. initialize_array(app, array, num_transmitters, num_receivers)
   - Purpose: Initializes a phased array with transmitters and receivers.
   - Parameters:
     - app (QApplication): The application context.
     - array (dict): The array data.
     - num_transmitters (int): The number of transmitters.
     - num_receivers (int): The number of receivers.

3. update_curvature(app, array, curvature)
   - Purpose: Updates the curvature of the specified array.
   - Parameters:
     - app (QApplication): The application context.
     - array (dict): The array data.
     - curvature (int): The curvature value.

4. redraw_array(app, array)
   - Purpose: Redraws the specified array.
   - Parameters:
     - app (QApplication): The application context.
     - array (dict): The array data.

5. clear_scene(app)
   - Purpose: Clears the scene and removes all arrays.
   - Parameters:
     - app (QApplication): The application context.

Dependencies:
-------------
- PyQt5: Used for user interface management.

Usage:
------
These functions are used internally by `main.py` to manipulate the graphical representation of arrays and their components within the Beamforming Simulator application.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsLineItem, QSlider, QHBoxLayout, QLabel
from phased_array import Element, ArrayBox


def add_array(app):
    array_id = len(app.arrays)

    curvature_slider = QSlider(Qt.Horizontal)
    curvature_slider.setRange(0, 100)
    curvature_slider.setValue(0)
    sliders_layout = QHBoxLayout()
    sliders_layout.addWidget(QLabel(f"Array {array_id} Curvature:"))
    sliders_layout.addWidget(curvature_slider)
    app.sliders_layout.addLayout(sliders_layout)

    array = {
        "id": array_id,
        "curvature_slider": curvature_slider,
        "transmitters": [],
        "receivers": [],
        "position_offset_x": 0,
        "position_offset_y": 0,
        "box": None
    }
    app.arrays.append(array)

    initialize_array(app, array, app.num_transmitters.value(), app.num_receivers.value())

    curvature_slider.valueChanged.connect(lambda: update_curvature(app, array, curvature_slider.value()))


def initialize_array(app, array, num_transmitters, num_receivers):
    max_x = 100 * (num_transmitters // 2)
    step_size = (2 * max_x) / (num_transmitters - 1) if num_transmitters > 1 else 0

    for i in range(num_transmitters):
        transmitter = Element(category="Transmitter", index=i, app=app, array_index=array["id"])
        x = -max_x + i * step_size
        y = 0
        transmitter.image.setPos(x, y)
        transmitter.position = (x, y)
        app.scene.addItem(transmitter.image)
        array["transmitters"].append(transmitter)

    max_x_receiver = 100 * (num_receivers // 2)
    for i in range(num_receivers):
        receiver = Element(category="Receiver", index=i, app=app, array_index=array["id"])
        x_receiver = -max_x_receiver + i * step_size
        y_receiver = 200
        receiver.image.setPos(x_receiver, y_receiver)
        receiver.position = (x_receiver, y_receiver)
        app.scene.addItem(receiver.image)
        array["receivers"].append(receiver)

    array_box = ArrayBox(array, app)
    app.scene.addItem(array_box)
    array["box"] = array_box

    redraw_array(app, array)


def update_curvature(app, array, curvature):
    num_transmitters = len(array["transmitters"])
    max_x = 100 * (num_transmitters // 2)
    step_size = (2 * max_x) / (num_transmitters - 1) if num_transmitters > 1 else 0
    position_offset_x = array["position_offset_x"]
    position_offset_y = array["position_offset_y"]

    for i, transmitter in enumerate(array["transmitters"]):
        x = -max_x + i * step_size
        y = -(curvature / 35000) * (x ** 2) if curvature > 0 else 0

        transmitter.image.setPos(x + position_offset_x, y + position_offset_y)
        transmitter.position = (x + position_offset_x, y + position_offset_y)

    max_x_receiver = 100 * (len(array["receivers"]) // 2)
    for i, receiver in enumerate(array["receivers"]):
        x_receiver = -max_x_receiver + i * step_size
        y_receiver = 200
        receiver.image.setPos(x_receiver + position_offset_x, y_receiver + position_offset_y)
        receiver.position = (x_receiver + position_offset_x, y_receiver + position_offset_y)

    redraw_array(app, array)


def redraw_array(app, array):
    if "lines" in array:
        for line in array["lines"]:
            if line in app.scene.items():
                app.scene.removeItem(line)
    array["lines"] = []

    for transmitter in array["transmitters"]:
        tx_x, tx_y = transmitter.position
        for receiver in array["receivers"]:
            rx_x, rx_y = receiver.position
            line = QGraphicsLineItem(tx_x + 30, tx_y + 27, rx_x + 25, rx_y + 12)
            line.setPen(QPen(Qt.blue, 3))
            app.scene.addItem(line)
            array["lines"].append(line)

    if "curve_item" in array and array["curve_item"] in app.scene.items():
        app.scene.removeItem(array["curve_item"])

    curve_path = QPainterPath()
    for i, transmitter in enumerate(array["transmitters"]):
        tx_x, tx_y = transmitter.position
        if i == 0:
            curve_path.moveTo(tx_x + 30, tx_y + 27)
        else:
            curve_path.lineTo(tx_x + 30, tx_y + 27)

    curve_item = QGraphicsPathItem(curve_path)
    curve_item.setPen(QPen(Qt.red, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    app.scene.addItem(curve_item)
    array["curve_item"] = curve_item


def clear_scene(app):
    app.scene.clear()
    app.arrays = []

    while app.sliders_layout.count():
        while app.sliders_layout.itemAt(0).count():
            item1 = app.sliders_layout.itemAt(0).takeAt(0)
            widget = item1.widget()
            if widget is not None:
                widget.deleteLater()
        item2 = app.sliders_layout.takeAt(0)
        widget2 = item2.widget()
        if widget2 is not None:
            widget2.deleteLater()
