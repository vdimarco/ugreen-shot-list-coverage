# Demo Video

## Concept preview (this folder)

`shot-list-coverage-concept.mp4`: 1920 x 1080, 30 fps, 97 seconds, English narration.

**This is a concept preview. It is not a recording of the Skill on a UGREEN AI NAS.** Each frame says so in a banner. It shows:

- the AI-generated demo shoot from `../generated/`,
- the client shot list from `../shot-list/`,
- the **expected** report from `../expected/expected-full.csv`, labeled "Example of the expected report",
- an illustration of the conversation, labeled "expected flow".

Use it to explain the idea, for example on the Devpost project page or in a pitch. Do not present it as NAS output.

`shot-list-coverage-concept-storyboard.jpg` shows one frame from each of the 9 scenes.

### Scenes and narration

| # | Scene | Narration |
|---|---|---|
| 1 | Title | Shot List Coverage. A UGOS Skill for photographers. This is a concept preview, made with AI-generated photos. |
| 2 | The problem | A client sends you a shot list. After the event, you have hundreds of frames. Did you get every shot? |
| 3 | The shot list | This engagement party has twenty shots on the list. Eight of them are must-have. |
| 4 | The request | You copy the card to your NAS. Then you ask the Skill to check the shot list against the shoot folder. |
| 5 | How it checks | The Skill searches for each line by scene, people, objects, text, and time. Then the NAS vision model checks the best frames for match, focus, open eyes, and framing. |
| 6 | The report | You get a report. Missing must-have shots come first. Each shot is covered, weak, or missing, with the best frame and two alternates. |
| 7 | Closed eyes | If every frame of a shot has closed eyes, the shot is weak, not covered. You know before you leave the venue. |
| 8 | Album | After you approve, the Skill makes an album of the best frames and saves the report. It never changes a photo. |
| 9 | Close | Shot List Coverage. Private, on your NAS, and based on your client's own words. |

The narration is in `narration/` (Higgsfield Seed Audio, preset voice "Holden", about 6.3 credits).

### Rebuild

```bash
python3 demo/video/build_concept_video.py demo/video/narration demo/video/shot-list-coverage-concept.mp4
```

Needs Python with Pillow, `ffmpeg`, and `pdftoppm`.

## Final Round 2 video (to record on the test day)

The rules require a public YouTube video of no more than 3 minutes, with English narration or English subtitles, that shows the Skill running on **your assigned UGREEN AI NAS** during your assigned testing day.

Plan for the recording:

1. Start a screen recording before the first request. Record the whole run of Test 1 and Test 3 in `../test-plan.md`.
2. Keep the NAS address bar or the device name visible in at least one shot, so the judges can see that it is the NAS.
3. Record the album in the photo app and the saved report file.
4. After the test day, cut the recording to the same 9 scenes. Replace scenes 4 to 8 of the concept video with the real screen recording. Keep scenes 1 to 3 and 9 if you like.
5. Change the banner text and the title pill. Remove "Concept preview" and "Expected results shown", because the new footage is real.
6. Remove "AI-generated photos" from the banner only if you use your own shoot. With the generated shoot, keep it.
