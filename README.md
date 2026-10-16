# multipost5 — YouTube Automation (Channel 5)

Fully cloud-native YouTube auto-upload and channel management system running 100% on GitHub Actions.

## Channel Details
- **Channel Name:** Erica Hawkins
- **Channel ID:** `UCLOTIMzRzS7Q7sQlIztiLMw`
- **Owner Account:** `williamdsouza5445@gmail.com`
- **GitHub Account:** `williamdsouza5445-lang`

## Google Drive Folders
- **Inbox Folder ID:** `1w3BmKiRbzgZ-LtVYoreuqZR4fQA5p6Ep`
- **Uploaded Folder ID:** `14TuIAiGMJIHmeMFJDr34V5_Y2ENaEqsl`

## Automated Workflows & Schedules
1. **Daily Upload (`daily-upload.yml`):**
   - Cron: `45 3,9,15 * * *` (08:45, 14:45, 20:45 PKT)
   - Uploads up to 1 video per run (3 uploads/day)
   - Encodes via FFmpeg, generates AI titles/tags via Gemini, publishes to YouTube, updates `state/uploaded.json`, and moves source file to `Uploaded`.
2. **Comment Replies (`comment-replies.yml`):**
   - Cron: `30 16 * * *` (21:30 PKT)
   - Fetches unreplied comments, generates engaging context-aware replies via Gemini, and posts replies.
3. **Weekly Analytics (`weekly-analytics.yml`):**
   - Cron: `30 17 * * 0` (Sunday 22:30 PKT)
   - Aggregates 7-day YouTube analytics metrics and commits markdown report under `reports/`.

## Required GitHub Actions Secrets
- `DRIVE_FOLDER_ID`: Google Drive inbox folder ID
- `GEMINI_API_KEY`: Google Gemini API key for metadata and comment replies
- `YT_CLIENT_ID`: OAuth 2.0 Desktop Client ID
- `YT_CLIENT_SECRET`: OAuth 2.0 Desktop Client Secret
- `YT_REFRESH_TOKEN`: OAuth 2.0 Refresh Token with YouTube and Drive scopes
