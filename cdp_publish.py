import json,sys,time,urllib.request,websocket,pathlib
root=pathlib.Path(__file__).parent
data=json.load(open(root/"slides.json"))
imgs=[str(p) for p in sorted((root/"output").glob("slide_*.png"),key=lambda p:int(p.stem.split("_")[1]))]
tid=sys.argv[1]; submit=len(sys.argv)>2 and sys.argv[2]=="publish"
ver=json.load(urllib.request.urlopen("http://localhost:9222/json/version"))
ws=websocket.create_connection(f"ws://localhost:9222/devtools/page/{tid}",timeout=30,suppress_origin=True)
n=0
def c(m,**p):
    global n;n+=1;ws.send(json.dumps({"id":n,"method":m,"params":p}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n:
            if "error" in r: raise Exception(r["error"])
            return r["result"]
def ev(e): return c("Runtime.evaluate",expression=e,returnByValue=True,awaitPromise=True)["result"].get("value")
c("DOM.enable");c("Runtime.enable")
root_=c("DOM.getDocument",depth=-1)["root"]["nodeId"]
nid=c("DOM.querySelector",nodeId=root_,selector="input[type=file]")["nodeId"]
c("DOM.setFileInputFiles",nodeId=nid,files=imgs)
print("uploaded",len(imgs))
time.sleep(8)
print(ev("document.body.innerText.slice(0,500)"))
