SIGNAL_CHANGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, sans-serif; background: #0b0e11; color: #eaecef; padding: 24px;">
  <div style="max-width: 500px; margin: 0 auto; background: #1e2329; border-radius: 12px; padding: 24px; border: 1px solid #2b3139;">
    <h1 style="color: #f0b90b; font-size: 20px; margin: 0 0 16px;">INVESTOR Alert</h1>

    <div style="background: #2b3139; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
      <div style="font-size: 14px; color: #848e9c;">Signal Change</div>
      <div style="font-size: 24px; font-weight: bold; color: {signal_color};">{symbol} → {signal}</div>
      <div style="font-size: 14px; color: #848e9c; margin-top: 4px;">Confidence: {confidence:.0%}</div>
    </div>

    <div style="font-size: 14px; color: #eaecef; margin-bottom: 16px;">
      <strong>Alert:</strong> {message}
    </div>

    <div style="font-size: 13px; color: #848e9c; margin-bottom: 16px;">
      <div>TA Score: {ta_score}</div>
      <div>ML Score: {ml_score}</div>
      <div>Sentiment: {sentiment_score}</div>
    </div>

    <div style="font-size: 11px; color: #848e9c; border-top: 1px solid #2b3139; padding-top: 12px;">
      This is not financial advice. Always do your own research.
    </div>
  </div>
</body>
</html>
"""

SIGNAL_COLORS = {
    "STRONG_BUY": "#0ecb81",
    "BUY": "#0ecb81",
    "HOLD": "#f0b90b",
    "SELL": "#f6465d",
    "STRONG_SELL": "#f6465d",
}
