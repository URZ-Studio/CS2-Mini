"""MiniCraft EVO preview: build a separate local copy, never edit upstream or vanilla.
MIT upstream TeamKoprulu/SCEvoComplete, copyright Abraham Yunes.
"""
import argparse, collections, copy, json, os, re, runpy, shutil, sys, tempfile
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import xml.etree.ElementTree as ET

REV = "773c8e8ae8828121e8f37bb74ab82ceb761a45bc"
MODS = ("SCEvo_Assets.SC2Mod", "SCEvo_Core.SC2Mod", "SCEvo_Multi.SC2Mod")
BW_RACES = ("BWTe", "BWZe", "BWPr")
EXPECTED = {
 "Terran": {
 "units": "SCV Marine Firebat Medic Ghost Vulture SiegeTank Goliath Wraith Dropship Valkyrie ScienceVessel Battlecruiser SpiderMine Nuke",
 "buildings": "CommandCenter ComsatStation NuclearSilo SupplyDepot Refinery Barracks Bunker EngineeringBay MissileTurret Academy Factory MachineShop Starport ControlTower Armory ScienceFacility PhysicsLab CovertOps"},
 "Zerg": {
 "units": "Larva Egg Drone Overlord Zergling Hydralisk Lurker Mutalisk Scourge Queen Broodling InfestedTerran Ultralisk Defiler Guardian Devourer",
 "buildings": "Hatchery Lair Hive CreepColony SunkenColony SporeColony Extractor SpawningPool EvolutionChamber HydraliskDen Spire GreaterSpire QueensNest NydusCanal UltraliskCavern DefilerMound InfestedCommandCenter"},
 "Protoss": {
 "units": "Probe Zealot Dragoon HighTemplar Archon DarkTemplar DarkArchon Shuttle Reaver Scarab Observer Scout Carrier Interceptor Corsair Arbiter",
 "buildings": "Nexus Pylon Assimilator Gateway Forge ShieldBattery CyberneticsCore PhotonCannon RoboticsFacility Stargate CitadelOfAdun RoboticsBay FleetBeacon TemplarArchive Observatory ArbiterTribunal"}
}
ALIASES = {"Nuke":["NukeSCBW","NukeSCBW@Missile","NuclearMissileSCBW"],"TemplarArchive":["TemplarArchiveSCBW","TemplarArchivesSCBW"],"RoboticsBay":["RoboticsBaySCBW","RoboticsSupportBaySCBW"],"QueensNest":["QueensNestSCBW","QueenNestSCBW"]}
VITALS = {"LifeStart","LifeMax","LifeArmor","LifeRegenRate","ShieldsStart","ShieldsMax","ShieldArmor","ShieldRegenRate"}
RADII = {"Radius","SeparationRadius","InnerRadius","MinimapRadius"}
BUILD_ABILS = {"CAbilTrain","CAbilBuild","CAbilResearch","CAbilWarpTrain","CAbilArmMagazine"}
GAS = ("Refinery","Extractor","Assimilator","VespeneGeyser")
COUNTS = collections.Counter()

def number(v):
    try:
        d=Decimal(v)
        return d if d.is_finite() else None
    except (InvalidOperation,TypeError): return None

def scaled(v, factor, integer=False):
    d=number(v)
    if d is None: return v
    d*=Decimal(str(factor))
    if integer: d=d.quantize(Decimal("1"),rounding=ROUND_HALF_UP)
    return format(d.normalize(),"f") if d else "0"

def attr(e, key, factor, integer=False):
    if key in e.attrib:
        old=e.get(key); new=scaled(old,factor,integer)
        if old!=new: e.set(key,new); COUNTS["fields_changed"]+=1

def vector(e,key,factor):
    old=e.get(key)
    if old is None:return
    parts=old.split(",")
    if all(number(x) is not None for x in parts):
        new=",".join(scaled(x,factor) for x in parts)
        if new!=old:e.set(key,new);COUNTS["fields_changed"]+=1

