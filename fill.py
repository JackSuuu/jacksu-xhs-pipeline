import json,sys,time,websocket,pathlib
root=pathlib.Path(__file__).parent
d=json.load(open(root/"slides.json")); tid=sys.argv[1]
ws=websocket.create_connection(f"ws://localhost:9222/devtools/page/{tid}",timeout=30,suppress_origin=True)
n=0
def c(m,**p):
    global n;n+=1;ws.send(json.dumps({"id":n,"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n:
            if "error" in r: raise Exception(r["error"])
            return r["result"]
def ev(e): return c("Runtime.evaluate",expression=e,returnByValue=True)["result"].get("value")
ev("(()=>{for(const b of document.querySelectorAll('button'))if(b.innerText.trim()=='我知道了')b.click()})()")
ev("document.querySelector('input.d-text[placeholder*=标题]').focus()")
c("Input.insertText",text=d["title"]); time.sleep(.5)
ev("document.querySelector('.tiptap.ProseMirror').focus()")
body=d["caption"]
for i,line in enumerate(body.split("\n")):
    if i: c("Input.dispatchKeyEvent",type="keyDown",key="Enter",code="Enter",windowsVirtualKeyCode=13,text="\r");c("Input.dispatchKeyEvent",type="keyUp",key="Enter",code="Enter",windowsVirtualKeyCode=13)
    if line: c("Input.insertText",text=line)
# tags: type each then pick topic with Enter-less approach: insert text + space
c("Input.dispatchKeyEvent",type="keyDown",key="Enter",code="Enter",windowsVirtualKeyCode=13,text="\r");c("Input.dispatchKeyEvent",type="keyUp",key="Enter",code="Enter",windowsVirtualKeyCode=13)
for t in d["tags"]:
    c("Input.insertText",text=t); time.sleep(1.2)
    c("Input.insertText",text=" "); time.sleep(.3)
time.sleep(1)
print(ev("JSON.stringify({t:document.querySelector('input.d-text[placeholder*=标题]').value,b:document.querySelector('.tiptap').innerText,len:document.querySelector('.tiptap').innerText.length})"))
