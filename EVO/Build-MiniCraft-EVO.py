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

def xmlread(p):
    # SC2 catalog templates contain <?token ...?> processing instructions.
    return ET.parse(p,parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True,insert_pis=True)))
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
# Verified SC2Mapster Core/Liberty/VoidMulti model templates (not live client data).
VANILLA_MODEL_SCALES = {"__DEFAULT__":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"IGNORE":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"FXAPortrait":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Portrait":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Doodad":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Curtain":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Building":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BuildingDeath":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Unit":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PlanetViews":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PlanetIcons":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UnitDeath":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UnitDeathRagdoll":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Placement":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Skybox":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"FX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LaunchFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OneShotSpellFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MissileFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ImpactFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BuffFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PersistentSpellFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Splat":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SM":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SMCAMERA":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SMCHARACTER":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SMSET":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UI":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WizLaunchFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WizImpactFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WizSimpleBeam":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WizSimpleMissile":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RaceLaunchFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RaceImpactFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RaceMissileFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RacePersistentSpellFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RaceOneShotSpellFX":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Glaze":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UIFeedback":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UIGlue":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BeaconPing":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"Portrait_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Unit_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UnitDeath_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Building_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BuildingDeath_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Placement_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LaunchFX_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ImpactFX_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MissileFX_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PersistentSpellFX_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OneShotSpellFX_COOP":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BanelingDeathLowBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ClanGems":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StasisWardBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StasisWardDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StasisWardPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"Trophies":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PlacementEx":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BuildingEx":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BuildingDeathEx":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZergBuildingBuild":{"ScaleMin":"1.100000,1.100000,1.100000","ScaleMax":"1.100000,1.100000,1.100000"},"ZergBuildingBuild3x3":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"ZergBuildingBuild2x2Tall":{"ScaleMin":"0.550000,0.550000,0.800000","ScaleMax":"0.550000,0.550000,0.800000"},"ZergBuildingBuild2x2":{"ScaleMin":"0.550000,0.550000,0.550000","ScaleMax":"0.550000,0.550000,0.550000"},"ZergBuildingBuild1x1":{"ScaleMin":"0.350000,0.350000,0.350000","ScaleMax":"0.350000,0.350000,0.350000"},"TerranBuildingBuild":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TerranBuildingBuildSmall":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TerranBuildingBuildTiny":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"FusionCoreDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostAcademyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OrbitalCommandDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OrbitalCommandFlyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SensorTowerDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ReactorDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ReactorDetachedDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StarportDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StarportFlyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TechLabDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TechLabDetachedDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SpawningPoolDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoachWarrenDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BanelingNestDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"EvolutionChamberDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ExtractorBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"LurkerDenPlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"ExtractorPlacementBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"ExtractorDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ExtractorEmptyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ExtractorBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HatcheryBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"HatcheryBuildBase":{"ScaleMin":"1.100000,1.100000,1.100000","ScaleMax":"1.100000,1.100000,1.100000"},"LairBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"HiveBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"EvolutionChamberBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"EvolutionChamberBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"SpineCrawlerBase":{"ScaleMin":"0.950000,0.950000,0.950000","ScaleMax":"0.950000,0.950000,0.950000"},"SpineCrawlerDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SpineCrawlerBuildBase":{"ScaleMin":"0.550000,0.550000,0.550000","ScaleMax":"0.550000,0.550000,0.550000"},"SpineCrawlerPlacementBase":{"ScaleMin":"0.950000,0.950000,0.950000","ScaleMax":"0.950000,0.950000,0.950000"},"SpineCrawlerUnburrowedDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SporeCrawlerBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"SporeCrawlerDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SporeCrawlerBuildBase":{"ScaleMin":"0.550000,0.550000,0.550000","ScaleMax":"0.550000,0.550000,0.550000"},"SporeCrawlerPlacementBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"SporeCrawlerUnburrowedDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SpawningPoolBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HatcheryDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LairDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HiveDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SpawningPoolBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"BanelingNestBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"HydraliskDenBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"HydraliskDenDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HydraliskDenMorphBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HydraliskDenBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"SpireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SpireBuildBase":{"ScaleMin":"0.550000,0.550000,0.800000","ScaleMax":"0.550000,0.550000,0.800000"},"GreaterSpireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GreaterSpireBuildBase":{"ScaleMin":"0.550000,0.550000,0.800000","ScaleMax":"0.550000,0.550000,0.800000"},"SpireMorphBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusWormBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GreaterSpireDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusCanalBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusCanalPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusRumbleBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusCanalDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusCanalDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusCanalDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoachWarrenBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"RoachWarrenBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"InfestationPitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestationPitDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestationPitBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"UltraliskCavernBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"UltraliskCavernDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UltraliskCavernBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"LarvaBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusNetworkBase":{"ScaleMin":"0.700000,0.700000,0.700000","ScaleMax":"0.700000,0.700000,0.700000"},"NydusNetworkDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusNetworkBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"CreepTumorBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CreepTumorDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CreepTumorBuildBase":{"ScaleMin":"0.350000,0.350000,0.350000","ScaleMax":"0.350000,0.350000,0.350000"},"InfestationPitPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusNetworkPlacementBase":{"ScaleMin":"0.700000,0.700000,0.700000","ScaleMax":"0.700000,0.700000,0.700000"},"SpirePlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CreepTumorPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HydraliskDenPlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"CreepTumorMissileBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SpawningPoolPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HatcheryPlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"EvolutionChamberPlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"BanelingNestPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LurkerDenBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"LurkerDenDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LurkerDenBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"RoachWarrenPlacementBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"UltraliskCavernPlacementBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"LarvaPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BanelingCocoonPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CocoonPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"EggPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NydusWormPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BanelingCocoonBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"BanelingCocoonUpgradeBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"BanelingCocoonDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"EggBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"EggDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"EggSuperBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"EggDeathVariationBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"EggsplosionGeneric1Base":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"EggsplosionGeneric2Base":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ArmoryBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ArmoryPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ArmoryDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BarracksBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"BarracksDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BarracksPlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"BarracksFlyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BunkerBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BunkerDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BunkerEmptyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BunkerUpgradeBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BunkerUpgradeDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BunkerUpgradeEmptyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BunkerPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BunkerUpgradePlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CommandCenterBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"CommandCenterPlacementBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"OrbitalCommandPlacementBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"EngineeringBayBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"EngineeringBayPlacementBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"EngineeringBayDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"FactoryBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"FactoryPlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"FactoryDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"FactoryFlyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TechLabBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"TechLabPlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"SensorTowerBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SensorTowerPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"FusionCoreBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"FusionCorePlacementBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"GhostAcademyBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostAcademyPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MissileTurretBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MissileTurretPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MissileTurretDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ReactorBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"ReactorPlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"RefineryBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"RefineryPlacementBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"RefineryDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RefineryEmptyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StarportBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"StarportPlacementBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"SupplyDepotBase":{"ScaleMin":"0.600000,0.600000,0.600000","ScaleMax":"0.600000,0.600000,0.600000"},"SupplyDepotDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SupplyDepotLoweredDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SupplyDepotPlacementBase":{"ScaleMin":"0.600000,0.600000,0.600000","ScaleMax":"0.600000,0.600000,0.600000"},"SupplyDepotAttachmentBase":{"ScaleMin":"0.600000,0.600000,0.600000","ScaleMax":"0.600000,0.600000,0.600000"},"SupplyDepotAttachmentDeathBase":{"ScaleMin":"0.600000,0.600000,0.600000","ScaleMax":"0.600000,0.600000,0.600000"},"SupplyDepotAttachmentLoweredDeathBase":{"ScaleMin":"0.600000,0.600000,0.600000","ScaleMax":"0.600000,0.600000,0.600000"},"CommandCenterDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CommandCenterFlyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CommandCenterMorphDeathBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"PlanetaryFortressDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RefineryBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CommandCenterBuildBase":{"ScaleMin":"1.100000,1.100000,1.100000","ScaleMax":"1.100000,1.100000,1.100000"},"SupplyDepotBuildBase":{"ScaleMin":"0.450000,0.450000,0.450000","ScaleMax":"0.450000,0.450000,0.450000"},"BunkerBuildBase":{"ScaleMin":"0.700000,0.700000,0.700000","ScaleMax":"0.700000,0.700000,0.700000"},"EngineeringBayBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"GhostAcademyBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BarracksBuildBase":{"ScaleMin":"0.930000,0.930000,0.930000","ScaleMax":"0.930000,0.930000,0.930000"},"FactoryBuildBase":{"ScaleMin":"0.950000,0.950000,0.950000","ScaleMax":"0.950000,0.950000,0.950000"},"ArmoryBuildBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"StarportBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"FusionCoreBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"TechLabBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"ReactorBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"SensorTowerBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MissileTurretBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AssimilatorBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"AssimilatorPlacementBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"AssimilatorDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AssimilatorEmptyDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NexusBase":{"ScaleMin":"1.200000,1.200000,1.200000","ScaleMax":"1.200000,1.200000,1.200000"},"NexusPlacementBase":{"ScaleMin":"1.200000,1.200000,1.200000","ScaleMax":"1.200000,1.200000,1.200000"},"NexusDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PylonBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"PylonPlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"GatewayBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"GatewayPlacementBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"ForgeBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"ForgePlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"ForgeDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TwilightCouncilBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"TwilightCouncilPlacementBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"TwilightCouncilDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CyberneticsCoreBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CyberneticsCoreDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CyberneticsCorePlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoboticsBayBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoboticsBayWarpInBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoboticsBayPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoboticsFacilityBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"RoboticsFacilityPlacementBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"StargateBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"StargatePlacementBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"FleetBeaconPlacementBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"FleetBeaconBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"TemplarArchiveBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"TemplarArchiveDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TemplarArchivePlacementBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"DarkShrineBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"DarkShrinePlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"DarkShrineDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PhotonCannonBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"PhotonCannonPlacementBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"PhotonCannonDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PhotonCannonUnpoweredDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ShieldBatteryBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ShieldBatteryPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ShieldBatteryDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GatewayDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoboticsFacilityDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoboticsFacilityUnpoweredDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoboticsBayDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoboticsBayUnpoweredDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StargateDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StargateUnpoweredDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TemplarArchiveWarpInBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"WarpGateDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PylonDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"FleetBeaconDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"FleetBeaconUnpoweredDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AssimilatorWarpInBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"CyberneticsCoreWarpInBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DarkShrineWarpInBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"FleetBeaconWarpInBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"ForgeWarpInBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"GatewayWarpInBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"NexusWarpInBase":{"ScaleMin":"1.200000,1.200000,1.200000","ScaleMax":"1.200000,1.200000,1.200000"},"PhotonCannonWarpInBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"PylonWarpInBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"RoboticsFacilityWarpInBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"StargateWarpInBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"TwilightCouncilWarpInBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"ShieldBatteryWarpInBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LocustDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodlingPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LocustDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LocustDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LocustDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LocustPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UltraliskDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UltraliskDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UltraliskDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BattlecruiserDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BattlecruiserYamatoDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoachDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoachDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SentryDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SiegeTankDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SiegeTankSiegedDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DroneDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DroneDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MedivacDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HydraliskDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HydraliskDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CarrierDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InterceptorDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OverlordDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OverseerDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RavenPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SCVDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VikingFighterDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoachBase":{"ScaleMin":"1.100000,1.100000,1.100000","ScaleMax":"1.100000,1.100000,1.100000"},"RoachDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BanelingPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CorruptorPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OverlordPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OverseerPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoachPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoachUpgradeBase":{"ScaleMin":"1.100000,1.100000,1.100000","ScaleMax":"1.100000,1.100000,1.100000"},"ZerglingDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZerglingDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZerglingDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZerglingDeathEviscerateBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZerglingUpgradeDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZerglingUpgradeDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZerglingUpgradeDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZerglingUpgradeDeathEviscerateBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodLordPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZerglingPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HydraliskPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MutaliskPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AdeptPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CarrierPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ImmortalPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VoidRayPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ColossusDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ColossusBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"ColossusPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ProbeDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ProbeBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"ProbePortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZealotPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZealotBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"ZealotWarpInBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"ZealotDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ImmortalBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"ImmortalDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HighTemplarDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HighTemplarBase":{"ScaleMin":"0.950000,0.950000,0.950000","ScaleMax":"0.950000,0.950000,0.950000"},"HighTemplarShadowBase":{"ScaleMin":"0.950000,0.950000,0.950000","ScaleMax":"0.950000,0.950000,0.950000"},"HighTemplarWarpInBase":{"ScaleMin":"0.950000,0.950000,0.950000","ScaleMax":"0.950000,0.950000,0.950000"},"HighTemplarPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DarkTemplarPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DarkTemplar2PortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DarkTemplarBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"DarkTemplarWarpInBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"DarkTemplarDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DarkTemplarDeath00Base":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DarkTemplarDeath01Base":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ObserverBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"ObserverWarpInBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"ObserverPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ObserverDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CarrierBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"CarrierWarpInStargateBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"InterceptorBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"ArchonBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"ArchonDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ArchonPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PhoenixPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PhoenixBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"PhoenixWarpInBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"PhoenixWarpInStargateBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"PhoenixDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WarpPrismBase":{"ScaleMin":"0.550000,0.550000,0.550000","ScaleMax":"0.550000,0.550000,0.550000"},"WarpPrismPhasingBase":{"ScaleMin":"0.550000,0.550000,0.550000","ScaleMax":"0.550000,0.550000,0.550000"},"WarpPrismWarpInBase":{"ScaleMin":"0.550000,0.550000,0.550000","ScaleMax":"0.550000,0.550000,0.550000"},"WarpPrismDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WarpPrismPhasingDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WarpPrismPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VoidRayDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VoidRayBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"VoidRayWarpInStargateBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"StalkerDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StalkerBase":{"ScaleMin":"0.690000,0.690000,0.690000","ScaleMax":"0.690000,0.690000,0.690000"},"StalkerWarpInBase":{"ScaleMin":"0.690000,0.690000,0.690000","ScaleMax":"0.690000,0.690000,0.690000"},"StalkerPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AutoTurretBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"AutoTurretDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AutoTurretPlacementBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"BattlecruiserBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"MedivacPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BattlecruiserPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MedivacBase":{"ScaleMin":"0.700000,0.700000,0.700000","ScaleMax":"0.700000,0.700000,0.700000"},"ThorBase":{"ScaleMin":"0.500000,0.500000,0.500000","ScaleMax":"0.500000,0.500000,0.500000"},"ThorPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ThorTransitBase":{"ScaleMin":"0.500000,0.500000,0.500000","ScaleMax":"0.500000,0.500000,0.500000"},"ThorDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarineDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarineDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarineDeathBlastBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarineDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarineDeathEviscerateBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarinePortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarineBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ReaperBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"ReaperDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ReaperPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RavenBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"RavenDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SCVBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"SCVPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SiegeTankBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"SiegeTankPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SiegeTankSiegedBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"SiegeTankMorphBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"VikingAssaultPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VikingPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VikingFighterBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"VikingMorphBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"BansheeBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"BansheePortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BansheeDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"InfestorDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DroneBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"DroneDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DronePortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OverlordBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"OverseerBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"ZerglingBase":{"ScaleMin":"0.770000,0.770000,0.770000","ScaleMax":"0.770000,0.770000,0.770000"},"ZerglingUpgradeBase":{"ScaleMin":"0.770000,0.770000,0.770000","ScaleMax":"0.770000,0.770000,0.770000"},"HydraliskDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HydraliskBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"CorruptorBase":{"ScaleMin":"0.700000,0.700000,0.700000","ScaleMax":"0.700000,0.700000,0.700000"},"CorruptorDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MutaliskBase":{"ScaleMin":"0.600000,0.600000,0.600000","ScaleMax":"0.600000,0.600000,0.600000"},"MutaliskDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodLordBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"BroodLordDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodlingBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodlingDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodlingDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodlingDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodlingEscortBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"QueenBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"QueenDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"QueenDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"QueenDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"QueenPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UltraliskBaseNoAnims":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"UltraliskBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"UltraliskPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BanelingBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"BanelingDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VikingAssaultDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VikingAssaultBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"BroodLordWeaponBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodLordBWeaponBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MothershipBase":{"ScaleMin":"0.600000,0.600000,0.600000","ScaleMax":"0.600000,0.600000,0.600000"},"MothershipDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MothershipPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarauderBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarauderDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarauderDeathEviscerateBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarauderPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SentryBase":{"ScaleMin":"0.600000,0.600000,0.600000","ScaleMax":"0.600000,0.600000,0.600000"},"SentryPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SentryWarpInBase":{"ScaleMin":"0.600000,0.600000,0.600000","ScaleMax":"0.600000,0.600000,0.600000"},"HellionBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"HellionPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HellionDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StalkerBlinkOutBase":{"ScaleMin":"0.690000,0.690000,0.690000","ScaleMax":"0.690000,0.690000,0.690000"},"GhostAlternateBaseNoAnims":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostAlternateBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostAlternatePortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostAlternateDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostAlternateDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostAlternateDeathBlastBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostAlternateDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostAlternateDeathEviscerateBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostAlternateDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BansheeDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BattlecruiserDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodlingDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodLordDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CarrierDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ColossusDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CorruptorDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DroneDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HellionMorphPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HellionHellbatBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"HellionMorphBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"HellionHellbatDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HellionDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HellionHellbatDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HydraliskDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BattlecruiserHyperjumpInBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BattlecruiserHyperjumpOutBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BattlecruiserYamatoHyperjumpInBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BattlecruiserYamatoHyperjumpOutBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ImmortalDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InterceptorDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LocustBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"LurkerBase":{"ScaleMin":"1.250000,1.250000,1.250000","ScaleMax":"1.250000,1.250000,1.250000"},"LurkerDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LurkerDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LurkerDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LurkerPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarauderDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MarineDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MedivacDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MothershipCoreMorphAdditionBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MothershipCorePortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MothershipCoreBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"MothershipDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"MutaliskDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ObserverDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OracleBase":{"ScaleMin":"0.650000,0.650000,0.650000","ScaleMax":"0.650000,0.650000,0.650000"},"OracleDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OracleMorphDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OracleDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OracleWalkDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OraclePortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OracleMorphDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OracleWarpInStargateBase":{"ScaleMin":"0.650000,0.650000,0.650000","ScaleMax":"0.650000,0.650000,0.650000"},"OverlordDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OverseerDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"PhoenixDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ProbeDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"QueenDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RavenDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ReaperDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoachDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SCVDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SentryDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SiegeTankDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SiegeTankSiegedDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StalkerDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SwarmHostPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TempestWarpInStargateBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SwarmHostDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SwarmHostBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SwarmHostDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SwarmHostMPBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SwarmHostMPDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SwarmHostDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SwarmHostDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TempestDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TempestPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TempestBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"TempestDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ThorDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ThorMorphDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UltraliskDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VikingAssaultDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VikingFighterDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ViperBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"ViperDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ViperPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"VoidRayDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WarpPrismDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WarpPrismPhasingDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WidowMineBase":{"ScaleMin":"0.750000,0.750000,0.750000","ScaleMax":"0.750000,0.750000,0.750000"},"WidowMineBurrowDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WidowMinePortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WidowMineDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WidowMineDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZealotDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZerglingDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZerglingUpgradeDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AdeptBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AdeptDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AdeptDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AdeptWarpInBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AdeptProtossSpiritDeathModelBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BattlecruiserHyperjumpPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"BattlecruiserYamatoHyperjumpPlacementBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CycloneDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CycloneDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CycloneBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CyclonePortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DarkTemplarDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DisruptorDeathBase":{"ScaleMin":"1.350000,1.350000,1.350000","ScaleMax":"1.350000,1.350000,1.350000"},"DisruptorBase":{"ScaleMin":"1.350000,1.350000,1.350000","ScaleMax":"1.350000,1.350000,1.350000"},"DisruptorDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"DisruptorPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"HighTemplarDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LiberatorBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LiberatorAGBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LiberatorPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LiberatorDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LiberatorSiegedDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LiberatorDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LocustFlyerBase":{"ScaleMin":"0.900000,0.900000,0.900000","ScaleMax":"0.900000,0.900000,0.900000"},"LocustFlyerDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LurkerDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OverlordTransportBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"OverlordTransportDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RavagerBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RavagerDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RavagerDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RavagerDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RavagerDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RavagerPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostDeathBlastBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostDeathEviscerateBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GhostPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"OverseerOversightAdditionBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"RepairDroneBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RepairDroneDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"UI_Screen_Numbers":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"WaterBloodSquibDefault":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AutoTurretDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorTerranBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorTerranPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorTerranDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorTerranDeathAcidBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorTerranDeathFireBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorTerranDeathTimeoutBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"InfestorTerranDeathRagdollBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ArchonLowBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"BanelingNestBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"SpireDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LarvaDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZergBuildingDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZergBuildingDeathLowBase":{"ScaleMin":"1.400000,1.400000,1.400000","ScaleMax":"1.400000,1.400000,1.400000"},"ZergBuildingPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TerranBuildingPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ProtossBuildingPortraitBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZergBuildingLargeDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ZergBuildingLargeDeathLowBase":{"ScaleMin":"1.800000,1.800000,1.800000","ScaleMax":"1.800000,1.800000,1.800000"},"OverseerCocoonBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"OverseerCocoonDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"LurkerCocoonBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"LurkerCocoonDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RavagerCocoonBase":{"ScaleMin":"1.200000,1.200000,1.200000","ScaleMax":"1.000000,1.000000,1.000000"},"RavagerCocoonDeathBase":{"ScaleMin":"1.200000,1.200000,1.200000","ScaleMax":"1.000000,1.000000,1.000000"},"BroodLordCocoonBase":{"ScaleMin":"0.850000,0.850000,0.850000","ScaleMax":"0.850000,0.850000,0.850000"},"BroodLordCocoonDeathBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ProtossBuildingBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ProtossBuildingBuildLargeBase":{"ScaleMin":"1.200000,1.200000,1.200000","ScaleMax":"1.200000,1.200000,1.200000"},"ProtossBuildingBuildSmallBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"DarkShrineBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"ShieldBatteryBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"PhotonCannonBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"PylonBuildBase":{"ScaleMin":"0.800000,0.800000,0.800000","ScaleMax":"0.800000,0.800000,0.800000"},"AssimilatorBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"CyberneticsCoreBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"FleetBeaconBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"ForgeBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"GatewayBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoboticsBayBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"RoboticsFacilityBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"StargateBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TemplarArchiveBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"TwilightCouncilBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"AssimilatorRichBuildBase":{"ScaleMin":"1.000000,1.000000,1.000000","ScaleMax":"1.000000,1.000000,1.000000"},"NexusBuildBase":{"ScaleMin":"1.200000,1.200000,1.200000","ScaleMax":"1.200000,1.200000,1.200000"}}
TERRAN_BODY_MODELS = set()
ZERG_BODY_MODELS = set()
def visual_race(rel):
    if rel.startswith("SCBW_01."): return "terran"
    if rel.startswith("SCBW_02."): return "zerg"
    return None
