#!/usr/bin/env python3
"""Fill (and optionally publish) an image note via the logged-in Arc (CDP :9222).
Usage: publish.py posts/002-mini-infer.json [--publish]
Without --publish it stops after filling and saves output/<name>/preview_form.png"""
import json,sys,time,base64,urllib.request,urllib.parse,websocket,pathlib
root=pathlib.Path(__file__).parent
src=pathlib.Path(sys.argv[1]); go="--publish" in sys.argv
d=json.load(open(src)); out=root/"output"/src.stem
imgs=sorted(map(str,out.glob("slide_*.png")),key=lambda p:int(p.rsplit("_",1)[1][:-4]))
req=urllib.request.Request("http://localhost:9222/json/new?"+urllib.parse.quote("https://creator.xiaohongshu.com/publish/publish?source=official&from=menu&target=image",safe=""),method="PUT")
tid=json.load(urllib.request.urlopen(req))["id"]
ws=websocket.create_connection(f"ws://localhost:9222/devtools/page/{tid}",timeout=60,suppress_origin=True)
n=0
def c(m,**p):
    global n;n+=1;ws.send(json.dumps({"id":n,"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n:
            if "error" in r: raise Exception(r["error"])
            return r["result"]
def ev(e): return c("Runtime.evaluate",expression=e,returnByValue=True)["result"].get("value")
def key(k,code,vk):
    c("Input.dispatchKeyEvent",type="keyDown",key=k,code=code,windowsVirtualKeyCode=vk,text="\r");c("Input.dispatchKeyEvent",type="keyUp",key=k,code=code,windowsVirtualKeyCode=vk)
time.sleep(3)
ev("[...document.querySelectorAll('.creator-tab,[class*=tab]')].filter(e=>e.innerText&&e.innerText.trim()=='\u4e0a\u4f20\u56fe\u6587').forEach(e=>e.click())");time.sleep(2)
for _ in range(20):
    if ev("!!document.querySelector('input[type=file][accept*=jpg]')"): break
    time.sleep(1)
else: sys.exit("upload input not found (not logged in?)")
c("DOM.enable"); r=c("DOM.getDocument",depth=-1)["root"]["nodeId"]
c("DOM.setFileInputFiles",nodeId=c("DOM.querySelector",nodeId=r,selector="input[type=file][accept*=jpg]")["nodeId"],files=imgs)
for _ in range(30):
    if ev("!!document.querySelector('input.d-text[placeholder*=\u6807\u9898]')"): break
    time.sleep(1)
time.sleep(6)
ev("[...document.querySelectorAll('button')].forEach(b=>{if(b.innerText.trim()=='\u6211\u77e5\u9053\u4e86')b.click()})")
ev("document.querySelector('input.d-text[placeholder*=\u6807\u9898]').focus()"); c("Input.insertText",text=d["title"]); time.sleep(.5)
ev("document.querySelector('.tiptap.ProseMirror').focus()")
for i,line in enumerate(d["caption"].split("\n")):
    if i: key("Enter","Enter",13)
    if line: c("Input.insertText",text=line)
key("Enter","Enter",13)
for t in d["tags"]:
    c("Input.insertText",text=t+" "); time.sleep(.4)
time.sleep(1)
shot=out/"preview_form.png"
shot.write_bytes(base64.b64decode(c("Page.captureScreenshot",format="png",captureBeyondViewport=True)["data"]))
print("filled; form screenshot:",shot, "| uploaded",len(imgs),"imgs | title:",ev("document.querySelector('input.d-text[placeholder*=\u6807\u9898]').value"))
if go:
    w,h=ev("[innerWidth,innerHeight]")
    for t in("mousePressed","mouseReleased"): c("Input.dispatchMouseEvent",type=t,x=w//2,y=h-46,button="left",clickCount=1)
    time.sleep(5); print("after click:",ev("location.href"))
