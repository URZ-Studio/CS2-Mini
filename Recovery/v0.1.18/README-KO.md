# MiniCraft Recovery v0.1.18 (staged rebuild)
기준: 저장 성공한 MiniCraft-II-DataOnly.SC2Mod. 기존 게시용 파일은 백업 후 유지.
이 패키지는 Triggers, Triggers.version, Lib*_h.galaxy를 직접 생성하지 않는다.
Galaxy Editor가 라이브러리 가져오기 및 저장을 통해 해당 파일들을 생성하도록 한다.

## 1단계 - 초기화
1. DataOnly 모드 복사본을 에디터에서 연다.
2. F6 트리거 편집기 → 라이브러리 우클릭 → 라이브러리 가져오기 → Stage1-Probe.SC2Lib.
3. 스크립트에서 초기화 함수가 MCR_ProbeInit인지 확인한다. 필요 시 지정한다.
4. Ctrl+F12 컴파일, 저장. 비공개 테스트 경기 채팅에 [MiniCraft] Trigger init OK가 출력되는지 확인.
5. 실패 시 생성된 Triggers, Triggers.version, Lib*.galaxy와 정확한 컴파일 오류를 수집한다.

## 2단계 - 시작 메뉴/인구/자원
1단계와 다른 DataOnly 복사본을 사용한다. 두 라이브러리를 한 복사본에 넣지 않는다.
에디터를 닫고 Stage2/Base.SC2Data/TriggerLibs/MiniCraftRecovery.galaxy를 복사본의 동일 상대 경로에 복사한다.
에디터에서 Stage2-Menu.SC2Lib를 가져온다. 초기화 함수 MCR_MenuInit 확인 후 컴파일 및 저장.
메뉴: 인구 200/300/400/500, 자원 100/150/200/300/500%. 20 게임초 후 자동 적용.
경기 멈춤, 꿀광 교체, 생산 배수, 일꾼 면제 및 강화 AI는 이번 테스트에 포함하지 않는다.
게임 안에서 인구 및 자원 실제 적용 여부를 테스트해야 한다.

## 가져오기 실패시 수동 대체
F6에서 새 사용자 지정 스크립트를 하나 만들고 Stage1의 Probe.galaxy 내용을 붙여넣어 초기화 함수 MCR_ProbeInit를 지정한다.
2단계는 코드 한 줄 include "TriggerLibs/MiniCraftRecovery"와 초기화 함수 MCR_MenuInit만 입력한다.
같은 모드에서 자동 생성기 Build-MiniCraft.bat를 다시 실행하지 않는다.
기존 AI 및 full builder는 유지한다. Galaxy Editor 실행/실제 게임 검증은 아직 하지 못했다.

## 0.1.18a: import source truncation
The editor screenshot shows missing bool/void prefixes in generated code. SC2Lib ScriptCode now uses multiline indented blocks and CRLF. This is a candidate fix; editor import is not tested. For reliable diagnosis, open Bootstrap in trigger editor and replace the entire script with Stage1-Probe.galaxy directly, not the generated-code preview. Verify generated bool/void declarations and closing braces before compiling. The previous ZIP remains obsolete; use these individual files. Stage2 native argument order also corrected.