ZERG_VISUAL_KEEP = re.compile(r"fungal|parasiticbomb|blindingcloud|corrosivebile|darkswarm|plague|ensnare|creep(?!tumor)|tentacle|attackspike|groundcracks|webby|primal|mutant|collector|skin",re.I)
ZERG_VISUAL_SMALL = re.compile(r"burrow|unburrow|cocoon|egg|spawn|emerge|spine|spit|acid|tentacle|claw|swipe|squib|overhead|transfusion|consume|parasite|broodling",re.I)
VISUAL_KEEP = re.compile(r"portrait|icon|cursor|range|radius|sight|vision|scan|search|targeting|target.?area|area|aoe|indicator|reticle|telegraph|decal|nuke|nuclear|emp|irradiate|explosion|blast|splash|shockwave|sensor|selection|beam|cone", re.I)
VISUAL_SMALL = re.compile(r"placement|death|birth|warp|build|splat|lift.?off|land|thruster|engine|missile|projectile|muzzle|launch|impact|stimpack|heal|repair|lockdown|yamato|attack|weapon|shell|bullet|tracer|flame|grenade|morph|transform|cloak|matrix|restoration|opticflare", re.I)

def original_field(uid, key, seen=None):
    seen = set() if seen is None else seen
    if uid in seen: return None
    seen.add(uid)
    data = MODEL_ORIGINALS.get(uid)
    if data is None: return VANILLA_MODEL_SCALES.get(uid, {}).get(key)
    return data.get(key) or (original_field(data["parent"], key, seen) if data.get("parent") else VANILLA_MODEL_SCALES.get(uid, {}).get(key) or VANILLA_MODEL_SCALES.get("__DEFAULT__", {}).get(key))

