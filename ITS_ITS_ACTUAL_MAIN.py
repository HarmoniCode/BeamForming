import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QSlider,
    QLabel,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys

class HeatMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beamforming Simulator")
        self.setGeometry(100, 100, 1800, 1200)
        self.setWindowIcon(QIcon("antenna_icon.png"))  # Replace with the actual path to your icon file

        # Initialize default values
        self.num_antennas = 2
        self.distance_m = 1  # Distance in meters
        self.delay_deg = 10  # Delay in degrees
        self.frequency = 99.99  # Default: 100 Hz
        self.propagation_speed = 99.99  # Default: Speed of light in m/s
        self.wave_type = "Isotropic"
        self.profile_orientation = "Horizontal"  # Default profile orientation
        self.array_geometry = "Linear"  # Default array geometry
        self.curvature = 0.0  # Default curvature for curved array

        self.initUI()

    def initUI(self):
        # Central widget for the window
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create the Matplotlib figures and canvases
        self.heatmap_fig = Figure()
        self.heatmap_canvas = FigureCanvas(self.heatmap_fig)
        self.profile_fig = Figure()
        self.profile_canvas = FigureCanvas(self.profile_fig)

        # Add canvases to the layout
        layout.addWidget(self.heatmap_canvas)
        layout.addWidget(self.profile_canvas)

        # Form layout for inputs
        form_layout = QFormLayout()

        # Number of antennas
        self.num_antennas_slider = QSlider(Qt.Horizontal)  # Horizontal slider
        self.num_antennas_slider.setMinimum(1)
        self.num_antennas_slider.setMaximum(10)
        self.num_antennas_slider.setValue(self.num_antennas)  # Set default value
        self.num_antennas_slider.setTickInterval(1)  # Set tick intervals
        self.num_antennas_slider.setTickPosition(QSlider.TicksBelow)  # Show ticks below the slider

        # Label to display the current value of the slider
        self.num_antennas_label = QLabel(f"{self.num_antennas}")  # Display initial value
        self.num_antennas_label.setAlignment(Qt.AlignCenter)

        # Connect slider value change signal to update the label
        self.num_antennas_slider.valueChanged.connect(
            lambda value: self.num_antennas_label.setText(f"{value}")
        )

        # Add slider and label to the form layout
        form_layout.addRow("Number of Antennas:", self.num_antennas_slider)
        form_layout.addRow("Selected Antennas:", self.num_antennas_label)

        # self.num_antennas_spinbox = QSpinBox()
        # self.num_antennas_spinbox.setMinimum(1)
        # self.num_antennas_spinbox.setMaximum(10)
        # self.num_antennas_spinbox.setValue(self.num_antennas)
        # form_layout.addRow("Number of Antennas:", self.num_antennas_spinbox)

        # Distance between antennas
        self.distance_slider = QSlider(Qt.Horizontal)  # Horizontal slider
        self.distance_slider.setMinimum(1)
        self.distance_slider.setMaximum(10)
        self.distance_slider.setValue(self.distance_m)  # Set default value
        self.distance_slider.setTickInterval(1)  # Set tick intervals
        self.distance_slider.setTickPosition(QSlider.TicksBelow)  # Show ticks below the slider

        # Label to display the current value of the slider
        self.distance_label = QLabel(f"{self.distance_m}")  # Display initial value
        self.distance_label.setAlignment(Qt.AlignCenter)

        # Connect slider value change signal to update the label
        self.distance_slider.valueChanged.connect(
            lambda value: self.distance_label.setText(f"{value}")
        )

        # Add slider and label to the form layout
        form_layout.addRow("Distance between antennas (m):", self.distance_slider)
        form_layout.addRow("Distance (m):", self.distance_label)

        # self.distance_spinbox = QDoubleSpinBox()
        # self.distance_spinbox.setDecimals(2)
        # self.distance_spinbox.setMinimum(0)
        # self.distance_spinbox.setMaximum(10)
        # self.distance_spinbox.setValue(self.distance_m)
        # form_layout.addRow("Distance between antennas (in meters):", self.distance_spinbox)

        # Delay between antennas
        self.delay_slider = QSlider(Qt.Horizontal)  # Horizontal slider
        self.delay_slider.setMinimum(0)
        self.delay_slider.setMaximum(180)
        self.delay_slider.setValue(self.delay_deg)  # Set default value
        self.delay_slider.setTickInterval(1)  # Set tick intervals
        self.delay_slider.setTickPosition(QSlider.TicksBelow)  # Show ticks below the slider

        # Label to display the current value of the slider
        self.delay_label = QLabel(f"{self.distance_m}")  # Display initial value
        self.delay_label.setAlignment(Qt.AlignCenter)

        # Connect slider value change signal to update the label
        self.delay_slider.valueChanged.connect(
            lambda value: self.delay_label.setText(f"{value}")
        )

        # Add slider and label to the form layout
        form_layout.addRow("Delay between antennas (in degrees):", self.delay_slider)
        form_layout.addRow("Degrees:", self.delay_label)

        # self.delay_spinbox = QDoubleSpinBox()
        # self.delay_spinbox.setDecimals(3)
        # self.delay_spinbox.setValue(self.delay_deg)
        # form_layout.addRow("Delay between antennas (in degrees):", self.delay_spinbox)

        # Frequency of the wave
        self.frequency_spinbox = QDoubleSpinBox()
        self.frequency_spinbox.setDecimals(2)
        self.frequency_spinbox.setSingleStep(1.0)
        self.frequency_spinbox.setValue(self.frequency)
        self.frequency_spinbox.setMaximum(1e12)  # Large max value
        form_layout.addRow("Signal Frequency (Hz):", self.frequency_spinbox)

        # Propagation speed
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setDecimals(2)
        self.speed_spinbox.setValue(self.propagation_speed)
        form_layout.addRow("Propagation Speed (m/s):", self.speed_spinbox)

        # Wave equation type
        self.wave_type_combo = QComboBox()
        self.wave_type_combo.addItems(["Isotropic", "Sinc", "Gaussian", "Cosine"])
        form_layout.addRow("Wave Type:", self.wave_type_combo)

        # Beam Profile orientation (Horizontal or Vertical)
        self.profile_orientation_combo = QComboBox()
        self.profile_orientation_combo.addItems(["Horizontal", "Vertical"])
        form_layout.addRow("Beam Profile Orientation:", self.profile_orientation_combo)

        # Array geometry type (Linear or Curved)
        self.array_geometry_combo = QComboBox()
        self.array_geometry_combo.addItems(["Linear", "Curved"])
        self.array_geometry_combo.currentTextChanged.connect(self.toggle_curvature_slider)
        form_layout.addRow("Array Geometry:", self.array_geometry_combo)

        # Curvature slider
        self.curvature_slider_label = QLabel("Curvature (0 = Flat):")
        self.curvature_slider = QSlider(Qt.Horizontal)
        self.curvature_slider.setMinimum(0)
        self.curvature_slider.setMaximum(100)
        self.curvature_slider.setValue(0)
        self.curvature_slider.setTickInterval(10)
        self.curvature_slider.valueChanged.connect(self.update_curvature)
        self.curvature_slider.setDisabled(True)
        form_layout.addRow(self.curvature_slider_label, self.curvature_slider)

        # Generate button
        generate_button = QPushButton("Update Heatmap and Beam Profile")
        generate_button.clicked.connect(self.generate_heatmap_and_profile)
        form_layout.addWidget(generate_button)

        layout.addLayout(form_layout)

        # Generate initial heatmap and beam profile
        self.generate_heatmap_and_profile()

    def toggle_curvature_slider(self, value):
        if value == "Curved":
            self.curvature_slider.setDisabled(False)
        else:
            self.curvature_slider.setDisabled(True)
            self.curvature = 0.0  # Reset curvature

    def update_curvature(self, value):
        self.curvature = value / 100  # Normalize curvature value

    def plot_heatmap(self):
        # Clear the previous figure
        self.heatmap_fig.clear()

        ax = self.heatmap_fig.add_subplot(111) # 111 means a single subplot in a 1x1 grid.

        # Retrieve user inputs
        num_antennas = self.num_antennas_slider.value()
        distance_m = self.distance_slider.value()
        delay_deg = self.delay_slider.value()
        frequency = self.frequency_spinbox.value()
        speed = self.speed_spinbox.value()
        wave_type = self.wave_type_combo.currentText()
        array_geometry = self.array_geometry_combo.currentText()

        # Generate grid for the heatmap
        size = 500  # Grid size:  number of points along each axis (500x500 grid)
        extent = 10  # Coordinate range (-extent to extent): the grid covers coordinates from -10 to 10
        x = np.linspace(-extent, extent, size) # Generates 500 equally spaced points between -10 and 10
        y = np.linspace(-extent, extent, size)
        self.X, self.Y = np.meshgrid(x, y) # Creates two 2D arrays (self.X and self.Y) representing the x and y coordinates at each grid point

        '''
        example:
          self.X  [ [1 2 3]
                     [1 2 3] ]
          self.Y  [ [4 4 4]
                     [5 5 5] ]
        This results in all possible (X, Y) pairs: (1, 4), (2, 4), (3, 4)
                                                   (1, 5), (2, 5), (3, 5)
        '''
        # Calculate wave properties
        wavelength = speed / frequency  # λ = propagation speed / f
        k = 2 * np.pi / wavelength  # Wavenumber (2π/λ)
        delay_rad = np.deg2rad(delay_deg)  # Convert delay from degrees to radians

        # Determine antenna x positions, evenly spaced and centered around 0
        antenna_positions = np.linspace(-((num_antennas - 1) * distance_m) / 2,
                                        ((num_antennas - 1) * distance_m) / 2,
                                        num_antennas)

        if array_geometry == "Curved":
            curvature = self.curvature
            y_positions = -curvature * (antenna_positions ** 2)  # Change Y positions only
        else:
            y_positions = np.full_like(antenna_positions, 0)  # If linear, set all y positions to 0

        # Superimpose waves from all antennas (superposition principle)
        self.Z = np.zeros_like(self.X) # a 2D array that contains the calculated wave amplitude values for each point on the grid
        for i, (x_pos, y_pos) in enumerate(zip(antenna_positions, y_positions)):
            R = np.sqrt((self.X - x_pos) ** 2 + (self.Y - y_pos) ** 2) # Calculate the distance R from the antenna to each grid point.
            phase_delay = -i * delay_rad # Apply a phase delay (phase_delay) for each antenna.

            # Based on the selected wave_type, add the contribution to the grid self.Z
            if wave_type == "Isotropic":
                self.Z += np.sin(k * R + phase_delay) # equation of sine wave as a function of position R
            elif wave_type == "Sinc":
                self.Z += np.sinc(k * R / np.pi + phase_delay)
            elif wave_type == "Gaussian":
                self.Z += np.exp(-((R - i * delay_rad) ** 2) / (2 * wavelength ** 2))
            elif wave_type == "Cosine":
                self.Z += np.cos(k * R + phase_delay)

        # Plot heatmap
        heatmap = ax.imshow(self.Z, cmap="gray", extent=[-extent, extent, -extent, extent]) # Displays the wave pattern (self.Z) as a grayscale image.
        self.heatmap_fig.colorbar(heatmap, ax=ax) # Adds a color bar to show the scale.

        # Plot antenna positions
        ax.scatter(antenna_positions, y_positions, color="blue", s=50, label="Antenna")

        # Add labels and title
        ax.set_title(f"{wave_type} Wave Heatmap")
        ax.set_xlabel("Distance (m)")
        ax.set_ylabel("Distance (m)")
        ax.legend()
        self.heatmap_canvas.draw()

    # plotting a cross-section (profile) of the heatmap, either horizontally or vertically.
    def plot_beam_profile(self):
        # Clear the previous figure
        self.profile_fig.clear()

        # # Create a polar subplot
        # ax = self.profile_fig.add_subplot(111, polar=True)

        # # Get the user's choice for the profile orientation
        # profile_orientation = self.profile_orientation_combo.currentText()

        # # Calculate the data for the polar plot
        # if profile_orientation == "Horizontal":
        #     central_row = self.Z[self.Z.shape[0] // 2, :]  # Central row of the heatmap
        #     angles = np.linspace(-np.pi, np.pi, len(central_row))  # Angle values in radians
        #     values = central_row
        # else:
        #     central_column = self.Z[:, self.Z.shape[1] // 2]  # Central column of the heatmap
        #     angles = np.linspace(-np.pi / 2, np.pi / 2, len(central_column))  # Angle values for vertical profile
        #     values = central_column

        # # Plot the data in polar coordinates
        # ax.plot(angles, values, label=f"{profile_orientation} Beam Profile")

        # # Add labels and title
        # ax.set_title(f"Beam Profile ({profile_orientation} Slice)")
        # ax.legend(loc="upper right")
        # self.profile_canvas.draw()

        ax = self.profile_fig.add_subplot(111)

        # Gets the user's choice for the profile orientation (Horizontal or Vertical)
        profile_orientation = self.profile_orientation_combo.currentText()

        # Plot the central row or column of the heatmap
        if profile_orientation == "Horizontal":
            central_row = self.Z[self.Z.shape[0] // 2, :] # Gets the central row of the heatmap
            ax.plot(self.X[0, :], central_row, label="Horizontal Beam Profile") # Plots the central row against x values
            ax.set_xlabel("X-axis")
        else:
            central_column = self.Z[:, self.Z.shape[1] // 2] # Gets the central column of the heatmap
            ax.plot(self.Y[:, 0], central_column, label="Vertical Beam Profile") # Plots the central column against y values
            ax.set_xlabel("Y-axis")
        '''
        when you take the middle row or column of self.Z, you are extracting a 1D slice of the 2D wave distribution, which represents the wave intensity (or amplitude) along a specific axis (x and y).
        '''

        # Add labels and title
        ax.set_title(f"Beam Profile ({profile_orientation} Slice)")
        ax.set_ylabel("Amplitude")
        ax.legend()
        self.profile_canvas.draw()

    def generate_heatmap_and_profile(self):
        self.plot_heatmap()
        self.plot_beam_profile()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = HeatMapWindow()
    main_window.show()
    sys.exit(app.exec_())
