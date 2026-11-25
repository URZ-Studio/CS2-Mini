# MiniCraft AI v0.1.9 — 실험용 활성화 및 검증

이 모듈은 기존 섬멸전 AI에 운영 보조 로직을 추가합니다. 현재 Galaxy 네이티브 컴파일/실제 게임 검증은 하지 못했습니다. 초기화가 연결되지 않으면 순정 AI 그대로 동작합니다.

## 적용 (최초 1회)

1. 기존 Build-MiniCraft.bat 실행. 자동 백업 후 모드 구성 요소 폴더의 Base.SC2Data/TriggerLibs/MiniCraftAI.galaxy가 갱신됩니다.
2. 에디터에서 기존 MiniCraft 구성 요소 폴더를 열고 트리거 모듈(F6)에서 모드용 라이브러리를 생성하거나 기존 전용 라이브러리를 선택합니다.
3. 라이브러리에 Custom Script 요소를 추가하고 아래 코드를 넣습니다. 에디터가 외부 스크립트를 인식하도록 가져오기 관리자/구성 요소 경로를 확인합니다.

```galaxy
include "TriggerLibs/MiniCraftAI"
```

4. Custom Script의 Initialization Function에 `MiniCraftAI_Init`를 지정합니다(함수명만). 해당 입력란이 없는 경우 맵 초기화 트리거의 Custom Script 액션에서 `MiniCraftAI_Init();`를 한 번 호출합니다. 중복 호출은 방지되어 있습니다. include 방식이 인식되지 않을 경우 Galaxy 파일 본문을 Custom Script에 붙여넣는 수동 대안도 있으나 이후에는 직접 갱신해야 합니다.
5. 스크립트 검사 후 저장 및 비공개 게시. 오류 발생 시 기존 백업으로 돌아가고 컴파일 오류 전문을 기록합니다. **에디터가 외부 파일을 저장 과정에서 누락시키는지도 확인하십시오.**
6. 기존 섬멸전 초기화/AI 시작을 제거하지 않습니다. 정예(비치터), 핸디캡 100%로 비교 테스트합니다. 기존 치터 난이도의 보너스를 제거하는 모드는 아닙니다.

## 정책 및 안전장치

- 4 게임 초 주기, 활성 컴퓨터 및 섬멸전 기지가 있는 경우만 처리.
- AI stock 목표 배율 2.0/2.5는 절대값 설정으로 적용. 반복 곱셈 금지. 순정 난이도별 스크립트에서 해당 API를 읽는지는 테스트 대상.
- 생산/건설 요청은 AITechCount(대기열 포함), 내부 요청 대기열, 시간 제한을 확인. 건설 요청 간 최소 12 게임 초, 병력 요청 간 최소 4 게임 초, 확장 시도 간 최소 100 게임 초.
- 저그는 추가 부화장·여왕을 요청하지만 자동 애벌레 생성 또는 주입 성공은 엔진 AI가 담당.
- 적 공중 유닛은 AIKnownUnitCount로 확인. 전 맵 적 유닛을 직접 검색하지 않음.
- 시야/회피/수리/가스/후퇴 등의 기본 난이도 플래그 활성화, APM 600 시범 상한. 실제 난이도 선택 UI는 바꾸지 않음.
- 실제 유닛/건물 생성, 무료 자원, 기존 플레이어 데이터 조작, 기존 AI 대기열 강제 삭제 없음.

## 실게임 검수표

| 검수 | 판정 |
|---|---|
| 에디터 스크립트 검사 통과 | 미검증 |
| 모드 저장/재게시 후 초기화 메시지 확인 | 미검증 |
| 테란/저그/프로토스 각각 5·10·15분 광물·가스 비교 | 미검증 |
| 생산시설 및 실제 생산량 비교 | 미검증 |
| 보급 막힘 및 건설 동선 | 미검증 |
| 4대4 이상 성능 및 AI 요청 충돌 | 미검증 |

스크립트 변수 mcai_debug를 true로 설정하면 60 게임 초마다 에디터 디버그 출력에 각 AI 플레이어의 자원·기지 수와 누적 요청 횟수를 남깁니다. 이 값은 **요청 횟수이지 성공한 생산 횟수가 아닙니다.** 실제 유닛 수와 건설 수는 관전자/리플레이에서 함께 확인합니다.

## 참고

- [AISetStockArmyDefaultScale](https://mapster.talv.space/galaxy/reference/ai-set-stock-army-default-scale)
- [AIBuild](https://mapster.talv.space/galaxy/reference/ai-build)
- [AITrain](https://mapster.talv.space/galaxy/reference/ai-train)
- [AITechCount](https://mapster.talv.space/galaxy/reference/ai-tech-count)
- [AIKnownUnitCount](https://mapster.talv.space/galaxy/reference/ai-known-unit-count)
- [에디터 모드 및 라이브러리 가이드](https://s2editor-guides.readthedocs.io/New_Tutorials/01_Introduction/007_Creating_Mods/)
