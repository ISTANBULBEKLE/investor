from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.symbols import SUPPORTED_SYMBOLS
from app.database import get_db
from app.models.db_models import UserSettings
from app.schemas.settings import UserSettingsResponse, UserSettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


async def _get_or_create_settings(db: AsyncSession) -> UserSettings:
    result = await db.execute(select(UserSettings).limit(1))
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = UserSettings(
            symbols=["BTC", "ETH", "HBAR", "IOTA"],
            email="",
            alert_preferences={
                "signal_change": True,
                "rsi_extreme": True,
                "macd_crossover": True,
                "price_drop": True,
                "fear_greed_extreme": True,
                "confidence_spike": True,
            },
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.get("", response_model=UserSettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)) -> UserSettingsResponse:
    settings = await _get_or_create_settings(db)
    return UserSettingsResponse.model_validate(settings)


@router.put("", response_model=UserSettingsResponse)
async def update_settings(
    update: UserSettingsUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserSettingsResponse:
    settings = await _get_or_create_settings(db)

    if update.symbols is not None:
        if not (2 <= len(update.symbols) <= 10):
            raise HTTPException(
                status_code=400, detail="Between 2 and 10 symbols required"
            )
        for s in update.symbols:
            if s.upper() not in SUPPORTED_SYMBOLS:
                raise HTTPException(
                    status_code=400, detail=f"Unsupported symbol: {s}"
                )
        settings.symbols = [s.upper() for s in update.symbols]

    if update.email is not None:
        settings.email = update.email

    if update.alert_preferences is not None:
        settings.alert_preferences = update.alert_preferences

    await db.commit()
    await db.refresh(settings)
    return UserSettingsResponse.model_validate(settings)
