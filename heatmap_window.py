import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QSizePolicy,
    QSpacerItem,
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QSlider,
    QLabel,
    QFrame,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys
import logging
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename='logging.log', filemode='w'
)
logger = logging.getLogger()

class HeatMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.info("Initializing HeatMapWindow")
        self.setWindowTitle("Beamforming Simulator")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize default values
        self.num_antennas = 10
        self.distance_m = 2  # (1/Distance) * wavelength
        self.delay_deg = 0  # Delay in degrees
        self.frequency = 100  # Default: 100 Hz
        self.propagation_speed = 100  # Default: Speed of light in m/s
        self.array_geometry = "Linear"  # Default array geometry
        self.curvature = 0.0  # Default curvature for curved array
        self.antenna_frequencies = [
            self.frequency
        ] * self.num_antennas  # Default frequency for all antennas
        self.antenna_positions = [
            -2.25,-1.75,-1.25,-0.75,-0.25,0.25,0.75,1.25,1.75,2.25
        ]
        self.y_positions = [0.00] * self.num_antennas  # Initialize y positions
        self.manual_position_update = False  # Flag to track manual position updates

        self.initUI()

    def initUI(self):
        logging.info("Setting up UI")
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

        profile_frame = QFrame()
        profile_frame.setObjectName("profile_frame")
        profile_frame.setMinimumWidth(800)
        profile_layout = QHBoxLayout()
        profile_layout.setContentsMargins(0, 0, 0, 0)  
        profile_layout.setSpacing(0)  
        profile_frame.setLayout(profile_layout)

        self.profile_fig = Figure()
        self.profile_canvas = FigureCanvas(self.profile_fig)
        self.profile_canvas.setContentsMargins(
            0, 0, 0, 0
        )
        profile_layout.addWidget(self.profile_canvas)
        self.profile_fig.subplots_adjust(left=0.1, right=0.9, top=1.5, bottom=-0.5)

        # Form layout for inputs
        from_frame = QFrame()
        from_frame.setObjectName("form_frame")
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        from_frame.setLayout(self.form_layout)

        five_g_file_path = 'scenarios/5g_scenario.json' 
        ultrasound_file_path = 'scenarios/ultrasound_scenario.json'
        tumor_file_path = 'scenarios/tumor_ablation_scenario.json'

        self._5g_button = QPushButton("5G")
        self._5g_button.clicked.connect(lambda value: self.load_data_from_json(five_g_file_path))

        self.tumor_button = QPushButton("Tumor")
        self.tumor_button.clicked.connect(lambda value: self.load_data_from_json(tumor_file_path))

        self.ultrasound_button = QPushButton("Ultrasound")
        self.ultrasound_button.clicked.connect(lambda value: self.load_data_from_json(ultrasound_file_path))

        H_layout_buttons = QHBoxLayout()
        H_layout_buttons.addWidget(self._5g_button)
        H_layout_buttons.addWidget(self.tumor_button)
        H_layout_buttons.addWidget(self.ultrasound_button)

        self.form_layout.addRow(H_layout_buttons)        

        # Add antenna selector
        self.antenna_selector = QComboBox()
        self.antenna_selector.addItems(
            [f"Antenna {i+1}" for i in range(self.num_antennas)]
        )
        self.antenna_selector.currentIndexChanged.connect(self.update_selected_antenna)
        self.add_labeled_row("Select Antenna:", self.antenna_selector)

        # Add position controls (x and y sliders)
        self.x_position_slider = QDoubleSpinBox()
        self.x_position_slider.setRange(-10, 10)
        self.x_position_slider.setSingleStep(0.1)
        self.x_position_slider.setValue(0)
        self.x_position_slider.valueChanged.connect(self.update_antenna_position)
        self.x_position_slider.setDisabled(True) # Disable by default until an antenna is selected
        self.add_labeled_row("X Position:", self.x_position_slider)

        self.y_position_slider = QDoubleSpinBox()
        self.y_position_slider.setRange(0, 10)
        self.y_position_slider.setSingleStep(0.1)
        self.y_position_slider.setValue(0)
        self.y_position_slider.valueChanged.connect(self.update_antenna_position)
        self.y_position_slider.setDisabled(True) # Disable by default until an antenna is selected
        self.add_labeled_row("Y Position:", self.y_position_slider)

        # Number of antennas
        self.num_antennas_slider = QSlider(
            Qt.Orientation.Horizontal
        )  # Horizontal slider
        self.num_antennas_slider.setMinimum(1)
        self.num_antennas_slider.setMaximum(10)
        self.num_antennas_slider.setValue(self.num_antennas)  
        self.num_antennas_slider.setTickInterval(1)  
        self.num_antennas_slider.setTickPosition(
            QSlider.TicksBelow
        )  

        # Label to display the current value of the slider
        self.num_antennas_label = QLabel(
            f"{self.num_antennas}"
        )  
        self.num_antennas_label.setObjectName("label_with_border")
        self.num_antennas_label.setMinimumWidth(50)
        self.num_antennas_label.setAlignment(Qt.AlignCenter)

        self.num_antennas_slider.valueChanged.connect(
            lambda value: self.num_antennas_label.setText(f"{value}")
        )
        self.num_antennas_slider.valueChanged.connect(
            self.generate_heatmap_and_profile
        )  # Update heatmap and profile dynamically
        self.num_antennas_slider.valueChanged.connect(lambda value: self.enable_disable_frequencies())
        self.num_antennas_slider.valueChanged.connect(lambda value: self.disable_antenna_selector_item())

        num_antennas_layout = QHBoxLayout()
        num_antennas_layout.addWidget(self.num_antennas_slider)
        num_antennas_layout.addWidget(self.num_antennas_label)
        self.add_labeled_row("Number of Antennas:", num_antennas_layout)

        # Distance between antennas
        self.distance_slider = QSlider(Qt.Horizontal)  
        self.distance_slider.setMinimum(1)
        self.distance_slider.setMaximum(20)
        self.distance_slider.setValue(self.distance_m)  # Set default value
        self.distance_slider.setTickInterval(1)  
        self.distance_slider.setTickPosition(
            QSlider.TicksBelow
        )  

        # Label to display the current value of the slider
        self.distance_label = QLabel(f"{self.distance_m}")  # Display initial value
        self.distance_label.setObjectName("label_with_border")
        self.distance_label.setMinimumWidth(50)
        self.distance_label.setAlignment(Qt.AlignCenter)

        # Connect slider value change signal to update the label
        self.distance_slider.valueChanged.connect(
            lambda value: self.distance_label.setText(f"λ/{value}")
        )
        self.distance_slider.valueChanged.connect(
            self.generate_heatmap_and_profile
        )  # Update heatmap and profile dynamically

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
        self.delay_slider.setTickPosition(
            QSlider.TicksBelow
        )  # Show ticks below the slider

        # Label to display the current value of the slider
        self.delay_label = QLabel(f"{self.distance_m}")  # Display initial value
        self.delay_label.setObjectName("label_with_border")
        self.delay_label.setMinimumWidth(50)
        self.delay_label.setAlignment(Qt.AlignCenter)

        # Connect slider value change signal to update the label
        self.delay_slider.valueChanged.connect(
            lambda value: self.delay_label.setText(f"{value}")
        )
        self.delay_slider.valueChanged.connect(
            self.generate_heatmap_and_profile
        )  # Update heatmap and profile dynamically

        delay_layout = QHBoxLayout()
        delay_layout.setAlignment(Qt.AlignCenter)
        delay_layout.addWidget(self.delay_slider)
        delay_layout.addWidget(self.delay_label)
        self.add_labeled_row("Delay between antennas (in degrees): ", delay_layout)

        # Frequency of All Antennas
        self.frequency_spinbox = QDoubleSpinBox()
        self.frequency_spinbox.setSingleStep(1)
        self.frequency_spinbox.setValue(self.frequency)
        self.frequency_spinbox.setMaximum(1e20)  # Large max value
        self.frequency_spinbox.valueChanged.connect(
            self.generate_heatmap_and_profile
        )  # Update heatmap and profile dynamically

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
        self.array_geometry_combo.currentTextChanged.connect(
            self.toggle_curvature_slider
        )
        self.array_geometry_combo.currentTextChanged.connect(self.generate_heatmap_and_profile) 
        self.add_labeled_row("Array Geometry: ", self.array_geometry_combo)

        # Curvature slider
        self.curvature_slider = QSlider(Qt.Horizontal)
        self.curvature_slider.setMinimum(0)
        self.curvature_slider.setMaximum(100)
        self.curvature_slider.setValue(0)
        self.curvature_slider.setTickInterval(10)
        self.curvature_slider.valueChanged.connect(self.update_curvature)
        self.curvature_slider.valueChanged.connect(
            self.generate_heatmap_and_profile
        )  # Update heatmap and profile dynamically
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
            spinbox.setMaximum(1e20)
            spinbox.setMinimum(1)
            spinbox.valueChanged.connect(
                lambda value, idx=i: self.update_antenna_frequency(idx, value)
            )
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

    def disable_antenna_selector_item(self): 
        model = self.antenna_selector.model()

        for index in range(len(self.frequency_controls)):
            item = model.item(index)
            if index < self.num_antennas_slider.value(): 
                item.setEnabled(True)
            else:
                item.setEnabled(False)

    def enable_disable_frequencies(self):
        for i in range(len(self.frequency_controls)):
            if i < self.num_antennas_slider.value():
                self.frequency_controls[i].setDisabled(False)
            else:
                self.frequency_controls[i].setDisabled(True)

    def load_data_from_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)

        distance = data["distance_m"]
        delay = data["delay_deg"]
        num_antennas = data["num_antennas"]
        array_geometry = data["array_geometry"]
        curvature = data["curvature"]

        frequencies = data.get("frequencies", [])
        for i, frequency in enumerate(frequencies):
                self.frequency_controls[i].setValue(frequency)

        if file_path == 'scenarios/tumor_ablation_scenario.json':
            self.curvature_slider.setDisabled(False)

        else: 
            self.curvature_slider.setDisabled(True)
        
        self.array_geometry_combo.setCurrentText(array_geometry)
        self.curvature_slider.setValue(curvature)
        self.num_antennas_slider.setValue(num_antennas)
        self.distance_slider.setValue(distance)
        self.delay_slider.setValue(delay)

        self.generate_heatmap_and_profile()

    def add_labeled_row(self, label_text, widget):
        logging.info(f"Adding labeled row: {label_text}")
        label_frame = QFrame()
        label_frame.setObjectName("label_frame")
        label_frame.setMinimumWidth(300)
        label_frame.setMaximumWidth(300)

        label_layout = QHBoxLayout()
        label_frame.setLayout(label_layout)
        label = QLabel(label_text)
        label_layout.addWidget(label)
        label_layout.addSpacerItem(
            QSpacerItem(50, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.form_layout.addRow(label_frame, widget)
    
    def reset_antenna_positions(self):
        logging.info("Resetting antenna positions")
        self.antenna_positions = [
            -2.25,-1.75,-1.25,-0.75,-0.25,0.25,0.75,1.25,1.75,2.25
        ]
        self.y_positions = [0.00] * self.num_antennas
        self.x_position_slider.setValue(0.00)
        self.y_position_slider.setValue(0.00)

    def update_selected_antenna(self):
        logging.info("Updating selected antenna")
        self.x_position_slider.setDisabled(False) # enable the x position spinbox
        self.y_position_slider.setDisabled(False) # enable the y position spinbox
        index = self.antenna_selector.currentIndex()
        self.x_position_slider.setValue(self.antenna_positions[index])
        self.y_position_slider.setValue(self.y_positions[index])

    def update_antenna_position(self):
        logging.info("Updating antenna position")
        index = self.antenna_selector.currentIndex()
        self.antenna_positions[index] = self.x_position_slider.value()
        self.y_positions[index] = self.y_position_slider.value()
        print(f"the y positions are now: {self.y_positions}")
        self.manual_position_update = True  # Indicate manual update
        self.generate_heatmap_and_profile()

    def update_antenna_frequency(self, index, value):
        logging.info(f"Updating frequency of antenna {index + 1} to {value} Hz")
        self.antenna_frequencies[index] = value

    def toggle_curvature_slider(self, value):
        logging.info(f"Toggling curvature slider: {value}")
        if value == "Curved":
            self.curvature_slider.setDisabled(False)
            self.antenna_selector.setDisabled(True)
            self.x_position_slider.setDisabled(True)
            self.y_position_slider.setDisabled(True)
            self.reset_antenna_positions()
        else:
            self.curvature_slider.setDisabled(True)
            self.antenna_selector.setDisabled(False)
            self.x_position_slider.setDisabled(False)
            self.y_position_slider.setDisabled(False)
            self.curvature = 0.0  # Reset curvature
            self.curvature_slider.setValue(0)  # Reset slider value

    def update_curvature(self, value):
        logging.info(f"Updating curvature to {value}")
        self.curvature = value / 100  # Normalize curvature value

    def plot_heatmap(self):
        logging.info("Plotting heatmap")
        # Clear the previous figure
        self.heatmap_fig.clear()

        ax = self.heatmap_fig.add_subplot(
            111
        )  # 111 means a single subplot in a 1x1 grid.

        # Retrieve user inputs
        num_antennas = self.num_antennas_slider.value()
        distance_m = self.distance_slider.value()
        delay_deg = self.delay_slider.value()
        # frequency = self.frequency_spinbox.value()
        frequency = max(self.antenna_frequencies)
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
        x = np.linspace(
            -extent, extent, size
        )  # Generates 500 equally spaced points between -10 and 10
        y = np.linspace(0, 20, size)
        self.X, self.Y = np.meshgrid(
            x, y
        )  # Creates two 2D arrays (self.X and self.Y) representing the x and y coordinates at each grid point

        if not self.manual_position_update:
            # Determine antenna x positions, evenly spaced and centered around 0
            self.antenna_positions = np.linspace(
                -((num_antennas - 1) * distance_lambda) / 2,
                ((num_antennas - 1) * distance_lambda) / 2,
                num_antennas,
            )

            if array_geometry == "Curved":
                curvature = self.curvature
                self.y_positions = 0.01 * np.max(self.Y) + curvature * (
                    self.antenna_positions**2
                )  # baseline Y-offset for all antennas + quadratic term which creates the parabolic curve
            # elif array_geometry == "Downward Curved":
            #     curvature = self.curvature
            #     center_x_value = 0.00
            #     self.y_positions = 0.01 * np.max(self.Y) - curvature * ((center_x_value - self.antenna_positions)**2)
            else:
                self.y_positions = np.full_like(
                    self.antenna_positions, 0
                )  # If linear, set all y positions to 0
        else:
            # Reset the flag after using the manually updated positions
            self.manual_position_update = False

        # Superimpose waves from all antennas (superposition principle)
        self.Waves_Sum = np.zeros_like(
            self.X
        )  # a 2D array that contains the calculated wave amplitude values for each point on the grid


        max_frequency = max(self.antenna_frequencies)

        # Update the loop in the plot_heatmap method to use the individual frequencies:
        for i, (x_pos, y_pos) in enumerate(
            zip(self.antenna_positions, self.y_positions)
        ):
            frequency = self.antenna_frequencies[i]
            wavelength = self.propagation_speed / frequency
            k = 2 * np.pi / wavelength

            # Normalize contribution based on frequency relative to max frequency
            frequency_scaling = frequency / max_frequency

            R = np.sqrt((self.X - x_pos) ** 2 + (self.Y - y_pos) ** 2)
            phase_delay = -i * delay_rad

            # self.Waves_Sum += np.sin(k * R + phase_delay) # Waves_Sum ->previously called Z<-
            self.Waves_Sum += frequency_scaling * np.sin(k * R + phase_delay)


        # Calculate wave amplitude with scaling
        Waves_Sum = np.abs(self.Waves_Sum)  # Take absolute value
        
        # Apply logarithmic scaling
        Waves_Sum_log = np.log1p(Waves_Sum) # log1p(x)=ln(1+x) to avoid zero values issue
        
        # Normalize to [0, 1] range
        Waves_Sum_normalized = (Waves_Sum_log - Waves_Sum_log.min()) / (Waves_Sum_log.max() - Waves_Sum_log.min())

        # Plot heatmap
        heatmap = ax.imshow(
            Waves_Sum_normalized, cmap="coolwarm", extent=[-extent, extent, 0, 20], origin="lower", vmin=-1, 
        vmax=1 #, interpolation="gaussian"
        )  # Displays the wave pattern (self.Waves_Sum) as a grayscale image.
        self.heatmap_fig.colorbar(
            heatmap, ax=ax, label="Intensity"
        )  # Adds a color bar to show the scale.

        # Plot antenna positions
        ax.scatter(
            self.antenna_positions,
            self.y_positions,
            color="blue",
            s=50,
            label="Antenna",
        )

        # Add labels and title
        ax.legend()
        self.heatmap_canvas.draw()

    def plot_beam_profile(self):
        logging.info("Plotting beam profile")
        # Retrieve user inputs
        num_antennas = self.num_antennas_slider.value()
        distance_m = self.distance_slider.value()
        delay_deg = self.delay_slider.value()
        delay_rad = np.deg2rad(delay_deg)
        # frequency = self.frequency_spinbox.value()
        frequency = max(self.antenna_frequencies)
        speed = self.propagation_speed
        # distance_lambda = (1 / distance_m) * wavelength

        self.profile_fig.clear()

        # Calculate wave properties
        wavelength = speed / frequency  # λ = propagation speed / f
        # if distance_m != 0:
        #     distance_lambda = (1 / distance_m) * wavelength  # Distance in wavelengths
        # else:
        #     distance_lambda = 0
        k = 2 * np.pi / wavelength  # Wavenumber (2π/λ)
        delay_rad = np.deg2rad(delay_deg)  # Convert delay from degrees to radians

        # Create arrays to store individual antenna parameters
        frequencies = self.antenna_frequencies
        x_positions = self.antenna_positions  # Array for x positions
        y_positions = self.y_positions  # Array for y positions
        phases = np.zeros(num_antennas)  # Array for phase delays

        for i, (x_pos, y_pos) in enumerate(
            zip(self.antenna_positions, self.y_positions)
        ):
            phases[i] = -i * delay_rad

        # Calculate beam pattern
        azimuth_angles = np.linspace(0, 2 * np.pi, 360)
        Beam_Summation = np.zeros_like(azimuth_angles, dtype=complex) # -> AF previously <-

        for i in range(num_antennas):
            # Convert Cartesian positions to polar coordinates
            r = np.sqrt(x_positions[i] ** 2 + y_positions[i] ** 2)
            theta = np.arctan2(y_positions[i], x_positions[i])
            # Calculate phase term including both position components and frequency
            phase_term = (
                -k * (frequencies[i] / frequency) * r * np.cos(azimuth_angles - theta)
                + phases[i]
            )

            Beam_Summation += np.exp(1j * phase_term)

        # Plot the gain pattern on a polar graph
        ax = self.profile_fig.add_subplot(111, polar=True)
        ax.plot(azimuth_angles, np.abs(Beam_Summation))
        # plt.show()

        ax.set_yticklabels([])

        # Configure the polar plot to show only half the circle (0 to 180 degrees or 0 to π radians)
        ax.set_theta_offset(0)  # Start at 0°
        ax.set_theta_direction(1)  # Clockwise direction
        ax.set_xlim([0, np.pi])  # Limit the visible angle range to 0 to π (half-circle)

        # Remove the upper half-circle and set the limits to the bottom half only
        ax.set_ylim(
            0, np.max(np.abs(Beam_Summation))
        )  # Optionally adjust the radial limits if needed

        # Add labels and title
        # ax.set_title("Beam Profile)")
        # ax.legend()
        self.profile_canvas.draw()

    def generate_heatmap_and_profile(self):
        logging.info("Generating heatmap and profile")
        self.plot_heatmap()
        self.plot_beam_profile()

