from fastapi import FastAPI
from api.score import router as score_router
from api.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from api.limiter import limiter
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Candidate Scoring App",
    version="0.1.0",
)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://resume-parser-r9dg.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(score_router)
app.include_router(auth_router)

@app.api_route("/", methods=['GET', 'HEAD'])
def health_check():
    return {"status":"ok"}

app.mount("/frontend", StaticFiles(directory="frontend"), name="candidate_application")




