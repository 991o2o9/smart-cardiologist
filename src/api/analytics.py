from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
from src.models.database import HeartPrediction, User
from src.services.database import get_db
from src.services.encryption_service import encryption_service
from src.utils.auth_middleware import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def parse_float(val):
    try:
        return float(val)
    except Exception:
        return None

def parse_int(val):
    try:
        return int(val)
    except Exception:
        return None


def calc_trend(first, last):
    if first is None or last is None:
        return None
    if first == 0:
        return "stable"
    diff = (last - first) / abs(first)
    if diff > 0.05:
        return "increasing"
    elif diff < -0.05:
        return "decreasing"
    else:
        return "stable"


@router.get("/", summary="User analysis analytics")
async def get_analytics(
    period: str = Query(..., regex="^(week|month)$", description="Period: week or month"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id

    now = datetime.utcnow()
    if period == "week":
        since = now - timedelta(days=7)
    else:
        since = now - timedelta(days=30)

    # Get user analyses for the period
    result = await db.execute(
        select(HeartPrediction)
        .where(and_(HeartPrediction.user_id == user_id, HeartPrediction.created_at >= since))
        .order_by(HeartPrediction.created_at.asc())
    )
    records = result.scalars().all()
    if not records:
        raise HTTPException(status_code=404, detail="No data for selected period")

    # Decrypt and collect data
    risks, pulses, systolics, created_ats = [], [], [], []
    for rec in records:
        decrypted = encryption_service.decrypt_medical_data({
            'pulse': rec.pulse,
            'risk_prediction': rec.risk_prediction,
            'trestbps': rec.trestbps
        })
        risk = parse_float(decrypted.get('risk_prediction'))
        pulse = parse_int(decrypted.get('pulse'))
        systolic = parse_int(decrypted.get('trestbps'))
        risks.append(risk)
        pulses.append(pulse)
        systolics.append(systolic)
        created_ats.append(rec.created_at)

    def safe_avg(arr):
        arr = [x for x in arr if x is not None]
        return sum(arr) / len(arr) if arr else None
    def safe_min(arr):
        arr = [x for x in arr if x is not None]
        return min(arr) if arr else None
    def safe_max(arr):
        arr = [x for x in arr if x is not None]
        return max(arr) if arr else None

    # Trends: compare first and last values
    risk_trend = calc_trend(risks[0], risks[-1])
    pulse_trend = calc_trend(pulses[0], pulses[-1])
    systolic_trend = calc_trend(systolics[0], systolics[-1])

    # Form response
    response = {
        "user_id": user_id,
        "period": period,
        "risk": {
            "avg": safe_avg(risks),
            "min": safe_min(risks),
            "max": safe_max(risks),
            "trend": risk_trend
        },
        "pulse": {
            "avg": safe_avg(pulses),
            "min": safe_min(pulses),
            "max": safe_max(pulses),
            "trend": pulse_trend
        },
        "pressure": {
            "avg": {"systolic": safe_avg(systolics), "diastolic": None},
            "min": {"systolic": safe_min(systolics), "diastolic": None},
            "max": {"systolic": safe_max(systolics), "diastolic": None},
            "trend": {"systolic": systolic_trend, "diastolic": None}
        },
        "last_updated": max(created_ats).isoformat() + "Z"
    }
    return response
