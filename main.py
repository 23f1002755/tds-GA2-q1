from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# YOUR VALUES
# ------------------------

EMAIL = "23f1002755@ds.study.iitm.ac.in"

API_KEY = "ak_rmubb14nsuf7y565nrgcpuzq"

# ------------------------

class Event(BaseModel):
    user: str
    amount: float
    ts: int

class RequestBody(BaseModel):
    events: List[Event]

@app.post("/analytics")
def analytics(
    body: RequestBody,
    x_api_key: str = Header(None)
):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    total_events = len(body.events)

    unique_users = len(set(e.user for e in body.events))

    revenue = 0

    user_total = {}

    for e in body.events:

        if e.amount > 0:

            revenue += e.amount

            user_total[e.user] = user_total.get(e.user, 0) + e.amount

    top_user = ""

    if user_total:
        top_user = max(user_total, key=user_total.get)

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user
    }