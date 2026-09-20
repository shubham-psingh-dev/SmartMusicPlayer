from pathlib import Path
import hashlib
from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QColor,QFont,QLinearGradient,QPainter,QPixmap
CACHE=Path.home()/".lyrx"/"local_covers"

def fallback_cover():
    CACHE.mkdir(parents=True,exist_ok=True); p=CACHE/"_lyrx_local_music.png"
    if p.exists(): return str(p)
    x=QPixmap(700,700); x.fill(Qt.transparent); q=QPainter(x); q.setRenderHint(QPainter.Antialiasing,True)
    g=QLinearGradient(0,0,700,700); g.setColorAt(0,QColor("#24153F")); g.setColorAt(.55,QColor("#6636D8")); g.setColorAt(1,QColor("#171126")); q.fillRect(x.rect(),g)
    q.setPen(QColor(255,255,255,30)); q.setBrush(QColor(255,255,255,15)); q.drawEllipse(QRectF(390,-70,390,390)); q.drawEllipse(QRectF(-100,450,350,350))
    f=QFont(); f.setPointSize(100); f.setBold(True); q.setFont(f); q.setPen(QColor("white")); q.drawText(QRectF(0,140,700,250),Qt.AlignCenter,"♫")
    f.setPointSize(36); q.setFont(f); q.drawText(QRectF(40,390,620,90),Qt.AlignCenter,"LYRx LOCAL")
    f.setPointSize(17); f.setBold(False); q.setFont(f); q.setPen(QColor("#D8C7FF")); q.drawText(QRectF(40,480,620,60),Qt.AlignCenter,"Your Music • Offline")
    q.end(); x.save(str(p),"PNG"); return str(p)

def _save(path,data,mime="image/jpeg"):
    if not data:return ""
    CACHE.mkdir(parents=True,exist_ok=True); ext=".png" if "png" in (mime or "").lower() or data.startswith(b"\\x89PNG") else ".jpg"
    p=CACHE/(hashlib.sha1(str(path.resolve()).encode()).hexdigest()+ext)
    try:p.write_bytes(data);return str(p)
    except:return ""

def read_local_media(file):
    p=Path(str(file)); r={"path":str(p.resolve()),"title":p.stem.replace("_"," ").strip() or "Local Track","artist":"Local Music","album":"","duration":0,"cover_path":fallback_cover()}
    try:
        from mutagen import File
        a=File(str(p),easy=False)
        if not a:return r
        if getattr(a,"info",None) and getattr(a.info,"length",0):r["duration"]=int(round(a.info.length))
        e=File(str(p),easy=True); t=getattr(e,"tags",None) if e else None
        if t:
            def one(k,d=""):
                v=t.get(k); return str(v[0]).strip() if v else d
            r["title"]=one("title",r["title"]);r["artist"]=one("artist",r["artist"]);r["album"]=one("album","")
        tags=getattr(a,"tags",None)
        if tags:
            for k in tags.keys():
                if str(k).startswith("APIC"):
                    f=tags.get(k); c=_save(p,getattr(f,"data",b""),getattr(f,"mime","image/jpeg"))
                    if c:r["cover_path"]=c;return r
            try:
                cov=tags.get("covr")
                if cov:
                    c=_save(p,bytes(cov[0])); 
                    if c:r["cover_path"]=c;return r
            except:pass
        pics=getattr(a,"pictures",None) or []
        if pics:
            c=_save(p,pics[0].data,getattr(pics[0],"mime","image/jpeg"))
            if c:r["cover_path"]=c
    except Exception as e: print("LYRx local metadata warning:",e)
    return r

def format_duration(s):
    try:s=max(0,int(s))
    except:s=0
    m,s=divmod(s,60);h,m=divmod(m,60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
