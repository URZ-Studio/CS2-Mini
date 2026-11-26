# SCEvo 5.0.15 reference audit

Source: https://github.com/TeamKoprulu/SCEvoComplete/tree/773c8e8ae8828121e8f37bb74ab82ceb761a45bc

These twelve upstream XML delta catalogs are vendored verbatim for offline audit, not included in the playable mod. The upstream data is not the full current ladder catalog. An upstream-only ID does not imply missing MiniCraft content: many are decor, UI, or inherited definitions. Matching IDs do not establish field-level correctness. Do not copy upstream balance over the intended MiniCraft multipliers automatically.

| Catalog | Upstream IDs | Shared IDs | Upstream-only IDs |
|---|---:|---:|---:|
| AbilData.xml | 36 | 8 | 28 |
| ActorData.xml | 8 | 2 | 6 |
| BehaviorData.xml | 22 | 0 | 22 |
| EffectData.xml | 23 | 6 | 17 |
| FootprintData.xml | 1 | 0 | 1 |
| ModelData.xml | 1 | 0 | 1 |
| RaceData.xml | 3 | 3 | 0 |
| RequirementData.xml | 4 | 0 | 4 |
| SoundData.xml | 2 | 0 | 2 |
| UnitData.xml | 87 | 49 | 38 |
| UpgradeData.xml | 11 | 10 | 1 |
| WeaponData.xml | 2 | 0 | 2 |

## Provenance and upstream-only IDs

- AbilData.xml (blob 94cc7c15a67e5e67a001a42ef43983ef38d95cd3): AmorphousArmorcloud, BurrowInfestorDown, BurrowInfestorUp, BurrowRoachDown, BurrowRoachUp, ChannelSnipe, GenerateCreep, HallucinationAdept, HallucinationArchon, HallucinationColossus, HallucinationDisruptor, HallucinationHighTemplar, HallucinationImmortal, HallucinationOracle, HallucinationPhoenix, HallucinationProbe, HallucinationStalker, HallucinationVoidRay, HallucinationWarpPrism, HallucinationZealot, MorphBackToGateway, OracleStasisTrapBuild, PhasingMode, SpawnChangeling, SpawnLarva, TransportMode, UpgradeToWarpGate, WidowMineAttack

- ActorData.xml (blob b7940d9c948b64de1312df11e7b9ab20b74c6b7a): LurkerMPAttackSpikeSound, ProtossFastWarpinMarker, ProtossWarpIn, PylonPlacementModel, WidowMineTargetingBeam, XelNagaTowerRange

- BehaviorData.xml (blob 05bfdafadb51302dbf1bb091568000f9281634da): ChannelSnipeCombat, HighYieldMineralFieldMinerals, HighYieldMineralFieldMinerals750, LarvaWander, LocustMPFlyingSwoopUncommandable, MineralFieldMinerals, MineralFieldMinerals450, MineralFieldMinerals750, MineralFieldMineralsOpaque, MineralFieldMineralsOpaque900, MorphingintoWarpGate, NeuralParasite, NeuralParasiteChildren, NydusCreepGrowth, PowerUserWarpable, RawRichVespeneGeyserGas, RawVespeneGeyserGas, SpawnLarva, YoinkMarker, makeCreep2x2Overlord, makeCreep4x4, makeCreep8x6

- EffectData.xml (blob bab405c1ee8d556d99f2937380ef3aa93338f929): ChannelSnipeEnergyRefund, CreepTumorLaunchMissileSet, DisguiseEx3FinalSet, GlaiveWurmE1, GlaiveWurmE2, HerdInteractSet, HerdIssueMoveOrderSelf, KD8Charge, NeuralParasiteLaunchMissile, NeuralParasitePersistentSet, RavagerCorrosiveBileSet, SpawnChangeling, SpawnLarvaSet, YoinkSet, YoinkSetVikingAir, YoinkSetVikingGround, YoinkStartCreatePlaceholder

- FootprintData.xml (blob ccf26d176f086a157e221d238ccd214e770379ad): FootprintGeyserRounded

- ModelData.xml (blob b89e6f1c10daae43ad439cd31f02a3a8a4062810): GhostEMPAttackImpactEffect

- RaceData.xml (blob e7825e5778dc2f4cc71feccf1acc14b3c54a5b9e): none

- RequirementData.xml (blob 0bd23449dcedc768fcfedac4296b366a2911644f): HaveCyberneticsCore, HaveDarkShrine, HaveTemplarArchives, HaveTwilightCouncil

- SoundData.xml (blob 8371e593731b836daf6e884445d5cf03452d2da7): ArchonMergeHighComplete, ArchonMergeLowComplete

- UnitData.xml (blob f96a696f8c2e2ff9110ebb98258becce9e60264e): Anteplott, Artosilope, CarrionBird, CleaningBot, Cow, Crabeetle, DesertPlanetStreetlight, DestructibleBillboardScrollingText, DestructibleBillboardTall, DestructibleBullhornLights, DestructibleSearchlight, DestructibleSignsConstruction, DestructibleSignsDirectional, DestructibleSignsFunny, DestructibleSignsIcons, DestructibleSignsWarning, DestructibleStoreFrontCityProps, DestructibleTrafficSignal, Dog, GlobeStatue, IceProtossCrates, KarakFemale, KarakMale, LabBot, Lyote, MengskStatue, MengskStatueAlone, ProtossCrates, RedstoneLavaCritter, RedstoneLavaCritterInjured, ReptileCrate, Scantipede, Sheep, SlaynSwarmHostSpawnFlyer, ThornLizard, TrafficSignal, WolfStatue, XelNagaTower

- UpgradeData.xml (blob 592bfb3d2dd7a9ea1a99a5bbb4d3658845fe78c8): WarpGateResearch

- WeaponData.xml (blob 68c88613786a349dd99f78bd27a6d651bcf45343): C10CanisterRifle, GlaiveWurm
