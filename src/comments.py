import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import time
import argparse
import requests

try:
    import yaml
except ImportError:
    yaml = None

CHANNEL_ID = "UCLOTIMzRzS7Q7sQlIztiLMw"
STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state")
REPLIED_FILE = os.path.join(STATE_DIR, "replied.json")

def load_config():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for filename in ["config.ci.yaml", "config.json"]:
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    if filename.endswith((".yaml", ".yml")):
                        if yaml:
                            return yaml.safe_load(f) or {}
                    else:
                        return json.load(f) or {}
            except Exception:
                pass
    return {}

def load_replied_ids():
    if os.path.exists(REPLIED_FILE):
        try:
            with open(REPLIED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("replied_ids", []))
        except Exception:
            return set()
    return set()

def save_replied_ids(replied_ids):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(REPLIED_FILE, "w", encoding="utf-8") as f:
        json.dump({"replied_ids": sorted(list(replied_ids))}, f, indent=2)

def generate_friendly_reply_gemini(comment_text, gemini_api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
    headers = {"x-goog-api-key": gemini_api_key, "Content-Type": "application/json"}
    prompt = f"Write a very short, polite, warm 1-sentence reply as the YouTube creator Jennifer Castro to this viewer comment: '{comment_text}'. Keep it natural, under 15 words."
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, headers=headers, json=body, timeout=15)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[reply] Gemini reply error: {e}", flush=True)
    return "Thank you so much for watching and supporting the channel!"

def generate_friendly_reply_groq(comment_text, groq_api_key, model="qwen/qwen3.8-27b"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"Write a very short, polite, warm 1-sentence reply as the YouTube creator Jennifer Castro to this viewer comment: '{comment_text}'. Keep it natural, under 15 words. Return ONLY the reply text, no quotes or explanations."
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 100
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"].strip()
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1].strip()
            return text
        else:
            print(f"[reply] Groq API returned {r.status_code}: {r.text[:200]}", flush=True)
    except Exception as e:
        print(f"[reply] Groq reply error: {e}", flush=True)
    return "Thank you so much for watching and supporting the channel!"

def generate_friendly_reply(comment_text, api_key, provider="gemini", model="qwen/qwen3.8-27b"):
    if provider == "groq":
        return generate_friendly_reply_groq(comment_text, api_key, model=model)
    return generate_friendly_reply_gemini(comment_text, api_key)

def run_comment_responder(access_token, api_key, max_replies=5, dry_run=False, provider="gemini", model="qwen/qwen3.8-27b"):
    mode_str = " (DRY-RUN MODE)" if dry_run else ""
    print(f"[comments] Checking for new viewer comments... [Provider: {provider}, Model: {model}]{mode_str}", flush=True)
    replied_ids = load_replied_ids()
    threads_url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "allThreadsRelatedToChannelId": CHANNEL_ID,
        "maxResults": 25,
        "order": "time"
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    
    res = requests.get(threads_url, headers=headers, params=params, timeout=20)
    if res.status_code != 200:
        print(f"[comments] Failed to fetch comment threads: {res.status_code} {res.text[:200]}", flush=True)
        # Even if API fails (e.g. no comments permission), test generation in dry run
        if dry_run:
            print("[comments] [dry-run] Testing AI reply generation with sample viewer comment...", flush=True)
            sample_comment = "Loved this video! Subscribed for more content."
            reply_text = generate_friendly_reply(sample_comment, api_key, provider=provider, model=model)
            print(f"[reply] [dry-run] Sample comment -> '{reply_text}'", flush=True)
        return

    items = res.json().get("items", [])
    replied_count = 0

    if not items:
        print("[comments] No comments found on channel.", flush=True)
        if dry_run:
            print("[comments] [dry-run] Testing AI reply generation with sample viewer comment...", flush=True)
            sample_comment = "Loved this video! Subscribed for more content."
            reply_text = generate_friendly_reply(sample_comment, api_key, provider=provider, model=model)
            print(f"[reply] [dry-run] Sample comment -> '{reply_text}'", flush=True)
        return

    for item in items:
        if replied_count >= max_replies:
            break
        top = item.get("snippet", {}).get("topLevelComment", {})
        comment_id = top.get("id")
        snippet = top.get("snippet", {})
        author_channel = snippet.get("authorChannelId", {}).get("value")
        text = snippet.get("textDisplay", "")

        # Do not reply to self or already replied comments (unless dry_run testing)
        if author_channel == CHANNEL_ID:
            continue
        if not dry_run and comment_id in replied_ids:
            continue

        reply_text = generate_friendly_reply(text, api_key, provider=provider, model=model)
        print(f"[reply] {comment_id} -> '{reply_text}'", flush=True)

        if not dry_run:
            reply_url = "https://www.googleapis.com/youtube/v3/comments?part=snippet"
            reply_body = {
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": reply_text
                }
            }
            r_res = requests.post(reply_url, headers=headers, json=reply_body, timeout=15)
            if r_res.status_code in [200, 201]:
                replied_ids.add(comment_id)
                replied_count += 1
                print(f"[comments] Replied to comment {comment_id}: '{reply_text}'", flush=True)
                time.sleep(1.5)
            else:
                print(f"[comments] Reply failed for {comment_id}: {r_res.status_code} {r_res.text[:100]}", flush=True)
        else:
            replied_count += 1
            print(f"[comments] [dry-run] Dry run active. Skipping YouTube post for comment {comment_id}.", flush=True)

    if not dry_run:
        save_replied_ids(replied_ids)
    print(f"[comments] Completed comment run. Replied to {replied_count} new comment(s).", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Comment Responder")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--max-replies", type=int, default=5, help="Max replies to post")
    args = parser.parse_args()

    is_dry_run = args.dry_run or os.environ.get("DRY_RUN", "false").lower() in ["true", "1", "yes"]

    from src.auth_env import get_access_token, get_ai_provider, get_gemini_api_key, get_groq_api_key
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

    run_comment_responder(token, api_key, max_replies=args.max_replies, dry_run=is_dry_run, provider=provider, model=model)
