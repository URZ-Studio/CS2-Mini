"""Build a disposable stock-profile test mod for future in-match craft selection.

No production mod is edited. Run the test only in a private match.
A catalog readback PASS does not prove the live actor/pathing/AI changed.
"""
import argparse
import importlib.util
from pathlib import Path
import tempfile
import shutil
import xml.etree.ElementTree as ET

# Test representative fields from the actual mini catalog, plus a stock
# footprint link from another building. All changes are immediately restored.
PROBES = [
    ("Unit", "Marine", "LifeMax", "4.5", True),
    ("Unit", "Marine", "Food", "-0.5", True),
    ("Unit", "Marine", "Radius", "0.28125", True),
    ("Unit", "Marine", "SeparationRadius", "0.28125", True),
    ("Unit", "Marine", "CostResource[0]", "25", True),
    ("Unit", "Nexus", "LifeMax", "100", True),
    ("Effect", "AcidSalivaU", "Amount", "1.6", True),
    ("Abil", "BarracksTrain", "InfoArray[0].Time", "12.5", True),
    ("Upgrade", "TerranInfantryWeaponsLevel1", "EffectArray[1].Value", "0.1", True),
    ("Model", "Marine", "ScaleMin", "0.75,0.75,0.75", False),
    ("Model", "Marine", "ScaleMax", "0.75,0.75,0.75", False),
    ("Actor", "Marine", "BarWidth", "18", True),
    ("Actor", "Marine", "UnitFlags[ShowBlobShadow]", "0", False),
]

SCRIPT = r'''
int mc_probePassed = 0;
int mc_probeBlocked = 0;
int mc_probeSkipped = 0;
bool mc_probeUnsafe = false;
void MC_ProbeLog(string message) {
    UIDisplayMessage(PlayerGroupAll(),c_messageAreaChat,StringToText("[Craft Probe] "+message));
    TriggerDebugOutput(1,StringToText("[Craft Probe] "+message),true);
}
bool MC_ProbeEqual(string a,string b,bool numeric) {
    if (a == b) { return true; }
    if (!numeric || a == "" || b == "") { return false; }
    return StringToFixed(a) == StringToFixed(b);
}
void MC_ProbeField(int cat,string id,string field,int p,string target,bool numeric) {
    string key = id+"."+field;
    string old;
    string changed;
    string restored;
    bool accepted;
    bool restoreOK;
    if (mc_probeUnsafe) { return; }
    MC_ProbeLog("TEST "+key);
    if (!CatalogEntryIsValid(cat,id)) {
        mc_probeSkipped += 1;
        MC_ProbeLog("SKIP missing entry "+key);
        return;
    }
    old = CatalogFieldValueGet(cat,id,field,p);
    if (old == "" || target == "" || MC_ProbeEqual(old,target,numeric)) {
        mc_probeSkipped += 1;
        MC_ProbeLog("SKIP empty or same "+key+" ["+old+"]");
        return;
    }
    accepted = CatalogFieldValueSet(cat,id,field,p,target);
    changed = CatalogFieldValueGet(cat,id,field,p);
    // Even a rejected call may have changed state; restore whenever needed.
    restoreOK = true;
    if (changed != old) {
        restoreOK = CatalogFieldValueSet(cat,id,field,p,old);
    }
    restored = CatalogFieldValueGet(cat,id,field,p);
    if (!restoreOK || !MC_ProbeEqual(restored,old,numeric)) {
        mc_probeUnsafe = true;
        MC_ProbeLog("RESTORE FAILED "+key+" old="+old+" actual="+restored+" END TEST MATCH");
        return;
    }
    if (accepted && MC_ProbeEqual(changed,target,numeric)) {
        mc_probePassed += 1;
        MC_ProbeLog("PASS readback "+key+" "+old+" -> "+changed+" -> "+restored);
    } else {
        mc_probeBlocked += 1;
        MC_ProbeLog("BLOCKED/UNCONFIRMED "+key+" old="+old+" readback="+changed);
    }
}
void MC_RunCraftProbe() {
    int p = mc_host;
    string foot;
    string placement;
    if (!MC_Active(p)) {
        p = 1;
        while (p <= 15 && !MC_Active(p)) { p += 1; }
    }
    if (p > 15) { MC_ProbeLog("No active player"); return; }
    MC_ProbeLog("START: private test only; readback is not live gameplay proof");
    // Probe a stock alternative link; no MiniFootprint dependency required.
    foot = CatalogFieldValueGet(c_gameCatalogUnit,"SupplyDepot","Footprint",p);
    placement = CatalogFieldValueGet(c_gameCatalogUnit,"SupplyDepot","PlacementFootprint",p);
    MC_ProbeField(c_gameCatalogUnit,"Barracks","Footprint",p,foot,false);
    MC_ProbeField(c_gameCatalogUnit,"Barracks","PlacementFootprint",p,placement,false);
    // INSERT_PROBES
    if (mc_probeUnsafe) { return; }
    MC_ProbeLog("END pass="+IntToString(mc_probePassed)+" blocked="+IntToString(mc_probeBlocked)+" skipped="+IntToString(mc_probeSkipped));
    MC_ProbeLog("Catalog only: live geometry, skins, existing units and AI still require tests.");
}
'''
def inject(source):
    lines = []
    for cat, entry, field, target, numeric in PROBES:
        lines.append(f'    MC_ProbeField(c_gameCatalog{cat},"{entry}","{field}",p,"{target}",{str(numeric).lower()});')
    probe = SCRIPT.replace("    // INSERT_PROBES", "\n".join(lines))
    apply = "void MC_Apply() {"
    anchor = "    mc_mult = mc_choice[1]+1;"
    if source.count(apply) != 1 or source.count(anchor) != 1:
        raise ValueError("Builder source changed; probe not injected")
    source = source.replace(apply, probe + "\n" + apply, 1)
    source = source.replace(anchor, "    MC_RunCraftProbe();\n    if (mc_probeUnsafe) { return; }\n" + anchor, 1)
    return source

