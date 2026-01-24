import sys 
import os 
from src.exception import CustomException 
from src.logger import logging 
import json
from src.utils import score_points

points = {
            "required_skills": 0,
            "preferred_skills": 0,
            "min_experience_months":0,
            "education_required":0,
            "keywords":0
        }      

class Candidate_Score():
    def __init__(self, resume_data, jd_data):
        self.resume_data = resume_data
        self.jd_data = jd_data

    def skills_score(self):
        try:
            if not isinstance(self.resume_data, dict) and not isinstance(self.jd_data, dict):
                raise TypeError(f"Expected 'dict' for resume_data and jd_data, but got '{type(self.resume_data).__name__}' and '{type(self.jd_data).__name__}'")   
            
            # print(f"Resume data: {self.resume_data["skills"]}\n\n")
            # print(f"Jd data required_skills: {self.jd_data['required_skills']}\n\n")            
            # print(f"Jd data preferred skills: {self.jd_data["preferred_skills"]}\n\n")            
            
            candidate_skills = set(self.resume_data["skills"])
            
            required_skills = set(self.jd_data['required_skills'])
            preferred_skills = set(self.jd_data["preferred_skills"])
            
            matched_required_skills = candidate_skills & required_skills
            if len(required_skills) > 0:
                ratio_req = len(matched_required_skills) / len(required_skills)
                # print("matched required skills: ",matched_required_skills)
                score_req = ratio_req * 45.0
                # print(f"score_required_skills: {round(score_req,1)}")
            else:
                score_req = 0.0
                # print(f"score_required_skills: {round(score_req,1)}")    
            
            matched_preferred_skills = candidate_skills & preferred_skills
            if len(preferred_skills) > 0:
                ratio_pref = len(matched_preferred_skills) / len(preferred_skills)
                # print("matched preferred skills: ",matched_preferred_skills)
                score_pref = ratio_pref * 15.0
                # print(f"score_preferred_skills: {round(score_pref, 1)}")
            else:
                score_pref = 0.0
                # print(f"score_preferred_skills: {round(score_pref, 1)}")
                
            skill_score = score_req + score_pref
            # print("\nTotal Skill_Score: ", round(skill_score, 2))
            
            points["required_skills"] = score_req
            points["preferred_skills"] = score_pref
            
            # print(points)
            
            return points             
        
        except Exception as e:
            raise CustomException(e, sys)

    def experience_score(self):
        
        try:
            
            if not isinstance(self.resume_data, dict) or not isinstance(self.jd_data, dict):
                raise TypeError("Expected dicts for resume and jd data")     
            
            current_points = self.skills_score()
            
            required_months = self.jd_data.get("min_experience_months") or 0
            half_req = required_months / 2
            
            total_exp_score = []
            
            for exp in self.resume_data.get("experience", []):
                duration = exp.get("duration_months", 0)
                if duration != None:
                    if duration >= required_months:
                        score = 10.0
                        total_exp_score.append(score)
                        
                    elif duration >= half_req:
                        score = 5.0
                        total_exp_score.append(score)
                        
                    elif duration > 0 and duration < half_req:
                        score = 2.0
                        total_exp_score.append(score)
                        
                    else:
                        
                        score = 0.0
                        total_exp_score.append(score)
                else:
                    duration = 0.0        
                    total_exp_score.append(duration)
            print(total_exp_score)    
            
           
        except Exception as e:
            raise CustomException(e, sys)