def half_vector(value):
    if not value: return None
    parts = value.split(",")
    if len(parts) not in (1, 3) or not all(number(p) is not None for p in parts): return None
    return ",".join(scaled(p, .5) for p in parts)

def race_visual_model(e, rel):
    race = visual_race(rel)
    bodies = ZERG_BODY_MODELS if race=="zerg" else TERRAN_BODY_MODELS
    uid = e.get("id", "")
    row = {"id":uid, "file":rel, "type":"CModel", "changed":[], "unresolved":[]}
    VISUAL_AUDIT.append(row)
    if e.get("default") == "1" or VISUAL_KEEP.search(uid) or (race=="zerg" and ZERG_VISUAL_KEEP.search(uid)):
        row["status"] = "preserve template/UI/area/shared effect"
        return
    def field(key):
        child = e.find(key)
        return original_field(uid,key) or (child.get("value") if child is not None else None)
    if (VISUAL_SMALL.search(uid) or (race=="zerg" and ZERG_VISUAL_SMALL.search(uid))) and uid not in bodies:
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
    COUNTS[race+"_visual_models_patched"] += bool(row["changed"])
    COUNTS[race+"_visual_scale_unresolved"] += bool(row["unresolved"])

def collect_visual_originals(stage):
    MODEL_ORIGINALS.clear(); TERRAN_BODY_MODELS.clear(); ZERG_BODY_MODELS.clear(); VISUAL_AUDIT.clear()
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
                elif e.tag == "CActorUnit" and visual_race(path.relative_to(data).as_posix()):
                    bodies = ZERG_BODY_MODELS if visual_race(path.relative_to(data).as_posix())=="zerg" else TERRAN_BODY_MODELS
                    bodies.add(uid)
                    model = e.find("Model")
                    if model is not None and model.get("value"): bodies.add(model.get("value"))

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
            if visual_race(rel) and tag=="CActorUnit":
                flag=e.find("UnitFlags[@index='ShowBlobShadow']")
                if flag is None: flag=ET.SubElement(e,"UnitFlags",index="ShowBlobShadow")
                flag.set("value","0")
                if not any(x.get("Terms")=="ActorCreation" and x.get("Send")=="SetCastShadows" for x in e.findall("On")):
                    ET.SubElement(e,"On",Terms="ActorCreation",Send="SetCastShadows")
                COUNTS[visual_race(rel)+"_actor_shadow_records"]+=1
    elif tag=="CModel":
        if visual_race(rel):
            race_visual_model(e,rel)
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
                if visual_race(rel) and e.get("id") and e.tag.startswith(("CActor","CEffect","CAbil","CUnit","CWeapon","CUpgrade","CBehavior","CAccumulator")):
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


