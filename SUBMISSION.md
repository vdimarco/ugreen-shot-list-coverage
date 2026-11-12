# Devpost Submission: Shot List Coverage

Copy each field into the Devpost project form. Round 1 closes Sunday, Nov 15, 2026, at 11:45 PM PT.

## Files to upload

| Devpost item | File | Size | Limit |
|---|---|---|---|
| Project Proposal (PDF) | `proposal/shot-list-coverage-proposal.pdf` | 37 KB, 2 pages, about 480 words | 1 MB, 500 words |
| Pre-test Skill Package (ZIP) | `dist/shot-list-coverage.zip` | 7 KB, 4 files | 10 MB, 100 files, 1 MB per file |
| Cover image (gallery) | `media/cover.png` | 3:2 | none |
| Video demo link (optional) | `demo/video/shot-list-coverage-concept.mp4` | 97 s, 19 MB, 1080p | YouTube, Vimeo, or Youku link only |

## Project name

Shot List Coverage

## Elevator pitch

Did you get every shot? Shot List Coverage checks a client's shot list against the photos of a shoot on your NAS, and shows which shots are covered, weak, or missing, with the best frame for each.

## Track

Unleash Your Creativity

## About the project

### Inspiration

Wedding and event clients send shot lists of 30 to 60 shots. After a shoot of 1,000 frames, the photographer checks the list from memory or by scrolling. A missed "bride with grandmother" cannot be taken again after the event. We wanted the photographer to know what is missing before they leave the venue.

### What it does

The photographer copies the card to the NAS and asks: "Did I get the shot list?"

1. The Skill reads the shot list (PDF, Word, text, or pasted) and asks the user to confirm it.
2. It searches the shoot folder for each line by scene, named people, objects, visible text, and time.
3. The NAS vision model checks the best candidates: does the photo show the shot, is it in focus, are the eyes open, is anything cut off?
4. It reports each shot as covered, weak, or missing, with the best frame, two alternates, and a reason. Missing must-have shots come first.
5. After the user confirms, it makes an album of the best frames and saves the report in the shoot folder.

The Skill never moves, edits, deletes, or shares a photo.

### How we built it

The Skill is one SKILL.md with three reference files, built with the UGREEN Skill Developer Package (uliya-skill-kit 0.7.3). It delegates self-contained tasks to four registered NAS experts:

- `photo-agent`: checks the photo index, searches by scene, person, object, OCR text, and time, runs the vision checks, and makes the album.
- `document-agent`: reads the shot list into structured items.
- `file-agent`: counts the images in the shoot folder.
- `knowledge-agent`: saves the coverage report.

### Challenges we ran into

- Vision checks take time. One run checks at most 150 photos, and must-have shots go first.
- A shot must not be "covered" by a similar photo. Only a "yes" from the vision model, in focus, with eyes open and nothing cut off, gives covered. A partial match gives weak.
- A new shoot can be only partly indexed. The Skill compares the file count with the photo index, and warns the user.

### Accomplishments that we're proud of

- The package passes the kit's static check with 0 errors and 0 warnings.
- The demo kit has a 20-line shot list, printable props, a capture plan with planned misses and decoys, a smoke test, and a scoring script.

### What we learned

Photographers do not need a general quality score as much as an answer to the client's own list. The photos are already on the NAS, so the check can run there, with no upload of client photos.

### What's next

- Test on a real UGREEN AI NAS with the staged shoot and the scoring script.
- Optional color tags on the best frames for the editing workflow.
- Lists for real estate and product shoots.

## Built with

ugos, ugreen-ai-nas, uliya-skill-kit, markdown, claude

## Try it out

- https://github.com/vdimarco/ugreen-shot-list-coverage

## Video demo link

Round 1 does not require a video. This concept preview is optional. It explains the idea with AI-generated photos and the expected results. It is not a recording on a UGREEN NAS, and every frame says so. Round 2 needs a new video recorded on your assigned NAS (see `demo/video/README.md`).

Devpost does not accept a video file. Upload the video first, then paste the link:

1. Upload `demo/video/shot-list-coverage-concept.mp4` to YouTube. Set it to Public or Unlisted.
2. Use the title and description below.
3. Paste the YouTube link into the Devpost field "Video demo link".

**YouTube title**

Shot List Coverage: concept preview (UGREEN Hackathon 2026 on AI NAS)

**YouTube description**

Shot List Coverage is a UGOS Skill for photographers. It checks a client's shot list against the photos of a shoot on a UGREEN AI NAS, and shows which shots are covered, weak, or missing, with the best frame for each.

This video is a concept preview. The photos are AI-generated and the people are fictional. The report on screen is the expected result for the demo shoot. It is not a recording of the Skill on a UGREEN NAS. The final demo will be recorded on a UGREEN AI NAS in Round 2.

Code and demo kit: https://github.com/vdimarco/ugreen-shot-list-coverage
Entry for the UGREEN Hackathon 2026 on AI NAS, track Unleash Your Creativity.

## Before you submit

- [ ] Check the entrant name in the proposal PDF ("Vaughn DiMarco"). Add teammates and their consent if you have any.
- [ ] Confirm on the Devpost Rules tab that a team can enter more than one Skill.
- [ ] Upload the PDF and the ZIP above.
- [ ] Optional: upload the concept video to YouTube and paste the link into "Video demo link".
