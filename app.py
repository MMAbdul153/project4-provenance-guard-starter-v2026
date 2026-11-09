#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

Routes:
    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      ← YOU BUILD THIS (Milestone 3, 4, 5)
    POST /appeal      ← YOU BUILD THIS (Milestone 5)
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

import uuid
from flask import Flask, jsonify, request

import audit
import config
import detector
import stylometry, scoring

app = Flask(__name__)


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
class _LimiterOff:
    """Stands in for the real limiter while rate limiting is off."""
    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        audit.log_rejection(
            creator_id=payload.get("creator_id", "unknown"),
            reason="rate_limited",
            limit=str(exc.description),
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


# ── The worked example. Already works. Don't edit. ────────────────────────────
@app.post("/ping")
def ping():
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── YOU BUILD THIS ────────────────────────────────────────────────────────────
@app.post("/submit")
# @limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """
    Take a piece of text, decide about it, log the decision, answer.
    ← Milestone 3 (Single signal + route + audit log)
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "bad_request", "message": "Expected JSON object."}), 400

    text = payload.get("text")
    creator_id = payload.get("creator_id")

    # Validate inputs (handles empty, missing, or oversized text)
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "bad_request", "message": "Field 'text' must be a non-empty string."}), 400
    if not isinstance(creator_id, str) or not creator_id.strip():
        return jsonify({"error": "bad_request", "message": "Field 'creator_id' must be a non-empty string."}), 400
    if len(text) > 20000:
        return jsonify({"error": "bad_request", "message": "Field 'text' exceeds 20,000 character limit."}), 400

    content_id = str(uuid.uuid4())

    # Milestone 3: Real Signal 1 from detector.py
    model_score = round(float(detector.model_signal(text)), 4)
    style_score = round(float(stylometry.style_signal(text)), 4)

    # Placeholders for Milestone 4 (stylometry) and Milestone 5 (labeling)
    style_score = 0.50
    confidence = scoring.combine_signals(model_score, style_score)
    label = scoring.score_to_label(confidence)
    guess = "ai" if confidence >= 0.50 else "human"

    # Write to audit.py using its exact parameter signature
    audit.log_decision(
        content_id=content_id,
        creator_id=creator_id,
        guess=guess,
        model_score=model_score,
        style_score=style_score,
        combined_score=confidence,
        label=label,
        status="decided",
        text_length=len(text),
    )

    # Return JSON with all fields needed by both the client and the evaluator
    return jsonify({
        "content_id": content_id,
        "guess": guess,
        "confidence": confidence,
        "label": label,
        "model_score": model_score,
        "style_score": style_score,
    }), 200


@app.post("/appeal")
def appeal():
    """
    A writer says you got it wrong. ← TODO — Milestone 5
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "error": "not_implemented",
        "message": "POST /appeal isn't built yet — see the TODO in app.py.",
        "you_sent": payload,
    }), 501


# ── Already works ─────────────────────────────────────────────────────────────
@app.get("/log")
def get_log():
    """The audit log, most recent last."""
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:   {config.DETECTOR_MODEL}")
    print(f"  rate limiting:    {'ON' if config.RATE_LIMITING_ENABLED else 'off (unit 8)'}")
    print(f"  audit log:        {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()