def put(e,tag,value):
    child=e.find(tag)
    if child is None: child=ET.SubElement(e,tag)
    child.set("value",str(value))

def xmlread(p): return ET.parse(p)
def xmlwrite(t,p):
    p.parent.mkdir(parents=True,exist_ok=True)
    t.write(p,encoding="utf-8",xml_declaration=True)

def inventory(src):
    rows=[]; ids=collections.defaultdict(set); unit_sources=collections.defaultdict(list)
    for mod in MODS[1:]:
        data=src/mod/"Base.SC2Data/GameData"
        for f in sorted(data.rglob("*.xml")):
            root=xmlread(f).getroot()
            if root.tag!="Catalog":continue
            for e in root:
                uid=e.get("id")
                if not uid:continue
                tag=e.tag
                family=next((x for x in ("CUnit","CAbil","CUpgrade","CWeapon","CEffect","CActor","CModel","CBehavior","CAccumulator","CFootprint") if tag.startswith(x)),None)
                if not family:continue
                rel=f.relative_to(data).as_posix()
                if "SCBW" not in uid and not rel.startswith("SCBW"):continue
                ids[family].add(uid)
                rows.append({"mod":mod,"file":rel,"type":tag,"id":uid,"parent":e.get("parent"),"template":e.get("default")=="1"})
                if tag=="CUnit":
                    unit_sources[uid].append(rel)
    crosswalk={}
    for race,groups in EXPECTED.items():
        crosswalk[race]={}
        for group,names in groups.items():
            crosswalk[race][group]={}
            for name in names.split():
                candidates=ALIASES.get(name,[name+"SCBW"])
                found=[x for x in candidates if x in unit_sources]
                if not found:
                    found=sorted(x for x in unit_sources if x.lower().replace("@","").startswith((name+"SCBW").lower()))
                crosswalk[race][group][name]=found
    return {"source_revision":REV,"counts":{k:len(v) for k,v in ids.items()},"crosswalk":crosswalk,"ids":{k:sorted(v) for k,v in ids.items()},"records":rows}

def scope(e,rel):
    uid=e.get("id","")
    return bool(uid) and ("SCBW" in uid or rel.startswith(("SCBW_01.","SCBW_02.","SCBW_03.","SCBW_xx.")))


# Model-space changes only. Keep gameplay area indicators and shared FX intact.
VISUAL_AUDIT = []
MODEL_ORIGINALS = {}
TERRAN_BODY_MODELS = set()
VISUAL_KEEP = re.compile(r"portrait|icon|cursor|range|radius|sight|vision|scan|search|targeting|target.?area|area|aoe|indicator|reticle|telegraph|decal|nuke|nuclear|emp|irradiate|explosion|blast|splash|shockwave|sensor|selection|beam|cone", re.I)
VISUAL_SMALL = re.compile(r"placement|death|birth|warp|build|splat|lift.?off|land|thruster|engine|missile|projectile|muzzle|launch|impact|stimpack|heal|repair|lockdown|yamato|attack|weapon|shell|bullet|tracer|flame|grenade|morph|transform|cloak|matrix|restoration|opticflare", re.I)

def original_field(uid, key, seen=None):
    seen = set() if seen is None else seen
    if uid in seen: return None
    seen.add(uid)
    data = MODEL_ORIGINALS.get(uid, {})
    return data.get(key) or (original_field(data["parent"], key, seen) if data.get("parent") else None)

def half_vector(value):
    if not value: return None
    parts = value.split(",")
    if len(parts) not in (1, 3) or not all(number(p) is not None for p in parts): return None
    return ",".join(scaled(p, .5) for p in parts)