# Reassert explicit transformed BW vital fields in the final Multi layer.
# Copy already-scaled values, never scale them a second time.
def final_bw_vitals(stage):
    records = {}
    for mod in MODS[1:]:
        base = stage/mod/"Base.SC2Data"
        manifest = xmlread(base/"GameData.xml").getroot()
        for entry in manifest:
            rel = entry.get("path","")
            if not rel.startswith("GameData/") or not rel.endswith(".xml"): continue
            path = base/rel
            if not path.is_file(): continue
            root = xmlread(path).getroot()
            if root.tag != "Catalog": continue
            for e in root:
                uid = e.get("id","")
                if e.tag != "CUnit" or not uid or e.get("default") == "1": continue
                if not scope(e,rel[len("GameData/"):]): continue
                fields = records.setdefault(uid,{})
                for key in VITALS:
                    if key in e.attrib and number(e.get(key)) is not None:
                        fields[key] = e.get(key)
                    child = e.find(key)
                    if child is not None and number(child.get("value")) is not None:
                        fields[key] = child.get("value")
    expected = {"MarineSCBW":"4","ZerglingSCBW":"3.5"}
    for uid,hp in expected.items():
        if number(records.get(uid,{}).get("LifeMax")) != number(hp):
            raise ValueError("BW health build mismatch: "+uid+" expected "+hp)
    out = ET.Element("Catalog")
    for uid,fields in sorted(records.items()):
        if not fields: continue
        e = ET.SubElement(out,"CUnit",id=uid)
        for key,value in sorted(fields.items()): put(e,key,value)
    base = stage/MODS[2]/"Base.SC2Data"
    path = "GameData/MiniCraftBWFinalVitals.xml"
    xmlwrite(ET.ElementTree(out),base/path)
    add_include(base,path)
    return {"BW":{uid:records[uid]["LifeMax"] for uid in expected},
            "BW_vital_records":len(out),"final_catalog":path}

