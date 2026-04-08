import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.db_models import Holdings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


class HoldingUpdate(BaseModel):
    symbol: str
    amount: float
    avg_buy_price: float


class HoldingResponse(BaseModel):
    symbol: str
    amount: float
    avg_buy_price: float

    model_config = {"from_attributes": True}


@router.get("", response_model=list[HoldingResponse])
async def get_portfolio(db: AsyncSession = Depends(get_db)) -> list[HoldingResponse]:
    result = await db.execute(select(Holdings).order_by(Holdings.symbol))
    rows = result.scalars().all()
    return [HoldingResponse.model_validate(r) for r in rows]


@router.post("", response_model=HoldingResponse)
async def add_holding(
    holding: HoldingUpdate,
    db: AsyncSession = Depends(get_db),
) -> HoldingResponse:
    symbol = holding.symbol.upper()
    result = await db.execute(select(Holdings).where(Holdings.symbol == symbol))
    existing = result.scalar_one_or_none()
    if existing:
        existing.amount = holding.amount
        existing.avg_buy_price = holding.avg_buy_price
    else:
        existing = Holdings(
            symbol=symbol,
            amount=holding.amount,
            avg_buy_price=holding.avg_buy_price,
        )
        db.add(existing)
    await db.commit()
    await db.refresh(existing)
    return HoldingResponse.model_validate(existing)


@router.delete("/{symbol}")
async def delete_holding(symbol: str, db: AsyncSession = Depends(get_db)) -> dict:
    symbol = symbol.upper()
    result = await db.execute(select(Holdings).where(Holdings.symbol == symbol))
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail=f"No holding for {symbol}")
    await db.delete(existing)
    await db.commit()
    return {"deleted": symbol}
