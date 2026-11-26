# MiniCraft EVO — v0.1.6 preview

Separate local derivative of SCEvoComplete at commit 773c8e8ae8828121e8f37bb74ab82ceb761a45bc. MIT license retained. Original MiniCraft, upstream, and published mods are not edited.

## Build
Download the unified `../Build-MiniCraft.bat` once, close Galaxy Editor, and double-click it. Classic and EVO are installed/updated automatically. Enter the installed StarCraft II **Mods folder** only if no saved or standard installation path is available. Git for Windows and Python 3 required. The launcher fetches current MiniCraft source and a pinned EVO checkout; the upstream repository is large, allow several GB. It caches source and remembers the Mods path. It builds a new local tree Mods/MiniCraft-EVO containing Assets, Core, Multi. Open SCEvo_Multi.SC2Mod/ComponentList.SC2Components in the editor; check dependencies resolve to the local copies, save and test. Publishing requires publishing local dependencies and configuring Battle.net references; do not overwrite original EVO. Build backs up an existing owned output directory before replacing it. No ZIP.

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

## Core trigger recovery (0.1.3 preview)

Close Galaxy Editor without saving a broken regenerated script, then run the existing unified launcher. The builder verifies that the Mods directory belongs to the game installation, uses local-only Core/Assets references in the upstream custom-mod path format, preserves XML token processing instructions, and verifies shared SCEV library definitions and unmodified trigger sources before replacing the previous build. Explorer selects the freshly generated Multi ComponentList.SC2Components after success. Open that document, not an older separately saved packed SC2Mod. The output audit includes trigger_check and health_check. The actual Editor dependency resolver and compilation remain untested; local dependencies still require publishing/configuring separate dependencies for Battle.net.

## Binary dependency header recovery (0.1.4 preview)

The original H2CS version-8 DocumentHeader contains a second dependency list. Rewrite it alongside DocumentInfo, verifying the original lists match and preserving all trailing localized metadata bytes. Verify the generated XML/header lists agree for Assets, Core, and Multi, with no original custom Battle.net dependencies. Round-trip layout checked against all three pinned upstream header files. The actual Galaxy Editor resolver and compilation are still untested. Do not save a document after a missing-dependency warning; reopen the freshly generated Multi document after updating.

## Installation path recovery (0.1.5 preview)

The launcher now delegates installation discovery to Python (saved path, Windows registry, standard folders and common drive paths). It accepts the game root or Mods path, creates Mods if absent, and asks for the actual game installation folder only when discovery fails. The remembered path is written in UTF-8 after successful generation. Modified tracked upstream cache files are backed up as a binary Git diff before restoring the pinned checkout; never open the upstream cache in the editor. The successful build opens Explorer at the generated Multi component file. Windows execution and Galaxy Editor loading remain unverified.

## Battle.net publication workflow (0.1.6 preview)

After updating with the same launcher, open the installed `Mods/MiniCraft-EVO` folder. `Open-1-Assets.cmd`, `Open-2-Core.cmd`, and `Open-3-Multi.cmd` select their component documents in Explorer. `EVO-PUBLISH.txt` shows the exact local paths and dependency status. Publish Assets as **MiniCraft EVO Assets**, Core as **MiniCraft EVO Core**, and Multi as **MiniCraft EVO** in the same region/account. Bind Core to your published Assets and Multi to your published Core in the Blizzard dependency column. Keep the local file override and save the component documents in place after editing/publishing. Do not use the original SCEvo online publications. Subsequent rebuilds preserve the saved DocumentInfo/DocumentHeader pair and DocInfo localization fields, restoring a missing local override when needed; unexpected dependency layouts or unsupported saved headers fail safely before replacing the previous build. The strict title checks intentionally require the names above. Separate packed Save As documents are not imported. The builder cannot confirm remote publication, sign in, or publish; the editor's saved metadata format and online publication still require real-world validation. The current audit records publication dependencies, not a guarantee of account-level publication state.