def local_dependency(name):
    # Match the upstream custom-mod path separator convention, without the
    # upstream Battle.net identity (which could load unmodified Core).
    return "file:Mods\\MiniCraft-EVO\\"+name


# The pinned upstream uses H2CS v8: 44-byte prefix, uint32 dependency
# count, NUL-terminated UTF-8 dependency strings, then localized metadata.
# The Editor can read these before XML DocumentInfo, so both must agree.
def header_dependencies(raw):
    if len(raw)<48 or raw[:4]!=b"H2CS" or int.from_bytes(raw[4:8],"little")!=8:
        raise ValueError("Unsupported EVO DocumentHeader format")
    count=int.from_bytes(raw[44:48],"little")
    if count>128: raise ValueError("Unexpected EVO dependency count")
    pos=48
    refs=[]
    for _ in range(count):
        end=raw.find(b"\x00",pos)
        if end<0: raise ValueError("Truncated EVO DocumentHeader dependency")
        refs.append(raw[pos:end].decode("utf-8"))
        pos=end+1
    return refs,pos

def replace_header_dependencies(raw, before, after):
    refs,end=header_dependencies(raw)
    if refs!=before:
        raise ValueError("Original DocumentHeader and DocumentInfo dependencies disagree: "+str(refs))
    result=raw[:44]+len(after).to_bytes(4,"little")+b"".join(x.encode("utf-8")+b"\x00" for x in after)+raw[end:]
    check,tail=header_dependencies(result)
    if check!=after or result[tail:]!=raw[end:]:
        raise ValueError("DocumentHeader rewrite verification failed")
    return result

def verify_trigger_chain(stage, src):
    core = stage/MODS[1]
    multi = stage/MODS[2]
    for folder in (core,multi):
        manifest = xmlread(folder/"ComponentList.SC2Components").getroot()
        if not any(x.get("Type")=="trig" and x.text=="Triggers" for x in manifest):
            raise ValueError("Missing trigger component: "+str(folder))
        original = src/folder.name/"Triggers"
        if (folder/"Triggers").read_bytes() != original.read_bytes():
            raise ValueError("Trigger source changed: "+str(folder))
    lib = xmlread(core/"Triggers").getroot().find("./Library[@Id='SCEV']")
    if lib is None or lib.find("LibraryShareToMods") is None:
        raise ValueError("Core SCEV library is missing or not shared to mods")
    for tag,uid in (("FunctionDef","3EC1A15D"),("FunctionDef","3FB1045E"),("PresetValue","F665AC2C")):
        if lib.find(".//Element[@Type='"+tag+"'][@Id='"+uid+"']") is None:
            raise ValueError("Missing Core trigger definition: "+uid)
    core_base = core/"Base.SC2Data"
    multi_base = multi/"Base.SC2Data"
    for p in (core_base/"LibSCEV.galaxy",core_base/"LibSCEV_h.galaxy",multi_base/"Lib8FCB4FA8.galaxy",multi_base/"Lib8FCB4FA8_h.galaxy"):
        if not p.is_file() or not p.stat().st_size:
            raise ValueError("Missing Galaxy library: "+str(p))
    script = (multi_base/"Lib8FCB4FA8.galaxy").read_text(encoding="utf-8-sig")
    for token in ('include "LibSCEV"',"libSCEV_InitVariables();","libSCEV_gf_SCEvoFeatureActive(libSCEV_ge_SCEvoFeatures_MissChance)","libSCEV_gf_SCEvoActivateFeature(libSCEV_ge_SCEvoFeatures_MissChance, true)"):
        if token not in script:
            raise ValueError("Broken Multi initialization: "+token)
    if re.search(r"if\s*\(\s*\(\s*==",script):
        raise ValueError("Broken empty comparison in Multi initialization")
    return {"shared_library":"SCEV","multi_library":"8FCB4FA8","source_triggers_preserved":True,"initialization_symbols_present":True}


def split_dependency(ref):
    parts=ref.split(",file:",1)
    if ref.startswith("file:"): return "",ref[5:].replace("\\","/").lower()
    if ref.startswith("bnet:"): return parts[0],parts[1].replace("\\","/").lower() if len(parts)==2 else ""
    raise ValueError("Unsupported dependency: "+ref)

