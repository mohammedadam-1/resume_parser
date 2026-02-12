import sys 
from src.exception import CustomException 
from src.logger import logging 
from src.llm_pipeline.data_validation_normalization import (
    ResumeSchema,
    JdSchema
)
from sentence_transformers import SentenceTransformer, util
import torch
from typing import Tuple
from pydantic import BaseModel, PrivateAttr, Field
import threading
  
# Global model instance with thread-safe lazy loading
_model_lock = threading.Lock()
_model_instance_ = None 

def get_shared_model() -> SentenceTransformer:
    """lazy loading using threading"""
    
    global _model_instance_
    
    if _model_instance_ is None:
        with _model_lock:
            if _model_instance_ is None:
                logging.info("Loading SentenceTransformer model...")
                _model_instance_ = SentenceTransformer("all-MiniLM-L6-v2")
                logging.info("Model loaded successfully")
                
    return _model_instance_        

class Candidate_Score(BaseModel):
    resume_data: ResumeSchema
    jd_data: JdSchema 
    _model: SentenceTransformer = PrivateAttr()
    current_points: dict[str, float] = Field(default_factory=lambda: {
            "required_skills": 0.0,
            "preferred_skills": 0.0,
            "min_experience_months": 0.0,
            "education_required": 0.0,
            "keywords": 0.0
        }) 
    def model_post_init(self, _):
        self._model = get_shared_model()
        
           
    def skills_score(self) -> dict[str, float]:
        """Calculate the Score for candidate's skills and assign points accordingly"""
        try:
            logging.info("Initialized skills scoring")
    
            candidate_skills = set(self.resume_data.skills)
            logging.info("Loaded candidate_skills for scoring from resume")
            
            required_skills = set(self.jd_data.required_skills)
            logging.info("Loaded required_skills for scoring from jd")
        
            preferred_skills = set(self.jd_data.preferred_skills)
            logging.info("Loaded preferred_skills for scoring from jd")
            
            req_score_list = []
            pref_score_list = []
            
            logging.info("Intialized skills matching for required_skills using sets, for exact str match")  
            
            if len(required_skills) > 0:
                matched_required_skills = candidate_skills & required_skills
                logging.info("Matched candidate skills & required skills")
                ratio_req = len(matched_required_skills) / len(required_skills)
        
                score_req = round(ratio_req * 50.0, 2)
                logging.info(f"Calculated the score:{score_req} for matched required_skills")
                req_score_list.append(score_req)
                
                if len(candidate_skills) > 0:
                    logging.info("Initialized semantic skills matching for required_skills using cosine similariy")
                    embed_candidate_skills = ", ".join(list(candidate_skills))
                    candidate_skills_embedding = self._model.encode(embed_candidate_skills, convert_to_tensor=True)
                    embed_required_skills = ", ".join(list(required_skills))
                    required_skills_embedding = self._model.encode(embed_required_skills, convert_to_tensor=True) 
                    cos_score_req = util.cos_sim(candidate_skills_embedding, required_skills_embedding)
                    logging.info("Calculated the cosine similariy score for required_skills")
                    
                    if cos_score_req >= 0.90:
                        score = 50.0
                        req_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in required_skills")
                    elif cos_score_req >= 0.80:
                        score = 40.0
                        req_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in required_skills")

                    elif cos_score_req >= 0.70:
                        score = 30.0
                        req_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in required_skills")

                    elif cos_score_req >= 0.60:
                        score = 20.0 
                        req_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in required_skills")
                          
                    elif cos_score_req >= 0.50:
                        score = 10.0 
                        req_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in required_skills")
                              
                    else:
                        score = 5.0
                        req_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in required_skills")
                        
                    
                    final_score = round(float(sum(req_score_list) / 2), 2) 
                    logging.info(f"Summed and Averaged the required matched skill score & cosine_sim score: final_score:{final_score}")   
                    self.current_points["required_skills"] = final_score
                
            else:
                score_req = 0.0
                logging.info("Assigned score = 0.0 as len of required_skills is 0")
                
                self.current_points["required_skills"] = score_req
               
            logging.info("Intialized skills matching for preferred_skills using sets, for exact str match")    
                 
            if len(preferred_skills) > 0:
                matched_preferred_skills = candidate_skills & preferred_skills                  
                logging.info("Matched candidate skills & preferred skills")
                ratio_pref = len(matched_preferred_skills) / len(preferred_skills)
                score_pref = ratio_pref * 15.0
                logging.info(f"Calculated the score for matched preferred_skills: {score_pref}")
                
                if len(candidate_skills) > 0:
                    logging.info("Initialized semantic skills matching for preferred_skills using cosine similariy")
                    embed_preferred_skills = ", ".join(list(preferred_skills))
                    preferred_skills_embedding = self._model.encode(embed_preferred_skills, convert_to_tensor=True)
                    cos_score_pref = util.cos_sim(candidate_skills_embedding, preferred_skills_embedding)
                    logging.info("Calculated the cosine similariy score for preferred_skills")

                
                    if cos_score_pref >= 0.90:
                        score = 50.0
                        pref_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in preferred_skills")
                    elif cos_score_pref >= 0.80:
                        score = 40.0
                        pref_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in preferred_skills")

                    elif cos_score_pref >= 0.70:
                        score = 30.0
                        pref_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in preferred_skills")

                    elif cos_score_pref >= 0.60:
                        score = 20.0 
                        pref_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in preferred_skills")
                          
                    elif cos_score_pref >= 0.50:
                        score = 10.0 
                        pref_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in preferred_skills")
                              
                    else:
                        score = 5.0
                        pref_score_list.append(score)
                        logging.info(f"{score} points assigned to candidate for semantic similarity in preferred_skills")
                        
                    
                    pref_final_score = round(float(sum(pref_score_list) / 2), 2) 
                    logging.info(f"Summed and Averaged the preferred matched skill score & cosine_sim score: final_score:{pref_final_score}")   
   
                    self.current_points["preferred_skills"] = pref_final_score
                
            else:
                score_pref = 0.0
                self.current_points["preferred_skills"] = score_pref
                logging.info("Assigned score = 0.0 as len of preferred_skills is 0")
            
            
            logging.info("Scored and returned candidate's required_skills & preferred_skills") 
            return self.current_points             
        
        except Exception as e:
            logging.info("Unable to score candidate's skill section") 
            raise CustomException(e, sys)

    def experience_score(self, points: dict[str, float]) -> dict[str, float]:
        """Calculate the Score for candidate's total experience(months) and assign points accordingly"""
        try: 
            logging.info("Initialized scoring for candidate's experience_score")
            current_points = points
        
            required_months = self.jd_data.min_experience_months or 0
            logging.info("Loaded required_months experience from JD")
            half_req = required_months / 2 # Half months required of total required months in JD
            logging.info("Calculated half of required_months for scoring")
            candidate_experience = self.resume_data.total_experience_months or 0
            logging.info("Loaded candidate_experience from Resume")
            
            if candidate_experience >= required_months:
                score = 15.0
                logging.info(f"Assigned {score} points for min_experience_months")
                current_points["min_experience_months"] = score
                
            elif candidate_experience >= half_req:
                score = 10.0
                logging.info(f"Assigned {score} points for min_experience_months")
                current_points["min_experience_months"] = score
                
            elif candidate_experience > 0 and candidate_experience < half_req:
                score = 5.0
                logging.info(f"Assigned {score} points for min_experience_months")
                current_points["min_experience_months"] = score
                       
            else:
                score = 0.0
                logging.info(f"Assigned {score} points for min_experience_months")
                current_points["min_experience_months"] = score
             
            logging.info("Scored and returned candidate experience")    
            return current_points    
            
        except Exception as e:
            logging.info("Unable to calculate and score candidate experience")
            raise CustomException(e, sys)
        
    def education_score(self) -> dict[str, float]:
        """Calculate the score for candidate's education and assign points accordingly"""  
        
        try:
            logging.info("Initialized scoring for candidate's education_score section")
            current_points = self.skills_score()
            logging.info("Loaded current_points from skills_score")
            
            try:
                candidate_qualification = self.resume_data.education[0].degree_level   
                logging.info("Loaded candidate_qualification from resume")
            except (TypeError, KeyError, IndexError):
                candidate_qualification = None    
                
            try:    
                required_qualification = self.jd_data.required_education[0].degree_level
                logging.info("Loaded required_qualification from JD")
            except (TypeError, KeyError, IndexError):
                required_qualification = None  
            
            try:
                candidate_education_field = self.resume_data.education[0].field
                logging.info("Loaded candidate_education_field")
            except (TypeError, KeyError, IndexError):
                candidate_education_field = None    
            # print(f"candidate_education_field: {candidate_education_field}")
            try:
                required_education_field = self.jd_data.required_education[0].field
                logging.info("Loaded required_education_field")
            except (TypeError, KeyError, IndexError):
                required_education_field = None    
            
            
            if required_qualification is None:
                current_points["education_required"] = 10.0
                logging.info("10.0 points assigned to candidate for education as required_qualification is None")
                return current_points
            
            elif candidate_qualification is None:
                current_points["education_required"] = 0.0
                logging.info("0.0 points assigned to candidate for education as candidate_qualification is None")
                return current_points
            
            elif required_qualification: 
   
                if required_qualification <= candidate_qualification:
                    current_points["education_required"] = 3.0
                    logging.info("3.0 points assigned to candidate for education as required_qualification matched")
                
                else:
                    current_points["education_required"] = 0.0
                    logging.info("0.0 points assigned to candidate for education as required_qualification matched is None")
                    return current_points
                    
                
                if required_education_field is None:
                    current_points["education_required"] += 7.0
                    logging.info("7.0 points assigned to candidate for required_education_field as its None")
                    return current_points
                
                elif candidate_education_field is None:
                    current_points["education_required"] += 0.0
                    logging.info("0.0 points assigned to candidate for candidate_education_field as its None")
                    return current_points
                
                else:
                    embed_required_field = [required_education_field]
                    embed_candidate_field = [candidate_education_field]
                    
                    required_field_embeddings = self._model.encode(embed_required_field, convert_to_tensor=True)
                    candidate_field_embeddings = self._model.encode(embed_candidate_field, convert_to_tensor=True)
                    logging.info("Converted education fields to vectors")
                    cosine_scores = util.cos_sim(required_field_embeddings, candidate_field_embeddings)
                    logging.info("Calculated cosine score using cosine_similariy")
            
                    if cosine_scores >= 0.90:
                        score = 7.0
                        current_points["education_required"] += score
                        logging.info(f"{score} points assigned to candidate's education_field")
                    elif cosine_scores >= 0.80:
                        score = 5.0
                        current_points["education_required"] += score
                        logging.info(f"{score} points assigned to candidate's education_field")
                    elif cosine_scores >= 0.70:
                        score = 4.0
                        current_points["education_required"] += score
                        logging.info(f"{score} points assigned to candidate's education_field")
                    elif cosine_scores >= 0.60:
                        score = 3.0
                        current_points["education_required"] += score 
                        logging.info(f"{score} points assigned to candidate's education_field")  
                    elif cosine_scores >= 0.50:
                        score = 2.0
                        current_points["education_required"] += score 
                        logging.info(f"{score} points assigned to candidate's education_field")      
                    else:
                        score = 1.5
                        current_points["education_required"] += score
                        logging.info(f"{score} points assigned to candidate's education_field")     
             
            logging.info("Semantically calculated the education field and returned score")   
                    
            return current_points     
                
        except Exception as e:
            logging.info("Unable to compare and score candidate education")
            raise CustomException(e, sys)
        
    def keywords_score(self, points: dict[str, float]) -> dict[str, float]:
        """Calculate the score for keywords present in candidate's resume and JD, assign points accordingly"""  
        
        try:
            logging.info("Initialized scoring for candidate's keywords_score section")
            current_points = points
            
            candidate_keywords = self.resume_data.keywords
            logging.info("Loaded candidate_keywords from resume")
            job_desc_keywords = self.jd_data.keywords
            logging.info("Loaded jd_keywords from JD")
            
            if not job_desc_keywords:
                score = 10.0
                current_points["keywords"] = score
                logging.info(f"{score} points assigned to candidate's keyword as job_desc_keywords is None")
                
            elif not candidate_keywords:
                score = 0.0
                current_points["keywords"] = score
                logging.info(f"{score} points assigned to candidate's keyword as job_desc_keywords is None")

                
            else:
                embed_candidate_keywords = candidate_keywords
                embed_job_desc_keywords = job_desc_keywords
                # convert keywords into vector embeddings
                candidate_keywords_embedding = self._model.encode(embed_candidate_keywords, convert_to_tensor=True) 
                job_desc_embedding = self._model.encode(embed_job_desc_keywords, convert_to_tensor=True)
                logging.info("candidate_keywords and job_desc_keywords embeded")
            
                cosine_scores = util.cos_sim(candidate_keywords_embedding, job_desc_embedding)
                logging.info("Calculated semantic score for keywords")
                # pick the most matching keywords
                best_matches_per_keyword, _ = torch.max(cosine_scores, dim=1)
                logging.info("found the best matched keywords")
                # print(f"best_matches_per_keyword: {best_matches_per_keyword}")
                final_similarity = torch.mean(best_matches_per_keyword).item() 
                logging.info("Averaged the score by dividing final_similarity by the len of best_matches_per_keyword")
                keywords_score = round(final_similarity * 10, 2) 
                logging.info(f"{keywords_score} points assigned to candidate's keywords")
    
                current_points["keywords"] = keywords_score
                
            return current_points
        
        except Exception as e:
            logging.info("Unable to compare and score keywords")
            raise CustomException(e, sys)
        
    def candidate_total_score(self, points: dict[str, float]) -> Tuple[dict[str, float], float]:
        """Return current points and the sum of points assigned to candidate"""
        
        try:
            logging.info("Initialized to sum the points assigned to candidate")
            
            current_points = self.experience_score(points)
            logging.info("Loaded current_points from experience_score")
            current_points = self.keywords_score(current_points)
            logging.info("Loaded current_points from keywords_score")
            
            total_score = sum(current_points.values())
            candidate_total_score = round(total_score, 2)
            
            logging.info(f"Calculated and retured sum of all points: {candidate_total_score}")
            return current_points, candidate_total_score
             
        except Exception as e:
            logging.info("Unable to sum the candidate score")
            raise CustomException(e, sys)
        
        