def terran_visual_model(e, rel):
    uid = e.get("id", "")
    row = {"id":uid, "file":rel, "type":"CModel", "changed":[], "unresolved":[]}
    VISUAL_AUDIT.append(row)
    if e.get("default") == "1" or VISUAL_KEEP.search(uid):
        row["status"] = "preserve template/UI/area/shared effect"
        return
    def field(key):
        child = e.find(key)
        return original_field(uid,key) or (child.get("value") if child is not None else None)
    if VISUAL_SMALL.search(uid) and uid not in TERRAN_BODY_MODELS:
        for key in ("ScaleMin", "ScaleMax"):
            value = half_vector(field(key))
            if value is not None:
                put(e, key, value); row["changed"].append(key)
            else: row["unresolved"].append(key)
    for key in ("ShadowRadius", "SelectionRadius", "Radius"):
        value = field(key)
        if number(value) is not None:
            put(e, key, scaled(value,.5)); row["changed"].append(key)
    row["status"] = "patched" if row["changed"] else "inherited or review"
    COUNTS["terran_visual_models_patched"] += bool(row["changed"])
    COUNTS["terran_visual_scale_unresolved"] += bool(row["unresolved"])

def collect_visual_originals(stage):
    MODEL_ORIGINALS.clear(); TERRAN_BODY_MODELS.clear(); VISUAL_AUDIT.clear()
    for mod in MODS[1:]:
        data = stage/mod/"Base.SC2Data/GameData"
        for path in sorted(data.rglob("*.xml")):
            root = xmlread(path).getroot()
            if root.tag != "Catalog": continue
            for e in root:
                uid = e.get("id")
                if not uid: continue
                if e.tag == "CModel":
                    record = MODEL_ORIGINALS.setdefault(uid,{})
                    if e.get("parent"): record["parent"] = e.get("parent")
                    for key in ("ScaleMin","ScaleMax","ShadowRadius","SelectionRadius","Radius"):
                        value = e.find(key)
                        if value is not None and value.get("value") is not None: record[key] = value.get("value")
                elif e.tag == "CActorUnit" and path.relative_to(data).as_posix().startswith("SCBW_01."):
                    TERRAN_BODY_MODELS.add(uid)
                    model = e.find("Model")
                    if model is not None and model.get("value"): TERRAN_BODY_MODELS.add(model.get("value"))