def validate_dependency_list(mod,refs):
    idx=MODS.index(mod)
    standard=("liberty","void","voidmulti")[idx]
    if len(refs)!=(1 if idx==0 else 2):
        raise ValueError("Unexpected dependency count in "+mod)
    bnet,local=split_dependency(refs[0])
    standard_title=("liberty (mod)","void (mod)","void multi (mod)")[idx]
    if not bnet.lower().startswith("bnet:"+standard_title+"/") or (local and local!="mods/"+standard+".sc2mod"):
        raise ValueError("Unexpected standard dependency in "+mod+": "+refs[0])
    if idx==0: return False
    bnet,local=split_dependency(refs[1])
    dep=MODS[idx-1]
    expected="mods/minicraft-evo/"+dep.lower()
    title=("minicraft evo assets","minicraft evo core")[idx-1]
    if local and local!=expected:
        raise ValueError("Wrong local dependency in "+mod+": "+refs[1])
    if not bnet and local!=expected:
        raise ValueError("Missing local dependency in "+mod)
    if bnet:
        # Never silently reconnect the upstream author's published files.
        if not bnet.lower().startswith("bnet:"+title+"/"):
            raise ValueError("Unexpected published dependency in "+mod+"; expected "+title+": "+bnet)
        if bnet.rsplit("/",1)[-1] in ("444267","444268"):
            raise ValueError("Original EVO publication is not a MiniCraft dependency")
    return bool(bnet)

def preserve_editor_metadata(stage,previous):
    status={}
    for mod in MODS:
        dest=stage/mod
        old=previous/mod
        source=old/"DocumentInfo"
        header=old/"DocumentHeader"
        if previous.exists():
            if not source.is_file() or not header.is_file():
                raise ValueError("Existing component metadata missing: "+str(old))
            refs=[e.text or "" for e in xmlread(source).getroot().findall("./Dependencies/Value")]
            remote=validate_dependency_list(mod,refs)
            binary_refs,_=header_dependencies(header.read_bytes())
            if binary_refs!=refs:
                raise ValueError("Saved editor header/XML disagree; reopen and save component before updating: "+str(old))
            # Keep the editor's exact metadata pair, including opaque header fields.
            shutil.copy2(source,dest/"DocumentInfo")
            shutil.copy2(header,dest/"DocumentHeader")
            if remote and not split_dependency(refs[1])[1]:
                before=refs[:]
                refs[1]+=","+local_dependency(MODS[MODS.index(mod)-1])
                tree=xmlread(dest/"DocumentInfo")
                tree.getroot().findall("./Dependencies/Value")[1].text=refs[1]
                (dest/"DocumentHeader").write_bytes(replace_header_dependencies(header.read_bytes(),before,refs))
                xmlwrite(tree,dest/"DocumentInfo")
            for old_strings in old.glob("*.SC2Data/LocalizedData/GameStrings.txt"):
                new_strings=dest/old_strings.relative_to(old)
                if not new_strings.is_file(): continue
                old_lines=old_strings.read_text(encoding="utf-8-sig").splitlines()
                doc_lines=[x for x in old_lines if x.startswith("DocInfo/")]
                if not doc_lines: continue
                new_lines=new_strings.read_text(encoding="utf-8-sig").splitlines()
                keys={x.partition("=")[0] for x in doc_lines}
                new_lines=[x for x in new_lines if x.partition("=")[0] not in keys]
                new_strings.write_text("\n".join(new_lines+doc_lines)+"\n",encoding="utf-8-sig")
            status[mod]={"editor_metadata_preserved":True,"published_dependency":remote,"dependencies":refs}
        else:
            refs=[e.text or "" for e in xmlread(dest/"DocumentInfo").getroot().findall("./Dependencies/Value")]
            status[mod]={"editor_metadata_preserved":False,"published_dependency":validate_dependency_list(mod,refs),"dependencies":refs}
    return status

def write_publish_guide(stage,out,status):
    lines=["MINICRAFT EVO - Battle.net publishing checklist","",
           "Publish through Galaxy Editor while signed into your own account.","",
           "1. Open Assets, publish as MiniCraft EVO Assets, then save the component document in place.",
           "2. Open Core. Double-click its blank Blizzard dependency name, select your published MiniCraft EVO Assets, keep its local file, save in place, then publish as MiniCraft EVO Core.",
           "3. Open Multi. Double-click its blank Blizzard dependency name, select your published MiniCraft EVO Core, keep its local file, save in place, then publish as MiniCraft EVO.",
           "4. For a separate map, attach the published MiniCraft EVO and any other required published dependencies.",
           "", "Use the same region and account. Do not select the original SCEvo publications.",
           "Save the component folders themselves; separate packed Save As files are not imported by the updater.",
           "A published dependency in this report does not verify online publication or availability.",
           "The updater preserves saved component metadata; Battle.net publication itself is manual.",""]
    for mod in MODS:
        lines.append(str(out/mod/"ComponentList.SC2Components"))
        lines.extend("  "+x for x in status[mod]["dependencies"])
        lines.append("")
    (stage/"EVO-PUBLISH.txt").write_text("\n".join(lines)+"\n",encoding="utf-8-sig")
    # Explorer shortcuts are plain cmd files; paths are relative to the installed folder.
    for idx,mod in enumerate(MODS,1):
        label=("Assets","Core","Multi")[idx-1]
        (stage/("Open-"+str(idx)+"-"+label+".cmd")).write_text('@echo off\r\nstart "" explorer.exe /select,"%~dp0'+mod+'\\ComponentList.SC2Components"\r\n',encoding="ascii",newline="")

def verify_generated(stage):
    # Both editor metadata formats must agree, including standard dependencies.
    for mod in MODS:
        root=xmlread(stage/mod/"DocumentInfo").getroot()
        refs=[e.text or "" for e in root.findall("./Dependencies/Value")]
        binary_refs,_=header_dependencies((stage/mod/"DocumentHeader").read_bytes())
        if binary_refs!=refs:
            raise ValueError("Header/XML dependency mismatch in "+mod)
        validate_dependency_list(mod,refs)
    base = stage/MODS[2]/"Base.SC2Data"
    includes = [x.get("path") for x in xmlread(base/"GameData.xml").getroot()]
    if includes[-2:] != ["GameData/MiniCraftSC2.xml","GameData/MiniCraftBWFinalVitals.xml"]:
        raise ValueError("MiniCraft data catalogs must load last")
    root = xmlread(base/"GameData/MiniCraftSC2.xml").getroot()
    result = {}
    for uid,hp in (("Marine","4.5"),("Zergling","3.5")):
        e = root.find("./CUnit[@id='"+uid+"']/LifeMax")
        if e is None or number(e.get("value")) != number(hp):
            raise ValueError("SC2 health build mismatch: "+uid)
        result[uid] = e.get("value")
    return result

