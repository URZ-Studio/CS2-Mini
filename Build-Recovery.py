"""Clean-room export for diagnosing editor load/save errors. Never patches an existing mod."""
from pathlib import Path
import base64
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime

HOME = Path(__file__).resolve().parent
BUILDER = HOME / "Build-MiniCraft.py"
spec = importlib.util.spec_from_file_location("mini_builder", BUILDER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def write_payload(root, payload):
    for rel, data in payload.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

def data_only(root):
    m.validate()
    m.apply_size_014()
    payload = {p: base64.b64decode(v, validate=True) for p,v in m.METADATA.items()}
    manifest = ET.fromstring(payload["ComponentList.SC2Components"])
    for node in list(manifest):
        if node.get("Type") == "trig":
            manifest.remove(node)
    payload["ComponentList.SC2Components"] = ET.tostring(manifest, encoding="utf-8", xml_declaration=True)
    for name, xml in m.CATALOGS.items():
        tree = ET.fromstring(xml)
        if name == "GameData":
            for game in tree.findall("CGame"):
                for entry in game.findall("TriggerLibs"):
                    game.remove(entry)
        payload["Base.SC2Data/GameData/"+name+".xml"] = ET.tostring(tree, encoding="utf-8", xml_declaration=True)
    key = "koKR.SC2Data/LocalizedData/GameStrings.txt"
    payload[key] = m.merge_strings(payload.get(key,b""),{
        "DocInfo/Name":"URZ MiniCraft II Data Recovery",
        "DocInfo/DescShort":"Data-only diagnostic; no scripted options",
        "DocInfo/DescLong":"MiniCraft static catalog only. No enhanced AI, match menu, or scripted production multipliers.",
        **m.TOOLTIPS,
    })
    assert not any("Trigger" in p or p.endswith(".galaxy") for p in payload)
    assert not ET.fromstring(payload["Base.SC2Data/GameData/GameData.xml"]).findall(".//TriggerLibs")
    write_payload(root,payload)

def package(root):
    target=root.parent/(root.name+".zip")
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file():
                z.write(p,p.relative_to(root.parent).as_posix())
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
    return target

def check_full(root):
    manifest=ET.parse(root/"ComponentList.SC2Components").getroot()
    assert any(n.get("Type")=="trig" and n.text=="Triggers" for n in manifest)
    assert (root/"Triggers.version").stat().st_size==44
    tr=ET.parse(root/"Triggers").getroot()
    assert tr.findtext(".//ScriptCode").strip()=='include "TriggerLibs/MiniCraftAI"'
    source=(root/"Base.SC2Data/TriggerLibs/MiniCraftAI.galaxy").read_text(encoding="utf-8")
    assert source.count("void MiniCraftAI_Init()")==1
    assert source.startswith("// MiniCraft")
    for p in root.rglob("*.xml"): ET.parse(p)

def main():
    if not hasattr(m,"OLD_OPTIONS_LIBRARY"):
        raise SystemExit("Use the latest repository ZIP: outdated builder.")
    out = HOME / ("Recovery-"+datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    out.mkdir()
    data=data_only(out/"MiniCraft-II-DataOnly.SC2Mod")
    print("Data-only ZIP:",package(out/"MiniCraft-II-DataOnly.SC2Mod"))
    env=os.environ.copy()
    env.pop("MINICRAFT_TARGET_FILE",None)
    env["MINICRAFT_HOME"]=str(out)
    try:
        subprocess.run([sys.executable,str(BUILDER),"--check"],env=env,check=True)
        subprocess.run([sys.executable,str(BUILDER)],env=env,check=True)
        full=out/"MiniCraft-II.SC2Mod"
        check_full(full)
        print("Full ZIP:",package(full))
    except (subprocess.CalledProcessError, AssertionError, OSError, ET.ParseError) as exc:
        print("Full export failed:",exc)
        print("Data-only diagnostic is still available. Do not publish failed full export.")
        return 1
    print("Open the full mod first, then the data-only mod if it fails.")
    print("Data-only has no start menu, enhanced AI, scripted multipliers or resource options.")
    print("Python/XML/ZIP checks are not Galaxy Editor compile checks.")
    return 0

if __name__=="__main__":
    sys.exit(main())
