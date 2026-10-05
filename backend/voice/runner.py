
"""
Optional Raspberry Pi voice runner.
The browser bridge is the recommended kiosk mode because it can synchronize
the invisible microphone/speaker with the HMS page. This runner is useful for
bench testing a USB microphone and speaker without the browser.
"""
import argparse, base64, os, subprocess, tempfile, time, requests

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--server",default="http://127.0.0.1:5000")
    ap.add_argument("--seconds",type=int,default=5)
    args=ap.parse_args()
    session=requests.post(args.server+"/api/voice/session",json={}).json()
    sid=session["session_id"]
    print("Voice session:",sid)
    print(session.get("speech",""))
    while True:
        wav="/tmp/marykutty_voice.wav"
        print("Speak...")
        subprocess.run(["arecord","-q","-f","S16_LE","-r","16000","-c","1","-d",str(args.seconds),wav],check=False)
        with open(wav,"rb") as f:
            r=requests.post(args.server+"/api/voice/audio",data={"session_id":sid},
                            files={"audio":("voice.wav",f,"audio/wav")},timeout=40)
        data=r.json()
        print("You:",data.get("transcript",""))
        print("Robot:",data.get("speech",data.get("message","")))
        b64=data.get("audio_base64")
        if b64:
            out="/tmp/marykutty_tts.wav"
            with open(out,"wb") as f:f.write(base64.b64decode(b64))
            subprocess.run(["aplay","-q",out],check=False)
        if data.get("state")=="END": break
        time.sleep(.2)

if __name__=="__main__":
    main()
