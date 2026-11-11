# Shot List Coverage: Project Proposal

**Skill name:** shot-list-coverage · **Track:** Unleash Your Creativity · **Entrant:** Vaughn DiMarco

<!-- answers-start -->

## 1. What does your Skill do?

It compares a client shot list with the photos of a shoot on the NAS, and reports each shot as covered, weak, or missing, with its best frame.

## 2. Who is your target user, and what is their problem?

Wedding, event, real estate, and product photographers. Clients send lists of 30 to 60 shots. After a shoot of 1,000 frames, the photographer checks coverage from memory or by scrolling. A missed "bride with grandmother" cannot be taken again after the event.

## 3. What is your solution?

The photographer copies the card to the NAS and asks: "Did I get the shot list?" The Skill searches the shoot for each line by scene, named people, objects, visible text, and time. The NAS vision model checks the best candidates for match, focus, open eyes, and framing.

## 4. What is the main user flow?

Give the shot list file and the shoot folder. Confirm the parsed list. The Skill searches and checks. It shows missing must-haves, counts, and a table with the best frame and two alternates for each shot. After approval, it makes an album of best frames and saves the report in the shoot folder.

## 5. How is your idea different from existing tools or common AI solutions?

Culling tools score general quality, but they do not know the client's list. Cloud AI needs gigabytes of client photos uploaded. This Skill checks against the client's own words, runs where the photos already are, and never changes a photo.

## 6. Which UGREEN AI NAS features does your Skill use, and at which step?

- photo-agent (ug-photo): index check (step 1); search by scene, person, object, OCR text, and time (step 3); vision model check (step 4); album (step 5).
- document-agent (ug-document): read the shot list into items (step 2).
- file-agent (ug-filesystem): count images (step 1).
- knowledge-agent (ug-knowledge): save the coverage report (step 5).

## 7. What is your technical approach?

Six steps, each a self-contained delegation to a registered expert. The user confirms the shot list before the search. Each shot gets up to 8 candidates and up to 6 vision checks with 4 fixed questions. A run checks at most 150 photos, must-haves first. Covered needs a match in focus, with eyes open and nothing cut off. Weak has a partial match or a quality problem. Photos stay read-only. Only NAS models are used. All five delegation states are handled.

## 8. What have you built so far? What is not built yet? What still needs testing on a NAS?

Built: SKILL.md, coverage rules, and report format. They pass the uliya-skill-kit static check with 0 errors. Not built: tags on best frames. NAS tests: index time for a new shoot, scene search quality, vision model accuracy and speed, and RAW previews.

## 9. How will you test your Skill if you become a Finalist?

Core 1: a 300-frame staged shoot and a 20-line shot list, with 16 shots in the photos. Expect 16 covered and 4 missing. Core 2: make the album and the report. Expect 16 best frames in shot list order and the report file in the folder. Edge: a shot where every frame has closed eyes. Expect weak, with the reason.

## 10. What are the known limits, risks, or outside dependencies of your Skill?

Accuracy depends on photo indexing, scene search, and the vision model. A new shoot can need time to index. Named roles need named faces in the photo app. Still images only. It depends only on UGOS experts.

<!-- answers-end -->

## Third-party components and licenses

None. The Skill contains only Markdown. It uses no third-party library, service, or model. It was built and checked with the UGREEN uliya-skill-kit 0.7.3 from the Hackathon Starter Kit, which is not part of the package. AI tool: Claude (Anthropic), used to research, draft, and review the files.
