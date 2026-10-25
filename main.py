import sys
import os
import argparse
from src.ci_run import execute_pipeline
from src.comments import run_comment_responder, load_config
from src.analytics import run_weekly_analytics
from src.auth_env import get_access_token, get_ai_provider, get_gemini_api_key, get_groq_api_key

def main():
    parser = argparse.ArgumentParser(description="Channel 5 Automation Pipeline")
    parser.add_argument("--mode", choices=["upload", "comments", "analytics"], default="upload",
                        help="Mode to run: upload (default), comments, or analytics")
    parser.add_argument("--config", default="config.ci.yaml", help="Path to config file")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    args = parser.parse_args()

    if args.mode == "upload":
        execute_pipeline(args.config)
    elif args.mode == "comments":
        token = get_access_token()
        cfg = load_config()
        provider = cfg.get("metadata", {}).get("ai_provider") or cfg.get("ai_provider") or get_ai_provider()
        model = cfg.get("metadata", {}).get("model") or cfg.get("model") or "qwen/qwen3.8-27b"
        if provider == "groq" or (os.environ.get("GROQ_API_KEY") and not os.environ.get("GEMINI_API_KEY")):
            api_key = get_groq_api_key()
            provider = "groq"
        else:
            api_key = get_gemini_api_key()
            provider = "gemini"
        run_comment_responder(token, api_key, dry_run=args.dry_run, provider=provider, model=model)
    elif args.mode == "analytics":
        token = get_access_token()
        run_weekly_analytics(token)

if __name__ == "__main__":
    main()
