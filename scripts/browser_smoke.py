"""Optional local UI check: install playwright and its Chromium before running.

python scripts/browser_smoke.py
Uses a disposable store and synthetic token; never connects to an AI provider.
"""
import json
import os
import shutil
import sys
import tempfile
import threading
from pathlib import Path
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.hub import app


def main():
    with tempfile.TemporaryDirectory() as directory:
        app.config.update(HAB_TOKEN="browser-test-" + "x" * 40,
                          HAB_STORE=directory, HAB_PLANNING_LIMIT=100)
        server = make_server("127.0.0.1", 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        errors = []
        output = Path("exports")
        output.mkdir(exist_ok=True)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True,
                                             executable_path=os.environ.get("HAB_TEST_BROWSER"),
                                             env={**os.environ, "LD_LIBRARY_PATH":
                                                  os.environ.get("HAB_TEST_LIBRARY_PATH",
                                                                 os.environ.get("LD_LIBRARY_PATH", ""))},
                                             args=["--no-sandbox", "--disable-dev-shm-usage",
                                                   "--disable-gpu", "--no-proxy-server"])
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.set_default_timeout(10000)
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.goto(f"http://127.0.0.1:{server.server_port}", wait_until="domcontentloaded")
                page.locator("#token").fill(app.config["HAB_TOKEN"])
                page.locator("#unlock").click()
                page.wait_for_function("document.querySelector('#notice').textContent.includes('Operator connected')")
                assert page.locator("#token").input_value() == ""
                page.locator("#upload").set_input_files(
                    {"name": "reviewed.txt", "mimeType": "text/plain", "buffer": b"reviewed-source"})
                page.wait_for_function("document.querySelector('#source-count').textContent === '1'")
                page.locator("#request").fill("archiveallfilesmergeskillsreviewcontracts")
                page.locator("#parse").click()
                page.wait_for_function("document.querySelector('#plan-output').textContent.includes('request_id')")
                result = json.loads(page.locator("#plan-output").inner_text())
                assert result["requires_clarification"]
                assert result["external_model_calls"] == 0
                page.locator("#save-record").click()
                page.wait_for_function("document.querySelector('#record-output').textContent.includes('review-source')")
                page.locator(".source input").check()
                with page.expect_download() as download:
                    page.locator("#export").click()
                assert download.value.suggested_filename.endswith(".zip")
                page.screenshot(path=str(output / "hab-desktop.png"))
                page.set_viewport_size({"width": 390, "height": 844})
                page.screenshot(path=str(output / "hab-mobile.png"), full_page=True)
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.goto(f"http://127.0.0.1:{server.server_port}/legacy", wait_until="domcontentloaded")
                assert "Legacy workspace" in page.title()
                page.get_by_role("button", name="Unlock legacy APIs").wait_for()
                assert errors == [], errors
                browser.close()
            print(json.dumps({"browser": "Chromium", "desktop": "passed", "mobile": "passed",
                              "flows": ["unlock", "intake", "run-on parse", "record", "export", "legacy"],
                              "javascript_errors": errors}))
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