def patch_record(e,rel,fp,unit_ids):
    uid=e.get("id",""); tag=e.tag
    if tag=="CRace" and uid in BW_RACES:
        put(e,"FoodCeiling","300");return
    if uid=="SCBW_DamageFormula@Minimum" and tag=="CAccumulatorConstant":
        put(e,"Amount","0.05");return
    if not scope(e,rel):return
    if tag=="CUnit":
        for child in e:
            if child.tag in VITALS:attr(child,"value",.1)
            elif child.tag in RADII and not any(x in uid for x in GAS):attr(child,"value",.5)
            elif child.tag=="Food" and number(child.get("value")) is not None and number(child.get("value"))<0:attr(child,"value",.5)
            elif child.tag=="CostResource" and child.get("index") in ("Minerals","Vespene"):attr(child,"value",.5,True)
            elif child.tag=="BuildTime":attr(child,"value",.5)
            elif child.tag in ("Footprint","PlacementFootprint") and not any(x in uid for x in GAS):
                val=child.get("value","")
                if "Mini"+val in fp:child.set("value","Mini"+val);COUNTS["footprints"]+=1
                elif val:COUNTS["unmapped_footprint_references"]+=1
        # Scalar fields may be serialized as attributes.
        for key in VITALS:attr(e,key,.1)
        if not any(x in uid for x in GAS):
            for key in RADII:attr(e,key,.5)
    elif tag.startswith("CActor") and (e.get("unitName") in unit_ids or (tag=="CActorUnit" and uid in unit_ids)):
        # Concrete actor only: do not also shrink its base model.
        if e.get("default")!="1":
            sc=e.find("Scale")
            if sc is None:put(e,"Scale","0.5,0.5,0.5")
            else:vector(sc,"value",.5)
            COUNTS["unit_actor_records"]+=1
            if rel.startswith("SCBW_01.") and tag=="CActorUnit":
                flag=e.find("UnitFlags[@index='ShowBlobShadow']")
                if flag is None: flag=ET.SubElement(e,"UnitFlags",index="ShowBlobShadow")
                flag.set("value","0")
                if not any(x.get("Terms")=="ActorCreation" and x.get("Send")=="SetCastShadows" for x in e.findall("On")):
                    ET.SubElement(e,"On",Terms="ActorCreation",Send="SetCastShadows")
                COUNTS["terran_actor_shadow_records"]+=1
    elif tag=="CModel":
        if rel.startswith("SCBW_01."):
            terran_visual_model(e,rel)
            return
        # Only explicit placement/death model sizes; body actor is scaled above.
        if any(x in uid.lower() for x in ("placement","death","birth","warp")):
            for child in e:
                if child.tag in ("ScaleMin","ScaleMax"):vector(child,"value",.5)
                elif child.tag in ("ShadowRadius","SelectionRadius","Radius"):attr(child,"value",.5)
    elif tag=="CEffectDamage":
        for child in e.iter():
            # Feedback converts unscaled Energy into damage; keep the energy drain unchanged.
            if child.tag=="VitalFractionCurrent" and child.get("index")=="Energy":attr(child,"value",.1)
            if child.tag in ("Amount","AttributeBonus","AttributeFactorBonus","ShieldBonus","ShieldFactorBonus"):
                if child.tag not in ("AttributeFactorBonus","ShieldFactorBonus"):attr(child,"value",.1)
        attr(e,"Amount",.1)
    elif tag.startswith("CEffect"):
        # Health/shield changes, not energy, percentages, or movement.
        if tag in ("CEffectModifyUnit","CEffectModifyUnitVital","CEffectHeal"):
            for child in e.iter():
                if child.tag=="VitalArray" and child.get("index") in ("Life","Shields"):
                    attr(child,"Change",.1)
                    for sub in child:
                        if sub.tag in ("Change","ChangeAmount"):attr(sub,"value",.1)
        if tag in ("CEffectCreateHealer","CEffectModifyUnit"):
            v=e.find("RechargeVital")
            # Medic/SCV use the engine's default Life vital when absent.
            if (v is None and tag=="CEffectCreateHealer") or (v is not None and v.get("value") in ("Life","Shields")):
                for child in e.findall("RechargeVitalRate"):attr(child,"value",.1)
                drain=e.find("DrainVital")
                if drain is not None and drain.get("value")=="Energy":
                    for child in e.findall("DrainVitalCostFactor"):attr(child,"value",10)
    elif tag in BUILD_ABILS:
        for child in e.iter():
            if child.tag=="InfoArray":attr(child,"Time",.5)
            elif child.tag=="Time":attr(child,"value",.5)
            elif child.tag=="Resource" and child.get("index") in ("Minerals","Vespene"):attr(child,"value",.5,True)
    elif tag=="CAbilMorph":
        # Only paid morphs: leave siege, burrow, lift/land and other mode switches alone.
        resources=[x for x in e.iter("Resource") if x.get("index") in ("Minerals","Vespene") and number(x.get("value")) is not None and number(x.get("value"))>0]
        if resources:
            for x in resources:attr(x,"value",.5,True)
            for x in e.iter("DurationArray"):
                if x.get("index") in ("Delay","Duration"):attr(x,"value",.5)
            COUNTS["paid_morph_records"]+=1
    elif tag=="CUpgrade":
        for child in e.iter():
            if child.tag not in ("EffectArray","EffectArrayTemplate"):continue
            ref=child.get("Reference","").split(",")
            if len(ref)!=3:continue
            catalog,_,field=ref
            if (catalog=="Unit" and field in VITALS) or (catalog in ("Effect","Accumulator") and field=="Amount"):
                val=child.get("Value","")
                if number(val) is not None:attr(child,"Value",.1)
                elif val.startswith("{") and val.endswith("}") and "/" not in val:
                    child.set("Value",val[:-1]+"*0.1}");COUNTS["upgrade_formula_fields"]+=1
                else:COUNTS["unresolved_upgrade_expressions"]+=1
    elif tag=="CAccumulatorConstant" and (uid.endswith("@Damage") or uid=="ScienceVesselSCBWDefensiveMatrix"):
        for child in e.findall("Amount"):attr(child,"value",.1)
    elif tag=="CBehaviorBuff":
        for response in e.iter("DamageResponse"):
            for key in ("ModifyAmount","ModifyLimit","ModifyMinimumDamage"):attr(response,key,.1)
            for child in response:
                if child.tag in ("ModifyAmount","ModifyLimit","ModifyMinimumDamage"):attr(child,"value",.1)
        for mod in e.iter("Modification"):
            for key in ("LifeArmorBonus","ShieldArmorBonus"):attr(mod,key,.1)
            for child in mod:
                if child.tag in ("LifeArmorBonus","ShieldArmorBonus"):attr(child,"value",.1)

    if tag.startswith("CAbil"):
        # Life-paid skills (Stimpack etc.) scale with the new HP pool; Energy is unchanged.
        for child in e.iter("Vital"):
            if child.get("index")=="Life":attr(child,"value",.1)