def build(builder_path, output):
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"Probe folder already exists; rename or remove your test copy: {output}")
    spec = importlib.util.spec_from_file_location("minicraft_builder", builder_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.validate()
    module.apply_size_014()
    module.AI_SOURCE = inject(module.AI_SOURCE)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".craft-probe-", dir=output.parent))
    try:
        payload = module.normal_payload(stage)
        loc = "koKR.SC2Data/LocalizedData/GameStrings.txt"
        payload[loc] = module.merge_strings(payload[loc],{
            "DocInfo/Name":"URZ Craft Switch Probe (PRIVATE TEST)",
            "DocInfo/DescShort":"개발 전용 전환 진단",
            "DocInfo/DescLong":"비공개 테스트 전용. 일반 크래프트 경기 시작 시 전환 가능성을 진단합니다.",
        })
        trigger = ET.fromstring(payload["Triggers"])
        assert trigger.findtext(".//ScriptCode").strip() == 'include "TriggerLibs/MiniCraftAI"'
        code = payload["Base.SC2Data/TriggerLibs/MiniCraftAI.galaxy"].decode("utf-8")
        assert code.count("MC_RunCraftProbe();") == 1
        assert "mc_normalProfile = true" in code
        assert "UnitPauseAll(false);" in code
        assert code.index("UnitPauseAll(false);",code.index("void MC_Apply()")) < code.index("MC_RunCraftProbe();",code.index("void MC_Apply()"))
        for path, data in payload.items():
            dest = stage / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        # Also protect the probe from the normal MiniCraft patch path.
        (stage / module.NORMAL_MARKER).write_text("Disposable NormalCraft probe\n",encoding="utf-8")
        (stage / "CRAFT-PROBE-PRIVATE.txt").write_text("Disposable private test only. Do not publish as the normal MiniCraft or NormalCraft mod.\n",encoding="utf-8")
        if output.exists():
            raise FileExistsError(output)
        stage.rename(output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print("Probe component folder:",output)
    print("Open ComponentList.SC2Components in Galaxy Editor and save/publish privately under a NEW name.")
    print("Start a test match, press game start, capture [Craft Probe] chat lines. Exit after test.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--builder",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    build(args.builder,args.output)
