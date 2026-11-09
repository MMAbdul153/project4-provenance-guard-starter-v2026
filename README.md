# Provenance Guard

## What This Does

Provenance Guard is an automated content provenance and transparent attribution backend for creative publishing platforms. It provides two core endpoints:
- `POST /submit`: Accepts `{text, creator_id}`, validates payload boundaries, evaluates token predictability via a local pre-trained language model (`detector.py`) and text structural cadence via stylometry (`stylometry.py`), combines them via weighted aggregation with disagreement damping, records the complete trace in `logs/audit.jsonl`, and returns a calibrated confidence score with a transparent reader-facing label.
- `POST /appeal`: Accepts `{content_id, creator_id, reason}`, verifies existence in the audit trail, updates status to `under_review`, and records the creator's justification to prevent arbitrary automated penalties.

---

## Signals and Scoring

### Signal 1: Predictability (`detector.py::model_signal`)

- **What it measures**: The cross-entropy token perplexity of the text against `facebook/bart-large-mnli` / `gpt2`. Generates scores from 0.0 (unpredictable/human) to 1.0 (highly predictable/AI).
- **Blind spot**: Highly structured, formal, or technical human writing (e.g. legal briefs, academic literature reviews) appears synthetically predictable.

### Signal 2: Stylometry (`stylometry.py::style_signal`)

- **What it measures**: Structural text cadence combining coefficient of variation in sentence length (burstiness, weight 0.50), lexical diversity via Type-Token Ratio (weight 0.35), and punctuation frequency (weight 0.15).
- **Blind spot**: Repetitive or minimalist human poetry and deliberately prompt-engineered AI text requesting varied sentence structures.

### Combining Rule (`scoring.py::combine_signals`)

```python
# Weighted combination with disagreement dampening
raw_score = (0.65 * signal_1) + (0.35 * signal_2)
if abs(signal_1 - signal_2) > 0.40:
    # Pull toward 0.50 uncertainty zone when signals conflict
```

---

## Label Variants

| Label | Confidence Range | Intended Reader Meaning |
|---|---|---|
| `high-confidence human` | `0.00 <= score <= 0.38` | Strong stylistic and statistical markers of human cadence and vocabulary variation. |
| `unsure` | `0.38 < score < 0.68` | Conflicting signals or intermediate structural scores; no definitive automated attribution possible. |
| `high-confidence AI` | `0.68 <= score <= 1.00` | High token predictability combined with low sentence length variance typical of language model output. |

---

## Sample Run

### Request

```bash
curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Furthermore, it is imperative to recognize that machine learning models rely heavily on large-scale parallelized computation.", "creator_id": "creator_test_01"}'
```

### Response

```json
{
  "content_id": "7f9a1b2c-8d3e-4f5a-9b1c-2d3e4f5a6b7c",
  "guess": "ai",
  "confidence": 0.7842,
  "label": "high-confidence AI"
}
```

### Audit Log Record (`logs/audit.jsonl`)

```json
{"timestamp": "2026-11-08T18:30:15.123456+00:00", "event_type": "submission", "content_id": "7f9a1b2c-8d3e-4f5a-9b1c-2d3e4f5a6b7c", "creator_id": "creator_test_01", "text_preview": "Furthermore, it is imperative to recognize that machine learning models...", "signal_1": 0.8123, "signal_2": 0.7321, "confidence": 0.7842, "label": "high-confidence AI", "status": "logged"}
```

---

## How I Used AI

- **Moment 1 (Designing Stylometric Burstiness)**: I prompted Claude to explore why standard sentence length variance collapsed on short paragraphs. Claude demonstrated that raw standard deviation scales with average sentence length, recommending the coefficient of variation ($CV = \sigma / \mu$). I implemented this in `stylometry.py::calculate_burstiness` to prevent short sentences from artificially deflating human scores.
- **Moment 2 (Signal Disagreement Guardrail)**: When testing edge cases, I observed that when Signal 1 scored 0.95 and Signal 2 scored 0.15, the raw average (0.67) sat right at the edge of the AI threshold. I used Claude to formulate a threshold dampening rule in `scoring.py` that checks `abs(signal_1 - signal_2) > 0.40` and pulls the composite score toward the `unsure` band.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