def patch_bw(stage, inv, catalogs):
    collect_visual_originals(stage)
    fp={e.get("id") for e in ET.fromstring(catalogs["FootprintData"])}
    unit_ids=set(inv["ids"].get("CUnit",[]))
    for mod in MODS[1:]:
        data=stage/mod/"Base.SC2Data/GameData"
        for path in sorted(data.rglob("*.xml")):
            t=xmlread(path);root=t.getroot()
            if root.tag!="Catalog":continue
            old=ET.tostring(root)
            for e in root:
                rel=path.relative_to(data).as_posix()
                before=ET.tostring(e)
                patch_record(e,rel,fp,unit_ids)
                if rel.startswith("SCBW_01.") and e.get("id") and e.tag.startswith(("CActor","CEffect","CAbil","CUnit","CWeapon","CUpgrade","CBehavior","CAccumulator")):
                    VISUAL_AUDIT.append({"file":rel,"id":e.get("id"),"type":e.tag,"status":"changed" if before!=ET.tostring(e) else "unchanged / review"})
            if ET.tostring(root)!=old:
                xmlwrite(t,path);COUNTS["catalog_files_changed"]+=1
    core=stage/MODS[1]/"Base.SC2Data"
    # Footprints must already exist in Core, where BW units are defined.
    footprint=core/"GameData/MiniCraftBWFootprints.xml"
    footprint.write_text(catalogs["FootprintData"],encoding="utf-8")
    add_include(core,"GameData/MiniCraftBWFootprints.xml")
    # SCBW custom supply engine reads Race.FoodCeiling. Its default is also adjusted.
    # The generated Galaxy library may be regenerated by Editor; RaceData is authoritative.
    lib=core/"LibSCEV.galaxy"
    if lib.is_file():
        s=lib.read_text(encoding="utf-8-sig")
        s2=s.replace(".lv_ceiling = 200.0;",".lv_ceiling = 300.0;")
        if s2!=s:lib.write_text(s2,encoding="utf-8")

def add_include(base,relative):
    path=base/"GameData.xml"
    t=xmlread(path) if path.is_file() else ET.ElementTree(ET.Element("Includes"))
    root=t.getroot()
    if root.tag!="Includes":raise ValueError("Unexpected manifest: "+str(path))
    if not any(e.get("path")==relative for e in root):ET.SubElement(root,"Catalog",path=relative)
    xmlwrite(t,path)

def patch_sc2(stage,catalogs):
    # Load the existing MiniCraft SC2 catalog deltas after EVO's named SC2 changes.
    # Keep the original EVO triggers and race-selection system intact.
    base=stage/MODS[2]/"Base.SC2Data"
    out=ET.Element("Catalog")
    for name,raw in catalogs.items():
        if name=="FootprintData":continue # registered in Core
        for e in ET.fromstring(raw):out.append(copy.deepcopy(e))
    xmlwrite(ET.ElementTree(out),base/"GameData/MiniCraftSC2.xml")
    add_include(base,"GameData/MiniCraftSC2.xml")

