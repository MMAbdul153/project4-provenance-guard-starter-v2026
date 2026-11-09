# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
| --- | --- |
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---

## 1. False Positive Rate on Pure Human Literature

The system falsely flags no more than 1 in 20 purely human-written essays or creative submissions (False Positive Rate <= 0.05 / 5%) as `high-confidence AI`.

**Why this target:**
Falsely accusing a genuine human creator of AI generation destroys platform trust and community engagement. Because the human cost of a false accusation is vastly higher than missing an AI-generated post, the threshold for accusing human writers must remain strictly conservative.

---

## 2. Score Separation on Unambiguous Test Fixtures

On a calibration benchmark of 10 clear human articles and 10 raw AI generations, the mean combined confidence score for AI text is at least 0.35 points higher than the mean score for human text.

**Why this target:**
If the two distribution means cluster tightly together (e.g. difference < 0.20), the classifier is behaving like an uninformative coin flip. Requiring a 0.35 score spread ensures the combined scoring function produces measurable discriminant utility between clear cases.

---

## 3. Label Reachability Across the Continuum

In a batch of 50 diverse submissions across formal, casual, mixed, and heavily edited text, every one of the three transparency labels (`high-confidence AI`, `high-confidence human`, and `unsure`) is assigned to at least 15% of the total submissions.

**Why this target:**
A trivial system that maps 95% of submissions to `unsure` avoids false positives but provides zero value to moderators. Forcing balanced reachability verifies that all three buckets are actively utilized and reachable across realistic score boundaries.

---

## 4. Audit Log Integrity and Appeal State Transition

100% of valid requests submitted to `POST /submit` create an auditable entry in `logs/audit.jsonl`, and 100% of valid requests to `POST /appeal` update the content status to `under_review` in the audit log within 500ms.

**Why this target:**
Accountability requires that every moderation action has a traceable record. If appeals fail to transition or records drop out of the log, creators are left without legal or procedural recourse against automated decisions.

---

## 5. Input Validation on Edge-Case Payloads

When `POST /submit` receives empty text, whitespace-only text, missing attributes, or inputs exceeding 20,000 characters, it returns an HTTP 400 Bad Request 100% of the time without crashing the server or invoking model inference.

**Why this target:**
Running heavy transformer models or regex parsers on malformed or adversarial 100k-character payloads causes denial-of-service, memory leaks, and worker process lockup. Early rejection at the controller boundary protects backend availability
---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
