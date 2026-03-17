from fastapi import FastAPI
from api.score import router as score_router
from api.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Candidate Scoring App",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(score_router)
app.include_router(auth_router)

@app.get("/")
def health_check():
    return {"status":"ok"}


