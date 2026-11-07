---
name: shot-list-coverage
description: A shot list coverage check for photographers that compares a client shot list with the photos of a shoot on the NAS. It marks each shot as covered, weak, or missing, gives the best frames for each shot, and can make an album of the best frames and save a coverage report. Use when the user asks if a shoot covered the shot list, asks which shots are missing after a wedding, event, product, or real estate shoot, or wants the best frame for each item on a shot list.
---

# Goal

Tell the photographer, shot by shot, whether the photos in a shoot folder cover the client shot list. Use this while the photographer can still take the missing shots, or before the photographer delivers the photos.

For each line on the shot list, the Skill gives:

- **Status**: covered, weak, or missing. [Coverage rules](references/coverage-rules.md) defines each status.
- **Best frame**: the file path of the best photo for the shot.
- **Alternates**: up to 2 more good photos.
- **Notes**: why a shot is weak, for example "eyes closed" or "only one of the two people is in the frame".

Then, only after the user confirms, the Skill can make a photo album with the best frames and save a coverage report in the shoot folder.

The Skill only reads photos. It never moves, renames, edits, deletes, or shares photos.

Supported scope: still images (JPEG, HEIC, PNG, and RAW files that the photo app shows a preview for) in one shoot folder, and a shot list of up to 60 lines. Out of scope: video, culling of the whole shoot, photo editing, and delivery to clients.

# Required input

Collect only these items. If the request already gives an item, do not ask for it again.

1. **Shot list**: a file on the NAS (PDF, Word, text, or Markdown), or the list pasted in the conversation.
2. **Shoot folder**: the folder on the NAS with the photos of this shoot.
3. **Event name**: a short name for the album and the report, for example "Rivera wedding".
4. **Names of people** (optional): which named person in the photo app is each role on the shot list, for example "Bride: Ana Rivera". Ask only if the shot list names roles or people.
5. **Time windows** (optional): when each part of the event happened, for example "Ceremony 15:00 to 15:45". Ask only if the shot list has parts of the day.

Do not ask for client contact details or for any data that a child expert collects for itself.

Before you send a delegate command, replace each item in square brackets with the real value from this conversation or from a completed result of an earlier step. If you do not have the real value, stop that step and tell the user what is missing.

# Generation-time capability evidence

- `ug-filesystem` → `file-agent`
- `ug-document` → `document-agent`
- `ug-photo` → `photo-agent`
- `ug-knowledge` → `knowledge-agent`

| Expert | Work in this Skill | Effect |
|---|---|---|
| `file-agent` | Count the images in the shoot folder and read their capture times | read |
| `document-agent` | Read the shot list file and return each line as a structured item | read |
| `photo-agent` | Check the photo service, search the shoot folder by scene, person, object, text, and time, check candidates with the vision model, and make the album | read; state-change with approval |
| `knowledge-agent` | Save the coverage report | state-change with approval |

# Workflow

Read [Coverage rules](references/coverage-rules.md) before step 3. Read [Report format](references/report-format.md) before step 5.

## Step 1: Check the shoot folder and the photo service

`delegate --target file-agent --instruction 'In this folder and its subfolders only: [shoot folder]. Count the image files (jpg, jpeg, heic, png, and RAW formats such as cr3, nef, arw, raf, dng). Return the total count, the count for each file type, and the earliest and latest file modified time. Do not change any file.'`

`delegate --target photo-agent --instruction 'Check that the photo service is available and that it has indexed the photos in this folder: [shoot folder]. Return the service status, and the number of photos from this folder that the photo search can find now. Do not change anything.'`

- If the folder has no images, tell the user that the folder has no images. This is an empty result. Stop.
- If the photo search finds fewer than 90 percent of the images in the folder, tell the user that the photo app is still indexing. Give both numbers. Ask if the user wants to wait or continue with the indexed photos only.

## Step 2: Read the shot list

If the user pasted the shot list in the conversation, use it as it is and continue with step 3.

If the shot list is a file:

`delegate --target document-agent --instruction 'Read this shot list file: [shot list file path]. Return each shot as one item, in the order of the file. For each item, return the line number, the full text of the line, the section heading above it if there is one, the people or roles that the line names, the objects that the line names, any text that must be visible in the photo, and whether the line is marked as must-have, for example with an asterisk, the word must, or a must-have section. Do not add, merge, or reword items. If the file has no shot list, say that there are no results.'`

- If the result is an empty result, tell the user that the file has no shot list. Stop.
- If the list has more than 60 items, tell the user that this run checks the first 60 items and the next run continues.

Show the parsed list to the user in a short table with the item number, the shot, must-have, and the people. Ask the user to confirm the list or correct it. Continue only after the user confirms.

