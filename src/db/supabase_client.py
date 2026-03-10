import os 
import httpx
from pydantic import BaseModel, PrivateAttr, ConfigDict
from supabase import create_client, Client, ClientOptions
from typing import Any
from dotenv import load_dotenv
load_dotenv()

# custom_client = httpx.Client(verify=False) #only for testing use

class Get_Supabase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    _client: Client = PrivateAttr()
    
    def model_post_init(self, __context: Any) -> None: # __context, super() usage - clearity
        super().model_post_init(__context)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url and not supabase_service_role_key:
            raise ValueError("Supabase credentials not found in .env")
        
        self._client: Client = create_client(supabase_url=supabase_url,
                supabase_key=supabase_service_role_key
                ) #options: Only for testing purpose
        
    @property
    def client(self) -> Client:
        return self._client
    
supabase_instance = Get_Supabase()

supabase = supabase_instance.client

        
        
        
    