class BeamformingSystem:
    def __init__(self):
        self.arrays = []
        self.frequencies = []

    def add_array(self, phased_array):
        """Add a phased array to the system."""
        self.arrays.append(phased_array)

    def compute_combined_output(self):
        """Combine outputs from all arrays to calculate interference map."""
        combined_map = None
        for array in self.arrays:
            output = array.compute_interference(frequency=self.frequencies[0])
            combined_map = combined_map + output if combined_map else output
        return combined_map
