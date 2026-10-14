"""Print the guide to PDF. Run: python guide/make_pdf.py   (needs: pip install playwright, and Chrome)"""

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    page = browser.new_page()
    page.goto((HERE / "Atlas-Attendee-Guide.html").as_uri(), wait_until="networkidle")
    page.pdf(
        path=str(HERE / "Atlas-Attendee-Guide.pdf"), format="A4", print_background=True,
        margin={"top": "16mm", "bottom": "16mm", "left": "15mm", "right": "15mm"},
    )
    browser.close()
print("saved", HERE / "Atlas-Attendee-Guide.pdf")
