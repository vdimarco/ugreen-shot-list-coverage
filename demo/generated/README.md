# Generated Demo Shoot

A ready-made test shoot for the Rivera-Okoro engagement party shot list. It replaces the staged shoot in `../capture-plan.md` when people are not available. You can also use both.

**All photos are AI-generated. The people are fictional.** Each photo has a small "SAMPLE - AI-generated fictional photo" mark, and its EXIF data says the same.

## Contents

| Path | What it is |
|---|---|
| `photos/` | 53 JPEG photos, `IMG_2001.jpg` to `IMG_2053.jpg`, in time order. EXIF capture times are on 2026-11-21, between 16:00 and 18:50. |
| `manifest.csv` | For each file: capture time, shot number, role, content, and the Higgsfield job ID |
| `characters/` | The 4 reference portraits that keep the faces the same in each photo |

## Characters

| Role on the shot list | Name to give the face in the photo app | Portrait |
|---|---|---|
| Ana | Ana Rivera | `characters/ana.jpg` |
| Daniel | Daniel Okoro | `characters/daniel.jpg` |
| Grandma Rosa | Rosa Rivera | `characters/rosa.jpg` |
| Maya, best friend | Maya Chen | `characters/maya.jpg` |

## Roles in the manifest

| Role | Count | Meaning |
|---|---|---|
| match | 40 | Shows a shot from the list. Each of the 16 present shots has 2 or 3 matches. |
| closed-eyes | 3 | Ana and Rosa with their eyes closed (shot 10). Used by the edge run. |
| decoy | 5 | Looks like a missing shot, but is not: Daniel with friends his age (shot 5), adults at the dessert table (shot 14), plates with no menu card (shot 16). |
| filler | 5 | Candid frames that match no shot |

Expected results are the same as for the staged shoot: `../expected/expected-full.csv` (16 covered, 4 missing) and `../expected/expected-edge.csv`.

## Edge run

Copy `photos/` to a second folder and remove the 3 eyes-open frames of shot 10: `IMG_2027.jpg`, `IMG_2030.jpg`, and `IMG_2032.jpg`. Only the closed-eyes frames remain, so shot 10 must be weak.

## How it was made

- Model: GPT Image 2.6 on Higgsfield, with the 4 portraits as reusable character references.
- Portraits at medium quality, scenes at low quality, 1024 x 683 pixels.
- Cost: about 15.5 credits for 4 portraits and 53 scenes.
- EXIF capture times were set in the time windows of the shot list sections.
