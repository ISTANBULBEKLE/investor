"""
Train ML models for configured symbols.

Usage:
    cd backend && python -m scripts.train_models
    cd backend && python -m scripts.train_models --symbols BTC ETH --days 180
"""

import argparse
import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Train INVESTOR ML models")
    parser.add_argument("--symbols", nargs="+", default=None, help="Symbols to train")
    parser.add_argument("--days", type=int, default=365, help="Days of historical data")
    args = parser.parse_args()

    from app.models.training_pipeline import train_all

    results = await train_all(symbols=args.symbols, days=args.days)

    print("\n" + "=" * 60)
    print("TRAINING RESULTS")
    print("=" * 60)
    for r in results:
        print(f"\n{r['symbol']}:")
        if "xgboost" in r:
            xgb = r["xgboost"]
            if "error" in xgb:
                print(f"  XGBoost: FAILED — {xgb['error']}")
            else:
                print(f"  XGBoost: accuracy={xgb['accuracy']}, f1={xgb['f1_score']}")
        if "lstm" in r:
            lstm = r["lstm"]
            if "error" in lstm:
                print(f"  LSTM:    FAILED — {lstm['error']}")
            else:
                print(f"  LSTM:    accuracy={lstm['accuracy']}, epochs={lstm['epochs_trained']}")


if __name__ == "__main__":
    asyncio.run(main())
