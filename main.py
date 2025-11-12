import os
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import CaseStudy, Metric

app = FastAPI(title="White Circle API", description="From chaos to clarity – marketing case studies API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "White Circle Backend Running", "status": "ok"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# -------------------- Case Studies API --------------------
class CaseStudyOut(BaseModel):
    id: str
    brand: str
    logo_url: Optional[str] = None
    industry: str
    scope: List[str] = []
    campaign_type: str
    headline: str
    highlight: str
    metrics: List[Metric] = []
    tags: List[str] = []
    featured: bool = False
    performance_score: Optional[float] = None


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@app.get("/api/case-studies", response_model=List[CaseStudyOut])
def list_case_studies(
    q: Optional[str] = Query(None, description="Free text search in brand/headline/highlight"),
    industry: Optional[str] = None,
    scope: Optional[str] = Query(None, description="Filter by a single scope term"),
    campaign_type: Optional[str] = None,
    limit: int = Query(24, ge=1, le=100),
):
    filters: dict = {}
    if industry:
        filters["industry"] = industry
    if campaign_type:
        filters["campaign_type"] = campaign_type
    if scope:
        filters["scope"] = {"$in": [scope]}
    if q:
        filters["$or"] = [
            {"brand": {"$regex": q, "$options": "i"}},
            {"headline": {"$regex": q, "$options": "i"}},
            {"highlight": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}},
        ]
    docs = get_documents("casestudy", filters, limit)
    return [CaseStudyOut(**_serialize(d)) for d in docs]


@app.get("/api/case-studies/featured", response_model=List[CaseStudyOut])
def featured_case_studies(limit: int = Query(6, ge=1, le=12)):
    docs = get_documents("casestudy", {"featured": True}, limit)
    return [CaseStudyOut(**_serialize(d)) for d in docs]


@app.post("/api/case-studies", response_model=dict)
def create_case_study(payload: CaseStudy):
    inserted_id = create_document("casestudy", payload)
    return {"id": inserted_id}


@app.post("/api/seed", response_model=dict)
def seed_demo_data():
    """Insert a few demo case studies if collection is empty"""
    existing = get_documents("casestudy", {}, limit=1)
    if existing:
        return {"status": "exists", "inserted": 0}

    samples: List[CaseStudy] = [
        CaseStudy(
            brand="Aurora Beauty",
            logo_url="https://dummyimage.com/80x80/eeeeee/000000&text=A",
            industry="Beauty",
            scope=["Performance", "UGC", "Influencer"],
            campaign_type="Integrated",
            headline="From launch to leadership in 3 months",
            highlight="4.3x ROAS and 1M+ engagements",
            metrics=[
                Metric(label="ROAS", value="4.3x"),
                Metric(label="Engagements", value="1M+"),
                Metric(label="Reach", value="2.1M"),
            ],
            tags=["beauty", "makeup", "ecommerce"],
            featured=True,
            performance_score=92.5,
        ),
        CaseStudy(
            brand="Volt Wear",
            logo_url="https://dummyimage.com/80x80/eeeeee/000000&text=V",
            industry="Fashion",
            scope=["Branding", "Socials"],
            campaign_type="Organic",
            headline="Community-first brand building",
            highlight="3x engagement via full-funnel social",
            metrics=[
                Metric(label="Engagement", value="3x"),
                Metric(label="Followers", value="+120k"),
            ],
            tags=["fashion", "social"],
            featured=True,
            performance_score=88.0,
        ),
        CaseStudy(
            brand="Nova Foods",
            logo_url="https://dummyimage.com/80x80/eeeeee/000000&text=N",
            industry="FMCG",
            scope=["Performance", "Influencer"],
            campaign_type="Paid",
            headline="Retail lift with creator-led ads",
            highlight="2.7x incremental sales in pilot markets",
            metrics=[
                Metric(label="ROAS", value="3.1x"),
                Metric(label="Reach", value="1.8M"),
            ],
            tags=["fmcg", "retail"],
            featured=False,
            performance_score=81.0,
        ),
    ]

    inserted = 0
    for s in samples:
        create_document("casestudy", s)
        inserted += 1

    return {"status": "seeded", "inserted": inserted}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