def doc(stage,mod):
    path=stage/mod/"DocumentInfo";t=xmlread(path);root=t.getroot()
    deps=root.find("Dependencies")
    if deps is not None:
        for e in deps:
            for name in MODS:
                if name in (e.text or ""):
                    e.text="file:Mods/MiniCraft-EVO/"+name
    if mod==MODS[2]:
        flags=root.find("Flags")
        if flags is None:flags=ET.SubElement(root,"Flags")
        if not any(e.text=="ExtensionMod" for e in flags):ET.SubElement(flags,"Value").text="ExtensionMod"
        mt=root.find("ModType")
        if mt is None:mt=ET.SubElement(root,"ModType")
        if mt.find("Value") is None:ET.SubElement(mt,"Value")
        mt.find("Value").text="Gameplay"
    xmlwrite(t,path)
    for loc in ("enUS","koKR"):
        f=stage/mod/(loc+".SC2Data")/"LocalizedData/GameStrings.txt"
        if not f.is_file():continue
        data=f.read_text(encoding="utf-8-sig").splitlines()
        name="MiniCraft EVO" if mod==MODS[2] else "MiniCraft EVO "+mod.split("_")[1].split(".")[0]
        data=[x for x in data if not x.startswith("DocInfo/Name=")]
        data.append("DocInfo/Name="+name)
        f.write_text("\n".join(data)+"\n",encoding="utf-8-sig")