def doc(stage,mod):
    path=stage/mod/"DocumentInfo";t=xmlread(path);root=t.getroot()
    deps=root.find("Dependencies")
    before=[e.text or "" for e in root.findall("./Dependencies/Value")]
    if deps is not None:
        for e in deps:
            for name in MODS:
                if name in (e.text or ""):
                    e.text=local_dependency(name)
    if mod==MODS[2]:
        flags=root.find("Flags")
        if flags is None:flags=ET.SubElement(root,"Flags")
        if not any(e.text=="ExtensionMod" for e in flags):ET.SubElement(flags,"Value").text="ExtensionMod"
        mt=root.find("ModType")
        if mt is None:mt=ET.SubElement(root,"ModType")
        if mt.find("Value") is None:ET.SubElement(mt,"Value")
        mt.find("Value").text="Gameplay"
    after=[e.text or "" for e in root.findall("./Dependencies/Value")]
    header=stage/mod/"DocumentHeader"
    header.write_bytes(replace_header_dependencies(header.read_bytes(),before,after))
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
    e=ET.fromstring('<CModel id="HydraliskSCBWWeapon@Impact"><ScaleMin value="2,2,2"/><ScaleMax value="2,2,2"/></CModel>')
    patch_record(e,"SCBW_02.Zerg/h.xml",set(),set())
    assert e.find("ScaleMin").get("value")=="1,1,1"
    e=ET.fromstring('<CModel id="DefilerSCBWDarkSwarm@Impact"><ScaleMin value="2,2,2"/></CModel>')
    patch_record(e,"SCBW_02.Zerg/d.xml",set(),set())
    assert e.find("ScaleMin").get("value")=="2,2,2"
    e=ET.fromstring('<CActorUnit id="ZerglingSCBW" unitName="ZerglingSCBW"/>')
    patch_record(e,"SCBW_02.Zerg/z.xml",set(),{"ZerglingSCBW"})
    assert e.find("UnitFlags").get("value")=="0"
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/"tokens.xml"
        p.write_text('<Catalog><CUnit id="X"><?token id="Race" value="Terran"?><LifeMax value="40"/></CUnit></Catalog>',encoding="utf-8")
        tree=xmlread(p)
        patch_record(tree.getroot()[0],"SCBW_01.Terran/test.xml",set(),set())
        xmlwrite(tree,p)
        assert '<?token id="Race" value="Terran"?>' in p.read_text(encoding="utf-8")
        assert tree.getroot()[0].find("LifeMax").get("value")=="4"
    assert local_dependency(MODS[1]).replace(chr(92),"/")=="file:Mods/MiniCraft-EVO/SCEvo_Core.SC2Mod"
    old=["bnet:Void Multi (Mod)/0.0/999,file:Mods/VoidMulti.SC2Mod",r"bnet:SCEvo_Core/0.0/444268,file:Mods\SC Evolution Complete\SCEvo_Core.SC2Mod"]
    new=[old[0],local_dependency(MODS[1])]
    prefix=b"H2CS"+(8).to_bytes(4,"little")+bytes(36)
    tail=b"\x0c\x00\x00\x00\x0c\x00DocInfo/Name"
    raw=prefix+len(old).to_bytes(4,"little")+b"".join(x.encode("utf-8")+b"\x00" for x in old)+tail
    result=replace_header_dependencies(raw,old,new)
    refs,end=header_dependencies(result)
    assert refs==new and result[end:]==tail
    try:
        replace_header_dependencies(raw,new,new)
    except ValueError:
        pass
    else:
        raise AssertionError("Header/XML mismatch must fail")

    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)/"StarCraft II"
        root.mkdir()
        (root/"SC2Data").mkdir()
        (root/"Versions").mkdir()
        assert game_root(root)==root.resolve()
        assert game_root(root/"Mods")==root.resolve()
        assert not (root/"Mods").exists()
        assert game_root(Path(tmp)/"unrelated") is None

    standard="bnet:Void (Mod)/0.0/999,file:Mods/Void.SC2Mod"
    local=local_dependency(MODS[0])
    remote="bnet:MiniCraft EVO Assets/0.0/123456,"+local
    assert not validate_dependency_list(MODS[1],[standard,local])
    assert validate_dependency_list(MODS[1],[standard,remote])
    assert validate_dependency_list(MODS[1],[standard,"bnet:MiniCraft EVO Assets/0.0/123456"])
    for bad in ("bnet:SCEvo_Assets/0.0/444267,"+local,"bnet:MiniCraft EVO Assets/0.0/444267,"+local,"file:Mods/SC Evolution Complete/SCEvo_Assets.SC2Mod"):
        try: validate_dependency_list(MODS[1],[standard,bad])
        except ValueError: pass
        else: raise AssertionError("Unexpected dependency accepted: "+bad)
    with tempfile.TemporaryDirectory() as tmp:
        old=Path(tmp)/"old";new=Path(tmp)/"new"
        for idx,mod in enumerate(MODS):
            std=("bnet:Liberty (Mod)/0.0/999,file:Mods/Liberty.SC2Mod",standard,"bnet:Void Multi (Mod)/0.0/999,file:Mods/VoidMulti.SC2Mod")[idx]
            dep=[std]+([remote] if idx==1 else ["bnet:MiniCraft EVO Core/0.0/123457"] if idx==2 else [])
            for folder in (old,new):
                d=folder/mod;d.mkdir(parents=True)
                root=ET.Element("DocInfo");deps=ET.SubElement(root,"Dependencies")
                for value in dep: ET.SubElement(deps,"Value").text=value
                ET.ElementTree(root).write(d/"DocumentInfo",encoding="utf-8")
                raw=prefix+len(dep).to_bytes(4,"little")+b"".join(x.encode("utf-8")+b"\x00" for x in dep)+tail
                (d/"DocumentHeader").write_bytes(raw)
            (old/mod/"DocumentHeader").write_bytes(raw+b"editor metadata")
        status=preserve_editor_metadata(new,old)
        assert status[MODS[1]]["published_dependency"] and status[MODS[2]]["published_dependency"]
        assert status[MODS[2]]["dependencies"][1].endswith(","+local_dependency(MODS[1]))
        assert header_dependencies((new/MODS[2]/"DocumentHeader").read_bytes())[0]==status[MODS[2]]["dependencies"]
        assert (new/MODS[1]/"DocumentHeader").read_bytes()==(old/MODS[1]/"DocumentHeader").read_bytes()
        write_publish_guide(new,old,status)
        assert (new/"EVO-PUBLISH.txt").is_file()
        assert (new/"Open-1-Assets.cmd").is_file()
    COUNTS.clear(); VISUAL_AUDIT.clear()
    print("EVO transform self-tests passed.")


def game_root(value):
    if not value: return None
    p=Path(os.path.expandvars(str(value).strip().strip('"'))).expanduser()
    if p.name.lower()=="mods": p=p.parent
    if p.is_file(): p=p.parent
    for root in (p,p.parent):
        if (root/"SC2Data").is_dir() and ((root/"Versions").is_dir() or (root/"Support64").is_dir() or (root/"Support").is_dir()):
            return root.resolve()
    return None

