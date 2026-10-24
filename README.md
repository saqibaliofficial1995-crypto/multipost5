# multipost5 — YouTube Automation (Channel 5)

A fully cloud-native, automated YouTube publishing pipeline designed for **Erica Hawkins** (`UCLOTIMzRzS7Q7sQlIztiLMw`). Running 100% autonomously on GitHub Actions cloud runners.

## Channel & Asset Metadata
- **YouTube Channel:** Erica Hawkins
- **YouTube Channel ID:** `UCLOTIMzRzS7Q7sQlIztiLMw`
- **Owner Account:** `williamdsouza5445@gmail.com`
- **GitHub Account:** `saqibaliofficial1995-crypto`
- **GitHub Pages Site:** [https://saqibaliofficial1995-crypto.github.io/](https://saqibaliofficial1995-crypto.github.io/)
- **Privacy Policy:** [https://saqibaliofficial1995-crypto.github.io/privacy.html](https://saqibaliofficial1995-crypto.github.io/privacy.html)
- **First Live Video Published:** [https://youtu.be/Msyhi2iQ5mI](https://youtu.be/Msyhi2iQ5mI) (*Cat Party Surprise: Watch What Happens!*)

## Google Drive Integration
- **Inbox Folder ID:** `1w3BmKiRbzgZ-LtVYoreuqZR4fQA5p6Ep`
- **Uploaded Archive Subfolder ID:** `14TuIAiGMJIHmeMFJDr34V5_Y2ENaEqsl`

## Automated Workflows
1. **Daily Upload (`daily-upload.yml`)**:
   - **Cron:** `45 3,9,15 * * *` (08:45, 14:45, 20:45 PKT)
   - **Uploads:** 1 video per run (3 uploads / day)
   - Downloads next video chronologically from Drive inbox, normalizes to 1080x1920 30fps with FFmpeg, analyzes video with Gemini to generate high-performing titles/tags/descriptions, uploads to YouTube (public, not made for kids), moves file to `Uploaded/`, and commits state back to repository.
2. **Comment Replies (`comment-replies.yml`)**:
   - **Cron:** `30 16 * * *` (21:30 PKT)
   - Fetches unreplied comments on channel videos, drafts context-aware replies via Gemini, posts replies, and commits replied comment IDs to `state/replied.json`.
3. **Weekly Analytics (`weekly-analytics.yml`)**:
   - **Cron:** `30 17 * * 0` (Every Sunday at 22:30 PKT)
   - Aggregates channel metrics across the past 7 days and commits formatted markdown reports into `reports/`.

## Action Secrets Configuration
- `DRIVE_FOLDER_ID`: `1w3BmKiRbzgZ-LtVYoreuqZR4fQA5p6Ep`
- `GEMINI_API_KEY`: Google Gemini API key for metadata generation and comment interaction
- `YT_CLIENT_ID`: OAuth 2.0 Desktop Client ID
- `YT_CLIENT_SECRET`: OAuth 2.0 Desktop Client Secret
- `YT_REFRESH_TOKEN`: OAuth 2.0 Refresh Token with YouTube & Drive scopes
