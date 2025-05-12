# workflows/analysis_workflow.py
from google.adk.agents import Agent

from agents import DataRetrieverAgent, ProfileAnalyzerAgent, TaskRecommenderAgent
from tools.json_data_loader import load_json_data
# Main Workflow Function
async def run_analysis_workflow(student_profile_path, classification_file_path):
    data_retriever = DataRetrieverAgent(name="data_retriever")
    classification_data = load_json_data(classification_file_path)
    profile_analyzer = ProfileAnalyzerAgent(name="profile_analyzer", classification_system=classification_data)  # Pass classification data
    task_recommender = TaskRecommenderAgent(name="task_recommender")

    # Option 1: Pass references during initialization (if agents need persistent access)
    profile_analyzer.set_task_recommender(task_recommender)
    data_retriever.set_profile_analyzer(profile_analyzer)

    # Option 2: Call methods directly within the workflow
    user_profile = await data_retriever.get_user_profile(student_profile_path)
    if user_profile:
        classification_results = await profile_analyzer.analyze_profile(user_profile)
        if classification_results:
            recommended_tasks = await task_recommender.recommend_tasks(classification_results)
            print(f"Recommended Tasks: {recommended_tasks}")
        else:
            print("Profile analysis failed.")
    else:
        print("Failed to retrieve user profile.")

# Example usage in main.py
if __name__ == "__main__":
    import asyncio
    student_profile_path = "data/studentProfile.json"
    classification_file_path = "data/classification.json"
    asyncio.run(run_analysis_workflow(student_profile_path, classification_file_path))