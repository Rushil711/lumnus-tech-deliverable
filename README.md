# Lumnus Tech Deliverable — Outreach Studio

Research recognizable companies, compare projects for different teams, and review tailored outreach before sending. Built for Lumnus Consulting at UC San Diego, with projects grounded in [Lumnus’s published services](https://lumnusconsulting.net/services).

**Anyone with a Mac or Windows computer can run their own copy. No coding experience, developer account, or API key is needed for the free demonstration.** This is a local application: GitHub stores the software, not a hosted, shared workspace.

## Quick start — free demo

1. **Download the project:** click the green **Code** button above, then **Download ZIP**. Alternatively, [download it directly](https://github.com/Rushil711/lumnus-tech-deliverable/archive/refs/heads/main.zip).
2. **Extract the ZIP** into a folder you will keep, such as Documents. On Windows, choose **Extract All**; do not run the app from inside the ZIP.
3. **Install Python 3.10 or newer** from [python.org/downloads](https://www.python.org/downloads/) if needed. On Windows, enable **Add Python to PATH** in the installer. No extra packages or installation commands are required.
4. **Start the app:**
   - **Mac:** double-click `Launch Lumnus.command`.
   - **Windows:** double-click `Launch Lumnus.bat`.
   - Keep the window that opens running while you use the app.
5. Your browser opens at **http://127.0.0.1:8765**. If it does not, enter that address yourself after starting the launcher.
6. Click **Load all three demo companies**. Explore **HubSpot, Patagonia, and Oura**, each with three distinct team opportunities and editable pitches.

The prepared demo is free and works without internet access after download, except when opening external source links. It replays prepared research; it does not perform a new web search.

**Next time:** open the same launcher. Your saved companies and drafts will still be there. To stop, return to the launcher window and press **Control+C**.

## Try the workflow in five minutes

1. Open a company and expand **Compare all teams before choosing**.
2. Select a team. Read the public evidence, proposed need, Lumnus service match, deliverables, evaluation criteria, and assumptions.
3. Open **Draft & review**. Edit the email, enter a recipient, and click **Save changes**.
4. For a classroom demonstration only, use `demo@example.com`; do not send. For real outreach, independently verify the recipient and all claims.
5. Complete the three review checks, enter your reviewer name, then click **Approve saved draft**. Copy/email-app controls appear only after approval.
6. Edit the approved email and save again: approval clears, so the new text must be reviewed.
7. Open **Outreach pipeline** to track teams, owners, stages, and follow-up dates. **Sent** records a manual send; the app never sends emails itself.

Use **Company details** to record an owner, contact, warm connection, and coordination notes. HubSpot’s built-in connection is explicitly illustrative, not a real introduction. Warm-introduction guidance helps you ask a connector for permission before naming them in outreach.

## Research a brand-new company — optional paid mode

You can enter any new company name. This requires internet access and a funded OpenAI API account with access to the configured model. The account associated with the API key pays for usage; the repository does not provide credits or use its author’s account.

1. Obtain an API project key through your own or your team’s authorized OpenAI account. See [API keys](https://platform.openai.com/api-keys) and [usage](https://platform.openai.com/usage).
2. In the app, open **Settings & data**, paste your key into the password field, and choose **Save key on this computer**. Saving the key makes no paid request. Do not put keys in GitHub, screenshots, or chat messages.
3. Click **Add company**. Enter a company not already in your workspace. An optional city, region, or website helps distinguish similarly named companies.
4. Choose **Live web research · any company · paid API**, read and check the charge acknowledgment, then select **Start paid research**.
5. Keep the launcher running. You can browse while research runs. The workspace shows progress; a successful run creates a company with several opportunities and pitches.
6. Open the results and verify their sources and scope. Live output is a proposal for human review, not proof of a buying need or a verified contact.

The default model is `gpt-6.2-sol`. Each request allows at most five built-in tool calls and 8,000 output tokens, including reasoning; these are **not a dollar spending cap**. At rates checked November 25, 2026, an illustrative run with 20,000 input tokens, 5,000 output tokens, and five searches costs about **$0.14**. Actual usage varies; failed or interrupted requests may also be charged. There are no automatic paid retries. Check [current pricing](https://developers.openai.com/api/docs/pricing) before the demo.

**Verification limit:** the automated tests simulate provider responses. A successful real paid provider run has not yet been verified in this release. Rehearse one new-company run with your account before presenting; keep the prepared demo available as an honestly labeled fallback.

Only the company name, optional location/website hint, and public service catalog are submitted for research. Owner, contact, and warm-connection notes remain local. The key is stored in the local `.env` file, excluded from Git and the sharing package. Advanced users may set `OPENAI_MODEL` in `.env` to a compatible Responses/web-search model and restart; saving a key through Settings resets the model to the default.

## Add prepared research for another company — free

Choose **Import a prepared brief** in Add company. Download the example JSON from the dialog or Settings, replace it with genuine source-backed research for your company, and select the edited file. The brief’s company name must match the intake name. It needs 3–6 distinct opportunities, valid source URLs/dates, concrete deliverables, and recognized Lumnus service IDs, including a technology service for every project.

Imported research is explicitly labeled and makes no paid call. This is an advanced fallback for research prepared elsewhere; it does not automatically research an arbitrary company for free. A workspace backup JSON is a different format and cannot be used as a prepared brief.

## Using this with other Lumnus members

- Each person can download and run a separate copy using the same steps. No author-specific paths or credentials are required.
- Each computer has its **own saved records**. Copies do not synchronize automatically, and `127.0.0.1` always means the computer you are using.
- For an actual campaign, designate **one authoritative workspace and one owner per company**. Coordinate before contacting another team at that company.
- Use **Settings & data → Export pipeline CSV** to share a progress sheet. Review exports before sharing: they can contain contact details.
- Duplicate company checks, duplicate-recipient send checks, and stale-edit protection apply inside one workspace. They cannot coordinate independent copies.
- This prototype has no sign-in or authenticated reviewers. Do not expose its local server publicly. A hosted multi-user version requires authentication, shared storage, access controls, and campaign coordination described in the report.

## Save, back up, and update

Click **Save changes** to save draft edits. Records are stored in the automatically created `data` folder. Navigating away from unsaved draft edits prompts a warning.

**Full backup:** stop the app, then copy the entire `data` folder to a safe location. **Restore:** stop the app, keep the current folder as a fallback, and replace it with your backup. Exported workspace JSON is useful for inspection, but the app does not import it as a full restore.

**Update:** download the newer code into a new folder. With both copies stopped, copy your existing `data` folder into the new copy. Configure your API key again in Settings, or securely move your local `.env`. Keep the old copy until you have checked the new one.

## Troubleshooting

| What you see | What to do |
| --- | --- |
| Python is missing | Install Python 3.10+ from python.org, then reopen the launcher. On Windows enable Add Python to PATH. |
| Mac launcher will not execute | Open Terminal in the extracted folder and run `python3 server.py`. You can also run `chmod +x "Launch Lumnus.command"` once to restore the launcher's permission. Do not bypass an unfamiliar security warning. |
| Windows launcher does not find Python | Open a terminal in the extracted folder and run `py -3 server.py`, or reinstall Python with PATH enabled. |
| Browser cannot connect | Start the launcher and keep it open, then visit `http://127.0.0.1:8765`. Opening `index.html` directly does not start the app. |
| Port already in use | Reopen the already-running app, or start `python3 server.py --port 8766` and visit `http://127.0.0.1:8766`. |
| Key rejected or quota reached | Check your own API key, model access, and billing. A saved key is not a connectivity test. |
| Certificate error on Mac | Use the Python installer’s `Install Certificates.command`. Never disable certificate verification. |
| Research fails or returns incomplete sources | Existing records remain saved. Check provider usage before choosing a manual retry. Use prepared mode if needed; do not describe it as fresh research. |
| Company already exists | Search the workspace and enable **Show archived**. Open or restore the existing record instead of duplicating outreach. |
| Approval will not complete | Save edits first, add a verified recipient, complete all three checks, and enter a reviewer name. |
| Another window changed the draft | Refresh and review the latest saved version before editing again. |

## Report and project maintenance

- [Written report and presenter walkthrough](docs/REPORT.md)
- Printable report: open `static/report.html`, or **Playbook & report → Read report** in the app.
- [Implementation, tests, limitations, and next steps](PROJECT_STATUS.md)

For maintainers, the app uses Python’s standard library and SQLite. No package installation is needed:

```sh
python3 -m unittest discover -s tests -v
python3 build_report.py
python3 package_release.py
```

Tests use temporary records and no paid API calls. HTTP tests need permission to open a local test server. Mac workflow and local tests have been exercised; the Windows launcher has not yet been tested on a Windows machine. This repository contains software and public prepared examples, not private campaign records, keys, or a guarantee of consulting outcomes.
