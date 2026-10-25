import os
import time
import json
import requests

try:
    import yaml
except ImportError:
    yaml = None

BASE_REQUIRED_ENV_VARS = [
    "YT_CLIENT_ID",
    "YT_CLIENT_SECRET",
    "YT_REFRESH_TOKEN",
    "DRIVE_FOLDER_ID"
]

REQUIRED_ENV_VARS = BASE_REQUIRED_ENV_VARS

def get_ai_provider():
    """Read ai_provider from config.ci.yaml or config.json, default to 'gemini'."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for filename in ["config.ci.yaml", "config.json"]:
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    if filename.endswith((".yaml", ".yml")):
                        cfg = yaml.safe_load(f) if yaml else {}
                    else:
                        cfg = json.load(f)
                if isinstance(cfg, dict):
                    provider = cfg.get("metadata", {}).get("ai_provider") if isinstance(cfg.get("metadata"), dict) else None
                    if not provider:
                        provider = cfg.get("ai_provider")
                    if provider:
                        return str(provider).strip().lower()
            except Exception:
                pass
    return "gemini"

def validate_env():
    """Validate required environment variables, taking ai_provider into account."""
    missing = [v for v in BASE_REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        raise ValueError(f"Missing required environment variable(s): {', '.join(missing)}")

    provider = get_ai_provider()
    if provider == "groq":
        if not os.environ.get("GROQ_API_KEY"):
            raise ValueError(f"Missing required environment variable for provider '{provider}': GROQ_API_KEY")
    elif provider == "gemini":
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError(f"Missing required environment variable for provider '{provider}': GEMINI_API_KEY")
    else:
        if not os.environ.get("GROQ_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
            raise ValueError(f"Missing required environment variable for provider '{provider}': GROQ_API_KEY or GEMINI_API_KEY")

def get_access_token():
    validate_env()
    client_id = os.environ["YT_CLIENT_ID"]
    client_secret = os.environ["YT_CLIENT_SECRET"]
    refresh_token = os.environ["YT_REFRESH_TOKEN"]

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    for attempt in range(5):
        try:
            res = requests.post(token_url, data=data, timeout=20)
            if res.status_code == 200:
                return res.json()["access_token"]
            elif res.status_code in [400, 401]:
                raise RuntimeError(f"OAuth token refresh rejected: {res.status_code} {res.text}")
        except requests.exceptions.RequestException as e:
            if attempt == 4:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("Failed to obtain Google access token after multiple attempts.")

def get_gemini_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY is not set.")
    return key

def get_drive_folder_id():
    folder_id = os.environ.get("DRIVE_FOLDER_ID")
    if not folder_id:
        raise ValueError("DRIVE_FOLDER_ID is not set.")
    return folder_id

def get_groq_api_key():
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY is not set.")
    return key
