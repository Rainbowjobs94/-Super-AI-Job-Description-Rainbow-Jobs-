"""Operator-only API. No apply, rollback, signing or shell-execution endpoints."""
import io
import os
import zipfile
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request, send_file
from .core import Store, plan_merge

api = Blueprint("hab", __name__, url_prefix="/api/hab")


def store():
    return Store(current_app.config["HAB_STORE"])


@api.errorhandler(ValueError)
@api.errorhandler(zipfile.BadZipFile)
def invalid_request(error):
    return jsonify(status="error", message=str(error)), 400


@api.get("/catalog")
def catalog():
    return jsonify(status="success", sources=store().sources())


@api.post("/intake")
def intake():
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return jsonify(status="error", message="A file is required"), 400
    # Explicit upload endpoint, not arbitrary server-side file paths.
    content = uploaded.read(current_app.config["MAX_CONTENT_LENGTH"] + 1)
    source = store().ingest(uploaded.filename, content)
    return jsonify(status="success", source=source)


@api.post("/export")
def export():
    data = request.get_json()
    payload = store().export(data.get("source_ids"))
    return send_file(io.BytesIO(payload), as_attachment=True,
                     download_name="ia-guardian-hab-source-bundle.zip",
                     mimetype="application/zip")


@api.post("/parse")
def parse():
    data = request.get_json()
    result = store().plan_request(data.get("message"), data.get("request_id"),
                                  current_app.config["HAB_PLANNING_LIMIT"])
    return jsonify(status="success", result=result)


@api.route("/records/<kind>", methods=["GET", "POST"])
def records(kind):
    if request.method == "GET":
        return jsonify(status="success", records=store().records(kind))
    return jsonify(status="success", record=store().record(kind, request.get_json()))


@api.post("/merge-preview")
def merge_preview():
    data = request.get_json()
    # UI may preview only the explicit transfer staging directory.
    destination = Path(current_app.config["HAB_DESTINATION"])
    result = plan_merge(store(), data.get("source_id"), destination, data.get("mappings"))
    return jsonify(status="success", plan=result, apply_available="CLI only after approval")
