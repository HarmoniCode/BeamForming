################## add Scenarios here ######################


class ScenarioManager:
    @staticmethod
    def load_scenario(file_path):
        """Load a scenario from a file."""
        with open(file_path, 'r') as file:
            pass
            # return json.load(file)

    @staticmethod
    def save_scenario(file_path, scenario_data):
        """Save a scenario to a file."""
        with open(file_path, 'w') as file:
            pass
            # json.dump(scenario_data, file)
