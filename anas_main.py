"""
Module Documentation: main.py

This module initializes and runs the Beamforming Simulator application.

Classes:
--------

1. BeamformingSimulatorApp(QMainWindow)
   - Purpose: Serves as the main application window for the Beamforming Simulator.
   - Key Methods:
     - create_array_settings(): Creates controls for managing arrays.
     - create_graphics_view(title, scene=None): Creates a visualization view.
     - create_graphs_section(): Creates a section for displaying graphs.
     - add_array(): Adds a new phased array to the scene.
     - initialize_array(array, num_transmitters, num_receivers): Initializes a phased array with transmitters and receivers.
     - update_curvature(array_id): Updates the curvature of the specified array.
     - redraw_array(array): Redraws the red and blue lines for the specified array.
     - clear_scene(): Clears the scene and removes all arrays.

Dependencies:
-------------
- PyQt5: Required for graphical user interface components.

Usage:
------
Run `main.py` to launch the Beamforming Simulator application, which provides a visual interface for creating and managing phased arrays.
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSlider,
    QLabel, QPushButton, QGraphicsView, QSpinBox, QGraphicsScene
)
from PyQt5.QtCore import Qt
from simulator_ui import update_curvature, redraw_array, initialize_array, add_array, clear_scene


class BeamformingSimulatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.constructive_graph = None
        self.destructive_graph = None
        self.clear_scene_button = None
        self.sliders_layout = None
        self.add_array_button = None
        self.num_receivers = None
        self.num_transmitters = None
        self.setWindowTitle("Beamforming Simulator")
        self.setGeometry(100, 100, 1200, 800)

        self.scene = QGraphicsScene()
        self.arrays = []

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)
        array_settings = self.create_array_settings()
        controls_layout.addWidget(array_settings)

        visualization_layout = QVBoxLayout()
        self.BeamProfile = self.create_graphics_view("Beamforming Viewer", self.scene)
        visualization_layout.addWidget(self.BeamProfile)
        self.graphs_layout = self.create_graphs_section()
        visualization_layout.addLayout(self.graphs_layout)

        main_layout.addLayout(controls_layout)
        main_layout.addLayout(visualization_layout)

    def create_array_settings(self):
        """Create controls for managing arrays."""
        group = QWidget()
        layout = QVBoxLayout()
        group.setLayout(layout)

        title = QLabel("Array Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        num_layout = QHBoxLayout()
        num_layout.addWidget(QLabel("Number of Transmitters:"))
        self.num_transmitters = QSpinBox()
        self.num_transmitters.setRange(1, 100)
        self.num_transmitters.setValue(5)
        num_layout.addWidget(self.num_transmitters)
        num_layout.addWidget(QLabel("Number of Receivers:"))
        self.num_receivers = QSpinBox()
        self.num_receivers.setRange(1, 100)
        self.num_receivers.setValue(5)
        num_layout.addWidget(self.num_receivers)
        layout.addLayout(num_layout)

        self.add_array_button = QPushButton("Add Phased Array")
        self.add_array_button.clicked.connect(self.add_array)
        layout.addWidget(self.add_array_button)

        self.sliders_layout = QVBoxLayout()
        layout.addLayout(self.sliders_layout)

        self.clear_scene_button = QPushButton("Clear Scene")
        self.clear_scene_button.clicked.connect(self.clear_scene)
        layout.addWidget(self.clear_scene_button)

        return group

    def create_graphics_view(self, title, scene=None):
        """Create a visualization view."""
        group = QWidget()
        layout = QVBoxLayout()
        group.setLayout(layout)

        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(label)

        view = QGraphicsView(scene)
        view.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        layout.addWidget(view)

        return group

    def create_graphs_section(self):
        layout = QHBoxLayout()
        self.constructive_graph = QGraphicsView()
        self.constructive_graph.setStyleSheet("background-color: lightgreen; border: 1px solid black;")
        layout.addWidget(self.constructive_graph)
        self.destructive_graph = QGraphicsView()
        self.destructive_graph.setStyleSheet("background-color: lightcoral; border: 1px solid black;")
        layout.addWidget(self.destructive_graph)
        return layout

    def add_array(self):
        add_array(self)

    def initialize_array(self, array, num_transmitters, num_receivers):
        initialize_array(self, array, num_transmitters, num_receivers)

    def update_curvature(self, array_id):
        update_curvature(self, array_id)

    def redraw_array(self, array):
        redraw_array(self, array)

    def clear_scene(self):
        clear_scene(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BeamformingSimulatorApp()
    window.show()
    sys.exit(app.exec_())
