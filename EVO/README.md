# MiniCraft EVO — v0.1.0 preview

Separate local derivative of SCEvoComplete at commit 773c8e8ae8828121e8f37bb74ab82ceb761a45bc. MIT license retained. Original MiniCraft, upstream, and published mods are not edited.

## Build
Download `Build-MiniCraft-EVO.bat` once, close Galaxy Editor, and drag the installed StarCraft II **Mods folder** onto it (or enter its path). Git for Windows and Python 3 required. The launcher fetches current MiniCraft source and a pinned EVO checkout; the upstream repository is large, allow several GB. It caches source and remembers the Mods path. It builds a new local tree Mods/MiniCraft-EVO containing Assets, Core, Multi. Open SCEvo_Multi.SC2Mod/ComponentList.SC2Components in the editor; check dependencies resolve to the local copies, save and test. Publishing requires publishing local dependencies and configuring Battle.net references; do not overwrite original EVO. Build backs up an existing owned output directory before replacing it. No ZIP.

## Inventory
The builder scans all Core and Multi XML catalogs, including nested race files, common and miscellaneous definitions. EVO-audit.json records actual unit/ability/upgrade/weapon/effect/actor/model/behavior/accumulator/footprint IDs, parent and source file, and a canonical BW unit/building crosswalk. It reports missing names rather than silently inventing IDs. Counts include variants, templates, helpers and do not equal gameplay roster counts.

## Transform
BW explicit life/shield/armor/regeneration and damage fields 10%; unit actor and collision size 50%; known building footprints use MiniCraft definitions; gas footprint preserved; negative Food 50%, positive supply unchanged; race ceiling 300; explicit training/research/build time and mineral/gas cost 50%. Damage formula minimum 0.05; selected upgrade templates and recovery effects. Existing SC2 MiniCraft delta catalogs included after EVO SC2 changes. Original EVO race selection and AI are retained. Existing MiniCraft AI is not attached to EVO.

## Not verified
This is an experimental source builder, not a game-tested release. Inherited base models, all custom script-driven damage/recovery/armor, upgrade formula evaluation, paid morphs without explicit costs, build time sourced from custom data, special footprints and add-on spacing, all actor shadow/placement/skin variants, starting economy, custom race supply and AI, and compatibility of SC2 MiniCraft overrides with EVO balance require editor/game checks. Data audits are coverage checks, not evidence of runtime functionality. The builder deliberately reports unresolved mappings rather than claiming complete coverage. No automatic online publication.

Upstream: https://github.com/TeamKoprulu/SCEvoComplete/tree/773c8e8ae8828121e8f37bb74ab82ceb761a45bc
