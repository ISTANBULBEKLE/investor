from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./investor.db"

    # Binance
    binance_base_url: str = "https://api.binance.com/api/v3"

    # CoinGecko
    coingecko_api_key: str = ""
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"

    # Resend email
    resend_api_key: str = ""
    alert_email_to: str = ""
    alert_email_from: str = "investor@example.com"

    # Redis (optional in dev)
    redis_url: str = ""

    # Ollama LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.3"

    # Reddit
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "investor-app/1.0"

    # Analysis
    default_symbols: list[str] = ["BTC", "ETH", "HBAR", "IOTA"]
    analysis_interval_minutes: int = 30

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