## Step 3: Find candidates for each shot

For each confirmed item, build one search from the real values in the item: the names of the people from Required input, the objects, the visible text, the section time window, and the shot text as a scene keyword. Send one delegation for each group of up to 10 items.

`delegate --target photo-agent --instruction 'Search only the photos in this folder and its subfolders: [shoot folder]. For each shot below, find up to 8 candidate photos that may show the shot. Use the scene keyword, and also use the named people, objects, visible text, and time window when the shot gives them. Shots: [items with number, scene keyword, people names, objects, visible text, and time window]. For each shot, return the shot number and the candidate file paths with their capture times, best match first. If a shot has no candidates, return an empty list for that shot. Do not change anything.'`

Keep the real candidate paths for each shot. A shot with an empty list goes to step 4 with no candidates.

## Step 4: Check the candidates with the vision model

For each shot that has candidates, check up to 6 candidates, best match first. The whole run checks at most 150 photos. If a run needs more, check the must-have shots first and list the other shots as not checked.

`delegate --target photo-agent --instruction 'Look at each of these photos: [candidate file paths for one shot]. For each photo, answer these questions about this shot: [full shot text, with the names of the people]. Question 1: does the photo show the shot? Answer yes, partly, or no, and give one short reason. Question 2: is the main subject in sharp focus? Answer yes or no. Question 3: are the eyes of the main people open? Answer yes, no, or no faces. Question 4: is a person or object that the shot needs cut off by the edge of the frame? Answer yes or no. Return the answers for each photo with its file path. Do not change anything.'`

Then give each shot its status, best frame, alternates, and notes with the rules in [Coverage rules](references/coverage-rules.md). Use only the real answers from this step.

## Step 5: Report and offer the album and the report file

Show the coverage report as [Report format](references/report-format.md) defines it: missing must-have shots first, then the summary counts, then the full table.

Then ask: "Make an album with the best frames and save this report in the shoot folder? You can answer: album and report, album only, report only, or no."

- If the user answers no, stop. Tell the user that nothing changed on the NAS.

**Album** (only if the user confirmed it):

`delegate --target photo-agent --instruction 'Create a new album named [event name] shot list. Add exactly these photos, in this order: [best frame paths in shot list order]. Do not add other photos. Do not move, change, or remove any photo. Return the album name, the album ID, and the number of photos added.'`

**Report file** (only if the user confirmed it):

`delegate --target knowledge-agent --instruction 'Save this text as a Markdown file in this folder: [shoot folder]. Use the file name hint [event name] shot list coverage. Text: [full coverage report text]. Do not change other files. Return the path of the saved file.'`

## Step 6: Final message

Report the summary counts, the missing must-have shots, the album name and the number of photos in it, and the path of the report file. Report only results that the experts returned as completed.

# Completion and failure

Handle each delegation state as follows:

- `completed`: use only the real result that the expert returned. Pass only that real result to the next step. If the result is an empty result, say so and stop the steps that need it.
- `failed`: tell the user which step failed and the reason that the expert gave. Stop the steps that need that result. In step 3 or step 4, if one group fails, continue with the other groups and mark the shots in the failed group as not checked.
- `cancelled`: stop. Tell the user what was done before the cancel. Make no album and save no file.
- `waiting_user`: give the question of the expert to the user in plain words. Wait for the answer. Then continue the same step.
- `waiting_approval`: tell the user that the NAS asks for approval, and say what will change: the new album, or the new report file. Wait. Do not report the change as done until the step result is `completed`.

Partial results: if the album has fewer photos than the best frames, list the photos that are not in the album. If the album step completes and the report step fails, give the report text in the conversation, so that the user does not lose it.

Never mark a shot as covered without a "yes" answer from step 4. Never invent a file path. Never report a NAS action as done from local drafts or static checks.

# Safety rules

- Read photos only. Do not move, rename, edit, delete, or share photos.
- Get the user's confirmation before the album step and before the report step.
- Search only inside the shoot folder that the user gave.
- Use the names of people only to find photos for the shot list. Do not add names to the photo app and do not change face groups.
- Send NAS work only as delegations to the four experts in this Skill. Never call cli.invoke from this Skill.
- Reply in the language of the user. Do not translate file paths, file names, expert names, or status values.

# References

- [Coverage rules](references/coverage-rules.md): how to read a shot list, the search cues, the statuses, how to pick the best frame, and the limits. Read before step 3.
- [Report format](references/report-format.md): the coverage report layout. Read before step 5.
- [Disclosures](references/disclosures.md): third-party components, work done for the Hackathon, and AI tools used.
