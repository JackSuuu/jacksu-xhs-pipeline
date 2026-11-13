#!/usr/bin/env python3
"""Render posts/<name>.json -> output/<name>/slide_N.png (1080x1440). Usage: render_cards.py posts/002-mini-infer.json"""
import json,sys,pathlib
from playwright.sync_api import sync_playwright
root=pathlib.Path(__file__).parent
src=pathlib.Path(sys.argv[1]); data=json.load(open(src))
theme=sys.argv[2] if len(sys.argv)>2 else data.get("theme","A")
only=[int(x) for x in sys.argv[3].split(",")] if len(sys.argv)>3 else None
out=root/"output"/(src.stem if len(sys.argv)<4 else src.stem+"_theme"+theme); out.mkdir(parents=True,exist_ok=True)
for f in out.glob("slide_*.png"): f.unlink()
n=len(data["slides"])
with sync_playwright() as p:
    b=p.chromium.launch()
    for i,s in enumerate(data["slides"],1):
        if only and i not in only: continue
        pg=b.new_page(viewport={"width":1080,"height":1440})
        pg.add_init_script(f"window.THEME='{theme}';window.SLIDE={json.dumps(s,ensure_ascii=False)};window.PG='{i}/{n}';")
        pg.goto((root/"template.html").as_uri()); pg.wait_for_timeout(150)
        pg.screenshot(path=str(out/f"slide_{i}.png")); pg.close()
    b.close()
print("rendered",n,"->",out)
