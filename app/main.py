from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
import logging
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

NV_ORIGIN = os.getenv("NV_ORIGIN")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS")

if not NV_ORIGIN:
    NV_ORIGIN = "http://localhost:3000"

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = "localhost,127.0.0.1"

ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS.split(",")]

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("npi_proxy")

# -------------------------------------------------
# FastAPI app
# -------------------------------------------------
app = FastAPI(title="NPI Proxy API")

# -------------------------------------------------
# CORS Configuration
# -------------------------------------------------
origins = [
    NV_ORIGIN,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Trusted Hosts (Security)
# -------------------------------------------------
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[host.strip() for host in ALLOWED_HOSTS],
)

# -------------------------------------------------
# Rate Limiting
# -------------------------------------------------
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"ok": False, "reason": "too_many_requests", "detail": "Rate limit exceeded"},
    )

# -------------------------------------------------
# NPPES API Settings
# -------------------------------------------------
NPPES_API = "https://npiregistry.cms.hhs.gov/api/"
HTTP_TIMEOUT = httpx.Timeout(5.0)
HTTP_LIMITS = httpx.Limits(max_keepalive_connections=5, max_connections=10)

# -------------------------------------------------
# Endpoint: /check-npi
# -------------------------------------------------
@app.get("/check-npi")
@limiter.limit("10/minute")
async def check_npi(request: Request, number: str):

    if not number.isdigit() or len(number) != 10:
        raise HTTPException(status_code=400, detail="Invalid NPI number format")

    params = {"version": "2.1", "number": number}

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, limits=HTTP_LIMITS) as client:
            response = await client.get(NPPES_API, params=params)
            response.raise_for_status()
            data = response.json()

    except httpx.RequestError as e:
        logger.error(f"Connection error while checking NPI {number}: {e}")
        raise HTTPException(status_code=500, detail="NPPES API request failed")

    except httpx.HTTPStatusError as e:
        logger.error(f"NPPES API returned error for NPI {number}: {e.response.status_code}")
        raise HTTPException(status_code=500, detail="NPPES API returned error")

    if not data.get("results"):
        return {"ok": False, "reason": "not_found", "number": number}

    entry = data["results"][0]
    basic = entry.get("basic", {})
    status = (basic.get("status") or "").upper()
    type_ = entry.get("enumeration_type", "")

    if status != "A":
        return {"ok": False, "reason": "inactive", "number": number}

    return {
        "ok": True,
        "number": number,
        "type": type_,
        "first_name": basic.get("first_name"),
        "last_name": basic.get("last_name"),
    }
