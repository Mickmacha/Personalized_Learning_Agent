from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from pydantic_ai import Agent
from typing import List, Optional, Dict, Any
import json
import os
import asyncio
from datetime import datetime
import uvicorn

# Data Models
class PersonalInformation(BaseModel):
    fullName: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None

class Skill(BaseModel):
    name: str
    level: str
    category: Optional[str] = None

class Experience(BaseModel):
    title: str
    company: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None

class Education(BaseModel):
    degree: str
    institution: str
    year: Optional[str] = None
    gpa: Optional[float] = None

class StudentProfile(BaseModel):
    personalInformation: PersonalInformation
    skills: List[Skill] = []
    experience: List[Experience] = []
    education: List[Education] = []
    careerGoals: Optional[str] = None
    interests: List[str] = []

class StudentsData(BaseModel):
    students: List[StudentProfile]

class ClassificationResult(BaseModel):
    student_name: str
    classification: str
    confidence: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class RecommendationResult(BaseModel):
    student_name: str
    classification: str
    recommendations: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    results: List[Dict[str, Any]] = []

# Pydantic AI Agents
# Classification Agent
classification_agent = Agent(
    'gemini-1.5-flash',  # Using Gemini model
    system_prompt="""You are an expert career counselor and skills analyzer. 
    Analyze student profiles and classify their primary area of interest based on:
    - Technical skills and proficiency levels
    - Work experience and projects
    - Educational background
    - Stated career goals and interests
    
    Return ONLY the classification category (e.g., "AI/Machine Learning Engineer", 
    "Full-Stack Web Developer", "Data Scientist", "Blockchain Developer", etc.).
    Be specific and precise."""
)

# Recommendation Agent
recommendation_agent = Agent(
    'gemini-1.5-flash',
    system_prompt="""You are a learning path advisor. Based on a student's 
    classification, provide 2-3 specific, actionable learning recommendations.
    
    Format your response as a numbered list with concrete, practical suggestions.
    Focus on skills, technologies, or areas that would most benefit their career development."""
)

# FastAPI App
app = FastAPI(
    title="Student Profile Analysis API",
    description="AI-powered student profile analysis and recommendation system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility Functions
def ensure_results_directory():
    """Ensure the analysis_results directory exists"""
    os.makedirs("analysis_results", exist_ok=True)

def save_analysis_result(student_name: str, classification: str, recommendations: List[str]):
    """Save analysis results to JSON file"""
    ensure_results_directory()
    
    safe_name = student_name.replace(" ", "_").replace("/", "_")
    filename = f"{safe_name}_analysis.json"
    filepath = os.path.join("analysis_results", filename)
    
    result_data = {
        "student_name": student_name,
        "classification": classification,
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat(),
        "analysis_version": "1.0.0"
    }
    
    with open(filepath, 'w') as f:
        json.dump(result_data, f, indent=4)
    
    return filepath

async def analyze_single_student(student: StudentProfile) -> Dict[str, Any]:
    """Analyze a single student profile"""
    try:
        # Prepare profile data for analysis
        profile_summary = {
            "name": student.personalInformation.fullName,
            "skills": [{"name": skill.name, "level": skill.level} for skill in student.skills],
            "experience": [{"title": exp.title, "description": exp.description} for exp in student.experience],
            "education": [{"degree": edu.degree, "institution": edu.institution} for edu in student.education],
            "career_goals": student.careerGoals,
            "interests": student.interests
        }
        
        # Get classification
        classification_prompt = f"""
        Analyze this student profile and classify their primary career focus:
        {json.dumps(profile_summary, indent=2)}
        """
        
        classification_result = await classification_agent.run(classification_prompt)
        classification = classification_result.data.strip()
        
        # Get recommendations
        recommendation_prompt = f"""
        For a student classified as: {classification}
        
        Provide 2-3 specific learning recommendations to advance their career.
        """
        
        recommendation_result = await recommendation_agent.run(recommendation_prompt)
        recommendations_text = recommendation_result.data.strip()
        
        # Parse recommendations (split by lines and clean up)
        recommendations = [
            line.strip().lstrip('1234567890.-').strip() 
            for line in recommendations_text.split('\n') 
            if line.strip() and not line.strip().isdigit()
        ]
        
        # Save results
        filepath = save_analysis_result(
            student.personalInformation.fullName,
            classification,
            recommendations
        )
        
        return {
            "student_name": student.personalInformation.fullName,
            "classification": classification,
            "recommendations": recommendations,
            "saved_to": filepath,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "student_name": student.personalInformation.fullName,
            "error": str(e),
            "status": "error"
        }

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Student Profile Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze - Analyze student profiles",
            "health": "/health - Health check",
            "results": "/results/{student_name} - Get saved results"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_students(students_data: StudentsData, background_tasks: BackgroundTasks):
    """Analyze multiple student profiles"""
    if not students_data.students:
        raise HTTPException(status_code=400, detail="No student data provided")
    
    try:
        # Process all students concurrently
        tasks = [analyze_single_student(student) for student in students_data.students]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions in results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    "error": str(result),
                    "status": "error"
                })
            else:
                processed_results.append(result)
        
        success_count = sum(1 for r in processed_results if r.get("status") == "success")
        
        return AnalysisResponse(
            success=success_count > 0,
            message=f"Processed {len(processed_results)} students. {success_count} successful, {len(processed_results) - success_count} failed.",
            results=processed_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-single", response_model=Dict[str, Any])
async def analyze_single_student_endpoint(student: StudentProfile):
    """Analyze a single student profile"""
    try:
        result = await analyze_single_student(student)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/results/{student_name}")
async def get_student_results(student_name: str):
    """Get saved analysis results for a student"""
    safe_name = student_name.replace(" ", "_").replace("/", "_")
    filename = f"{safe_name}_analysis.json"
    filepath = os.path.join("analysis_results", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Results not found for this student")
    
    try:
        with open(filepath, 'r') as f:
            results = json.load(f)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading results: {str(e)}")

@app.get("/results")
async def list_all_results():
    """List all available analysis results"""
    ensure_results_directory()
    
    try:
        files = [f for f in os.listdir("analysis_results") if f.endswith("_analysis.json")]
        results = []
        
        for filename in files:
            filepath = os.path.join("analysis_results", filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    results.append({
                        "filename": filename,
                        "student_name": data.get("student_name"),
                        "classification": data.get("classification"),
                        "timestamp": data.get("timestamp")
                    })
            except Exception:
                continue
        
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing results: {str(e)}")

# Configuration and startup
if __name__ == "__main__":
    # Make sure to set your Gemini API key as an environment variable
    # export GEMINI_API_KEY="your-api-key-here"
    
    if not os.getenv("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY environment variable not set!")
        print("Please set it with: export GEMINI_API_KEY='your-api-key-here'")
    
    uvicorn.run(
        "main:app",  # Assuming this file is named main.py
        host="0.0.0.0",
        port=8000,
        reload=True
    )