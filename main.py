import json
import yaml
import os
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time
import uuid
import jwt

app = FastAPI()

# -----------------------------
# Q1 Configuration
# -----------------------------
ALLOWED_ORIGIN = "https://dash-pv9a2s.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------------------
# Q2 Configuration
# -----------------------------
ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-xws5xyla.apps.exam.local"

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----
"""

# -----------------------------
# Middleware
# -----------------------------
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.time() - start:.6f}"

    return response

# -----------------------------
# Q1 Endpoint
# -----------------------------
@app.get("/stats")
async def stats(values: str):

    nums = [int(x.strip()) for x in values.split(",") if x.strip()]

    return {
        "email": "23f1002755@ds.study.iitm.ac.in",
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums)
    }

# -----------------------------
# Q2 Models
# -----------------------------
class TokenRequest(BaseModel):
    token: str

# -----------------------------
# Q2 Endpoint
# -----------------------------
@app.post("/verify")
async def verify(data: TokenRequest):

    try:

        payload = jwt.decode(
            data.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
        )

        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud"),
        }

    except Exception:

        return JSONResponse(
            status_code=401,
            content={
                "valid": False
            }
        )

from fastapi import Query

@app.get("/effective-config")
def effective_config(set: str | list[str] = Query(None)):

    # Default layer
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000"
    }

    # YAML layer
    with open("config.development.yaml") as f:
        config.update(yaml.safe_load(f))

    # .env layer
    if os.getenv("APP_PORT"):
        config["port"] = int(os.getenv("APP_PORT"))

    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    if os.getenv("APP_DEBUG"):
        config["debug"] = os.getenv("APP_DEBUG").lower() in [
            "true","1","yes","on"
        ]

    # OS Environment
    if os.getenv("APP_WORKERS"):
        config["workers"] = int(os.getenv("APP_WORKERS"))

    if os.getenv("APP_LOG_LEVEL"):
        config["log_level"] = os.getenv("APP_LOG_LEVEL")

    if os.getenv("APP_API_KEY"):
        config["api_key"] = os.getenv("APP_API_KEY")

    if os.getenv("APP_PORT"):
        config["port"] = int(os.getenv("APP_PORT"))

    # CLI overrides (highest precedence)
      
    if set:
      try:
        if isinstance(set, list):
            # supports ?set=port=9000&set=debug=true
            for item in set:
                if "=" in item:
                    key, value = item.split("=", 1)

                    if key in ["port", "workers"]:
                        config[key] = int(value)
                    elif key == "debug":
                        config[key] = value.lower() in ["true", "1", "yes", "on"]
                    else:
                        config[key] = value
         else:
            # supports ?set={"port":"9000","debug":"true"}
            overrides = json.loads(set)

            for key, value in overrides.items():
                if key in ["port", "workers"]:
                    config[key] = int(value)
                elif key == "debug":
                    config[key] = str(value).lower() in ["true", "1", "yes", "on"]
                else:
                    config[key] = value
      Exception:
        pass