def locate_mods(explicit=None, remember=None):
    # A real installation need not have a Mods directory yet.
    candidates=[]
    if explicit: candidates.append(explicit)
    if remember and remember.is_file():
        candidates.append(remember.read_text(encoding="utf-8-sig").strip())
    for env in ("ProgramFiles(x86)","ProgramFiles","ProgramW6432"):
        if os.environ.get(env): candidates.append(Path(os.environ[env])/"StarCraft II")
    if os.name=="nt":
        import winreg
        for hive in (winreg.HKEY_LOCAL_MACHINE,winreg.HKEY_CURRENT_USER):
            for view in (winreg.KEY_WOW64_32KEY,winreg.KEY_WOW64_64KEY):
                for key in (r"SOFTWARE\Blizzard Entertainment\StarCraft II",r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StarCraft II"):
                    try:
                        with winreg.OpenKey(hive,key,0,winreg.KEY_READ|view) as reg:
                            for name in ("InstallPath","InstallLocation","GamePath"):
                                try: candidates.append(winreg.QueryValueEx(reg,name)[0])
                                except OSError: pass
                    except OSError: pass
        for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            for sub in ("StarCraft II",r"Games\StarCraft II",r"Program Files (x86)\StarCraft II",r"Program Files\StarCraft II"):
                candidates.append(Path(drive+":\\")/sub)
    for value in candidates:
        root=game_root(value)
        if root is not None:
            mods=root/"Mods"
            mods.mkdir(exist_ok=True)
            print("StarCraft II Mods:",mods,flush=True)
            return mods
        if explicit and value==explicit:
            print("Invalid explicit game path:",value,flush=True)
    while True:
        try: value=input("Enter StarCraft II installation folder (or Mods folder): ").strip().strip('"')
        except EOFError: raise SystemExit("No StarCraft II installation found. Enter the actual game installation path.")
        if not value: raise SystemExit("No StarCraft II installation selected.")
        root=game_root(value)
        if root is None:
            print("Not a StarCraft II installation. Choose the folder containing SC2Data and Versions/Support64.",flush=True)
            continue
        mods=root/"Mods"
        mods.mkdir(exist_ok=True)
        print("StarCraft II Mods:",mods,flush=True)
        return mods


def expose_output(out,launcher_home):
    """A Windows folder shortcut, not a second copy or relocated dependency."""
    import subprocess
    home=Path(launcher_home).resolve()
    if not home.is_dir(): return
    link=home/"MiniCraft-EVO.lnk"
    env=dict(os.environ,MINICRAFT_SHORTCUT_PATH=str(link),MINICRAFT_SHORTCUT_TARGET=str(out))
    script="""
$ErrorActionPreference = 'Stop'
$shell = New-Object -ComObject WScript.Shell
$path = $env:MINICRAFT_SHORTCUT_PATH
$target = $env:MINICRAFT_SHORTCUT_TARGET
$link = $shell.CreateShortcut($path)
if ((Test-Path -LiteralPath $path) -and ($link.TargetPath -ne $target)) {
    throw 'An existing shortcut points elsewhere; leaving it unchanged.'
}
$link.TargetPath = $target
$link.WorkingDirectory = $target
$link.Description = 'MiniCraft EVO installed mods and publishing tools'
$link.Save()
"""
    try:
        subprocess.run(["powershell.exe","-NoProfile","-NonInteractive","-Command",script],env=env,check=True,timeout=30)
        if not link.is_file(): raise OSError("Shortcut file was not created")
        print("Easy access:",link)
    except (OSError,subprocess.SubprocessError) as exc:
        print("Shortcut creation skipped (build is intact):",exc)
        print("Open the installed folder directly:",out)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--source",type=Path)
    p.add_argument("--mods",type=Path)
    p.add_argument("--remember-mods",type=Path)
    p.add_argument("--open-output",action="store_true")
    p.add_argument("--mini",type=Path,default=Path(__file__).resolve().parents[1]/"Build-MiniCraft.py")
    args=p.parse_args();selftest()
    if args.check:return
    if not args.source:p.error("--source required")
    src=args.source.resolve()
    mods=locate_mods(args.mods,args.remember_mods)
    if (src/"SC Evo Complete").is_dir():src=src/"SC Evo Complete"
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
        health_check=final_bw_vitals(stage)
        for mod in MODS:doc(stage,mod)
        inv["publication"]=preserve_editor_metadata(stage,out)
        write_publish_guide(stage,out,inv["publication"])
        health_check["SC2"]=verify_generated(stage)
        inv["health_check"]=health_check
        inv["trigger_check"]=verify_trigger_chain(stage,src)
        license_path=src.parent/"LICENSE"
        if not license_path.is_file():raise SystemExit("Upstream LICENSE missing")
        shutil.copy2(license_path,stage/"LICENSE-SCEvo.txt")
        inv["transform_counts"]=dict(COUNTS)
        inv["terran_record_audit"]=[r for r in VISUAL_AUDIT if visual_race(r["file"])=="terran"]
        inv["zerg_record_audit"]=[r for r in VISUAL_AUDIT if visual_race(r["file"])=="zerg"]
        (stage/"EVO-audit.json").write_text(json.dumps(inv,indent=2,ensure_ascii=False),encoding="utf-8")
        (stage/"MINICRAFT-EVO.json").write_text(json.dumps({"source":REV,"version":"0.1.6-preview"},indent=2),encoding="utf-8")
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
    if args.remember_mods:
        args.remember_mods.parent.mkdir(parents=True,exist_ok=True)
        args.remember_mods.write_text(str(mods),encoding="utf-8")
    print("Built:",out/MODS[2]/"ComponentList.SC2Components")
    print("Verified generated XML health:",inv["health_check"])
    print("Verified trigger source and shared Core library:",inv["trigger_check"])
    print("Verified all three DocumentHeader and DocumentInfo dependency lists match.")
    print("Core dependency:",out/MODS[1])
    print("Battle.net publishing guide:",out/"EVO-PUBLISH.txt")
    for mod in MODS:
        print("Publication metadata:",mod,inv["publication"][mod])
    print("Open only the Built path above, NOT the upstream or cache copy.")
    print("Inventory:",inv["counts"])
    print("Transform:",dict(COUNTS))
    missing=[race+"/"+group+"/"+name for race,g in inv["crosswalk"].items() for group,items in g.items() for name,ids in items.items() if not ids]
    print("Unmapped canonical names (see audit):",missing)
    print("Editor and actual game still require validation. Close editor before rebuild.")
    if args.open_output and os.name=="nt":
        home=os.environ.get("MINICRAFT_LAUNCHER_HOME")
        if home: expose_output(out,home)
        import subprocess
        entry=out/MODS[2]/"ComponentList.SC2Components"
        try: subprocess.Popen(["explorer.exe","/select,"+str(entry)])
        except OSError as exc: print("Explorer could not open; use Built path above:",exc)
if __name__=="__main__":main()
