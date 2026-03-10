from typing import Dict, Literal 
from pydantic import BaseModel, Field 

class FilePath(BaseModel):
    file_path: str

class CurrentPoints(BaseModel):
    required_skills: float
    preferred_skills: float
    min_experience_months: float 
    education_required: float
    keywords: float

class ScoreBreakdown(BaseModel):
    required_skills: float = Field(..., ge=0.0)
    preferred_skills: float = Field(..., ge=0.0)
    experience: float = Field(..., ge=0.0)
    education: float = Field(..., ge=0.0)
    keywords: float = Field(..., ge=0.0)
    
class ClassificationResult(BaseModel):
    final_score: float = Field(..., ge=0.0, le=100.0)    
    classification: Literal[
        "Strong Fit",
        "Good Fit",
        "Potential Fit",
        "Not Fit"
    ]
    details: ScoreBreakdown
    
class ScoreInput(BaseModel):
    current_points: Dict[str, float]
    total_points: float = Field(..., ge=0.0, le=100.0)
    
    
    