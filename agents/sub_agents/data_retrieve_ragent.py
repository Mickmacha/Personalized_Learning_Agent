from google.adk.agents import Agent 
from tools.json_data_loader import load_json_data

class DataRetrieverAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.profile_analyzer = None

    def set_profile_analyzer(self, profile_analyzer):
        self.profile_analyzer = profile_analyzer

    async def get_user_profile(self, file_path: str):
        user_profile = load_json_data(file_path)
        if user_profile and self.profile_analyzer:
            return user_profile
        elif not user_profile:
            print("Error loading user profile.")
            return None
        return user_profile

    # No handle_message needed if using direct calls

    def describe(self):
        return "Retrieves user profile data from a specified JSON file."