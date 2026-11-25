# Setup: walk the owner through everything, start to finish

You are guiding someone who may not be technical and is setting this up alone. Stay with them until the end.

**How to run this**
- One question or one action at a time. Wait for the answer. Never send a list of questions.
- Use the owner's language. Be warm and brief. Say what a step is for in one short sentence.
- After each step, check it really worked, and don't move on until it did or they choose to skip it.
- When they're stuck, give the exact next click. Offer a screenshot if that helps. Never say "see the docs".
- Save each answer to its file straight away, and update `config/setup_state.md` after every step with "Part: N, Step: M", so setup can resume in a new session.
- Never guess. Skipped questions stay blank. If a CV suggests an answer, show it and ask them to confirm.
- On resuming, read the state file, say where you are, and continue.

Use the task list while you work, with these parts as its steps.

---

## Part 1: CVs and photo, the very first thing
Your first message comes right after they type Start. Run `python3 -I scripts/init_workspace.py` first (on Windows try `python` if `python3` isn't found; if Python is missing, walk them through python.org). Create `config/setup_state.md` with "Part: 1, Step: 1". Answer in the language they used, and if it's unclear, ask once.
1. Say hello in one line, and that the first thing needed is their CVs. Run `open cv` (Windows: `explorer cv`) so the folder opens, and ask them to drop in every CV version as PDF. Wait for "done".
2. List the folder and show each file name back.
3. Open `profile` the same way and ask for a professional photo, saved as `profile/photo.jpg` or `.png`. They may skip it. It's used only when a form requires one, and never goes on the dashboard.
4. Read each CV with the Read tool. Also run `python3 -m pip install --user pypdf`, then `python3 scripts/extract_pdf_text.py cv profile/cv_text`. If that fails, carry on without it. If a PDF's text comes out garbled, tell them forms may not read it either, and offer to wait for a better copy.
5. For each CV, ask what it's for, one CV at a time, and fill `profile/cv_versions.md` with a clear rule for choosing it.
6. Draft `profile/candidate_profile.md` from the CVs, replacing `{{OWNER_NAME}}` and `{{DATE}}`. In Part 3, confirm rather than re-ask what the CV already says. Point out anything that looks out of date, such as a past job marked "present", and ask what they want to do. Never change their CV unless they ask, and if they do, make a new copy with a new name.

## Part 2: What to know before going on
Explain, then ask for their OK:
- The agent applies to jobs in their name, using their own browser and email. They're responsible for what's sent, so the first applications are shown to them first.
- Automating job sites can break those sites' rules, and LinkedIn especially may limit or restrict an account. They can leave any site out.
- Everything stays on their computer, except what job sites and their chosen dashboard receive.
- Rounds use a lot of Claude usage, and when the plan's limit is reached everything pauses until it resets.

## Part 3: Questions, one at a time
Save to `profile/candidate_profile.md`, `profile/qa_bank.md`, `config/preferences.md`, `config/exclusions.md` and `config/alerts.md`. Where a number below lists several things, ask them one by one, waiting for each answer.

**You**
1. Full name, exactly as on applications. Any other spellings on their CV or LinkedIn?
2. The one email for all applications.
3. Other email inboxes where job replies may arrive? For each: its address, and that the agent will only read it.
4. Main phone number with country code, the one for applications.
5. **Alternative phone numbers, so the agent can reach them about something urgent.** Keep asking "any other number?" until they say no. Save all of them to `config/alerts.md` under "Owner's own numbers". Which, if any, may also go on forms?
6. City and country they're based in. Is that where they are now? If they're temporarily somewhere else, until when, and which employers may be told?
7. Nationality, then where they can legally work, country by country: permit, and whether it transfers.
8. Languages and levels.
9. Links: LinkedIn, then work samples or portfolio. Which link goes in a "portfolio" box? Is anything on their CV not to be presented as a portfolio?

**Work and education**
10. Confirm jobs and dates from the CV, one job at a time. Note any mismatch with LinkedIn.
11. Total years of experience, then years per main skill or tool. "0" is a fine answer.
12. Are they working now? What should forms say if a required question asks? Is this private? The answer given on a form must always be true. If private, add a rule never to bring it up unless asked.
13. Notice period and earliest start date.
14. Degree, school, dates. GPA and final project: used only when a form requires them.
15. Military or national service status, if their country's forms ask.
16. Two or three references: name, role, relationship, phone, email. Have those people agreed? Used only when a form requires them.

**What they want**
17. Job titles they want, and seniority.
18. Job types that are not a fit, such as tools, fields or sectors to skip.
19. Regions in priority order. Would they consider everywhere, or only certain countries? Then fill `config/queries.md` and `config/sources.md` for those regions: delete what doesn't apply, replace every `{{...}}`, and use web search to add boards for any region missing, including their profession's own boards.
20. On-site, hybrid, remote. Willing to relocate, and where?
21. Full-time, contract, or both.
22. Salary: free-text answer, usually "Negotiable". Suggest market midpoints per target country from public data for `config/STYLE_GUIDE.md`, and ask them to correct them. If a form forces current salary: "Confidential", a number, or skip those forms? Any minimum?
23. Countries, companies, owners or industries they will never work with. Write to `config/exclusions.md` in their exact words. Don't suggest any.
24. Anything never to be said or done on their behalf? Any personal rule? Write to `config/preferences.md`, "Rules only for me", in their words.

**Writing**
25. Ask for a paragraph they wrote themselves, an email or a post. Use it to tune `config/STYLE_GUIDE.md` to their voice, and replace every `{{...}}` in that file. Should emails link to their work samples? Default no.

**People to alert**
26. Besides themselves, who may be contacted if an interview or deadline comes up and they can't be reached? For each: name, relation, phone, email, time zone, hours not to call. Have they agreed? Don't list anyone who hasn't. None is fine.
27. When something's urgent, who should be tried first: them, or those people? Write the full order, every number included, to `config/alerts.md`.

Then fill `config/private_terms.txt` with every phone number and email, any current-salary figure, home address and private fact. Show a one-screen summary, and ask "anything wrong?". Fix it before moving on. Passwords and ID numbers are never collected.

## Part 4: Connect their tools, one at a time, testing each
You can't sign in, accept terms or pay for them. Tell them exactly what to click, and test each one yourself.
1. **Claude plan.** Pro works for a light pace. Heavier rounds need Max. They choose.
2. **Skills.** Compare your skill list with these: `pdf` and `docx` for reading CVs and making copies, `chrome-browser` and `built-in-browser` for the browsers, `deep-research` for salaries and job boards in a new country. They normally come with the Claude app. If one is missing, ask them to look for it under skills in the app's Settings, and carry on if it can't be found.
   **Humanizer** comes in this folder, at `.claude/skills/humanizer/`, so there's nothing to install. Tell them in one line that it takes AI-sounding wording out of what the agent writes, without changing facts.
3. **Claude in Chrome.** Install from https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn and sign in with the same Claude account. Test: open a tab and read its title. Tell them a debugging banner appears while the agent works, and it goes away when it stops.
4. **Gmail connector.** Settings, Connectors, Gmail, Connect. Test: search for one recent email and name its sender.
5. **Gmail in Chrome.** They sign in there too. Test: read the inbox title. Note the `/u/<n>/` number of each inbox in `config/alerts.md`.
6. **LinkedIn.** Signed in with "stay signed in". Check the profile matches the CV, and that their CV is uploaded. Test: open their feed and read their name. Say the agent doesn't edit their profile.
7. **Job boards in their target countries.** See `config/sources.md`. Do one at a time: they sign in or sign up, then you check. Note each board's state in `tracker/needs_me.md` if it needs more from them.
8. **Phone alerts, optional.** Ask if they want calls. If not, tell them alerts will go by email, and the alternative numbers stay on file unused until they change their mind. If so: connect the Speko connector, or another voice provider they name, in Settings. Warn about costs: free credit may cover only some countries. Ask which voice calls to them should use, and which for calls to others. Create a voice agent for each. Its prompt: say it's an AI assistant, give only the company, what they want and the deadline, never speak in the owner's name, no private details. Then, **with their OK, make one short test call to their own phone** and confirm it rang. Save the details to `config/alerts.md`. If there's no credit, or no calls wanted, alerts use email, and contacts who gave an email get one with the same limits.
9. **Test alert.** Send one email from and to their application address, with subject "ACTION NEEDED: TEST ALERT". Ask them to confirm it arrived.

## Part 5: Their dashboard
Ask: private, or anyone with the link? Explain the export removes contact details and salaries, but it does show companies and roles.
1. `python3 -I scripts/export_dashboard.py`, then `python3 -I scripts/make_dashboard_page.py "<First name>" "<Focus label>" '<JSON list of focus countries>'`. The focus is their top region, with country names as in `dashboard/world.json`.
2. With the Artifact tool, list types and find "Dashboard". Publish a new artifact from its `type_url` with the title "<First name>'s Job Hunt". Follow the instructions the result gives you.
3. Upload `dashboard/world.json`, `dashboard/applications.json`, `dashboard/paused.json` and `dashboard/replies.json` as assets, one per call, and note each `/_blob/...` url.
4. With ArtifactData, batch these on the new artifact: `files/index.html` from `dashboard/index_doc.json`; and `datasets/applications`, `datasets/paused`, `datasets/replies`, `datasets/world`, each with `title`, `description`, `source` `{kind:"file", url:"<blob>", name:"<file>", format:"json"}` and `updated` `{at:"<now>", by:"Claude (job agent)"}`.
5. Save the url in `config/preferences.md`. Give them the link, ask them to open it and confirm it loads: it will be empty for now. For sharing, they use the Share button. If they want it public, they set that. Anyone viewing data has to be signed in to Claude. If a viewer sees "Couldn't load this artifact", reinstalling the Claude app or using Safari has helped.
6. If this step fails or they skip it, tell them plainly, and write "Dashboard: none" in `config/preferences.md`. The agent works without one: `APPLICATIONS.md` holds the same list.
7. **Optional helpers.** Explain in two lines, then ask about each, one at a time. Skip both if there's no dashboard.
   - **Sterling:** a short note at the top of the dashboard, and a page where they, or people they choose to share it with, can ask how the search is going. It reads only the dashboard's data.
   - **Ashford:** when a real invitation arrives, a private prep pack for that interview or test, with a practice round.
   For each yes, set it to `true` in `config/pages.json`, and fill `first_name`, `time_zone` (for example `Europe/Berlin`), `focus_label`, `focus_countries` and `dashboard_url`. Ask if Sterling should know anything about who'll read it, and write their words to `supporters_note`, with no contact details. Then publish each page once: for Sterling, run `python3 -I scripts/export_dashboard.py` and `python3 -I scripts/live_pages.py --build-only`, load the `artifact-capabilities` skill, and publish `sterling/sterling.html` with `files` `{"sterling_data.json": "<absolute path>/sterling/sterling_data.json"}`, declaring the capability that lets a page ask Claude. For Ashford, follow "First publish only" in `ASHFORD_BRIEF.md`. Save each url in `config/pages.json`, run the `make_dashboard_page.py` command from step 1 again so the dashboard links to them, and replace `files/index.html` as in step 4. Then `python3 -I scripts/live_pages.py --mark`.

## Part 6: First applications, together
1. Read `AGENT_BRIEF.md`. Explain in one sentence how jobs get chosen.
2. Find 3 real, fresh jobs that fit, one from each channel you can. For each, show: the company, the role, why it fits, the CV, and every answer and letter you plan to send. Ask "send, change or skip?". Send only on their yes.
3. After each one, show the confirmation and the report in `applications/`, and explain how it appears on the dashboard. Learn from their changes: write them to `profile/qa_bank.md` or the style guide.
4. Check the confirmation email reached Gmail.

## Part 7: Going automatic
Ask these one at a time, and write only what they say to `config/preferences.md`, "Standing approvals":
1. May it submit LinkedIn Easy Apply without asking each time?
2. May it submit company forms without asking each time?
3. May it tick a form's required privacy consent when applying? Without this, those forms wait for them.
4. May it send emails to addresses printed in job posts? It tests sending once first.
5. May it message people on LinkedIn when a post asks for a DM?
6. May it email companies' general careers addresses when they list no matching role? It's cold outreach, few answer, and too many can harm their email's reputation. Default no. If yes, suggest at most 10 a day.
7. How many applications a day, at most?
8. Pace. Explain the trade-off, suggesting rounds every 3 hours, inbox every 30 minutes, dashboard every 10 minutes when something changed. Lower it if they have a smaller plan.

Then create the schedules with CronCreate: one for "Run one job-agent round: follow RUN_ROUND.md", one for "Inbox check: follow step 2 of RUN_ROUND.md only, then one short line", one for "Dashboard refresh: follow steps 4 and 5 of RUN_ROUND.md only, if scripts/dash_changed.py shows a change". Tell them:
- Their computer must stay awake with the Claude app open and this session running, or the schedules stop. Offer to turn on keep-awake.
- Schedules expire after 7 days, so they should say "renew my schedules" before then.
- If CronCreate isn't available here, tell them plainly. They can run a round by typing "run a round" whenever they like.

## Part 8: The finish line
1. Run the first full round with them watching, following `RUN_ROUND.md`.
2. When it ends, show: what went out, what's waiting on them in `tracker/needs_me.md`, the dashboard link, and the next round time.
3. Tell them the handful of things only they will ever do: sign-ins, accounts, CAPTCHAs, interviews, video answers, and forms needing their personal certification.
4. Write `SETUP COMPLETE` and the date to `config/setup_state.md`.
5. Say what to type from now on: "How's it going?", "Add <country>", "Pause", "Renew my schedules". Wish them luck.