def selftest():
    e=ET.fromstring('<CUnit id="MarineSCBW"><LifeMax value="40"/><Food value="-1"/><CostResource index="Minerals" value="50"/><Radius value="0.375"/></CUnit>')
    patch_record(e,"SCBW_01.Terran/m.xml",set(),{"MarineSCBW"})
    assert [c.get("value") for c in e]==["4","-0.5","25","0.1875"]
    e=ET.fromstring('<CEffectDamage id="MarineSCBWWeapon@Damage"><Amount value="6"/></CEffectDamage>')
    patch_record(e,"SCBW_01.Terran/m.xml",set(),set());assert e.find("Amount").get("value")=="0.6"
    e=ET.fromstring('<CUnit id="BarracksSCBW"><Footprint value="Footprint3x3Contour"/><Food value="8"/></CUnit>')
    patch_record(e,"SCBW_01.Terran/b.xml",{"MiniFootprint3x3Contour"},set())
    assert e.find("Footprint").get("value")=="MiniFootprint3x3Contour" and e.find("Food").get("value")=="8"
    e=ET.fromstring('<CUpgrade id="XSCBW"><EffectArrayTemplate Reference="Effect,X,Amount" Value="{DataCollection,X,DamagePerDice}"/></CUpgrade>')
    patch_record(e,"UpgradeData.xml",set(),set());assert e[0].get("Value").endswith("*0.1}")
    e=ET.fromstring('<CAccumulatorConstant id="BattlecruiserSCBWYamato@Damage"><Amount value="260"/></CAccumulatorConstant>')
    patch_record(e,"SCBW_01.Terran/b.xml",set(),set());assert e.find("Amount").get("value")=="26"
    e=ET.fromstring('<CEffectCreateHealer id="MedicSCBWHeal@Healer"><DrainVital value="Energy"/><DrainVitalCostFactor value="0.5"/><RechargeVitalRate value="12"/></CEffectCreateHealer>')
    patch_record(e,"SCBW_01.Terran/m.xml",set(),set());assert e.find("RechargeVitalRate").get("value")=="1.2" and e.find("DrainVitalCostFactor").get("value")=="5"
    e=ET.fromstring('<CModel id="MarineSCBWWeapon@Launch"><ScaleMin value="1,1,1"/><ScaleMax value="2,2,2"/></CModel>')
    patch_record(e,"SCBW_01.Terran/m.xml",set(),set())
    assert e.find("ScaleMin").get("value")=="0.5,0.5,0.5" and e.find("ScaleMax").get("value")=="1,1,1"
    e=ET.fromstring('<CModel id="ScienceVesselSCBWEMPShockwave@Impact"><ScaleMin value="2,2,2"/></CModel>')
    patch_record(e,"SCBW_01.Terran/m.xml",set(),set())
    assert e.find("ScaleMin").get("value")=="2,2,2"
    e=ET.fromstring('<CActorUnit id="MarineSCBW" unitName="MarineSCBW"/>')
    patch_record(e,"SCBW_01.Terran/m.xml",set(),{"MarineSCBW"})
    assert e.find("UnitFlags").get("value")=="0" and e.find("On").get("Send")=="SetCastShadows"
    COUNTS.clear(); VISUAL_AUDIT.clear()
    print("EVO transform self-tests passed.")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--source",type=Path)
    p.add_argument("--mods",type=Path)
    p.add_argument("--mini",type=Path,default=Path(__file__).resolve().parents[1]/"Build-MiniCraft.py")
    args=p.parse_args();selftest()
    if args.check:return
    if not args.source or not args.mods:p.error("--source and --mods required")
    src=args.source.resolve();mods=args.mods.resolve()
    if (src/"SC Evo Complete").is_dir():src=src/"SC Evo Complete"
    if not mods.is_dir() or mods.name.lower()!="mods":raise SystemExit("Select the installed StarCraft II Mods folder.")
    for mod in MODS:
        if not (src/mod/"ComponentList.SC2Components").is_file():raise SystemExit("Missing source components: "+mod)
    for mod in MODS[1:]:
        if not (src/mod/"Base.SC2Data/GameData").is_dir():raise SystemExit("Missing source catalogs: "+mod)
    catalogs=runpy.run_path(str(args.mini))["CATALOGS"]
    inv=inventory(src)
    for key in ("MarineSCBW","ZerglingSCBW","DragoonSCBW","DarkArchonSCBW","ReaverSCBW","DefilerSCBW"):
        if key not in inv["ids"].get("CUnit",[]):raise SystemExit("Unexpected source: missing "+key)
    out=mods/"MiniCraft-EVO"
    if out.exists() and not (out/"MINICRAFT-EVO.json").is_file():raise SystemExit("Refusing to replace unrecognized folder: "+str(out))
    stage=Path(tempfile.mkdtemp(prefix=".MiniCraft-EVO-stage-",dir=mods))
    backup=None
    try:
        for mod in MODS:shutil.copytree(src/mod,stage/mod)
        patch_bw(stage,inv,catalogs);patch_sc2(stage,catalogs)
        for mod in MODS:doc(stage,mod)
        license_path=src.parent/"LICENSE"
        if not license_path.is_file():raise SystemExit("Upstream LICENSE missing")
        shutil.copy2(license_path,stage/"LICENSE-SCEvo.txt")
        inv["transform_counts"]=dict(COUNTS)
        inv["terran_record_audit"]=VISUAL_AUDIT
        (stage/"EVO-audit.json").write_text(json.dumps(inv,indent=2,ensure_ascii=False),encoding="utf-8")
        (stage/"MINICRAFT-EVO.json").write_text(json.dumps({"source":REV,"version":"0.1.1-preview"},indent=2),encoding="utf-8")
        if out.exists():
            from datetime import datetime
            backup=out.with_name(out.name+".backup-"+datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
            out.rename(backup)
        try:stage.rename(out)
        except BaseException:
            if backup and not out.exists():backup.rename(out)
            raise
    finally:
        if stage.exists():shutil.rmtree(stage)
    print("Built:",out/MODS[2]/"ComponentList.SC2Components")
    print("Inventory:",inv["counts"])
    print("Transform:",dict(COUNTS))
    missing=[race+"/"+group+"/"+name for race,g in inv["crosswalk"].items() for group,items in g.items() for name,ids in items.items() if not ids]
    print("Unmapped canonical names (see audit):",missing)
    print("Editor and actual game still require validation. Close editor before rebuild.")
if __name__=="__main__":main()
