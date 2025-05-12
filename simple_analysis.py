import requests
import json
import os

def analyze_with_lm_studio(profile_data, lm_studio_url="http://localhost:1234"):
    prompt = f"""Analyze the following user profile and classify their primary area of interest (e.g., Blockchain Development, AI Engineering, etc.) based on their skills, experience, and career goals: {json.dumps(profile_data)}"""
    classification = None
    try:
        response = requests.post(f"{lm_studio_url}/v1/chat/completions", json={
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100
        })
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        classification = result['choices'][0]['message']['content'].strip()

        student_name = profile_data.get('personalInformation', {}).get('fullName', 'unknown').replace(" ", "_")
        filename = f"{student_name}_analysis.json"
        filepath = os.path.join("analysis_results", filename)
        os.makedirs("analysis_results", exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump({"classification": classification}, f, indent=4)
        print(f"Classification saved to: {filepath}")

        return classification
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to LM Studio: {e}")
        return None

def recommend_tasks(classification, lm_studio_url="http://localhost:1234"):
    prompt = f"Based on the profile classification: '{classification}', recommend 2-3 specific learning tasks or areas to explore."
    recommendations = []
    try:
        response = requests.post(f"{lm_studio_url}/v1/chat/completions", json={
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150
        })
        response.raise_for_status()
        result = response.json()
        recommendations = [task.strip() for task in result['choices'][0]['message']['content'].strip().split('\n') if task.strip()]
        return recommendations
    except requests.exceptions.RequestException as e:
        print(f"Error during recommendation: {e}")
        return []

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    student_profile_data = load_json("data/studentProfile.json")

    if student_profile_data and 'students' in student_profile_data:
        for student in student_profile_data['students']:
            classification = analyze_with_lm_studio(student)
            if classification:
                print(f"Profile Classification for {student['personalInformation']['fullName']}: {classification}")
                recommendations = recommend_tasks(classification)
                if recommendations:
                    print("Recommended Tasks:")
                    for task in recommendations:
                        print(f"- {task}")
            else:
                print(f"Failed to classify profile for {student['personalInformation']['fullName']}.")
    else:
        print("Failed to load student profile data correctly.")

if __name__ == "__main__":
    main()