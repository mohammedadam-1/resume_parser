from src.db.supabase_client import supabase

class UserAuth:
    
    @staticmethod
    def user_signup(user_email:str, user_password:str):
        response = supabase.auth.sign_up(
            {
                "email": user_email,
                "password": user_password
            }
        )
        
        return response
    
    @staticmethod
    def user_signin(user_email:str, user_password:str):
        response = supabase.auth.sign_in_with_password(
            {
                "email": user_email,
                "password": user_password
            }
        )
        return response
    
    @staticmethod 
    def get_session():
        response = supabase.auth.get_session()
        return response 
    
    
    @staticmethod
    def user_signout():
        response = supabase.auth.sign_out()
        return response 
        