import os 
import sys 
from src.exception import CustomException
from src.logger import logging
import tempfile
from src.utils import check_file_extension, check_file_size, parse_experience_from_resume
from pathlib import Path 
import shutil
from src.extraction_pipeline.data_extraction import Extract
from src.llm_pipeline.llm_semantic_parsing import Parse_Resume_Data
from src.llm_pipeline.data_validation_normalization import Validate
from src.llm_pipeline.data_validation_normalization import Normalize
from src.llm_pipeline.llm_semantic_parsing import Parse_Jd_Data
from src.input_pipeline.jd_input import Jd_Parsing
from src.semantic_scoring.candidate_score import Candidate_Score
 
class FileInput():
    def __init__(self, file_path):
        self.file_path : str = file_path
        
        
        
    def return_valid_file(self):
        """User uploads a resume file. Based on the conditions the
        file is uploaded successfully, else"""
        
        try:
            
            if os.path.exists(self.file_path):
                logging.info(f'the file {self.file_path} exists')
                file_type = check_file_extension(self.file_path)
                
                if file_type == self.file_path:
                    logging.info('file extension is valid, return file path')
                    file_size_type = check_file_size(self.file_path)
                    
                    if file_size_type == self.file_path:
                        logging.info('file size is valid, return file path')
                        
                        temp_dir = tempfile.mkdtemp()
                        
                        filename = os.path.basename(self.file_path)
                        temp_file_path = os.path.join(temp_dir, filename)
                        
                        # copying the file
                        shutil.copy2(self.file_path, temp_file_path)

                        return temp_dir, temp_file_path
                           
                        
                    else:
                        print(f"invalid file size, filesize supported till 100Mb")   
                        
                else:
                    print(f"Please check and re-upload a valid file.")
                    
            else:
                print("File does not exists") 
                   
        except Exception as e:
            logging.info('invalid file')
            raise CustomException(e, sys)
    
    
    
    
if __name__ == '__main__':
    
    check_filepath = FileInput(r'data\Resume_data_analyst_fresher.pdf')  
    temp_dir, file_path = check_filepath.return_valid_file()
    
    file_obj = Extract(file_path)
    file_content = file_obj.extract_text()
    print("Resume \n", file_content, "------------------------------")
    a = parse_experience_from_resume(file_content)
#     llm_obj = Parse_Resume_Data(file_content)
#     llm_response = llm_obj.llm_resume_parser()
#     print(f"\n\n{llm_response}\n\n")
#     validate_obj = Validate(llm_response)
#     validated_data = validate_obj.data_validation()
    
#     normalize_obj = Normalize(validated_data)
#     normalized_resume_data = normalize_obj.projects()
#     print(normalized_resume_data)
#     jd_obj = Jd_Parsing("""About the job
# About Digitap.ai:

# DIGITAP.AI is an Enterprise SaaS company providing high-tech advanced AI/ML, Alternate Data Solutions to new-age internet-driven businesses for reliable, fast, and 100% compliant Customer Onboarding, Alternate Data Solutions for Automated Risk Management, and other Value-Added Services. Our proprietary Machine Learning Algorithms and Modules provide one of the best success rates in the market. We work with the top digital lenders of India & the team brings together deep and vibrant experience in Fintech Product & Risk Management, Fraud Detection, and Risk Analytics.

# Culture and Benefits:

# Innovative Start-up Environment: Enjoy the flexibility to design, implement, and influence the development of cutting-edge solutions.
# Transparency and Meritocracy: We value clear communication, eschew politics, and promote an open culture where contributions are recognized and rewarded.
# Ownership and Impact: We encourage team members to take ownership, think beyond their roles, and contribute to the company's success in meaningful ways.
# Competitive Compensation: We offer a competitive salary and a potential equity package, aligning your success with the company's growth.


# Job Description:

# As a Data Scientist – Machine Learning, you will design and develop advanced ML models for credit scoring and risk assessment, while also leading research and innovation in large-scale transformer-based systems.

# Key Responsibilities:

# Credit & Risk Analytics: Design, develop, and optimize ML models for credit scoring, risk prediction, and scorecard generation.
# Model Deployment & Automation: Implement scalable pipelines for model training, validation, and deployment in production environments.
# Feature Engineering: Identify, extract, and engineer key features from structured and unstructured data to enhance model performance.
# Model Monitoring: Establish continuous monitoring frameworks to track model drift, performance metrics, and data quality.
# Research & Innovation: Explore and apply state-of-the-art ML and transformer architectures to improve predictive accuracy and interpretability.
# Collaboration: Work closely with data engineers, product managers, and domain experts to translate business objectives into robust ML solutions.


# Required Skills and Experience:

# Machine Learning: 2+ years of hands-on experience in developing, training, and deploying ML models for structured or tabular data.
# Statistical Modeling: Solid understanding of statistical concepts, feature engineering, and model evaluation techniques.
# ML Frameworks: Experience with scikit-learn, PyTorch, or TensorFlow for building and optimizing predictive models.
# Python Programming: Strong proficiency in Python, with experience using NumPy, Pandas, and Matplotlib for data manipulation and analysis.
# Data Handling: Practical experience with large datasets, data cleaning, preprocessing, and transformation for ML workflows.
# SQL & APIs: Proficiency in writing SQL queries and integrating ML models with APIs or backend systems.
# Version Control & Collaboration: Familiarity with Git and collaborative model development practices.
# Analytical Thinking: Strong problem-solving skills with the ability to translate business problems into data-driven ML solutions.


# Preferred Qualifications:

# Education: Bachelor’s or Master’s degree in Computer Science, Data Science, Mathematics, or a related quantitative field.
# Experience: Min2 years of experience in machine learning, data analytics, or applied statistics roles.
# Cloud Platforms: Exposure to AWS, GCP, or Azure for model deployment or data processing.
# Domain Knowledge: Familiarity with fintech, credit risk, or business analytics domains.
# Automation & MLOps: Basic understanding of model deployment, monitoring, or pipeline automation tools.
# Continuous Learning: Enthusiasm for exploring new ML algorithms, open-source tools, and emerging technologies in data science.   
# """)
#     jd_data = jd_obj.jd_data()
#     llm_jd_obj = Parse_Jd_Data(jd_data)
#     llm_jd_response = llm_jd_obj.llm_jd_parser()
#     validate_jd_obj = Validate(llm_jd_response)
#     validated_jd = validate_jd_obj.data_validation()
#     normalize_jd_obj = Normalize(validated_jd)
#     normalized_jd = normalize_jd_obj.normalize_jd()
#     score_obj = Candidate_Score(normalized_resume_data, normalized_jd)
#     cand_score = score_obj.experience_score()
    
    shutil.rmtree(temp_dir) 
            
            