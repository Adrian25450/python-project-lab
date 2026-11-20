"""Preview-first file organizer that copies, never deletes."""
import argparse
import csv
from datetime import datetime
from pathlib import Path
import shutil

CATEGORIES = {"Documentos": {".pdf",".doc",".docx",".xls",".xlsx",".ppt",".pptx",".txt",".csv"},
              "Imagenes": {".png",".jpg",".jpeg",".gif",".webp",".svg"},
              "Audio": {".mp3",".wav",".m4a",".flac"}, "Video": {".mp4",".mov",".mkv",".avi"},
              "Comprimidos": {".zip",".rar",".7z",".tar",".gz"}}

def plan(source: Path, destination: Path):
    source, destination = source.resolve(), destination.resolve()
    if not source.is_dir(): raise ValueError(f"No existe la carpeta origen: {source}")
    if destination == source or source in destination.parents: raise ValueError("La carpeta destino no puede estar dentro del origen")
    reserved = set(); actions=[]
    for file in sorted(source.rglob("*")):
        if not file.is_file() or destination in file.parents: continue
        category = next((name for name, exts in CATEGORIES.items() if file.suffix.lower() in exts), "Otros")
        month = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m")
        folder = destination / category / month; candidate = folder / file.name; n=1
        while candidate in reserved or candidate.exists():
            candidate = folder / f"{file.stem} ({n}){file.suffix}"; n+=1
        reserved.add(candidate); actions.append((file,candidate,category))
    return actions

def main():
    parser=argparse.ArgumentParser(description="FileFlow · vista previa segura de organización")
    parser.add_argument("source",type=Path); parser.add_argument("--output",type=Path,required=True); parser.add_argument("--apply",action="store_true"); parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    try:
        actions=plan(args.source,args.output)
        for source,dest,category in actions:
            state="COPIAR" if args.apply else "VISTA PREVIA"
            print(f"{state:<14} {category:<14} {source.name} -> {dest}")
        if args.apply:
            for source,dest,_ in actions: dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,dest)
            print(f"\n{len(actions)} archivos copiados. Los originales siguen intactos.")
        else: print(f"\n{len(actions)} archivos analizados; no se modificó nada. Añade --apply para copiar.")
        if args.report:
            args.report.parent.mkdir(parents=True,exist_ok=True)
            with args.report.open("w",newline="",encoding="utf-8-sig") as f:
                writer=csv.writer(f); writer.writerow(["origen","destino","categoria","bytes","accion"])
                writer.writerows([[str(src),str(dst),cat,src.stat().st_size,"copiar" if args.apply else "vista previa"] for src,dst,cat in actions])
    except (OSError,ValueError) as error: parser.error(str(error))

if __name__ == "__main__": main()

