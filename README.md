# Shot List Coverage

An entry for the [UGREEN Hackathon 2026 on AI NAS](https://ugreenhackathon.devpost.com/), track Unleash Your Creativity.

Shot List Coverage is a UGOS Skill for photographers. It compares a client shot list with the photos of a shoot on the NAS. It marks each shot as covered, weak, or missing, and gives the best frame and 2 alternates for each shot. After the photographer confirms, it makes an album of the best frames and saves a coverage report in the shoot folder. It only reads photos.

## Contents

| Path | What it is |
|---|---|
| `shot-list-coverage/` | The Skill package: `SKILL.md` and `references/` |
| `dist/shot-list-coverage.zip` | The Pre-test Skill Package for Round 1 |

## Workflow

1. Check the shoot folder and the photo index.
2. Read the shot list and confirm it with the user.
3. Find candidates for each shot by scene, person, object, text, and time.
4. Check the candidates with the vision model: match, focus, eyes, and framing.
5. Report each shot, then make the album and save the report after confirmation.

## Check and build

```bash
node path/to/uliya-skill-kit/scripts/check-skill.mjs shot-list-coverage
```

```bash
rm -f dist/shot-list-coverage.zip && zip -qrX dist/shot-list-coverage.zip shot-list-coverage
```

Last result: `static-pass`, 0 errors, 0 warnings.
