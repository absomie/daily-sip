# The Daily Sip ☕
A free, cozy personal news reader. Mobile-friendly, archived by day, automatically refreshed around 10 AM Bangkok time.

## Publish it for $0 with GitHub Pages

1. Create a **public** repository on GitHub called `daily-sip`. Public repositories are necessary for GitHub Pages on GitHub Free.
2. Upload **all the files and folders** from this project to the repository, including the hidden `.github/workflows/daily.yml` file. Easiest: extract the ZIP, open the folder in VS Code, then use GitHub Desktop to publish the folder as a public repository. Alternatively, use `git init`, `git add .`, commit and push.
3. In your repository, go to **Settings → Pages → Build and deployment → Source → GitHub Actions**.
4. Go to **Actions → Publish Daily Sip → Run workflow** to generate your first real edition and deploy your site.
5. Open the URL displayed in **Settings → Pages**. It will normally look like `https://YOUR-USERNAME.github.io/daily-sip/`.
6. Subsequent updates run automatically every day around **10 AM Bangkok time** (03:00 UTC). GitHub Actions schedules may be delayed or skipped during heavy load; use Run workflow to retry.

## What is free, and what isn't?
- GitHub Pages hosting and scheduled GitHub Actions are free for a small public repository within the GitHub Free limits.
- This version reads **publisher RSS feeds** (BBC, Guardian, Al Jazeera, NPR, Bangkok Post, CNA) with Google News RSS as a fallback, not paid news APIs.
- Summaries are written by Gemini (free tier) from the article's own text, in a friendly "tea" voice. Add a `GEMINI_API_KEY` repository secret (Settings → Secrets and variables → Actions). Without it, cards just show headlines and links.
- It does not generate original reporting or verify stories. If an article can't be read (paywall, blocked), the card links out instead of guessing.
- RSS availability and terms may change. For a personal reader, use links to the original sources; do not present this as a licensed syndication service.
- GitHub Pages sites are **public**, even if you're the only intended reader. Don't put private information or API keys in the repo.
- The archive keeps up to 90 dates in the dropdown. Older JSON files remain in the repository unless you remove them.

## Test locally

```bash
python scripts/update.py
python -m http.server 8000
```
Open `http://localhost:8000` (the update command needs internet access).

## Customize
- Edit colors in `styles.css` (`:root`).
- Edit the site name and introduction in `index.html`.
- Change sources and topics in `scripts/update.py` under `SLOTS`. Change the voice in the `PROMPT` text.
- Change the publishing time in `.github/workflows/daily.yml` (cron is UTC).

## Troubleshooting
- **Empty site:** Run the workflow manually; it won't show real articles until the first successful run.
- **RSS errors:** News feeds may temporarily block requests; the script preserves the previous edition if fewer than 3 feeds succeed.
- **Action permission error:** Settings → Actions → General → Workflow permissions → Read and write permissions (if available), then rerun.
- **404:** Confirm Pages is set to GitHub Actions and wait a minute after deployment.
