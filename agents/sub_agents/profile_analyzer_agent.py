from google.adk.agents import Agent # Corrected import
# from tools.profile_classifier import classify_profile # Removed direct tool call
import json
import httpx

class ProfileAnalyzerAgent(Agent):
    def __init__(self, name=None, classification_system=None):
        super().__init__(name=name)
        self.classification_system = classification_system
        self.task_recommender = None

    def set_task_recommender(self, task_recommender):
        self.task_recommender = task_recommender

    async def analyze_profile(self, user_profile: dict):
        """
        Analyzes the user profile using LM Studio.
        """
        if self.classification_system:
            # Prepare the prompt for LM Studio, incorporating the classification data
            prompt = f"Analyze the following user profile and classify it based on these categories: {json.dumps(self.classification_system)}.  User Profile: {json.dumps(user_profile)}"
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post("http://localhost:1234/v1/chat/completions", json={
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 150  # Adjust as needed
                    })
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                classification_results = response.json()
                return classification_results
            except httpx.HTTPStatusError as e:
                 print(f"HTTP error analyzing profile: {e}")
                 return None
            except httpx.RequestError as e:
                print(f"Error connecting to LM Studio: {e}")
                return None
        else:
            print("Classification system not loaded.")
            return None

    # No handle_message needed

    def describe(self):
        return "Analyzes a user profile and classifies it based on a defined classification system using LM Studio."