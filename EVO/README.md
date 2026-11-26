# MiniCraft EVO — v0.1.1 preview

Separate local derivative of SCEvoComplete at commit 773c8e8ae8828121e8f37bb74ab82ceb761a45bc. MIT license retained. Original MiniCraft, upstream, and published mods are not edited.

## Build
Download the unified `../Build-MiniCraft.bat` once, close Galaxy Editor, choose option 2 (EVO), and enter the installed StarCraft II **Mods folder** when prompted. Git for Windows and Python 3 required. The launcher fetches current MiniCraft source and a pinned EVO checkout; the upstream repository is large, allow several GB. It caches source and remembers the Mods path. It builds a new local tree Mods/MiniCraft-EVO containing Assets, Core, Multi. Open SCEvo_Multi.SC2Mod/ComponentList.SC2Components in the editor; check dependencies resolve to the local copies, save and test. Publishing requires publishing local dependencies and configuring Battle.net references; do not overwrite original EVO. Build backs up an existing owned output directory before replacing it. No ZIP.

## Inventory
The builder scans all Core and Multi XML catalogs, including nested race files, common and miscellaneous definitions. EVO-audit.json records actual unit/ability/upgrade/weapon/effect/actor/model/behavior/accumulator/footprint IDs, parent and source file, and a canonical BW unit/building crosswalk. It reports missing names rather than silently inventing IDs. Counts include variants, templates, helpers and do not equal gameplay roster counts.

## Transform
BW explicit life/shield/armor/regeneration and damage fields 10%; unit actor and collision size 50%; known building footprints use MiniCraft definitions; gas footprint preserved; negative Food 50%, positive supply unchanged; race ceiling 300; explicit training/research/build time and mineral/gas cost 50%. Damage formula minimum 0.05; selected upgrade templates and recovery effects. Existing SC2 MiniCraft delta catalogs included after EVO SC2 changes. Original EVO race selection and AI are retained. Existing MiniCraft AI is not attached to EVO.

## Not verified
This is an experimental source builder, not a game-tested release. Inherited base models, all custom script-driven damage/recovery/armor, upgrade formula evaluation, paid morphs without explicit costs, build time sourced from custom data, special footprints and add-on spacing, all actor shadow/placement/skin variants, starting economy, custom race supply and AI, and compatibility of SC2 MiniCraft overrides with EVO balance require editor/game checks. Data audits are coverage checks, not evidence of runtime functionality. The builder deliberately reports unresolved mappings rather than claiming complete coverage. No automatic online publication.

Upstream: https://github.com/TeamKoprulu/SCEvoComplete/tree/773c8e8ae8828121e8f37bb74ab82ceb761a45bc

## Source audit and targeted corrections

[109-file source audit and BW crosswalk](SOURCE-AUDIT.md). 98/98 canonical unit/building names found with exact IDs; source inventory includes additional states, missiles and helpers. Explicitly handle accumulator damage (including Yamato and nuclear strike), Defensive Matrix capacity, Feedback energy-derived damage, Medic/SCV default-Life healer, Shield Battery, and Life-paid skills. Tests are included but not executed in Galaxy Editor or Python in this environment. Production morphs using target BuildTime inherit that scaled value; explicit morph transition costs/times still require checks.

## Terran visual pass (2026-11-26)

The builder audits Terran XML records at build time, scales independently identified model-space effects from explicit/inherited numeric values, and adds unit shadow controls. The `terran_record_audit` array in EVO-audit.json records changed, preserved, and unresolved entries. Range/area indicators, portraits, and ambiguous shared FX are preserved; unknown inheritance and runtime attachment scaling still need testing. No actual Galaxy Editor or gameplay validation yet.

## Zerg visual pass (2026-11-26)

Zerg now uses the same independent visual model and shadow pass as Terran, with separate `zerg_record_audit` output. Preserve creep, Dark Swarm, Plague, Ensnare, area indicators and uncertain attached models; exclude body models from duplicate scaling. Actual counts and unresolved inheritance are recorded during local build; no gameplay or editor validation yet.
