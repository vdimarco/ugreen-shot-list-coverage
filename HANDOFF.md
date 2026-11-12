# Handoff: UGREEN Hackathon 2026 on AI NAS

Read this first in a new session. It is the same file in both repos.

## Repos

| Entry | Repo | Track |
|---|---|---|
| Household Wiki | https://github.com/vdimarco/ugreen-household-wiki. (the name ends with a period, on purpose) | Open Innovation |
| Shot List Coverage | https://github.com/vdimarco/ugreen-shot-list-coverage | Unleash Your Creativity |

```bash
git clone "https://github.com/vdimarco/ugreen-household-wiki."
```

```bash
git clone https://github.com/vdimarco/ugreen-shot-list-coverage
```

## Dates (Pacific Time)

| Date | What |
|---|---|
| Sun Nov 15, 11:45 PM | Round 1 closes: proposal PDF and Skill ZIP on Devpost |
| Sat Nov 21 | Finalists are told by email (up to 30) |
| Nov 22 to Nov 28 | One assigned test day on a remote UGREEN AI NAS iDX6011 Pro |
| Mon Nov 30, 11:45 PM | Round 2 closes: final Skill ZIP and a public YouTube video, 3 minutes or less, recorded on the assigned NAS |

Devpost: https://ugreenhackathon.devpost.com/ (automated fetches get HTTP 403; read it in a browser).

## Status

Done in both repos:

- Skill package in `household-wiki/` or `shot-list-coverage/`. Static check: `static-pass`, 0 errors, 0 warnings.
- `dist/*.zip`: the Round 1 Pre-test Skill Package. It matches the Skill folder.
- `proposal/*.pdf`: the Round 1 proposal, 2 pages, under 500 words.
- `SUBMISSION.md`: copy-paste text for every Devpost field, the files to upload, and a checklist.
- `media/cover.png`: the Devpost gallery cover.
- `demo/`: demo data, test plan, expected results, and a concept preview video with narration.

Not done (needs the user):

1. Check the Devpost Rules tab: can one team enter two Skills? If not, submit Household Wiki only.
2. Check the entrant name "Vaughn DiMarco" in both proposals. Add teammates and their consent if any.
3. Create the Devpost projects and upload the files in `SUBMISSION.md`.
4. Optional: upload the concept videos to YouTube and paste the links into Devpost.

After Round 1, if selected:

1. On the test day, run the test plans: `demo/test-plan.md` in each repo.
2. Score Shot List Coverage reports with `demo/score_report.py`.
3. Record the real run, then rebuild the videos with real footage (`demo/video/README.md`).
4. Fix the Skills from the test results, run the static check again, and rebuild `dist/*.zip`.

## Static check (the UGREEN Skill kit)

The kit is not in the repos, because it is UGREEN's file. Download it from the Starter Kit page: https://ai.ugreen.com/pages/hackathon-starter-kit. The file used here was `uliya-skill-kit-0.7.3-en.zip`:

https://cdn.shopify.com/s/files/1/0630/9416/1602/files/uliya-skill-kit-0.7.3-en.zip?v=1790578898

```bash
node path/to/uliya-skill-kit/scripts/check-skill.mjs household-wiki
```

```bash
node path/to/uliya-skill-kit/scripts/check-skill.mjs shot-list-coverage
```

Rules the checker enforces, learned while building:

- Only `SKILL.md` and Markdown files in `references/` are allowed. No README, scripts, or other files in the Skill folder.
- Required headings: `# Goal`, `# Required input`, `# Workflow`, `# Completion and failure`.
- Evidence heading `# Generation-time capability evidence` with lines like ``- `ug-photo` → `photo-agent` `` (the arrow is the Unicode character →).
- Each delegate line: `` `delegate --target AGENT --instruction '...'` `` in backticks, the instruction in single quotes, with no apostrophes, no `<...>`, and no ` --` inside it.
- The text "delegate --" must not appear anywhere else, even in a sentence.
- No paths that start with `/nas`, `/mnt`, `/volume`, or `/share`, and no words such as "cat ", "rm ", "fetch(" outside delegate lines.
- Do not put "skip", "ignore", "bypass", or "disable" near "approval" or "permission" in one line.
- All five states must appear: `completed`, `failed`, `cancelled`, `waiting_user`, `waiting_approval`.

## Higgsfield assets (Shot List Coverage)

The demo shoot in `demo/generated/` was made on Higgsfield with GPT Image 2.6. The 4 characters are saved as reference elements in the user's Higgsfield workspace. Use them to make more photos with the same faces (put `<<<ELEMENT_ID>>>` in the prompt):

| Character | Element name | Element ID |
|---|---|---|
| Ana | slc-ana | e556ddc8-2778-461c-81e8-101d28a1008b |
| Daniel | slc-daniel | e3f6b62b-4edc-4276-b9b7-3e45d7e2b013 |
| Grandma Rosa | slc-rosa | 148b0206-af1d-4b78-96de-1a54a51dd32b |
| Maya | slc-maya | be292ade-dcdc-419f-b87c-2e4458e86346 |

Notes:

- Scenes at quality "low", 1k, 3:2 cost 0.25 credits each and look real enough.
- The image service allows about 7 jobs at a time. Larger batches fail with 429; failed submissions are not charged.
- Narration: Seed Audio, preset voices "Holden" (Shot List Coverage) and "Helena" (Household Wiki). Cost was 0.6 to 1.2 credits per line, more than the 0.7 preflight.
- Spent in the first session: about 32 credits. The account also showed 40 credits of "3D Rigging" on Nov 11 that the first session did not make. The user should check it.

## Memory

Project notes are in Honcho, workspace `shared-memory`, session `ccr-ugreen-hackathon-2026-11`, peer `von`.
