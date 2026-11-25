# MiniCraft II — 유닛·건물 능력 공개 검수표

기준: v0.1.7 / 2026-11-26 / [순정 SC2GameData](https://github.com/SC2Mapster/SC2GameData) / [MiniCraft 빌더](Build-MiniCraft.py).

**배포 전 검수용이며, 실게임 검증 완료를 뜻하지 않습니다.** 원본의 Core → Liberty → LibertyMulti → Swarm → SwarmMulti → Void → VoidMulti 카탈로그를 읽어 현재 MiniCraft UnitData의 194개 ID를 조사했습니다. 현행 Battle.net 라이브 데이터와 일치하는지는 미확인입니다. 능력 배열은 순차 인덱스 변경과 부모 상속을 근사 반영하고, 명령 카드에만 등장하는 과거/조건부 링크를 별도 표시합니다. 기본 이동/정지/공격/대기열/집결은 제외합니다. 생산·건설·연구·변태 및 숨겨진 행동, 수동/자동 능력은 포함합니다. 기본 공격 자체와 업그레이드가 부여하는 모든 수치/조건, UI 문자열, 원본에서 모드에 포함되지 않은 유닛은 별도 감사 대상입니다.

| 표기 | 뜻 |
|---|---|
| 직접 | AbilData에 해당 ID 재정의 존재 (전체 수치 검증 아님) |
| 효과 | 능력에 직접 연결된 EffectData가 MiniCraft에서 재정의됨 |
| 상속/미확인 | 순정 정의는 존재하나 직접 수정 또는 직결 효과 수정 확인 안 됨; 유지가 의도일 수도 있음 |
| 원본 미해결 | 해당 ID 정의를 가져온 계층에서 확인 못 함 |
| 행동 수정 | BehaviorData에 직접 재정의 존재 |

모든 항목의 인게임 판정은 **미검증**입니다. 체크 표시를 완료 인증으로 사용하지 않습니다.

## 1. 유닛별 목록

### 테란 (64)

| 유닛 ID | 능력 배열 | 카드에만 있는 후보 | 자동/지속 행동 | 패시브 카드 |
|---|---|---|---|---|
| `SCV` | `Repair`, `SCVHarvest`, `TerranBuild`, `SprayTerran`, `WorkerStopIdleAbilityVespene` | — | — | — |
| `MULE` | `MULEGather`, `MULERepair` | `SCVHarvest` | `MuleRepairAutocastCheck` | — |
| `Marine` | `Stimpack` | — | — | — |
| `Marauder` | `StimpackMarauder` | — | — | — |
| `Reaper` | `KD8Charge` | `255` | `ReaperJump` | `JetPack`, `CombatDrugs` |
| `Ghost` | `GhostCloak`, `ChannelSnipe`, `TacNukeStrike`, `GhostHoldFire`, `EMP`, `GhostWeaponsFree` | `Snipe` | — | — |
| `Hellion` | `MorphToHellionTank` | — | — | `ResearchHighCapacityBarrels`, `ResearchSmartServos` |
| `HellionTank` | `MorphToHellion` | — | — | `ResearchHighCapacityBarrels`, `ResearchSmartServos` |
| `WidowMine` | `WidowMineBurrow`, `WidowMineAttack` | — | `WidowMineDrillingClawsTracker` | `WidowMineBioSplash`, `DrillClaws`, `WidowMineConcealment` |
| `WidowMineBurrowed` | `WidowMineUnburrow`, `WidowMineAttack` | — | `WidowMineArmed`, `WidowMineBurrowedCloakingBehavior`, `WidowMineDrillingClawsTracker` | `WidowMineBioSplash`, `DrillClaws`, `WidowMineConcealment` |
| `SiegeTank` | `SiegeMode` | — | — | — |
| `SiegeTankSieged` | `Unsiege` | — | — | — |
| `Cyclone` | `LockOnCancel`, `LockOn` | — | — | `CycloneLockOnAir` |
| `Thor` | `ThorAPMode` | `250mmStrikeCannons` | — | `ResearchSmartServos` |
| `ThorAP` | `ThorNormalMode` | — | — | `ResearchSmartServos` |
| `VikingFighter` | `AssaultMode` | — | — | `ResearchSmartServos` |
| `VikingAssault` | `FighterMode` | — | — | `ResearchSmartServos` |
| `Medivac` | `MedivacHeal`, `MedivacTransport`, `MedivacSpeedBoost` | — | — | `CaduceusReactor` |
| `Liberator` | `LiberatorMorphtoAG`, `LiberatorAGTarget` | — | — | `LiberatorAGRangeUpgrade` |
| `LiberatorAG` | `LiberatorMorphtoAA`, `LiberatorMorphtoAG`, `LiberatorAATarget` | — | `LiberatorInitialMovable` | `LiberatorAGRangeUpgrade` |
| `Raven` | `RavenScramblerMissile`, `RavenShredderMissile`, `BuildAutoTurret` | `SeekerMissile`, `PlacePointDefenseDrone` | `Detector11` | `Detector` |
| `Banshee` | `BansheeCloak` | — | — | — |
| `Battlecruiser` | `BattlecruiserStop`, `BattlecruiserAttack`, `BattlecruiserMove`, `Yamato`, `Hyperjump` | — | — | — |
| `CommandCenter` | `CommandCenterTrain`, `CommandCenterTransport`, `CommandCenterLiftOff`, `UpgradeToPlanetaryFortress`, `UpgradeToOrbital` | — | `TerranBuildingBurnDown`, `CommandCenterKnockbackBehavior` | — |
| `OrbitalCommand` | `CalldownMULE`, `SupplyDrop`, `CommandCenterTrain`, `ScannerSweep`, `OrbitalLiftOff` | — | `TerranBuildingBurnDown`, `CommandCenterKnockbackBehavior` | — |
| `PlanetaryFortress` | `CommandCenterTrain`, `CommandCenterTransport` | — | `TerranBuildingBurnDown` | — |
| `SupplyDepot` | `SupplyDepotLower` | — | `TerranBuildingBurnDown` | — |
| `SupplyDepotLowered` | `SupplyDepotRaise` | — | `TerranBuildingBurnDown` | — |
| `Refinery` | — | — | `HarvestableVespeneGeyserGas`, `TerranBuildingBurnDown`, `WorkerPeriodicRefineryCheck`, `SCVMoveToGatherSeek` | — |
| `Barracks` | `BarracksTrain`, `BarracksAddOns`, `BarracksLiftOff` | — | `TerranBuildingBurnDown`, `ReactorQueue`, `TerranStructuresKnockbackBehavior` | — |
| `Factory` | `FactoryTrain`, `FactoryAddOns`, `FactoryLiftOff` | — | `TerranBuildingBurnDown`, `ReactorQueue`, `TerranStructuresKnockbackBehavior` | — |
| `Starport` | `StarportTrain`, `StarportAddOns`, `StarportLiftOff` | — | `TerranBuildingBurnDown`, `ReactorQueue`, `TerranStructuresKnockbackBehavior` | — |
| `BarracksReactor` | `FactoryReactorMorph`, `StarportReactorMorph`, `ReactorMorph` | — | `TerranBuildingBurnDown` | — |
| `FactoryReactor` | `BarracksReactorMorph`, `StarportReactorMorph`, `ReactorMorph` | — | `TerranBuildingBurnDown` | — |
| `StarportReactor` | `BarracksReactorMorph`, `FactoryReactorMorph`, `ReactorMorph` | — | `TerranBuildingBurnDown` | — |
| `EngineeringBay` | `EngineeringBayResearch` | — | `TerranBuildingBurnDown` | — |
| `Armory` | `ArmoryResearch`, `ArmoryResearchSwarm` | — | `TerranBuildingBurnDown` | — |
| `FusionCore` | `FusionCoreResearch` | — | `TerranBuildingBurnDown` | — |
| `GhostAcademy` | `ArmSiloWithNuke`, `GhostAcademyResearch` | — | `TerranBuildingBurnDown`, `ReactorQueue` | — |
| `Bunker` | `BunkerTransport`, `SalvageEffect`, `StimpackRedirect`, `StimpackMarauderRedirect`, `StopRedirect`, `AttackRedirect` | `SalvageShared` | `TerranBuildingBurnDown` | — |
| `MissileTurret` | — | — | `TerranBuildingBurnDown`, `Detector11`, `UnderConstruction` | `Detector` |
| `SensorTower` | `SalvageEffect` | — | `SensorTowerRadar`, `TerranBuildingBurnDown`, `UnderConstruction` | `RadarField` |
| `RefineryRich` | — | — | `HarvestableRichVespeneGeyserGas`, `TerranBuildingBurnDown`, `WorkerPeriodicRefineryCheck`, `SCVMoveToGatherSeek` | — |
| `PointDefenseDrone` | — | — | `TerranBuildingBurnDown` | `PointDefense` |
| `BarracksFlying` | `BarracksLand`, `BarracksAddOns` | — | `TerranBuildingBurnDown` | — |
| `AutoTurret` | — | — | `TerranBuildingBurnDown` | — |
| `FactoryFlying` | `FactoryAddOns`, `FactoryLand` | — | `TerranBuildingBurnDown` | — |
| `StarportFlying` | `StarportAddOns`, `StarportLand` | — | `TerranBuildingBurnDown` | — |
| `Reactor` | `BarracksReactorMorph`, `FactoryReactorMorph`, `StarportReactorMorph` | — | `TerranBuildingBurnDown` | — |
| `TechLab` | `BarracksTechLabMorph`, `FactoryTechLabMorph`, `StarportTechLabMorph` | — | `TerranBuildingBurnDown` | — |
| `CommandCenterFlying` | `CommandCenterLand`, `CommandCenterTransport` | — | `TerranBuildingBurnDown` | — |
| `OrbitalCommandFlying` | `OrbitalCommandLand` | `CommandCenterTransport` | `TerranBuildingBurnDown` | — |
| `ScopeTest` | — | — | — | — |
| `GhostAlternate` | `GhostCloak`, `ChannelSnipe`, `TacNukeStrike`, `GhostHoldFire`, `EMP`, `GhostWeaponsFree`, `MorphToGhostNova` | `Snipe` | — | — |
| `GhostNova` | `GhostCloak`, `ChannelSnipe`, `TacNukeStrike`, `GhostHoldFire`, `EMP`, `GhostWeaponsFree` | `Snipe` | — | — |
| `WarHound` | `TornadoMissile` | — | — | — |
| `HERCPlacement` | — | — | — | — |
| `HERC` | — | — | — | — |
| `KD8Charge` | — | — | — | — |
| `BypassArmorDrone` | — | — | `TerranBuildingBurnDown`, `BypassArmorDroneTimedLife`, `BypassArmorDroneInitialUnselectable` | — |
| `RavenRepairDrone` | `RavenRepairDroneHeal` | — | `TerranBuildingBurnDown` | — |
| `BarracksTechLab` | `BarracksTechLabMorph`, `FactoryTechLabMorph`, `StarportTechLabMorph`, `TechLabMorph`, `BarracksTechLabResearch`, `MercCompoundResearch` | — | `TerranBuildingBurnDown` | — |
| `FactoryTechLab` | `BarracksTechLabMorph`, `FactoryTechLabMorph`, `StarportTechLabMorph`, `TechLabMorph`, `FactoryTechLabResearch` | — | `TerranBuildingBurnDown` | — |
| `StarportTechLab` | `BarracksTechLabMorph`, `FactoryTechLabMorph`, `StarportTechLabMorph`, `TechLabMorph`, `StarportTechLabResearch` | — | `TerranBuildingBurnDown` | — |

### 저그 (83)

| 유닛 ID | 능력 배열 | 카드에만 있는 후보 | 자동/지속 행동 | 패시브 카드 |
|---|---|---|---|---|
| `Drone` | `ZergBuild`, `DroneHarvest`, `BurrowDroneDown`, `SprayZerg`, `WorkerStopIdleAbilityVespene` | `255`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | — |
| `DroneBurrowed` | `BurrowDroneUp` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | — |
| `Zergling` | `BurrowZerglingDown`, `MorphToBaneling` | `MorphZerglingToBaneling`, `BurrowDroneDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | — |
| `ZerglingBurrowed` | `BurrowZerglingUp` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | — |
| `Baneling` | `BurrowBanelingDown`, `Explode`, `VolatileBurstBuilding` | `SapStructure`, `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | `BanelingExplode` | — |
| `BanelingBurrowed` | `Explode`, `BurrowBanelingUp`, `VolatileBurstBuilding` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | `BanelingExplode`, `BurrowCracks` | — |
| `Roach` | `BurrowRoachDown`, `MorphToRavager` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | `RapidRegeneration` |
| `RoachBurrowed` | `BurrowRoachUp` | `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp`, `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown` | `PermanentBurrowMoveCloaked` | `RapidRegeneration` |
| `Ravager` | `BurrowRavagerDown`, `RavagerCorrosiveBile` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | — |
| `RavagerBurrowed` | `BurrowRavagerUp` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | — |
| `Hydralisk` | `BurrowHydraliskDown`, `MorphToLurker`, `HydraliskFrenzy` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | — |
| `HydraliskBurrowed` | `BurrowHydraliskUp` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | `BurrowCracks` | — |
| `LurkerMP` | `BurrowLurkerMPDown` | — | — | — |
| `LurkerMPBurrowed` | `BurrowLurkerMPUp`, `BurrowLurkerMPDown`, `LurkerHoldFire`, `LurkerRemoveHoldFire` | — | — | — |
| `Infestor` | `BurrowInfestorDown`, `NeuralParasite`, `FungalGrowth`, `InfestorEnsnare`, `AmorphousArmorcloud` | `InfestedTerrans`, `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | `BurrowedMove` |
| `InfestorBurrowed` | `BurrowInfestorUp`, `NeuralParasite`, `InfestorEnsnare`, `AmorphousArmorcloud` | `InfestedTerrans`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowUltraliskUp`, `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown` | `PermanentBurrowMoveCloaked` | `BurrowedMove` |
| `SwarmHostMP` | `MorphToSwarmHostBurrowedMP`, `SpawnLocustsTargeted` | `SwarmHostSpawnLocusts`, `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | `FlyingLocusts` |
| `SwarmHostBurrowedMP` | `MorphToSwarmHostMP`, `SwarmHostSpawnLocusts`, `SpawnLocustsTargeted` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | `FlyingLocusts` |
| `Ultralisk` | `BurrowUltraliskDown`, `UltraliskWeaponCooldown` | `BurrowChargeRevD`, `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | `Frenzy` | `Frenzied`, `EvolveChitinousPlating`, `EvolveAnabolicSynthesis2` |
| `UltraliskBurrowed` | `BurrowUltraliskUp` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp` | `Frenzy` | `Frenzied` |
| `Queen` | `QueenBuild`, `BurrowQueenDown`, `SpawnLarva`, `Transfusion` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | `QueenMustBeOnCreep` | — |
| `QueenBurrowed` | `BurrowQueenUp` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | — |
| `Mutalisk` | — | — | — | `MutaliskRegeneration` |
| `Corruptor` | `CausticSpray`, `MorphToBroodLord` | `Corruption` | — | — |
| `BroodLord` | `BroodLordHangar`, `BroodLordQueue2` | — | — | `SwarmSeeds`, `Frenzied` |
| `Viper` | `ViperConsumeStructure`, `BlindingCloud`, `Yoink`, `ParasiticBomb` | — | — | — |
| `Overlord` | `OverlordTransport`, `MorphToOverseer`, `GenerateCreep`, `MorphToTransportOverlord` | — | — | — |
| `OverlordTransport` | `OverlordTransport`, `MorphToOverseer`, `GenerateCreep` | — | `IsTransportOverlord` | — |
| `Overseer` | `SpawnChangeling`, `Contaminate`, `OverseerMorphtoOverseerSiegeMode` | — | `Detector11` | `Detector` |
| `Hatchery` | `UpgradeToLair`, `TrainQueen`, `LairResearch` | — | `makeCreep8x6`, `SpawnLarva`, `ZergBuildingDies9` | — |
| `Lair` | `LairResearch`, `UpgradeToHive`, `TrainQueen` | — | `makeCreep8x6`, `SpawnLarva`, `ZergBuildingDies9` | — |
| `Hive` | `LairResearch`, `TrainQueen` | — | `makeCreep8x6`, `SpawnLarva`, `ZergBuildingDies9` | — |
| `Extractor` | — | — | `HarvestableVespeneGeyserGasZerg`, `WorkerPeriodicRefineryCheck`, `SCVMoveToGatherSeek` | — |
| `SpawningPool` | `SpawningPoolResearch` | — | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | — |
| `EvolutionChamber` | `evolutionchamberresearch` | — | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | — |
| `RoachWarren` | `RoachWarrenResearch` | — | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | — |
| `BanelingNest` | `BanelingNestResearch` | — | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | — |
| `SpineCrawler` | `SpineCrawlerUproot` | — | `OnCreep`, `ZergBuildingNotOnCreep` | — |
| `SpineCrawlerUprooted` | `SpineCrawlerRoot` | — | — | — |
| `SporeCrawler` | `SporeCrawlerUproot` | — | `Detector11`, `OnCreep`, `ZergBuildingNotOnCreep`, `UnderConstruction` | `Detector` |
| `SporeCrawlerUprooted` | `SporeCrawlerRoot` | — | — | — |
| `HydraliskDen` | `HydraliskDenResearch` | `UpgradeToLurkerDenMP` | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | — |
| `LurkerDenMP` | `LurkerDenResearch` | `HydraliskDenResearch` | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | — |
| `InfestationPit` | `InfestationPitResearch` | — | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | — |
| `Spire` | `UpgradeToGreaterSpire`, `SpireResearch` | — | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | — |
| `GreaterSpire` | `SpireResearch` | — | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | — |
| `UltraliskCavern` | `UltraliskCavernResearch` | — | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | — |
| `NydusNetwork` | `NydusCanalTransport`, `BuildNydusCanal` | — | `OnCreep`, `ZergBuildingNotOnCreep`, `ZergBuildingDies6` | `NydusWormIncreasedArmorPassive` |
| `NydusCanal` | `BuildinProgressNydusCanal`, `NydusWormTransport` | `NydusCanalTransport` | `NydusCreepGrowth`, `NydusDetect`, `NydusWormArmor` | — |
| `CreepTumorQueen` | `BurrowCreepTumorDown` | — | `makeCreep4x4` | — |
| `ExtractorRich` | — | — | `HarvestableRichVespeneGeyserGasZerg`, `WorkerPeriodicRefineryCheck`, `SCVMoveToGatherSeek` | — |
| `LurkerMPEgg` | `MorphToLurker` | `LurkerAspectMP`, `LurkerAspectMPFromHydraliskBurrowed` | — | — |
| `RavagerCocoon` | `MorphToRavager` | — | — | — |
| `TransportOverlordCocoon` | `MorphToTransportOverlord` | — | — | — |
| `Larva` | `LarvaTrain` | — | `LarvaWander`, `DeathOffCreep`, `LarvaPauseWander` | — |
| `Egg` | — | — | — | — |
| `BanelingCocoon` | `MorphToBaneling` | — | — | — |
| `OverlordCocoon` | `MorphToOverseer` | — | `MassiveVoidRayVulnerability` | — |
| `BroodLordCocoon` | `MorphToBroodLord` | — | — | — |
| `CreepTumor` | `BurrowCreepTumorDown` | — | `makeCreep4x4`, `CreepTumorActive` | — |
| `CreepTumorBurrowed` | `CreepTumorBuild` | — | `makeCreep4x4`, `CreepTumorActive` | — |
| `InfestorTerran` | `BurrowInfestorTerranDown` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | — |
| `InfestorTerranBurrowed` | `BurrowInfestorTerranUp` | `BurrowDroneDown`, `BurrowZerglingDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | — | — |
| `Broodling` | — | — | — | — |
| `BroodlingEscort` | — | — | `StandardMissile`, `BroodlingAttackDelay` | — |
| `Changeling` | `DisguiseAsMarineWithShield`, `DisguiseAsMarineWithoutShield`, `DisguiseAsZerglingWithWings`, `DisguiseAsZerglingWithoutWings` | — | `ChangelingDisguiseEx3` | `Disguise` |
| `ChangelingZealot` | `Charge` | — | `ChangelingDisable` | — |
| `ChangelingMarineShield` | `Stimpack` | — | `ChangelingDisable` | — |
| `ChangelingMarine` | `Stimpack` | — | `ChangelingDisable` | — |
| `ChangelingZergling` | `BurrowZerglingDown`, `MorphToBaneling` | `MorphZerglingToBaneling`, `BurrowDroneDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | `ChangelingDisable` | — |
| `ChangelingZerglingWings` | `BurrowZerglingDown`, `MorphToBaneling` | `MorphZerglingToBaneling`, `BurrowDroneDown`, `BurrowBanelingDown`, `BurrowRoachDown`, `BurrowHydraliskDown`, `BurrowRavagerDown`, `MorphToSwarmHostBurrowedMP`, `BurrowQueenDown`, `BurrowInfestorTerranDown`, `BurrowInfestorDown`, `BurrowUltraliskDown`, `BurrowDroneUp`, `BurrowZerglingUp`, `BurrowBanelingUp`, `BurrowRoachUp`, `BurrowHydraliskUp`, `BurrowRavagerUp`, `MorphToSwarmHostMP`, `BurrowQueenUp`, `BurrowInfestorTerranUp`, `BurrowInfestorUp`, `BurrowUltraliskUp` | `ChangelingDisable` | — |
| `NydusCanalAttacker` | `BuildinProgressNydusCanal` | — | `MakeCreepNydusAttacker`, `NydusDestroyerInvulnerability` | — |
| `NydusCanalCreeper` | `BuildinProgressNydusCanal`, `DigesterCreepSpray` | — | `MakeCreepNydusCreeper`, `DigesterCreepSprayFinal` | — |
| `LocustMP` | `LocustMPMorphToAir` | — | — | — |
| `LocustMPFlying` | `LocustMPFlyingMorphToGround`, `LocustMPFlyingSwoop`, `LocustMPFlyingSwoopAttack` | — | — | — |
| `ScourgeMP` | — | — | — | — |
| `DefilerMP` | `DefilerMPConsume`, `DefilerMPDarkSwarm`, `DefilerMPPlague`, `DefilerMPBurrow` | — | — | — |
| `DefilerMPBurrowed` | `DefilerMPUnburrow` | — | — | — |
| `QueenMP` | `QueenMPEnsnare`, `QueenMPSpawnBroodlings`, `QueenMPInfestCommandCenter` | — | — | — |
| `OverseerSiegeMode` | `SpawnChangeling`, `Contaminate`, `OverseerMorphtoOverseerSiegeMode`, `OverseerSiegeModeMorphtoOverseer` | — | `Detector11`, `Detector13p75` | `Detector` |
| `InfestedTerransEgg` | `MorphToInfestedTerran` | — | `InfestedTerransEggTimedLife` | — |
| `GuardianCocoonMP` | `MorphToGuardianMP` | — | — | — |
| `DevourerCocoonMP` | `MorphToDevourerMP` | — | — | — |

### 프로토스 (46)

| 유닛 ID | 능력 배열 | 카드에만 있는 후보 | 자동/지속 행동 | 패시브 카드 |
|---|---|---|---|---|
| `Probe` | `ProtossBuild`, `ProbeHarvest`, `SprayProtoss`, `WorkerStopIdleAbilityVespene` | `255` | — | — |
| `Zealot` | `Charge` | — | — | — |
| `Stalker` | `Blink` | — | — | — |
| `Sentry` | `ForceField`, `GuardianShield`, `HallucinationArchon`, `HallucinationColossus`, `HallucinationHighTemplar`, `HallucinationImmortal`, `HallucinationPhoenix`, `HallucinationProbe`, `HallucinationStalker`, `HallucinationVoidRay`, `HallucinationWarpPrism`, `HallucinationZealot`, `HallucinationOracle`, `HallucinationDisruptor`, `HallucinationAdept` | — | — | — |
| `Adept` | `AdeptPhaseShift`, `AdeptPhaseShiftCancel` | — | — | `AdeptPiercingUpgrade` |
| `HighTemplar` | `PsiStorm`, `ArchonWarp`, `Feedback` | — | — | — |
| `DarkTemplar` | `ArchonWarp`, `DarkTemplarBlink` | — | — | `PermanentlyCloaked` |
| `Archon` | `Mergeable` | — | — | — |
| `Immortal` | — | `ImmortalOverload` | `BarrierDamageResponse`, `ImmortalOverload` | `HardenedShield` |
| `Colossus` | — | — | — | `CliffWalk` |
| `Disruptor` | `PurificationNovaTargeted`, `PurificationNova`, `PurificationNovaMorph` | — | — | — |
| `Observer` | `ObserverMorphtoObserverSiege` | — | `Detector11` | `PermanentlyCloakedObserver`, `Detector` |
| `WarpPrism` | `PhasingMode`, `WarpPrismTransport` | — | `WarpPrismLoadupDecelerationFix` | — |
| `WarpPrismPhasing` | `TransportMode`, `WarpPrismTransport`, `AttackWarpPrism` | — | `WarpPrismPowerSource` | `ImprovedEnergy` |
| `Phoenix` | `GravitonBeam` | — | — | — |
| `VoidRay` | `VoidRaySwarmDamageBoost`, `VoidRaySwarmDamageBoostCancel` | — | — | `PrismaticBeam` |
| `Oracle` | `OracleRevelation`, `OracleWeapon`, `OracleStasisTrapBuild` | `VoidSiphon`, `ResourceStun`, `LightofAiur`, `TemporalField` | — | — |
| `Tempest` | — | `LightningBomb`, `TempestDisruptionBlast` | — | `TempestGroundAttackUpgrade` |
| `Carrier` | `CarrierHangar`, `HangarQueue5` | — | — | `GravitonCatapult` |
| `Mothership` | `TemporalField`, `MassRecall`, `MothershipCloak` | `Vortex`, `MothershipMassRecall` | `MothershipTargetFireTracker`, `MothershipLastTargetTracker` | `CloakingField` |
| `Nexus` | `ChronoBoostEnergyCost`, `NexusTrain`, `stopProtossBuilding`, `NexusInvulnerability`, `NexusTrainMothership`, `NexusMassRecall`, `EnergyRecharge` | `TimeWarp`, `NexusTrainMothershipCore`, `attackProtossBuilding` | `NexusDeath` | — |
| `Pylon` | `PurifyMorphPylon` | — | `PowerSource` | `ImprovedEnergy` |
| `Assimilator` | — | — | `HarvestableVespeneGeyserGasProtoss`, `WorkerPeriodicRefineryCheck`, `SCVMoveToGatherSeek` | — |
| `Gateway` | `GatewayTrain`, `UpgradeToWarpGate`, `MorphBuildingGatewayWarpGateFree` | `WarpGateTrain` | `PowerUserQueue`, `FastEnablerGatewayMorphingPowerSource`, `GatewayTrainingState` | — |
| `WarpGate` | `WarpGateTrain`, `MorphBackToGateway` | — | `PowerUserQueue`, `FastEnablerPowerSource` | — |
| `CyberneticsCore` | `CyberneticsCoreResearch` | — | `PowerUserQueue` | — |
| `Forge` | `ForgeResearch` | — | `PowerUserQueue` | — |
| `PhotonCannon` | — | — | `Detector11`, `PowerUserBaseDefenseSmall`, `UnderConstruction` | `Detector` |
| `ShieldBattery` | `ShieldBatteryRechargeEx5` | `ShieldBatteryRechargeChanneled` | `PowerUserQueueSmall` | — |
| `TwilightCouncil` | `TwilightCouncilResearch` | — | `PowerUserQueue`, `StalkerIcon` | — |
| `TemplarArchive` | `TemplarArchivesResearch` | — | `PowerUserQueue` | — |
| `DarkShrine` | `DarkShrineResearch` | — | `PowerUserQueue` | — |
| `RoboticsFacility` | `RoboticsFacilityTrain` | — | `PowerUserQueue` | — |
| `RoboticsBay` | `RoboticsBayResearch` | — | `PowerUserQueue` | — |
| `Stargate` | `StargateTrain` | — | `PowerUserQueue` | — |
| `FleetBeacon` | `FleetBeaconResearch` | — | `PowerUserQueue` | — |
| `AssimilatorRich` | — | — | `HarvestableRichVespeneGeyserGasProtoss`, `WorkerPeriodicRefineryCheck`, `SCVMoveToGatherSeek` | — |
| `Interceptor` | — | — | — | — |
| `ForceField` | `Shatter` | — | — | — |
| `MothershipCore` | `MothershipCoreMassRecall`, `TemporalField`, `MorphToMothership`, `MothershipCorePurifyNexus` | `MothershipCoreEnergize`, `MothershipCorePurifyNexusCancel` | — | — |
| `DisruptorPhased` | `PurificationNova`, `PurificationNovaMorphBack` | — | — | — |
| `VoidMPImmortalReviveCorpse` | `VoidMPImmortalReviveRebuild` | — | — | — |
| `OracleStasisTrap` | `OracleStasisTrapActivate` | — | `OracleStasisTrapCloak`, `StasisWardTimedLife` | `ActivateStasisWard`, `PermanentlyCloakedStasis` |
| `AdeptPhaseShift` | `AdeptShadePhaseShiftCancel` | — | — | — |
| `ObserverSiegeMode` | `ObserverMorphtoObserverSiege`, `ObserverSiegeMorphtoObserver` | — | `Detector11`, `Detector15` | `PermanentlyCloakedObserver`, `Detector` |
| `PylonOvercharged` | `PurifyMorphPylon`, `PurifyMorphPylonBack`, `attackProtossBuilding`, `stopProtossBuilding` | — | `PowerSource`, `PowerSourceFast`, `FastEnablerPowerUser` | `ImprovedEnergy` |

### 기타 / 종족 미해결 (1)

| 유닛 ID | 능력 배열 | 카드에만 있는 후보 | 자동/지속 행동 | 패시브 카드 |
|---|---|---|---|---|
| `LocustMPPrecursor` | — | — | — | — |

## 2. 개별 능력 정의 및 수정 여부 (311개)

| 능력 ID | 유형 | 연결 유닛 | 직접 수정 | 직결 효과 ID | 판정 |
|---|---|---|---|---|---|
| `250mmStrikeCannons` | CAbilEffectTarget | `Thor` | 아니오 | `250mmStrikeCannonsCreatePersistent` | 상속/미확인 |
| `255` | — | `Reaper`, `Drone`, `Probe` | 아니오 | — | 원본 미해결 |
| `AdeptPhaseShift` | CAbilEffectTarget | `Adept` | 아니오 | `AdeptPhaseShiftInitialSet` | 상속/미확인 |
| `AdeptPhaseShiftCancel` | CAbilEffectInstant | `Adept` | 아니오 | `AdeptPhaseShiftCancelAB` | 상속/미확인 |
| `AdeptShadePhaseShiftCancel` | CAbilEffectInstant | `AdeptPhaseShift` | 아니오 | — | 상속/미확인 |
| `AmorphousArmorcloud` | CAbilEffectTarget | `Infestor`, `InfestorBurrowed` | 아니오 | `AmorphousArmorcloudCP` | 상속/미확인 |
| `ArchonWarp` | CAbilMerge | `HighTemplar`, `DarkTemplar` | 아니오 | — | 상속/미확인 |
| `ArmoryResearch` | CAbilResearch | `Armory` | 예 | — | 직접 |
| `ArmoryResearchSwarm` | CAbilResearch | `Armory` | 아니오 | — | 상속/미확인 |
| `ArmSiloWithNuke` | CAbilArmMagazine | `GhostAcademy` | 예 | — | 직접 |
| `AssaultMode` | CAbilMorph | `VikingFighter` | 아니오 | — | 상속/미확인 |
| `attackProtossBuilding` | CAbilAttack | `PylonOvercharged`, `Nexus` | 아니오 | — | 상속/미확인 |
| `AttackRedirect` | CAbilRedirectTarget | `Bunker` | 아니오 | — | 상속/미확인 |
| `AttackWarpPrism` | CAbilAttack | `WarpPrismPhasing` | 아니오 | — | 상속/미확인 |
| `BanelingNestResearch` | CAbilResearch | `BanelingNest` | 예 | — | 직접 |
| `BansheeCloak` | CAbilBehavior | `Banshee` | 아니오 | — | 상속/미확인 |
| `BarracksAddOns` | CAbilBuild | `Barracks`, `BarracksFlying` | 예 | — | 직접 |
| `BarracksLand` | CAbilMorphPlacement | `BarracksFlying` | 아니오 | — | 상속/미확인 |
| `BarracksLiftOff` | CAbilMorph | `Barracks` | 아니오 | — | 상속/미확인 |
| `BarracksReactorMorph` | CAbilMorph | `FactoryReactor`, `StarportReactor`, `Reactor` | 아니오 | — | 상속/미확인 |
| `BarracksTechLabMorph` | CAbilMorph | `TechLab`, `BarracksTechLab`, `FactoryTechLab`, `StarportTechLab` | 아니오 | — | 상속/미확인 |
| `BarracksTechLabResearch` | CAbilResearch | `BarracksTechLab` | 예 | — | 직접 |
| `BarracksTrain` | CAbilTrain | `Barracks` | 예 | — | 직접 |
| `BattlecruiserAttack` | CAbilAttack | `Battlecruiser` | 아니오 | — | 상속/미확인 |
| `BattlecruiserMove` | CAbilMove | `Battlecruiser` | 아니오 | — | 상속/미확인 |
| `BattlecruiserStop` | CAbilStop | `Battlecruiser` | 아니오 | — | 상속/미확인 |
| `BlindingCloud` | CAbilEffectTarget | `Viper` | 아니오 | `BlindingCloudCP` | 상속/미확인 |
| `Blink` | CAbilEffectTarget | `Stalker` | 아니오 | — | 상속/미확인 |
| `BroodLordHangar` | CAbilArmMagazine | `BroodLord` | 예 | — | 직접 |
| `BroodLordQueue2` | CAbilQueue | `BroodLord` | 아니오 | — | 상속/미확인 |
| `BuildAutoTurret` | CAbilEffectTarget | `Raven` | 아니오 | `AutoTurretRelease` | 상속/미확인 |
| `BuildinProgressNydusCanal` | CAbilBuildable | `NydusCanal`, `NydusCanalAttacker`, `NydusCanalCreeper` | 아니오 | — | 상속/미확인 |
| `BuildNydusCanal` | CAbilBuild | `NydusNetwork` | 예 | — | 직접 |
| `BunkerTransport` | CAbilTransport | `Bunker` | 아니오 | — | 상속/미확인 |
| `BurrowBanelingDown` | CAbilMorph | `Baneling`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowBanelingUp` | CAbilMorph | `BanelingBurrowed`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowChargeRevD` | CAbilEffectTarget | `Ultralisk` | 아니오 | `BurrowChargeInitialRevD` | 상속/미확인 |
| `BurrowCreepTumorDown` | CAbilMorph | `CreepTumorQueen`, `CreepTumor` | 아니오 | — | 상속/미확인 |
| `BurrowDroneDown` | CAbilMorph | `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowDroneUp` | CAbilMorph | `DroneBurrowed`, `Drone`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowHydraliskDown` | CAbilMorph | `Hydralisk`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowHydraliskUp` | CAbilMorph | `HydraliskBurrowed`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowInfestorDown` | CAbilMorph | `Infestor`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowInfestorTerranDown` | CAbilMorph | `InfestorTerran`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowInfestorTerranUp` | CAbilMorph | `InfestorTerranBurrowed`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowInfestorUp` | CAbilMorph | `InfestorBurrowed`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowLurkerMPDown` | CAbilMorph | `LurkerMP`, `LurkerMPBurrowed` | 아니오 | — | 상속/미확인 |
| `BurrowLurkerMPUp` | CAbilMorph | `LurkerMPBurrowed` | 아니오 | — | 상속/미확인 |
| `BurrowQueenDown` | CAbilMorph | `Queen`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowQueenUp` | CAbilMorph | `QueenBurrowed`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowRavagerDown` | CAbilMorph | `Ravager`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowRavagerUp` | CAbilMorph | `RavagerBurrowed`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowRoachDown` | CAbilMorph | `Roach`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowRoachUp` | CAbilMorph | `RoachBurrowed`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowUltraliskDown` | CAbilMorph | `Ultralisk`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowUltraliskUp` | CAbilMorph | `UltraliskBurrowed`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `BurrowZerglingDown` | CAbilMorph | `Zergling`, `ChangelingZergling`, `ChangelingZerglingWings`, `Drone`, `DroneBurrowed`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed` | 아니오 | — | 상속/미확인 |
| `BurrowZerglingUp` | CAbilMorph | `ZerglingBurrowed`, `Drone`, `DroneBurrowed`, `Zergling`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `CalldownMULE` | CAbilEffectTarget | `OrbitalCommand` | 아니오 | `CalldownMULECreateUnit`, `OrbitalCommandCreateMuleSwitch` | 상속/미확인 |
| `CarrierHangar` | CAbilArmMagazine | `Carrier` | 예 | — | 직접 |
| `CausticSpray` | CAbilEffectTarget | `Corruptor` | 아니오 | `CausticSprayBasePersistent` | 상속/미확인 |
| `ChannelSnipe` | CAbilEffectTarget | `Ghost`, `GhostAlternate`, `GhostNova` | 아니오 | `ChannelSnipeInitialSet` | 상속/미확인 |
| `Charge` | CAbilAugment | `Zealot`, `ChangelingZealot` | 아니오 | — | 상속/미확인 |
| `ChronoBoostEnergyCost` | CAbilEffectTarget | `Nexus` | 아니오 | `ChronoBoostEnergyCostAB` | 상속/미확인 |
| `CommandCenterLand` | CAbilMorphPlacement | `CommandCenterFlying` | 아니오 | — | 상속/미확인 |
| `CommandCenterLiftOff` | CAbilMorph | `CommandCenter` | 아니오 | — | 상속/미확인 |
| `CommandCenterTrain` | CAbilTrain | `CommandCenter`, `OrbitalCommand`, `PlanetaryFortress` | 예 | — | 직접 |
| `CommandCenterTransport` | CAbilTransport | `CommandCenter`, `PlanetaryFortress`, `CommandCenterFlying`, `OrbitalCommandFlying` | 아니오 | — | 상속/미확인 |
| `Contaminate` | CAbilEffectTarget | `Overseer`, `OverseerSiegeMode` | 아니오 | — | 상속/미확인 |
| `Corruption` | CAbilEffectTarget | `Corruptor` | 아니오 | — | 상속/미확인 |
| `CreepTumorBuild` | CAbilBuild | `CreepTumorBurrowed` | 아니오 | — | 상속/미확인 |
| `CyberneticsCoreResearch` | CAbilResearch | `CyberneticsCore` | 예 | — | 직접 |
| `DarkShrineResearch` | CAbilResearch | `DarkShrine` | 예 | — | 직접 |
| `DarkTemplarBlink` | CAbilEffectTarget | `DarkTemplar` | 아니오 | — | 상속/미확인 |
| `DefilerMPBurrow` | CAbilMorph | `DefilerMP` | 아니오 | — | 상속/미확인 |
| `DefilerMPConsume` | CAbilEffectTarget | `DefilerMP` | 아니오 | `DefilerMPConsumeApplyBehavior` | 상속/미확인 |
| `DefilerMPDarkSwarm` | CAbilEffectTarget | `DefilerMP` | 아니오 | `DefilerMPDarkSwarmLM` | 상속/미확인 |
| `DefilerMPPlague` | CAbilEffectTarget | `DefilerMP` | 아니오 | `DefilerMPPlagueSearch` | 상속/미확인 |
| `DefilerMPUnburrow` | CAbilMorph | `DefilerMPBurrowed` | 아니오 | — | 상속/미확인 |
| `DigesterCreepSpray` | CAbilEffectTarget | `NydusCanalCreeper` | 아니오 | `DigesterCreepInitialSet` | 상속/미확인 |
| `DisguiseAsMarineWithoutShield` | CAbilMorph | `Changeling` | 아니오 | — | 상속/미확인 |
| `DisguiseAsMarineWithShield` | CAbilMorph | `Changeling` | 아니오 | — | 상속/미확인 |
| `DisguiseAsZerglingWithoutWings` | CAbilMorph | `Changeling` | 아니오 | — | 상속/미확인 |
| `DisguiseAsZerglingWithWings` | CAbilMorph | `Changeling` | 아니오 | — | 상속/미확인 |
| `DroneHarvest` | CAbilHarvest | `Drone` | 아니오 | — | 상속/미확인 |
| `EMP` | CAbilEffectTarget | `Ghost`, `GhostAlternate`, `GhostNova` | 아니오 | `EMPLaunchMissile` | 상속/미확인 |
| `EnergyRecharge` | CAbilEffectTarget | `Nexus` | 아니오 | `EnergyRechargePersistent` | 상속/미확인 |
| `EngineeringBayResearch` | CAbilResearch | `EngineeringBay` | 예 | — | 직접 |
| `evolutionchamberresearch` | CAbilResearch | `EvolutionChamber` | 예 | — | 직접 |
| `Explode` | CAbilEffectInstant | `Baneling`, `BanelingBurrowed` | 아니오 | `VolatileBurst` | 상속/미확인 |
| `FactoryAddOns` | CAbilBuild | `Factory`, `FactoryFlying` | 예 | — | 직접 |
| `FactoryLand` | CAbilMorphPlacement | `FactoryFlying` | 아니오 | — | 상속/미확인 |
| `FactoryLiftOff` | CAbilMorph | `Factory` | 아니오 | — | 상속/미확인 |
| `FactoryReactorMorph` | CAbilMorph | `BarracksReactor`, `StarportReactor`, `Reactor` | 아니오 | — | 상속/미확인 |
| `FactoryTechLabMorph` | CAbilMorph | `TechLab`, `BarracksTechLab`, `FactoryTechLab`, `StarportTechLab` | 아니오 | — | 상속/미확인 |
| `FactoryTechLabResearch` | CAbilResearch | `FactoryTechLab` | 예 | — | 직접 |
| `FactoryTrain` | CAbilTrain | `Factory` | 예 | — | 직접 |
| `Feedback` | CAbilEffectTarget | `HighTemplar` | 아니오 | `FeedbackSet` | 상속/미확인 |
| `FighterMode` | CAbilMorph | `VikingAssault` | 아니오 | — | 상속/미확인 |
| `FleetBeaconResearch` | CAbilResearch | `FleetBeacon` | 예 | — | 직접 |
| `ForceField` | CAbilEffectTarget | `Sentry` | 아니오 | — | 상속/미확인 |
| `ForgeResearch` | CAbilResearch | `Forge` | 예 | — | 직접 |
| `FungalGrowth` | CAbilEffectTarget | `Infestor` | 아니오 | `FungalGrowthInitialSet` | 상속/미확인 |
| `FusionCoreResearch` | CAbilResearch | `FusionCore` | 예 | — | 직접 |
| `GatewayTrain` | CAbilTrain | `Gateway` | 예 | — | 직접 |
| `GenerateCreep` | CAbilBehavior | `Overlord`, `OverlordTransport` | 아니오 | — | 상속/미확인 |
| `GhostAcademyResearch` | CAbilResearch | `GhostAcademy` | 예 | — | 직접 |
| `GhostCloak` | CAbilBehavior | `Ghost`, `GhostAlternate`, `GhostNova` | 아니오 | — | 상속/미확인 |
| `GhostHoldFire` | CAbilEffectInstant | `Ghost`, `GhostAlternate`, `GhostNova` | 아니오 | — | 상속/미확인 |
| `GhostWeaponsFree` | CAbilEffectInstant | `Ghost`, `GhostAlternate`, `GhostNova` | 아니오 | — | 상속/미확인 |
| `GravitonBeam` | CAbilEffectTarget | `Phoenix` | 아니오 | — | 상속/미확인 |
| `GuardianShield` | CAbilEffectInstant | `Sentry` | 아니오 | `GuardianShieldPersistent` | 상속/미확인 |
| `HallucinationAdept` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateAdept` | 상속/미확인 |
| `HallucinationArchon` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateArchon` | 상속/미확인 |
| `HallucinationColossus` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateColossus` | 상속/미확인 |
| `HallucinationDisruptor` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateDisruptor` | 상속/미확인 |
| `HallucinationHighTemplar` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateHighTemplar` | 상속/미확인 |
| `HallucinationImmortal` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateImmortal` | 상속/미확인 |
| `HallucinationOracle` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateOracle` | 상속/미확인 |
| `HallucinationPhoenix` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreatePhoenix` | 상속/미확인 |
| `HallucinationProbe` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateProbe` | 상속/미확인 |
| `HallucinationStalker` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateStalker` | 상속/미확인 |
| `HallucinationVoidRay` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateVoidRay` | 상속/미확인 |
| `HallucinationWarpPrism` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateWarpPrism` | 상속/미확인 |
| `HallucinationZealot` | CAbilEffectInstant | `Sentry` | 아니오 | `HallucinationCreateZealot` | 상속/미확인 |
| `HangarQueue5` | CAbilQueue | `Carrier` | 아니오 | — | 상속/미확인 |
| `HydraliskDenResearch` | CAbilResearch | `HydraliskDen`, `LurkerDenMP` | 예 | — | 직접 |
| `HydraliskFrenzy` | CAbilEffectInstant | `Hydralisk` | 아니오 | `HydraliskFrenzyApplyBehavior` | 상속/미확인 |
| `Hyperjump` | CAbilEffectTarget | `Battlecruiser` | 아니오 | `HyperjumpCreatePrecursor`, `HyperjumpInitialCP` | 상속/미확인 |
| `ImmortalOverload` | CAbilEffectInstant | `Immortal` | 아니오 | `ImmortalOverloadAB` | 상속/미확인 |
| `InfestationPitResearch` | CAbilResearch | `InfestationPit` | 예 | — | 직접 |
| `InfestedTerrans` | CAbilEffectTarget | `Infestor`, `InfestorBurrowed` | 아니오 | `InfestedTerransCreateEgg` | 상속/미확인 |
| `InfestorEnsnare` | CAbilEffectTarget | `Infestor`, `InfestorBurrowed` | 아니오 | `InfestorEnsnareLM` | 상속/미확인 |
| `KD8Charge` | CAbilEffectTarget | `Reaper` | 아니오 | — | 상속/미확인 |
| `LairResearch` | CAbilResearch | `Hatchery`, `Lair`, `Hive` | 예 | — | 직접 |
| `LarvaTrain` | CAbilTrain | `Larva` | 예 | — | 직접 |
| `LiberatorAATarget` | CAbilEffectInstant | `LiberatorAG` | 아니오 | `LiberatorTargetAAMorphOrderSet` | 상속/미확인 |
| `LiberatorAGTarget` | CAbilEffectTarget | `Liberator` | 아니오 | `LiberatorTargetMorphOrderInitialSet` | 상속/미확인 |
| `LiberatorMorphtoAA` | CAbilMorph | `LiberatorAG` | 아니오 | — | 상속/미확인 |
| `LiberatorMorphtoAG` | CAbilMorph | `Liberator`, `LiberatorAG` | 아니오 | — | 상속/미확인 |
| `LightningBomb` | CAbilEffectTarget | `Tempest` | 아니오 | `LightningBombLM` | 상속/미확인 |
| `LightofAiur` | — | `Oracle` | 아니오 | — | 원본 미해결 |
| `LockOn` | CAbilEffectTarget | `Cyclone` | 아니오 | `LockOnGroundAirSet`, `LockOnInitialSetNew` | 상속/미확인 |
| `LockOnCancel` | CAbilEffectInstant | `Cyclone` | 아니오 | `LockOnDisableAttackRB` | 상속/미확인 |
| `LocustMPFlyingMorphToGround` | CAbilMorph | `LocustMPFlying` | 아니오 | — | 상속/미확인 |
| `LocustMPFlyingSwoop` | CAbilEffectTarget | `LocustMPFlying` | 아니오 | `LocustMPFlyingSwoopCreatePrecursor` | 상속/미확인 |
| `LocustMPFlyingSwoopAttack` | CAbilEffectTarget | `LocustMPFlying` | 아니오 | `LocustMPFlyingSwoopCreatePrecursorOffset` | 상속/미확인 |
| `LocustMPMorphToAir` | CAbilMorph | `LocustMP` | 아니오 | — | 상속/미확인 |
| `LurkerAspectMP` | CAbilMorph | `LurkerMPEgg` | 예 | — | 직접 |
| `LurkerAspectMPFromHydraliskBurrowed` | CAbilMorph | `LurkerMPEgg` | 예 | — | 직접 |
| `LurkerDenResearch` | CAbilResearch | `LurkerDenMP` | 예 | — | 직접 |
| `LurkerHoldFire` | CAbilEffectInstant | `LurkerMPBurrowed` | 아니오 | — | 상속/미확인 |
| `LurkerRemoveHoldFire` | CAbilEffectInstant | `LurkerMPBurrowed` | 아니오 | — | 상속/미확인 |
| `MassRecall` | CAbilEffectTarget | `Mothership` | 아니오 | `MassRecallSearch`, `MothershipStrategicRecallSearch` | 상속/미확인 |
| `MedivacHeal` | CAbilEffectTarget | `Medivac` | 아니오 | — | 상속/미확인 |
| `MedivacSpeedBoost` | CAbilEffectInstant | `Medivac` | 아니오 | — | 상속/미확인 |
| `MedivacTransport` | CAbilTransport | `Medivac` | 아니오 | — | 상속/미확인 |
| `MercCompoundResearch` | CAbilResearch | `BarracksTechLab` | 아니오 | — | 상속/미확인 |
| `Mergeable` | CAbilMergeable | `Archon` | 아니오 | — | 상속/미확인 |
| `MorphBackToGateway` | CAbilMorph | `WarpGate` | 아니오 | — | 상속/미확인 |
| `MorphBuildingGatewayWarpGateFree` | CAbilMorph | `Gateway` | 아니오 | — | 상속/미확인 |
| `MorphToBaneling` | CAbilMorph | `Zergling`, `BanelingCocoon`, `ChangelingZergling`, `ChangelingZerglingWings` | 예 | — | 직접 |
| `MorphToBroodLord` | CAbilMorph | `Corruptor`, `BroodLordCocoon` | 예 | — | 직접 |
| `MorphToDevourerMP` | CAbilMorph | `DevourerCocoonMP` | 아니오 | — | 상속/미확인 |
| `MorphToGhostNova` | CAbilMorph | `GhostAlternate` | 아니오 | — | 상속/미확인 |
| `MorphToGuardianMP` | CAbilMorph | `GuardianCocoonMP` | 아니오 | — | 상속/미확인 |
| `MorphToHellion` | CAbilMorph | `HellionTank` | 아니오 | — | 상속/미확인 |
| `MorphToHellionTank` | CAbilMorph | `Hellion` | 아니오 | — | 상속/미확인 |
| `MorphToInfestedTerran` | CAbilMorph | `InfestedTerransEgg` | 아니오 | — | 상속/미확인 |
| `MorphToLurker` | CAbilMorph | `Hydralisk`, `LurkerMPEgg` | 예 | — | 직접 |
| `MorphToMothership` | CAbilMorph | `MothershipCore` | 예 | — | 직접 |
| `MorphToOverseer` | CAbilMorph | `Overlord`, `OverlordTransport`, `OverlordCocoon` | 예 | — | 직접 |
| `MorphToRavager` | CAbilMorph | `Roach`, `RavagerCocoon` | 예 | — | 직접 |
| `MorphToSwarmHostBurrowedMP` | CAbilMorph | `SwarmHostMP`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostBurrowedMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `MorphToSwarmHostMP` | CAbilMorph | `SwarmHostBurrowedMP`, `Drone`, `DroneBurrowed`, `Zergling`, `ZerglingBurrowed`, `Baneling`, `BanelingBurrowed`, `Roach`, `RoachBurrowed`, `Ravager`, `RavagerBurrowed`, `Hydralisk`, `HydraliskBurrowed`, `Infestor`, `InfestorBurrowed`, `SwarmHostMP`, `Ultralisk`, `UltraliskBurrowed`, `Queen`, `QueenBurrowed`, `InfestorTerran`, `InfestorTerranBurrowed`, `ChangelingZergling`, `ChangelingZerglingWings` | 아니오 | — | 상속/미확인 |
| `MorphToTransportOverlord` | CAbilMorph | `Overlord`, `TransportOverlordCocoon` | 예 | — | 직접 |
| `MorphZerglingToBaneling` | CAbilTrain | `Zergling`, `ChangelingZergling`, `ChangelingZerglingWings` | 예 | — | 직접 |
| `MothershipCloak` | CAbilEffectInstant | `Mothership` | 아니오 | `CloakingFieldApplyCasterBehavior` | 상속/미확인 |
| `MothershipCoreEnergize` | CAbilEffectTarget | `MothershipCore` | 아니오 | — | 상속/미확인 |
| `MothershipCoreMassRecall` | CAbilEffectTarget | `MothershipCore` | 아니오 | `MothershipCoreMassRecallPrepare` | 상속/미확인 |
| `MothershipCorePurifyNexus` | CAbilEffectTarget | `MothershipCore` | 아니오 | `MothershipCoreApplyPurifyAB` | 상속/미확인 |
| `MothershipCorePurifyNexusCancel` | CAbilEffectInstant | `MothershipCore` | 아니오 | `MothershipCorePurifyNexusRemove` | 상속/미확인 |
| `MothershipMassRecall` | CAbilEffectTarget | `Mothership` | 아니오 | `MothershipMassRecallPrepare` | 상속/미확인 |
| `MULEGather` | CAbilHarvest | `MULE` | 아니오 | — | 상속/미확인 |
| `MULERepair` | CAbilEffectTarget | `MULE` | 아니오 | `Repair` | 상속/미확인 |
| `NeuralParasite` | CAbilEffectTarget | `Infestor`, `InfestorBurrowed` | 아니오 | `NeuralParasiteLaunchMissile` | 상속/미확인 |
| `NexusInvulnerability` | CAbilEffectTarget | `Nexus` | 아니오 | `NexusInvulnerabilityApplyBehavior` | 상속/미확인 |
| `NexusMassRecall` | CAbilEffectTarget | `Nexus` | 아니오 | `NexusMassRecallSearch` | 상속/미확인 |
| `NexusTrain` | CAbilTrain | `Nexus` | 예 | — | 직접 |
| `NexusTrainMothership` | CAbilTrain | `Nexus` | 예 | — | 직접 |
| `NexusTrainMothershipCore` | CAbilTrain | `Nexus` | 예 | — | 직접 |
| `NydusCanalTransport` | CAbilTransport | `NydusNetwork`, `NydusCanal` | 아니오 | — | 상속/미확인 |
| `NydusWormTransport` | CAbilTransport | `NydusCanal` | 아니오 | — | 상속/미확인 |
| `ObserverMorphtoObserverSiege` | CAbilMorph | `Observer`, `ObserverSiegeMode` | 아니오 | — | 상속/미확인 |
| `ObserverSiegeMorphtoObserver` | CAbilMorph | `ObserverSiegeMode` | 아니오 | — | 상속/미확인 |
| `OracleRevelation` | CAbilEffectTarget | `Oracle` | 아니오 | `OracleRevelationSearch` | 상속/미확인 |
| `OracleStasisTrapActivate` | CAbilEffectInstant | `OracleStasisTrap` | 아니오 | `OracleStasisTrapActivateSet` | 상속/미확인 |
| `OracleStasisTrapBuild` | CAbilBuild | `Oracle` | 아니오 | — | 상속/미확인 |
| `OracleWeapon` | CAbilBehavior | `Oracle` | 아니오 | — | 상속/미확인 |
| `OrbitalCommandLand` | CAbilMorphPlacement | `OrbitalCommandFlying` | 아니오 | — | 상속/미확인 |
| `OrbitalLiftOff` | CAbilMorph | `OrbitalCommand` | 아니오 | — | 상속/미확인 |
| `OverlordTransport` | CAbilTransport | `Overlord`, `OverlordTransport` | 아니오 | — | 상속/미확인 |
| `OverseerMorphtoOverseerSiegeMode` | CAbilMorph | `Overseer`, `OverseerSiegeMode` | 아니오 | — | 상속/미확인 |
| `OverseerSiegeModeMorphtoOverseer` | CAbilMorph | `OverseerSiegeMode` | 아니오 | — | 상속/미확인 |
| `ParasiticBomb` | CAbilEffectTarget | `Viper` | 아니오 | `ParasiticBombLM` | 상속/미확인 |
| `PhasingMode` | CAbilMorph | `WarpPrism` | 아니오 | — | 상속/미확인 |
| `PlacePointDefenseDrone` | CAbilEffectTarget | `Raven` | 아니오 | `PointDefenseDroneReleaseCreateUnit` | 상속/미확인 |
| `ProbeHarvest` | CAbilHarvest | `Probe` | 아니오 | — | 상속/미확인 |
| `ProtossBuild` | CAbilBuild | `Probe` | 예 | — | 직접 |
| `PsiStorm` | CAbilEffectTarget | `HighTemplar` | 아니오 | `PsiStormPersistent` | 상속/미확인 |
| `PurificationNova` | CAbilEffectInstant | `Disruptor`, `DisruptorPhased` | 아니오 | `PurificationNovaSet` | 상속/미확인 |
| `PurificationNovaMorph` | CAbilMorph | `Disruptor` | 아니오 | — | 상속/미확인 |
| `PurificationNovaMorphBack` | CAbilMorph | `DisruptorPhased` | 아니오 | — | 상속/미확인 |
| `PurificationNovaTargeted` | CAbilEffectTarget | `Disruptor` | 아니오 | `PurificationNovaTargettedInitialSet` | 상속/미확인 |
| `PurifyMorphPylon` | CAbilMorph | `Pylon`, `PylonOvercharged` | 아니오 | — | 상속/미확인 |
| `PurifyMorphPylonBack` | CAbilMorph | `PylonOvercharged` | 아니오 | — | 상속/미확인 |
| `QueenBuild` | CAbilBuild | `Queen` | 아니오 | — | 상속/미확인 |
| `QueenMPEnsnare` | CAbilEffectTarget | `QueenMP` | 아니오 | `QueenMPEnsnareLaunchMissile` | 상속/미확인 |
| `QueenMPInfestCommandCenter` | CAbilEffectTarget | `QueenMP` | 아니오 | `QueenMPInfestCommandCenterPersistent` | 상속/미확인 |
| `QueenMPSpawnBroodlings` | CAbilEffectTarget | `QueenMP` | 아니오 | `QueenMPSpawnBroodlingsLaunch` | 상속/미확인 |
| `RavagerCorrosiveBile` | CAbilEffectTarget | `Ravager` | 아니오 | `RavagerCorrosiveBileLaunchSet` | 상속/미확인 |
| `RavenRepairDroneHeal` | CAbilEffectTarget | `RavenRepairDrone` | 아니오 | — | 상속/미확인 |
| `RavenScramblerMissile` | CAbilEffectTarget | `Raven` | 아니오 | `RavenScramblerSwitchInitial` | 상속/미확인 |
| `RavenShredderMissile` | CAbilEffectTarget | `Raven` | 아니오 | `RavenShredderMissileLaunchMissile` | 상속/미확인 |
| `ReactorMorph` | CAbilMorph | `BarracksReactor`, `FactoryReactor`, `StarportReactor` | 아니오 | — | 상속/미확인 |
| `Repair` | CAbilEffectTarget | `SCV` | 아니오 | — | 상속/미확인 |
| `ResourceStun` | CAbilEffectTarget | `Oracle` | 아니오 | `ResourceStunInitialSet` | 상속/미확인 |
| `RoachWarrenResearch` | CAbilResearch | `RoachWarren` | 예 | — | 직접 |
| `RoboticsBayResearch` | CAbilResearch | `RoboticsBay` | 예 | — | 직접 |
| `RoboticsFacilityTrain` | CAbilTrain | `RoboticsFacility` | 예 | `WarpInEffect15` | 직접 |
| `SalvageEffect` | CAbilEffectInstant | `Bunker`, `SensorTower` | 아니오 | `SalvageCombatAB` | 상속/미확인 |
| `SalvageShared` | CAbilBehavior | `Bunker` | 아니오 | — | 상속/미확인 |
| `SapStructure` | CAbilEffectTarget | `Baneling` | 아니오 | `SapStructureIssueAttackOrder` | 상속/미확인 |
| `ScannerSweep` | CAbilEffectTarget | `OrbitalCommand` | 아니오 | — | 상속/미확인 |
| `SCVHarvest` | CAbilHarvest | `SCV`, `MULE` | 아니오 | — | 상속/미확인 |
| `SeekerMissile` | CAbilEffectTarget | `Raven` | 아니오 | `SeekerMissileLaunchMissile` | 상속/미확인 |
| `Shatter` | CAbilEffectTarget | `ForceField` | 아니오 | `Suicide` | 상속/미확인 |
| `ShieldBatteryRechargeChanneled` | CAbilEffectTarget | `ShieldBattery` | 예 | `ShieldBatteryRechargeChanneledSet` | 직접 |
| `ShieldBatteryRechargeEx5` | CAbilEffectTarget | `ShieldBattery` | 예 | — | 직접 |
| `SiegeMode` | CAbilMorph | `SiegeTank` | 아니오 | — | 상속/미확인 |
| `Snipe` | CAbilEffectTarget | `Ghost`, `GhostAlternate`, `GhostNova` | 아니오 | `SnipeDamage` (일부 수정) | 효과 |
| `SpawnChangeling` | CAbilEffectInstant | `Overseer`, `OverseerSiegeMode` | 아니오 | — | 상속/미확인 |
| `SpawningPoolResearch` | CAbilResearch | `SpawningPool` | 예 | — | 직접 |
| `SpawnLarva` | CAbilEffectTarget | `Queen` | 아니오 | `SpawnMutantLarvaApplyTimerBehavior`, `SpawnLarvaSet` | 상속/미확인 |
| `SpawnLocustsTargeted` | CAbilEffectTarget | `SwarmHostMP`, `SwarmHostBurrowedMP` | 아니오 | `LocustMPCreateSet` | 상속/미확인 |
| `SpineCrawlerRoot` | CAbilMorphPlacement | `SpineCrawlerUprooted` | 아니오 | — | 상속/미확인 |
| `SpineCrawlerUproot` | CAbilMorph | `SpineCrawler` | 아니오 | — | 상속/미확인 |
| `SpireResearch` | CAbilResearch | `Spire`, `GreaterSpire` | 예 | — | 직접 |
| `SporeCrawlerRoot` | CAbilMorphPlacement | `SporeCrawlerUprooted` | 아니오 | — | 상속/미확인 |
| `SporeCrawlerUproot` | CAbilMorph | `SporeCrawler` | 아니오 | — | 상속/미확인 |
| `SprayProtoss` | CAbilEffectTarget | `Probe` | 아니오 | — | 상속/미확인 |
| `SprayTerran` | CAbilEffectTarget | `SCV` | 아니오 | — | 상속/미확인 |
| `SprayZerg` | CAbilEffectTarget | `Drone` | 아니오 | — | 상속/미확인 |
| `StargateTrain` | CAbilTrain | `Stargate` | 예 | `WarpInEffect15`, `WarpInEffect` | 직접 |
| `StarportAddOns` | CAbilBuild | `Starport`, `StarportFlying` | 예 | — | 직접 |
| `StarportLand` | CAbilMorphPlacement | `StarportFlying` | 아니오 | — | 상속/미확인 |
| `StarportLiftOff` | CAbilMorph | `Starport` | 아니오 | — | 상속/미확인 |
| `StarportReactorMorph` | CAbilMorph | `BarracksReactor`, `FactoryReactor`, `Reactor` | 아니오 | — | 상속/미확인 |
| `StarportTechLabMorph` | CAbilMorph | `TechLab`, `BarracksTechLab`, `FactoryTechLab`, `StarportTechLab` | 아니오 | — | 상속/미확인 |
| `StarportTechLabResearch` | CAbilResearch | `StarportTechLab` | 예 | — | 직접 |
| `StarportTrain` | CAbilTrain | `Starport` | 예 | — | 직접 |
| `Stimpack` | CAbilEffectInstant | `Marine`, `ChangelingMarineShield`, `ChangelingMarine` | 예 | — | 직접 |
| `StimpackMarauder` | CAbilEffectInstant | `Marauder` | 예 | — | 직접 |
| `StimpackMarauderRedirect` | CAbilRedirectInstant | `Bunker` | 아니오 | — | 상속/미확인 |
| `StimpackRedirect` | CAbilRedirectInstant | `Bunker` | 아니오 | — | 상속/미확인 |
| `stopProtossBuilding` | CAbilStop | `Nexus`, `PylonOvercharged` | 아니오 | — | 상속/미확인 |
| `StopRedirect` | CAbilRedirectInstant | `Bunker` | 아니오 | — | 상속/미확인 |
| `SupplyDepotLower` | CAbilMorph | `SupplyDepot` | 아니오 | — | 상속/미확인 |
| `SupplyDepotRaise` | CAbilMorph | `SupplyDepotLowered` | 아니오 | — | 상속/미확인 |
| `SupplyDrop` | CAbilEffectTarget | `OrbitalCommand` | 아니오 | `SupplyDropApplyTempBehavior` | 상속/미확인 |
| `SwarmHostSpawnLocusts` | CAbilEffectInstant | `SwarmHostBurrowedMP`, `SwarmHostMP` | 아니오 | `LocustMPCreateSet` | 상속/미확인 |
| `TacNukeStrike` | CAbilEffectTarget | `Ghost`, `GhostAlternate`, `GhostNova` | 아니오 | `Nuke` | 상속/미확인 |
| `TechLabMorph` | CAbilMorph | `BarracksTechLab`, `FactoryTechLab`, `StarportTechLab` | 아니오 | — | 상속/미확인 |
| `TempestDisruptionBlast` | CAbilEffectTarget | `Tempest` | 아니오 | `TempestDisruptionBlastSet` | 상속/미확인 |
| `TemplarArchivesResearch` | CAbilResearch | `TemplarArchive` | 예 | — | 직접 |
| `TemporalField` | CAbilEffectTarget | `Mothership`, `MothershipCore`, `Oracle` | 아니오 | `TemporalFieldCreatePersistent`, `TemporalFieldGrowingBubbleCreatePersistent` | 상속/미확인 |
| `TerranBuild` | CAbilBuild | `SCV` | 예 | — | 직접 |
| `ThorAPMode` | CAbilMorph | `Thor` | 아니오 | — | 상속/미확인 |
| `ThorNormalMode` | CAbilMorph | `ThorAP` | 아니오 | — | 상속/미확인 |
| `TimeWarp` | CAbilEffectTarget | `Nexus` | 아니오 | `ChronoBoost`, `TimeWarpCP` | 상속/미확인 |
| `TornadoMissile` | CAbilAugment | `WarHound` | 아니오 | `TornadoMissileCP` | 상속/미확인 |
| `TrainQueen` | CAbilTrain | `Hatchery`, `Lair`, `Hive` | 예 | `QueenBirth` | 직접 |
| `Transfusion` | CAbilEffectTarget | `Queen` | 아니오 | `TransfusionImpactSet` | 상속/미확인 |
| `TransportMode` | CAbilMorph | `WarpPrismPhasing` | 아니오 | — | 상속/미확인 |
| `TwilightCouncilResearch` | CAbilResearch | `TwilightCouncil` | 예 | — | 직접 |
| `UltraliskCavernResearch` | CAbilResearch | `UltraliskCavern` | 예 | — | 직접 |
| `UltraliskWeaponCooldown` | CAbilEffectInstant | `Ultralisk` | 아니오 | — | 상속/미확인 |
| `Unsiege` | CAbilMorph | `SiegeTankSieged` | 아니오 | — | 상속/미확인 |
| `UpgradeToGreaterSpire` | CAbilMorph | `Spire` | 예 | — | 직접 |
| `UpgradeToHive` | CAbilMorph | `Lair` | 예 | — | 직접 |
| `UpgradeToLair` | CAbilMorph | `Hatchery` | 예 | — | 직접 |
| `UpgradeToLurkerDenMP` | CAbilMorph | `HydraliskDen` | 예 | — | 직접 |
| `UpgradeToOrbital` | CAbilMorph | `CommandCenter` | 예 | — | 직접 |
| `UpgradeToPlanetaryFortress` | CAbilMorph | `CommandCenter` | 예 | — | 직접 |
| `UpgradeToWarpGate` | CAbilMorph | `Gateway` | 아니오 | — | 상속/미확인 |
| `ViperConsumeStructure` | CAbilEffectTarget | `Viper` | 아니오 | `ViperConsumeStructureLaunchMissile` | 상속/미확인 |
| `VoidMPImmortalReviveRebuild` | CAbilMorph | `VoidMPImmortalReviveCorpse` | 아니오 | — | 상속/미확인 |
| `VoidRaySwarmDamageBoost` | CAbilEffectInstant | `VoidRay` | 아니오 | — | 상속/미확인 |
| `VoidRaySwarmDamageBoostCancel` | CAbilEffectInstant | `VoidRay` | 아니오 | — | 상속/미확인 |
| `VoidSiphon` | CAbilEffectTarget | `Oracle` | 아니오 | `OracleVoidSiphonPersistentSet` | 상속/미확인 |
| `VolatileBurstBuilding` | CAbilBehavior | `Baneling`, `BanelingBurrowed` | 아니오 | — | 상속/미확인 |
| `Vortex` | CAbilEffectTarget | `Mothership` | 아니오 | `VortexCreatePersistentInitial`, `VortexKillSet` | 상속/미확인 |
| `WarpGateTrain` | CAbilWarpTrain | `WarpGate`, `Gateway` | 예 | — | 직접 |
| `WarpPrismTransport` | CAbilTransport | `WarpPrism`, `WarpPrismPhasing` | 아니오 | — | 상속/미확인 |
| `WidowMineAttack` | CAbilEffectTarget | `WidowMine`, `WidowMineBurrowed` | 아니오 | — | 상속/미확인 |
| `WidowMineBurrow` | CAbilMorph | `WidowMine` | 아니오 | — | 상속/미확인 |
| `WidowMineUnburrow` | CAbilMorph | `WidowMineBurrowed` | 아니오 | — | 상속/미확인 |
| `WorkerStopIdleAbilityVespene` | CAbilEffectTarget | `SCV`, `Drone`, `Probe` | 아니오 | `WorkerChannelStopIdle` | 상속/미확인 |
| `Yamato` | CAbilEffectTarget | `Battlecruiser` | 아니오 | — | 상속/미확인 |
| `Yoink` | CAbilEffectTarget | `Viper` | 아니오 | `YoinkStartSwitch` | 상속/미확인 |
| `ZergBuild` | CAbilBuild | `Drone` | 예 | — | 직접 |

## 3. 자동/지속 행동 정의 (74개)

| 행동 ID | 연결 유닛 | 직접 수정 여부 |
|---|---|---|
| `BanelingExplode` | `Baneling`, `BanelingBurrowed` | 상속/미확인 |
| `BarrierDamageResponse` | `Immortal` | 상속/미확인 |
| `BroodlingAttackDelay` | `BroodlingEscort` | 상속/미확인 |
| `BurrowCracks` | `BanelingBurrowed`, `HydraliskBurrowed` | 상속/미확인 |
| `BypassArmorDroneInitialUnselectable` | `BypassArmorDrone` | 상속/미확인 |
| `BypassArmorDroneTimedLife` | `BypassArmorDrone` | 상속/미확인 |
| `ChangelingDisable` | `ChangelingZealot`, `ChangelingMarineShield`, `ChangelingMarine`, `ChangelingZergling`, `ChangelingZerglingWings` | 상속/미확인 |
| `ChangelingDisguiseEx3` | `Changeling` | 상속/미확인 |
| `CommandCenterKnockbackBehavior` | `CommandCenter`, `OrbitalCommand` | 상속/미확인 |
| `CreepTumorActive` | `CreepTumor`, `CreepTumorBurrowed` | 상속/미확인 |
| `DeathOffCreep` | `Larva` | 상속/미확인 |
| `Detector11` | `Raven`, `MissileTurret`, `Overseer`, `SporeCrawler`, `Observer`, `PhotonCannon`, `ObserverSiegeMode`, `OverseerSiegeMode` | 상속/미확인 |
| `Detector13p75` | `OverseerSiegeMode` | 상속/미확인 |
| `Detector15` | `ObserverSiegeMode` | 상속/미확인 |
| `DigesterCreepSprayFinal` | `NydusCanalCreeper` | 상속/미확인 |
| `FastEnablerGatewayMorphingPowerSource` | `Gateway` | 상속/미확인 |
| `FastEnablerPowerSource` | `WarpGate` | 상속/미확인 |
| `FastEnablerPowerUser` | `PylonOvercharged` | 상속/미확인 |
| `Frenzy` | `Ultralisk`, `UltraliskBurrowed` | 상속/미확인 |
| `GatewayTrainingState` | `Gateway` | 상속/미확인 |
| `HarvestableRichVespeneGeyserGas` | `RefineryRich` | 상속/미확인 |
| `HarvestableRichVespeneGeyserGasProtoss` | `AssimilatorRich` | 상속/미확인 |
| `HarvestableRichVespeneGeyserGasZerg` | `ExtractorRich` | 상속/미확인 |
| `HarvestableVespeneGeyserGas` | `Refinery` | 상속/미확인 |
| `HarvestableVespeneGeyserGasProtoss` | `Assimilator` | 상속/미확인 |
| `HarvestableVespeneGeyserGasZerg` | `Extractor` | 상속/미확인 |
| `ImmortalOverload` | `Immortal` | 행동 수정 |
| `InfestedTerransEggTimedLife` | `InfestedTerransEgg` | 상속/미확인 |
| `IsTransportOverlord` | `OverlordTransport` | 상속/미확인 |
| `LarvaPauseWander` | `Larva` | 상속/미확인 |
| `LarvaWander` | `Larva` | 상속/미확인 |
| `LiberatorInitialMovable` | `LiberatorAG` | 상속/미확인 |
| `makeCreep4x4` | `CreepTumorQueen`, `CreepTumor`, `CreepTumorBurrowed` | 상속/미확인 |
| `makeCreep8x6` | `Hatchery`, `Lair`, `Hive` | 상속/미확인 |
| `MakeCreepNydusAttacker` | `NydusCanalAttacker` | 상속/미확인 |
| `MakeCreepNydusCreeper` | `NydusCanalCreeper` | 상속/미확인 |
| `MassiveVoidRayVulnerability` | `OverlordCocoon` | 상속/미확인 |
| `MothershipLastTargetTracker` | `Mothership` | 상속/미확인 |
| `MothershipTargetFireTracker` | `Mothership` | 상속/미확인 |
| `MuleRepairAutocastCheck` | `MULE` | 상속/미확인 |
| `NexusDeath` | `Nexus` | 상속/미확인 |
| `NydusCreepGrowth` | `NydusCanal` | 상속/미확인 |
| `NydusDestroyerInvulnerability` | `NydusCanalAttacker` | 상속/미확인 |
| `NydusDetect` | `NydusCanal` | 상속/미확인 |
| `NydusWormArmor` | `NydusCanal` | 상속/미확인 |
| `OnCreep` | `SpawningPool`, `EvolutionChamber`, `RoachWarren`, `BanelingNest`, `SpineCrawler`, `SporeCrawler`, `HydraliskDen`, `LurkerDenMP`, `InfestationPit`, `Spire`, `GreaterSpire`, `UltraliskCavern`, `NydusNetwork` | 상속/미확인 |
| `OracleStasisTrapCloak` | `OracleStasisTrap` | 상속/미확인 |
| `PermanentBurrowMoveCloaked` | `RoachBurrowed`, `InfestorBurrowed` | 상속/미확인 |
| `PowerSource` | `Pylon`, `PylonOvercharged` | 상속/미확인 |
| `PowerSourceFast` | `PylonOvercharged` | 상속/미확인 |
| `PowerUserBaseDefenseSmall` | `PhotonCannon` | 상속/미확인 |
| `PowerUserQueue` | `Gateway`, `WarpGate`, `CyberneticsCore`, `Forge`, `TwilightCouncil`, `TemplarArchive`, `DarkShrine`, `RoboticsFacility`, `RoboticsBay`, `Stargate`, `FleetBeacon` | 상속/미확인 |
| `PowerUserQueueSmall` | `ShieldBattery` | 상속/미확인 |
| `QueenMustBeOnCreep` | `Queen` | 상속/미확인 |
| `ReactorQueue` | `Barracks`, `Factory`, `Starport`, `GhostAcademy` | 상속/미확인 |
| `ReaperJump` | `Reaper` | 상속/미확인 |
| `SCVMoveToGatherSeek` | `Refinery`, `Extractor`, `Assimilator`, `AssimilatorRich`, `ExtractorRich`, `RefineryRich` | 상속/미확인 |
| `SensorTowerRadar` | `SensorTower` | 상속/미확인 |
| `SpawnLarva` | `Hatchery`, `Lair`, `Hive` | 상속/미확인 |
| `StalkerIcon` | `TwilightCouncil` | 상속/미확인 |
| `StandardMissile` | `BroodlingEscort` | 상속/미확인 |
| `StasisWardTimedLife` | `OracleStasisTrap` | 상속/미확인 |
| `TerranBuildingBurnDown` | `CommandCenter`, `OrbitalCommand`, `PlanetaryFortress`, `SupplyDepot`, `SupplyDepotLowered`, `Refinery`, `Barracks`, `Factory`, `Starport`, `BarracksReactor`, `FactoryReactor`, `StarportReactor`, `EngineeringBay`, `Armory`, `FusionCore`, `GhostAcademy`, `Bunker`, `MissileTurret`, `SensorTower`, `RefineryRich`, `PointDefenseDrone`, `BarracksFlying`, `AutoTurret`, `FactoryFlying`, `StarportFlying`, `Reactor`, `TechLab`, `CommandCenterFlying`, `OrbitalCommandFlying`, `BypassArmorDrone`, `RavenRepairDrone`, `BarracksTechLab`, `FactoryTechLab`, `StarportTechLab` | 상속/미확인 |
| `TerranStructuresKnockbackBehavior` | `Barracks`, `Factory`, `Starport` | 상속/미확인 |
| `UnderConstruction` | `MissileTurret`, `SensorTower`, `SporeCrawler`, `PhotonCannon` | 상속/미확인 |
| `WarpPrismLoadupDecelerationFix` | `WarpPrism` | 상속/미확인 |
| `WarpPrismPowerSource` | `WarpPrismPhasing` | 상속/미확인 |
| `WidowMineArmed` | `WidowMineBurrowed` | 상속/미확인 |
| `WidowMineBurrowedCloakingBehavior` | `WidowMineBurrowed` | 상속/미확인 |
| `WidowMineDrillingClawsTracker` | `WidowMine`, `WidowMineBurrowed` | 상속/미확인 |
| `WorkerPeriodicRefineryCheck` | `Refinery`, `Extractor`, `Assimilator`, `AssimilatorRich`, `ExtractorRich`, `RefineryRich` | 상속/미확인 |
| `ZergBuildingDies6` | `SpawningPool`, `EvolutionChamber`, `RoachWarren`, `BanelingNest`, `HydraliskDen`, `LurkerDenMP`, `InfestationPit`, `Spire`, `GreaterSpire`, `UltraliskCavern`, `NydusNetwork` | 상속/미확인 |
| `ZergBuildingDies9` | `Hatchery`, `Lair`, `Hive` | 상속/미확인 |
| `ZergBuildingNotOnCreep` | `SpawningPool`, `EvolutionChamber`, `RoachWarren`, `BanelingNest`, `SpineCrawler`, `SporeCrawler`, `HydraliskDen`, `LurkerDenMP`, `InfestationPit`, `Spire`, `GreaterSpire`, `UltraliskCavern`, `NydusNetwork` | 상속/미확인 |

## 4. 집계 및 한계

- 상속/미확인: 241개
- 원본 미해결: 2개
- 직접: 67개
- 효과: 1개
- 원본 UnitData ID 미해결: —
- 카드 후보에는 제거된 역사적 능력이 포함될 수 있으므로 실제 사용 가능 판정으로 해석하지 않음.
- 효과 연결의 하위 검색/지속 피해/회복/행동·업그레이드 연결은 별도 수치 감사에서 확인.

## 5. 조사한 원본 blob SHA

| 계층 | UnitData | AbilData |
|---|---|---|
| core | a11dd056a0ed9f48799402d15ddca275656f390a | 88171a8d2765457aebfd4ca516d31fbc03e2b013 |
| liberty | 9975201c741b30686eeb2dbb33b5040cc3ada973 | bac69fecea9eb9fc8393b55a21ccd44945362307 |
| libertymulti | ef3562a1045dabc8f3cac227c03e4494572e40e6 | b2df4f7115039288923aa7136769aff61563853a |
| swarm | f5e1dd33da9efe1caec3194a162722b91c9a837d | 6bde3de75507e59e355cdc77ab773ef35296d613 |
| swarmmulti | 9011b6476f86a1439333c109dea4fd8cd00e2772 | 62a08ed6f7bd4f1dd6ff75200aece9aad37be5f3 |
| void | 5a64983c70ea4de17ea860d794aec3f94f1d5720 | 5d2eec0a6c5899614e1c666184f9d6e515ae3e12 |
| voidmulti | f0876d434b3469ef67ff6a46a80aaad21e997102 | 7bd2fa3a6f946275d691ad71fa99984bfe00c53c |
