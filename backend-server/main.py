from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from pydantic_ai import Agent
from typing import List, Optional, Dict, Any, Union
import json
import os
import asyncio
from datetime import datetime
import uvicorn

# Data Models - Updated to match frontend structure
class ProgrammingLanguage(BaseModel):
    name: str
    level: str

class OtherLanguage(BaseModel):
    language: str
    speaking: str
    reading: str
    writing: str

class Certification(BaseModel):
    name: str
    issuingOrganization: str
    dateObtained: str
    expiryDate: Optional[str] = None

class VolunteerWork(BaseModel):
    organizationName: str
    role: str
    duration: str
    keyResponsibilitiesAndAchievements: List[str] = []

class ComprehensiveStudentProfile(BaseModel):
    # Personal Information
    fullName: str
    dateOfBirth: Optional[str] = None
    gender: Optional[str] = None
    email: str
    countryOfResidence: Optional[str] = None
    preferredLanguages: List[str] = []
    
    # Academic Background
    highestEducation: Optional[str] = None
    fieldsOfStudy: List[str] = []
    institutions: List[str] = []
    graduationYear: Optional[str] = None
    achievements: List[str] = []
    enrollmentStatus: Optional[str] = None
    
    # Technical Skills
    programmingLanguages: List[ProgrammingLanguage] = []
    softwareProficiency: List[str] = []
    otherTechnicalSkills: List[str] = []
    
    # Soft Skills
    communication: Optional[str] = None
    teamwork: Optional[str] = None
    problemSolving: Optional[str] = None
    leadership: Optional[str] = None
    timeManagement: Optional[str] = None
    
    # Languages
    nativeLanguage: Optional[str] = None
    otherLanguages: List[OtherLanguage] = []
    
    # Certifications
    certifications: List[Certification] = []
    
    # Professional Experience
    employmentStatus: Optional[str] = None
    jobTitles: List[str] = []
    employers: List[str] = []
    employmentDuration: List[str] = []
    responsibilities: List[str] = []
    
    # Internships & Volunteer Work
    volunteerWork: List[VolunteerWork] = []
    
    # Career Goals
    shortTermGoals: Optional[str] = None
    longTermGoals: Optional[str] = None
    preferredIndustries: List[str] = []
    desiredJobTitles: List[str] = []
    motivation: Optional[str] = None
    keyFactors: List[str] = []
    
    # Learning Preferences
    learningStyle: List[str] = []
    skillsToAcquire: List[str] = []
    knowledgeAreas: List[str] = []
    learningChallenges: List[str] = []
    
    # Feedback & Support
    preferredFeedback: List[str] = []
    supportNeeded: List[str] = []
    positiveAspects: Optional[str] = None
    areasForImprovement: Optional[str] = None

class StudentsData(BaseModel):
    students: List[ComprehensiveStudentProfile]

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

# Pydantic AI Agents - Enhanced for comprehensive analysis
classification_agent = Agent(
    'gemini-1.5-flash',
    system_prompt="""You are an expert career counselor and skills analyzer. 
    Analyze comprehensive student profiles and classify their primary career focus based on:
    
    - Technical skills (programming languages, software proficiency, technical skills)
    - Professional experience (job titles, responsibilities, employers)
    - Educational background (degrees, fields of study, institutions)
    - Career goals (short-term, long-term aspirations)
    - Certifications and achievements
    - Learning preferences and skills to acquire
    
    Consider the student's overall profile holistically. Look for patterns across:
    - Current skill levels vs. desired skills
    - Academic background vs. career aspirations
    - Professional experience vs. future goals
    
    Return ONLY a specific classification category such as:
    - "AI/Machine Learning Engineer"
    - "Full-Stack Web Developer" 
    - "Data Scientist"
    - "DevOps Engineer"
    - "Mobile App Developer"
    - "Cybersecurity Specialist"
    - "Product Manager"
    - "UI/UX Designer"
    - "Backend Developer"
    - "Frontend Developer"
    - "Cloud Solutions Architect"
    - "Business Analyst"
    - "Digital Marketing Specialist"
    - etc.
    
    Be specific and precise based on the strongest indicators in their profile."""
)

