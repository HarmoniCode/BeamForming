import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QSizePolicy, QSpacerItem, QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QSpinBox, QDoubleSpinBox,
                             QComboBox, QPushButton, QSlider, QLabel, QFrame)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class HeatMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.debug("Initializing HeatMapWindow")
        self.setWindowTitle("Beamforming Simulator")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize default values
        self.num_antennas = 10
        self.distance_m = 2  # Distance in meters -> 1/2 wavelength
        self.delay_deg = 0  # Delay in degrees
        self.frequency = 100  # Default: 100 Hz
        self.propagation_speed = 100  # Default: Speed of light in m/s
        self.array_geometry = "Linear"  # Default array geometry
        self.curvature = 0.0  # Default curvature for curved array
        self.antenna_frequencies = [self.frequency] * self.num_antennas  # Default frequency for all antennas
        self.manual_position_update = False  # Flag to track manual position updates

        self.initUI()

    def initUI(self):
        logging.debug("Setting up UI")
        # Central widget for the window
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Create the Matplotlib figures and canvases
        heatmap_frame = QFrame()
        heatmap_frame.setObjectName("heatmap_frame")
        heatmap_frame.setMinimumWidth(800)
        heatmap_layout = QHBoxLayout()
        heatmap_frame.setLayout(heatmap_layout)
        self.heatmap_fig = Figure()
        self.heatmap_canvas = FigureCanvas(self.heatmap_fig)
        heatmap_layout.addWidget(self.heatmap_canvas)
        self.heatmap_fig.subplots_adjust(left=-0.35, right=1, top=0.9, bottom=0.1)

        profile_frame = QFrame()
        profile_frame.setObjectName("profile_frame")
        profile_frame.setMinimumWidth(800)
        profile_layout = QHBoxLayout()
        profile_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
        profile_layout.setSpacing(0)  # Remove spacing
        profile_frame.setLayout(profile_layout)

        self.profile_fig = Figure()
        self.profile_canvas = FigureCanvas(self.profile_fig)
        self.profile_canvas.setContentsMargins(0, 0, 0, 0)  # Remove padding from the canvas
        profile_layout.addWidget(self.profile_canvas)
        # Adjust subplot parameters to reduce padding around the plot area
        self.profile_fig.subplots_adjust(left=0.1, right=0.9, top=1.5, bottom=-0.5)

        # Form layout for inputs
        from_frame = QFrame()
        from_frame.setObjectName("form_frame")
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        from_frame.setLayout(self.form_layout)

        # Add antenna selector
        self.antenna_selector = QComboBox()
        self.antenna_selector.addItems([f"Antenna {i+1}" for i in range(self.num_antennas)])
        self.antenna_selector.currentIndexChanged.connect(self.update_selected_antenna)
        self.add_labeled_row("Select Antenna:", self.antenna_selector)

        # Add position controls (x and y sliders)
        self.x_position_slider = QDoubleSpinBox()
        self.x_position_slider.setRange(-10, 10)
        self.x_position_slider.setSingleStep(0.1)
        self.x_position_slider.setValue(0)
        self.x_position_slider.valueChanged.connect(self.update_antenna_position)
        self.add_labeled_row("X Position:", self.x_position_slider)

        self.y_position_slider = QDoubleSpinBox()
        self.y_position_slider.setRange(0, 10)
        self.y_position_slider.setSingleStep(0.1)
        self.y_position_slider.setValue(0)
        self.y_position_slider.valueChanged.connect(self.update_antenna_position)
        self.add_labeled_row("Y Position:", self.y_position_slider)

        # Number of antennas
        self.num_antennas_slider = QSlider(Qt.Orientation.Horizontal)  # Horizontal slider
        self.num_antennas_slider.setMinimum(1)
        self.num_antennas_slider.setMaximum(10)
        self.num_antennas_slider.setValue(self.num_antennas)  # Set default value
        self.num_antennas_slider.setTickInterval(1)  # Set tick intervals
        self.num_antennas_slider.setTickPosition(QSlider.TicksBelow)  # Show ticks below the slider

        # Label to display the current value of the slider
        self.num_antennas_label = QLabel(f"{self.num_antennas}")  # Display initial value
        self.num_antennas_label.setObjectName("label_with_border")
        self.num_antennas_label.setMinimumWidth(50)
        self.num_antennas_label.setAlignment(Qt.AlignCenter)

        # Connect slider value change signal to update the label
        self.num_antennas_slider.valueChanged.connect(
            lambda value: self.num_antennas_label.setText(f"{value}")
        )
        self.num_antennas_slider.valueChanged.connect(self.generate_heatmap_and_profile)  # Update heatmap and profile dynamically

        num_antennas_layout = QHBoxLayout()
        num_antennas_layout.addWidget(self.num_antennas_slider)
        num_antennas_layout.addWidget(self.num_antennas_label)
        self.add_labeled_row("Number of Antennas:", num_antennas_layout)

        # Distance between antennas
        self.distance_slider = QSlider(Qt.Horizontal)  # Horizontal slider
        self.distance_slider.setMinimum(1)
        self.distance_slider.setMaximum(10)
        self.distance_slider.setValue(self.distance_m)  # Set default value
        self.distance_slider.setTickInterval(1)  # Set tick intervals
        self.distance_slider.setTickPosition(QSlider.TicksBelow)  # Show ticks below the slider

        # Label to display the current value of the slider
        self.distance_label = QLabel(f"{self.distance_m}")  # Display initial value
        self.distance_label.setObjectName("label_with_border")
        self.distance_label.setMinimumWidth(50)
        self.distance_label.setAlignment(Qt.AlignCenter)

        # Connect slider value change signal to update the label
        self.distance_slider.valueChanged.connect(
            lambda value: self.distance_label.setText(f"{value}/λ")
        )
        self.distance_slider.valueChanged.connect(self.generate_heatmap_and_profile)  # Update heatmap and profile dynamically

        distance_layout = QHBoxLayout()
        distance_layout.addWidget(self.distance_slider)
        distance_layout.addWidget(self.distance_label)
        self.add_labeled_row("Distance between antennas: ", distance_layout)

        # Delay between antennas
        self.delay_slider = QSlider(Qt.Horizontal)  # Horizontal slider
        self.delay_slider.setMinimum(-180)
        self.delay_slider.setMaximum(180)
        self.delay_slider.setValue(self.delay_deg)  # Set default value
        self.delay_slider.setTickInterval(5)  # Set tick intervals
        self.delay_slider.setTickPosition(QSlider.TicksBelow)  # Show ticks below the slider

        # Label to display the current value of the slider
        self.delay_label = QLabel(f"{self.distance_m}")  # Display initial value
        self.delay_label.setObjectName("label_with_border")
        self.delay_label.setMinimumWidth(50)
        self.delay_label.setAlignment(Qt.AlignCenter)

        # Connect slider value change signal to update the label
        self.delay_slider.valueChanged.connect(
            lambda value: self.delay_label.setText(f"{value}")
        )
        self.delay_slider.valueChanged.connect(self.generate_heatmap_and_profile)  # Update heatmap and profile dynamically

        delay_layout = QHBoxLayout()
        delay_layout.setAlignment(Qt.AlignCenter)
        delay_layout.addWidget(self.delay_slider)
        delay_layout.addWidget(self.delay_label)
        self.add_labeled_row("Delay between antennas (in degrees): ", delay_layout)

        # Frequency of All Antennas
        self.frequency_spinbox = QDoubleSpinBox()
        self.frequency_spinbox.setSingleStep(1)
        self.frequency_spinbox.setValue(self.frequency)
        self.frequency_spinbox.setMaximum(1e12)  # Large max value
        self.frequency_spinbox.valueChanged.connect(self.generate_heatmap_and_profile)  # Update heatmap and profile dynamically

        # label_frame = QFrame()
        # label_frame.setObjectName("label_frame")
        # label_frame.setMinimumWidth(300)
        # label_layout = QHBoxLayout()
        # label_frame.setLayout(label_layout)
        # label = QLabel("Signal Frequency (Hz):")
        # label_layout.addWidget(label)
        # label_layout.addSpacerItem(QSpacerItem(50, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        # self.form_layout.addRow(label_frame, self.frequency_spinbox)
        

        # Array geometry type (Linear or Curved)
        self.array_geometry_combo = QComboBox()
        self.array_geometry_combo.addItems(["Linear", "Curved"])
        self.array_geometry_combo.currentTextChanged.connect(self.toggle_curvature_slider)
        self.add_labeled_row("Array Geometry: ", self.array_geometry_combo)

        # Curvature slider
        self.curvature_slider = QSlider(Qt.Horizontal)
        self.curvature_slider.setMinimum(0)
        self.curvature_slider.setMaximum(100)
        self.curvature_slider.setValue(0)
        self.curvature_slider.setTickInterval(10)
        self.curvature_slider.valueChanged.connect(self.update_curvature)
        self.curvature_slider.valueChanged.connect(self.generate_heatmap_and_profile)  # Update heatmap and profile dynamically
        self.curvature_slider.setDisabled(True)
        self.add_labeled_row("Curvature (0 = Flat): ", self.curvature_slider)

        # Frequency controls for each antenna
        self.frequency_controls = []
        frequency_frame = QFrame()
        frequency_frame.setObjectName("frequency_frame")
        frequency_layout = QVBoxLayout(frequency_frame)
        frequency_layout.setSpacing(10)

        for i in range(self.num_antennas):
            H_layout = QHBoxLayout()
            spinbox = QDoubleSpinBox()
            spinbox.setValue(self.frequency)  # Default frequency
            spinbox.setSingleStep(1)
            spinbox.setMaximum(1e12)
            spinbox.setMinimum(1)
            spinbox.valueChanged.connect(lambda value, idx=i: self.update_antenna_frequency(idx, value))
            self.frequency_controls.append(spinbox)
            frequency_label = QLabel(f"Frequency of Antenna {i+1} (Hz):")
            frequency_label.setObjectName("frequency_label")
            frequency_label.setMaximumWidth(250)
            H_layout.addWidget(frequency_label)
            H_layout.addWidget(spinbox)
            frequency_layout.addLayout(H_layout)

        self.form_layout.addRow("Frequencies:", frequency_frame)

        # Generate button
        generate_button = QPushButton("Update Heatmap and Beam Profile")
        generate_button.clicked.connect(self.generate_heatmap_and_profile)
        self.form_layout.addWidget(generate_button)

        layout.addWidget(from_frame)

        # Add canvases to the layout
        canvases_layout = QVBoxLayout()
        canvases_layout.addWidget(heatmap_frame)
        canvases_layout.addWidget(profile_frame)

        layout.addLayout(canvases_layout)

        # Generate initial heatmap and beam profile
        self.generate_heatmap_and_profile()

    def add_labeled_row(self, label_text, widget):
        logging.debug(f"Adding labeled row: {label_text}")
        label_frame = QFrame()
        label_frame.setObjectName("label_frame")
        label_frame.setMinimumWidth(300)
        label_frame.setMaximumWidth(300)

        label_layout = QHBoxLayout()
        label_frame.setLayout(label_layout)
        label = QLabel(label_text)
        label_layout.addWidget(label)
        label_layout.addSpacerItem(QSpacerItem(50, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.form_layout.addRow(label_frame, widget)

    def update_selected_antenna(self):
        logging.debug("Updating selected antenna")
        index = self.antenna_selector.currentIndex()
        self.x_position_slider.setValue(self.antenna_positions[index])
        self.y_position_slider.setValue(self.y_positions[index])

    def update_antenna_position(self):
        logging.debug("Updating antenna position")
        index = self.antenna_selector.currentIndex()
        self.antenna_positions[index] = self.x_position_slider.value()
        self.y_positions[index] = self.y_position_slider.value()
        self.manual_position_update = True  # Indicate manual update
        self.generate_heatmap_and_profile()

    def update_antenna_frequency(self, index, value):
        logging.debug(f"Updating frequency of antenna {index + 1} to {value} Hz")
        self.antenna_frequencies[index] = value

    def toggle_curvature_slider(self, value):
        logging.debug(f"Toggling curvature slider: {value}")
        if value == "Curved":
            self.curvature_slider.setDisabled(False)
        else:
            self.curvature_slider.setDisabled(True)
            self.curvature = 0.0  # Reset curvature

    def update_curvature(self, value):
        logging.debug(f"Updating curvature to {value}")
        self.curvature = value / 100  # Normalize curvature value

    def plot_heatmap(self):
        logging.debug("Plotting heatmap")
        # Clear the previous figure
        self.heatmap_fig.clear()

        ax = self.heatmap_fig.add_subplot(111)  # 111 means a single subplot in a 1x1 grid.

        # Retrieve user inputs
        num_antennas = self.num_antennas_slider.value()
        distance_m = self.distance_slider.value()
        delay_deg = self.delay_slider.value()
        frequency = self.frequency_spinbox.value()
        speed = self.propagation_speed
        array_geometry = self.array_geometry_combo.currentText()

        # Calculate wave properties
        wavelength = speed / frequency  # λ = propagation speed / f
        if distance_m != 0:
            distance_lambda = (1 / distance_m) * wavelength  # Distance in wavelengths
        else:
            distance_lambda = 0
        k = 2 * np.pi / wavelength  # Wavenumber (2π/λ)
        delay_rad = np.deg2rad(delay_deg)  # Convert delay from degrees to radians

        # Generate grid for the heatmap
        size = 500  # Grid size:  number of points along each axis (500x500 grid)
        extent = 10  # Coordinate range (-extent to extent): the grid covers coordinates from -10 to 10
        x = np.linspace(-extent, extent, size)  # Generates 500 equally spaced points between -10 and 10
        y = np.linspace(0, 20, size)
        self.X, self.Y = np.meshgrid(x, y)  # Creates two 2D arrays (self.X and self.Y) representing the x and y coordinates at each grid point

        if not self.manual_position_update:
            # Determine antenna x positions, evenly spaced and centered around 0
            self.antenna_positions = np.linspace(-((num_antennas - 1) * distance_lambda) / 2,
                                                 ((num_antennas - 1) * distance_lambda) / 2,
                                                 num_antennas)

            if array_geometry == "Curved":
                curvature = self.curvature
                self.y_positions = 0.4 * np.max(self.Y) - curvature * (self.antenna_positions ** 2)  # Change Y positions only
            else:
                self.y_positions = np.full_like(self.antenna_positions, 0)  # If linear, set all y positions to 0
        else:
            # Reset the flag after using the manually updated positions
            self.manual_position_update = False

        # Superimpose waves from all antennas (superposition principle)
        self.Z = np.zeros_like(self.X)  # a 2D array that contains the calculated wave amplitude values for each point on the grid

        # Update the loop in the plot_heatmap method to use the individual frequencies:
        for i, (x_pos, y_pos) in enumerate(zip(self.antenna_positions, self.y_positions)):
            frequency = self.antenna_frequencies[i]
            wavelength = self.propagation_speed / frequency
            k = 2 * np.pi / wavelength
            R = np.sqrt((self.X - x_pos) ** 2 + (self.Y - y_pos) ** 2)
            phase_delay = -i * delay_rad
            self.Z += np.sin(k * R + phase_delay)

        # Plot heatmap
        heatmap = ax.imshow(self.Z, cmap="gray", extent=[-extent, extent, 0, 20], origin='lower')  # Displays the wave pattern (self.Z) as a grayscale image.
        self.heatmap_fig.colorbar(heatmap, ax=ax, label="Intensity")  # Adds a color bar to show the scale.

        # Plot antenna positions
        ax.scatter(self.antenna_positions, self.y_positions, color="blue", s=50, label="Antenna")

        # Add labels and title
        ax.legend()
        self.heatmap_canvas.draw()

    def plot_beam_profile(self):
        logging.debug("Plotting beam profile")
        # Retrieve user inputs
        num_antennas = self.num_antennas_slider.value()
        distance_m = self.distance_slider.value()
        delay_deg = self.delay_slider.value()
        delay_rad = np.deg2rad(delay_deg)
        frequency = self.frequency_spinbox.value()
        speed = self.propagation_speed

        self.profile_fig.clear()

        # Calculate wave properties
        wavelength = speed / frequency  # λ = propagation speed / f
        if distance_m != 0:
            distance_lambda = (1 / distance_m) * wavelength  # Distance in wavelengths
        else:
            distance_lambda = 0
        k = 2 * np.pi / wavelength  # Wavenumber (2π/λ)
        delay_rad = np.deg2rad(delay_deg)  # Convert delay from degrees to radians

        # Create arrays to store individual antenna parameters
        frequencies = self.antenna_frequencies
        x_positions = self.antenna_positions  # Array for x positions
        y_positions = self.y_positions  # Array for y positions
        phases = np.zeros(num_antennas)       # Array for phase delays

        for i, (x_pos, y_pos) in enumerate(zip(self.antenna_positions, self.y_positions)):
            phases[i] = -i * delay_rad

        # Calculate beam pattern
        azimuth_angles = np.linspace(0, 2 * np.pi, 360)
        AF = np.zeros_like(azimuth_angles, dtype=complex)

        for i in range(num_antennas):
            # Convert Cartesian positions to polar coordinates
            r = np.sqrt(x_positions[i]**2 + y_positions[i]**2)
            theta = np.arctan2(y_positions[i], x_positions[i])
            
            # Calculate phase term including both position components and frequency
            phase_term = -k * (frequencies[i]/frequency) * r * np.cos(azimuth_angles - theta) + phases[i]
            AF += np.exp(1j * phase_term)

        # Plot the gain pattern on a polar graph
        ax = self.profile_fig.add_subplot(111, polar=True)
        ax.plot(azimuth_angles, np.abs(AF))
        # plt.show()

        ax.set_yticklabels([])

        # Configure the polar plot to show only half the circle (0 to 180 degrees or 0 to π radians)
        ax.set_theta_offset(0)  # Start at 0°
        ax.set_theta_direction(1)  # Clockwise direction
        ax.set_xlim([0, np.pi])  # Limit the visible angle range to 0 to π (half-circle)

        # Remove the upper half-circle and set the limits to the bottom half only
        ax.set_ylim(0, np.max(np.abs(AF)))  # Optionally adjust the radial limits if needed

        # Add labels and title
        # ax.set_title("Beam Profile)")
        # ax.legend()
        self.profile_canvas.draw()

    # def load_data_from_json(file_path):
    #     with open(file_path, 'r') as file:
    #         data = json.load(file)

    #     # Store each value in a variable
    #     num_antennas = data["num_antennas"]
    #     distance_m = data["distance_m"]
    #     delay_deg = data["delay_deg"]
    #     frequency = data["frequency"]
    #     array_geometry = data["array_geometry"]
    #     curvature = data["curvature"]

        
        # # You can now use these variables later
        # return num_antennas, distance_m, delay_deg, frequency, array_geometry, curvature
    
    # Example usage
    # file_path = 'scenarios/ultrasound_scenario.json'  # Replace with the actual path to your JSON file
    # num_antennas, distance_m, delay_deg, frequency, array_geometry, curvature = load_data_from_json(file_path)
        
    def generate_heatmap_and_profile(self):
        logging.debug("Generating heatmap and profile")
        self.plot_heatmap()
        self.plot_beam_profile()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("./Styles/index.qss") as f:
        app.setStyleSheet(f.read())
    main_window = HeatMapWindow()
    main_window.show()
    sys.exit(app.exec_())