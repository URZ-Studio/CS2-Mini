"""Clone an empty Galaxy Editor flat-map component folder and add the test arena.

The editor must regenerate MapScript.galaxy when the output is opened and saved.
No terrain binary, existing mod or original template is changed.
"""
import argparse
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT_ID = "4D434641"
def patch(template, output, script_file):
    template, output = template.resolve(), output.resolve()
    if output.exists() or output == template or template in output.parents:
        raise ValueError("Use a new output folder outside the template.")
    for name in ("ComponentList.SC2Components", "MapInfo", "t3Terrain.xml"):
        if not (template / name).is_file():
            raise ValueError("Not an editor-saved SC2Map component folder: missing " + name)
    triggers_path = template / "Triggers"
    triggers = ET.parse(triggers_path).getroot() if triggers_path.exists() else ET.Element("TriggerData")
    if triggers.tag != "TriggerData":
        raise ValueError("Unexpected Triggers format")
    root = triggers.find("Root")
    if root is None:
        root = ET.SubElement(triggers,"Root")
    if len(root) or triggers.findall("Element") or triggers.findall("Library"):
        raise ValueError("Delete all default triggers in the blank template, save and retry. This prevents double melee initialization.")
    script = script_file.read_text(encoding="utf-8")
    if script.count("void MCT_Init()") != 1:
        raise ValueError("Missing custom script initializer")
    ET.SubElement(root,"Item",{"Type":"CustomScript","Id":SCRIPT_ID})
    element = ET.SubElement(triggers,"Element",{"Type":"CustomScript","Id":SCRIPT_ID})
    ET.SubElement(element,"Identifier").text = "FastestAI"
    ET.SubElement(element,"ScriptCode").text = "\n"+script+"\n"
    ET.SubElement(element,"InitFunc").text = "MCT_Init"
    manifest = ET.parse(template / "ComponentList.SC2Components").getroot()
    if manifest.tag != "Components":
        raise ValueError("Unexpected component manifest")
    if not any(x.get("Type") == "trig" for x in manifest):
        ET.SubElement(manifest,"DataComponent",{"Type":"trig"}).text = "Triggers"
    output.parent.mkdir(parents=True,exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".mctest-",dir=output.parent))
    try:
        shutil.copytree(template,stage,dirs_exist_ok=True)
        ET.ElementTree(triggers).write(stage/"Triggers",encoding="utf-8",xml_declaration=True)
        ET.ElementTree(manifest).write(stage/"ComponentList.SC2Components",encoding="utf-8",xml_declaration=True)
        loc = stage/"koKR.SC2Data/LocalizedData/TriggerStrings.txt"
        loc.parent.mkdir(parents=True,exist_ok=True)
        with loc.open("a",encoding="utf-8") as f:
            f.write("\nCustomScript/Name/"+SCRIPT_ID+"=MiniCraft Fastest AI Assault\n")
        # Set document name for the new map without changing its dependencies.
        strings = stage/"koKR.SC2Data/LocalizedData/GameStrings.txt"
        strings.parent.mkdir(parents=True,exist_ok=True)
        old = strings.read_text(encoding="utf-8-sig") if strings.exists() else ""
        lines = [line for line in old.splitlines() if not line.startswith(("DocInfo/Name=", "DocInfo/DescShort="))]
        lines.extend(["DocInfo/Name=MiniCraft Fastest AI Assault", "DocInfo/DescShort=1 vs 3 AI fastest melee"])
        strings.write_text("\n".join(lines)+"\n",encoding="utf-8")
        # Do not hand-edit MapScript.galaxy; editor regenerates it from Triggers.
        stage.rename(output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print("Generated map components:", output)
    print("Open ComponentList.SC2Components, verify the custom script/init function, then Save As and Test Document.")
    print("If the editor does not import the custom script, paste FastestAI.galaxy into a root Custom Script and set its initialization function to MCT_Init.")

if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("template",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--script",type=Path,default=Path(__file__).with_name("FastestAI.galaxy"))
    a=p.parse_args()
    patch(a.template,a.output,a.script)