recommendation_agent = Agent(
    'gemini-1.5-flash',
    system_prompt="""You are a personalized learning path advisor. Based on a student's 
    comprehensive profile and classification, provide 3-4 specific, actionable learning 
    recommendations that will accelerate their career development.
    
    Consider their:
    - Current skill gaps vs. desired skills
    - Learning style preferences
    - Career timeline (short-term vs long-term goals)
    - Current experience level
    - Preferred learning methods
    
    Format your response as a numbered list with concrete, practical suggestions.
    Each recommendation should be:
    1. Specific (mention exact technologies, courses, or skills)
    2. Actionable (something they can start immediately)
    3. Relevant to their career path
    4. Progressive (building on their current level)
    
    Examples of good recommendations:
    - "Complete AWS Cloud Practitioner certification within 3 months to strengthen cloud fundamentals"
    - "Build 2-3 React projects with TypeScript to demonstrate frontend proficiency"
    - "Practice data structures and algorithms on LeetCode 30 minutes daily for technical interviews"
    """
)

# FastAPI App
app = FastAPI(
    title="Comprehensive Student Profile Analysis API",
    description="AI-powered comprehensive student profile analysis and personalized recommendation system",
    version="2.0.0"
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

def save_analysis_result(student_name: str, classification: str, recommendations: List[str], profile_summary: Dict[str, Any]):
    """Save comprehensive analysis results to JSON file"""
    ensure_results_directory()
    
    safe_name = student_name.replace(" ", "_").replace("/", "_")
    filename = f"{safe_name}_comprehensive_analysis.json"
    filepath = os.path.join("analysis_results", filename)
    
    result_data = {
        "student_name": student_name,
        "classification": classification,
        "recommendations": recommendations,
        "profile_summary": profile_summary,
        "timestamp": datetime.now().isoformat(),
        "analysis_version": "2.0.0"
    }
    
    with open(filepath, 'w') as f:
        json.dump(result_data, f, indent=4)
    
    return filepath

def create_profile_summary(student: ComprehensiveStudentProfile) -> Dict[str, Any]:
    """Create a comprehensive profile summary for AI analysis"""
    
    # Process programming languages
    tech_skills = []
    for lang in student.programmingLanguages:
        if lang.name.strip():
            tech_skills.append(f"{lang.name} ({lang.level})")
    
    # Process other languages
    language_skills = []
    if student.nativeLanguage:
        language_skills.append(f"Native: {student.nativeLanguage}")
    
    for lang in student.otherLanguages:
        if lang.language.strip():
            language_skills.append(f"{lang.language} (Speaking: {lang.speaking}, Reading: {lang.reading}, Writing: {lang.writing})")
    
    # Process certifications
    cert_list = []
    for cert in student.certifications:
        if cert.name.strip():
            cert_info = f"{cert.name}"
            if cert.issuingOrganization:
                cert_info += f" from {cert.issuingOrganization}"
            if cert.dateObtained:
                cert_info += f" ({cert.dateObtained})"
            cert_list.append(cert_info)
    
    # Process volunteer work
    volunteer_summary = []
    for vol in student.volunteerWork:
        if vol.organizationName.strip():
            vol_info = f"{vol.role} at {vol.organizationName}"
            if vol.duration:
                vol_info += f" ({vol.duration})"
            volunteer_summary.append(vol_info)
    
    return {
        "personal_info": {
            "name": student.fullName,
            "email": student.email,
            "location": student.countryOfResidence,
            "employment_status": student.employmentStatus
        },
        "education": {
            "highest_education": student.highestEducation,
            "fields_of_study": [field for field in student.fieldsOfStudy if field.strip()],
            "institutions": [inst for inst in student.institutions if inst.strip()],
            "graduation_year": student.graduationYear,
            "enrollment_status": student.enrollmentStatus
        },
        "technical_skills": {
            "programming_languages": tech_skills,
            "software_proficiency": [software for software in student.softwareProficiency if software.strip()],
            "other_technical_skills": [skill for skill in student.otherTechnicalSkills if skill.strip()]
        },
        "soft_skills": {
            "communication": student.communication,
            "teamwork": student.teamwork,
            "problem_solving": student.problemSolving,
            "leadership": student.leadership,
            "time_management": student.timeManagement
        },
        "languages": language_skills,
        "certifications": cert_list,
        "professional_experience": {
            "job_titles": [title for title in student.jobTitles if title.strip()],
            "employers": [emp for emp in student.employers if emp.strip()],
            "employment_duration": [dur for dur in student.employmentDuration if dur.strip()],
            "key_responsibilities": [resp for resp in student.responsibilities if resp.strip()]
        },
        "volunteer_work": volunteer_summary,
        "career_goals": {
            "short_term": student.shortTermGoals,
            "long_term": student.longTermGoals,
            "preferred_industries": [ind for ind in student.preferredIndustries if ind.strip()],
            "desired_job_titles": [title for title in student.desiredJobTitles if title.strip()],
            "motivation": student.motivation
        },
        "learning_preferences": {
            "learning_style": student.learningStyle,
            "skills_to_acquire": [skill for skill in student.skillsToAcquire if skill.strip()],
            "knowledge_areas": [area for area in student.knowledgeAreas if area.strip()],
            "learning_challenges": [challenge for challenge in student.learningChallenges if challenge.strip()]
        },
        "support_needs": {
            "preferred_feedback": student.preferredFeedback,
            "support_needed": [support for support in student.supportNeeded if support.strip()],
            "positive_aspects": student.positiveAspects,
            "areas_for_improvement": student.areasForImprovement
        }
    }

async def analyze_single_student(student: ComprehensiveStudentProfile) -> Dict[str, Any]:
    """Analyze a single comprehensive student profile"""
    try:
        # Create comprehensive profile summary
        profile_summary = create_profile_summary(student)
        
        # Get classification
        classification_prompt = f"""
        Analyze this comprehensive student profile and classify their primary career focus:
        
        STUDENT PROFILE:
        {json.dumps(profile_summary, indent=2)}
        
        Based on all the information provided (technical skills, experience, education, goals, certifications, etc.), 
        determine the most appropriate career classification for this student.
        """
        
        classification_result = await classification_agent.run(classification_prompt)
        classification = classification_result.data.strip()
        
        # Get personalized recommendations
        recommendation_prompt = f"""
        STUDENT PROFILE SUMMARY:
        Name: {student.fullName}
        Classification: {classification}
        
        CURRENT SKILLS:
        Technical Skills: {profile_summary['technical_skills']}
        Certifications: {profile_summary['certifications']}
        Experience: {profile_summary['professional_experience']}
        
        GOALS & PREFERENCES:
        Career Goals: {profile_summary['career_goals']}
        Learning Preferences: {profile_summary['learning_preferences']}
        Skills to Acquire: {profile_summary['learning_preferences']['skills_to_acquire']}
        
        SUPPORT NEEDS:
        {profile_summary['support_needs']}
        
        Provide 3-4 specific, personalized learning recommendations that will help this student 
        progress toward their career goals as a {classification}.
        """
        
        recommendation_result = await recommendation_agent.run(recommendation_prompt)
        recommendations_text = recommendation_result.data.strip()
        
        # Parse recommendations (split by lines and clean up)
        recommendations = []
        for line in recommendations_text.split('\n'):
            clean_line = line.strip().lstrip('1234567890.-').strip()
            if clean_line and not clean_line.isdigit() and len(clean_line) > 10:
                recommendations.append(clean_line)
        
        # Ensure we have at least some recommendations
        if not recommendations:
            recommendations = [
                f"Focus on strengthening core {classification.lower()} skills",
                "Build a portfolio of relevant projects",
                "Network with professionals in your target field",
                "Consider relevant certifications for career advancement"
            ]
        
        # Save results with full profile summary
        filepath = save_analysis_result(
            student.fullName,
            classification,
            recommendations,
            profile_summary
        )
        
        return {
            "student_name": student.fullName,
            "classification": classification,
            "recommendations": recommendations,
            "profile_summary": profile_summary,
            "saved_to": filepath,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "student_name": student.fullName,
            "error": str(e),
            "status": "error",
            "profile_summary": create_profile_summary(student) if student else None
        }

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Comprehensive Student Profile Analysis API",
        "version": "2.0.0",
        "endpoints": {
            "analyze": "/analyze - Analyze comprehensive student profiles",
            "analyze-single": "/analyze-single - Analyze single student profile", 
            "health": "/health - Health check",
            "results": "/results/{student_name} - Get saved results",
            "results-list": "/results - List all available results"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_students(students_data: StudentsData, background_tasks: BackgroundTasks):
    """Analyze multiple comprehensive student profiles"""
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
async def analyze_single_student_endpoint(student: ComprehensiveStudentProfile):
    """Analyze a single comprehensive student profile"""
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
    filename = f"{safe_name}_comprehensive_analysis.json"
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
        files = [f for f in os.listdir("analysis_results") if f.endswith("_comprehensive_analysis.json")]
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
                        "timestamp": data.get("timestamp"),
                        "analysis_version": data.get("analysis_version", "2.0.0")
                    })
            except Exception:
                continue
        
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing results: {str(e)}")

@app.post("/validate-profile")
async def validate_profile(student: ComprehensiveStudentProfile):
    """Validate a student profile without running analysis"""
    try:
        profile_summary = create_profile_summary(student)
        return {
            "valid": True,
            "message": "Profile is valid",
            "profile_summary": profile_summary
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Profile validation failed: {str(e)}"
        }

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