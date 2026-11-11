# Shot List Coverage: Test Plan

This plan is for the assigned test day on the UGREEN AI NAS (Nov 22 to 28). All names and events are fictional.

## Files

| Path | What it is |
|---|---|
| `shot-list/rivera-okoro-shot-list.pdf` | The 20-line client shot list. Also in `.docx` and `.md` (to paste). |
| `shot-list/props-to-print.pdf` | Props for the staged shoot: welcome sign, cake topper, place cards |
| `capture-plan.md` | How to shoot the about 300 frames, with planned misses and decoys |
| `smoke/` | A 6-line smoke shot list and 24 synthetic photos with EXIF capture times |
| `expected/expected-smoke.csv` | Expected results for the smoke test |
| `expected/expected-full.csv` | Expected results for the full shoot |
| `expected/expected-edge.csv` | Expected results for the edge run |
| `score_report.py` | Compares a coverage report with an expected file |
| `generate.py` | Makes the shot lists, props, smoke photos, and expected files again |
| `generated/` | A ready-made, AI-generated test shoot: 53 photos with EXIF times, a manifest, and 4 character portraits |

## Test 0: smoke test (first, about 15 minutes)

The smoke test checks the workflow with synthetic photos before the real shoot uses the vision model time. It tests text in photos, focus, cut-off frames, and missing shots. It does not test faces.

1. Upload `smoke/photos/` to the NAS as `Photos/Smoke test`. Upload `smoke/smoke-shot-list.pdf` to `Documents`.
2. Wait until the photo app shows the 24 photos.
3. Say: "Check the shot list Documents/smoke-shot-list.pdf against the photos in Photos/Smoke test. The event name is Smoke test."
4. Confirm the parsed list. Answer "report only" to the album question.
5. Copy the report file to your computer and run:

```bash
python3 demo/score_report.py "Smoke test shot list coverage.md" demo/expected/expected-smoke.csv
```

Expected: 6 of 6 pass. Shot 3 must be weak (out of focus), and missing is also accepted. Shot 6 can be weak, because the string lights photos are drawings.

`smoke-manifest.csv` lists the content and capture time of each synthetic photo, so you can check the best frames.

## Test 1 (core): full shoot coverage

Use the staged shoot from `capture-plan.md`, or the generated shoot in `generated/photos/` (53 photos). The expected results are the same for both. For the generated shoot, name the faces with the portraits in `generated/characters/`, and expect step 1 to count 53 images.

1. Upload the full shoot to `Photos/2026-11 Rivera-Okoro party` and the shot list PDF to `Documents`.
2. In the photo app, name the faces: Ana Rivera, Daniel Okoro, Rosa Rivera, and Maya Chen.
3. Wait until the photo app has indexed all photos.
4. Say: "Check my shot list Documents/rivera-okoro-shot-list.pdf against Photos/2026-11 Rivera-Okoro party. The event is the Rivera-Okoro engagement party. Ana is Ana Rivera, Daniel is Daniel Okoro, Grandma Rosa is Rosa Rivera, and Maya is Maya Chen." Give the real time windows from the capture plan.
5. Confirm the 20 parsed shots. Check that the must-have shots are 1, 4, 5, 7, 8, 10, 11, and 18.

Expected:
- [ ] Step 1 counts about 300 images and reports the photo index status.
- [ ] 16 shots covered, 4 missing (5, 14, 16, 20). No planned miss is marked covered, even with the decoys.
- [ ] Shot 5 is at the top, under "Missing must-have shots".
- [ ] Each covered shot has a best frame and up to 2 alternates, and no frame is the best frame of two shots.
- [ ] The run checks at most 150 photos.

Score it:

```bash
python3 demo/score_report.py "Rivera-Okoro engagement party shot list coverage.md" demo/expected/expected-full.csv
```

Pass: at least 18 of 20 shots, and 0 planned misses marked covered.

## Test 2 (core): album and report

At the end of Test 1, answer "album and report".

Expected:
- [ ] The NAS asks for approval, and the Skill reports `waiting_approval` until you approve.
- [ ] A new album "Rivera-Okoro engagement party shot list" has 16 photos, in shot list order.
- [ ] The report file is in the shoot folder.
- [ ] No photo was moved, renamed, or changed. Check the file count and the modified times.

## Test 3 (edge case): closed eyes

1. Make a copy of the shoot folder named `Photos/2026-11 Rivera-Okoro party edge`.
2. In the copy only, remove the eyes-open frames of shot 10. For the staged shoot, use the file name from the capture plan. For the generated shoot, remove `IMG_2027.jpg`, `IMG_2030.jpg`, and `IMG_2032.jpg`.
3. Run the same request on the copy, with the event name "Edge run".

Expected:
- [ ] Shot 10 is weak, with a note about closed eyes.
- [ ] Shot 10 is under "Missing must-have shots" with the reason.
- [ ] All other shots have the same status as in Test 1.

```bash
python3 demo/score_report.py "Edge run shot list coverage.md" demo/expected/expected-edge.csv
```

## Record results

For each test, record: pass or fail, the score output, the run time, each delegation state that occurred (`completed`, `failed`, `cancelled`, `waiting_user`, `waiting_approval`), and screenshots. Put the results in `demo/results/`.

## Demo video plan (3 minutes, English)

| Time | Shot |
|---|---|
| 0:00 to 0:15 | The problem: a card with 300 frames and a 20-line client list. "Did I get every shot?" |
| 0:15 to 0:45 | The request, and the parsed shot list to confirm |
| 0:45 to 1:45 | The report: missing must-have at the top, the table with best frames, a weak shot with its reason |
| 1:45 to 2:20 | The album of best frames in the photo app, and the saved report |
| 2:20 to 2:45 | The edge run: closed eyes give weak, not covered |
| 2:45 to 3:00 | Close: private, on the NAS, read-only, checks the client's own words |
