SIGNAL_ANALYSIS_PROMPT = """You are a cryptocurrency market analyst. Analyze the following data for {symbol} and provide a concise market assessment.

## Technical Analysis
- Signal: {ta_signal} (score: {ta_score})
- RSI(14): {rsi}
- MACD Histogram: {macd_hist}
- Price vs SMA200: {price_vs_sma200}

## ML Prediction
- Signal: {ml_signal} (confidence: {ml_confidence})
- XGBoost: {xgb_direction}
- LSTM: {lstm_direction}

## Sentiment
- Overall: {sentiment_signal} (score: {sentiment_score})
- Fear & Greed Index: {fear_greed}
- News sentiment: {news_score}

## Instructions
Respond in this exact JSON format:
{{
  "summary": "2-3 sentence market assessment",
  "action": "BUY / SELL / HOLD",
  "confidence": "HIGH / MEDIUM / LOW",
  "key_factors": ["factor 1", "factor 2", "factor 3"]
}}

Only respond with the JSON, no other text."""

NEWS_INTERPRETATION_PROMPT = """Summarize the market impact of these {symbol} headlines in 2-3 sentences:

{headlines}

Focus on what's actionable for a trader. Be concise."""
