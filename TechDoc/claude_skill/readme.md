# Claude Skills — 퀀트 투자 워크플로우

**2026.07.05 Dennis Kim**

> Claude에게 반복 가능한 퀀트 투자 점검 절차를 가르치는 Agent Skills을 만들었습니다. 이제는 헤지펀드에서 사용하는 퀀트 알고리즘에 따라 시장을 분석하고 내 포트폴리오를 관리하세요.
> "LLM은 엑셀이지 오라클이 아니다" — 모델의 재량이 아닌 명시적 규칙으로 투자 판단 재료를 생성하고 데이터 기반으로 분석할 프레임워크를 만듭니다.

이 폴더는 [Anthropic Agent Skills](https://github.com/anthropics/skills) 표준으로 만든
두 개의 투자 분석 스킬과, 스킬 제작 방법을 다룬 가이드 문서를 담고 있습니다.

---

## 문서 구성

| 파일 | 내용 | 이런 분께 |
|---|---|---|
| **[Claude_skill_guide.md](./Claude_skill_guide.md)** | Claude Skill 개념·구조·제작 방법 종합 가이드. 두 스킬의 설계 배경과 흔한 실수 교정표 포함 | Skill이 처음이거나 직접 만들고 싶은 분 |
| **[quant-market-brief_guide.md](./quant-market-brief_guide.md)** | 시황 브리핑 스킬의 설치 방법 + 전체 파일 전문 + 커스터마이징 | 스킬을 바로 설치·수정하려는 분 |
| **[portfolio-daily-review_guide.md](./portfolio-daily-review_guide.md)** | 포트폴리오 리뷰 스킬의 설치 방법 + 전체 파일 전문 + 트리거 스크립트 테스트 절차 | 〃 |
| `quant-market-brief.skill` | 시황 브리핑 스킬 설치 패키지 (zip 포맷) | 바로 업로드용 |
| `portfolio-daily-review.skill` | 포트폴리오 리뷰 스킬 설치 패키지 (zip 포맷) | 바로 업로드용 |

**읽는 순서 추천**: Skill 개념이 궁금하면 `Claude_skill_guide.md` →
설치가 목적이면 각 스킬의 `*_guide.md`로 바로 이동하세요.

---

## 스킬 소개

### 1. quant-market-brief — 퀀트 시황 브리핑

"오늘 장 어땠어?" 한 마디로 뉴스 나열이 아닌 **구조화된 레짐 브리핑**을 받습니다. 시장을 공포와 탐욕에 바라보지 말고 데이터 기반으로 바라봐야 합니다.

- **레짐 판정**: Risk-On / Risk-Off / Rotation / Chop 중 하나로 명시적 분류 (+확신도)
- **팩터 스코어카드**: 모멘텀·성장/가치·대형/소형·퀄리티 4축 판정
- **델타 중심**: "어제와 달라진 것"만 서술, 반증 조건 필수 포함
- **웹 검색 강제**: 학습 데이터의 기억이 아닌 실시간 데이터로만 답변

→ **설치 및 상세 설명: [quant-market-brief_guide.md](./quant-market-brief_guide.md)**

### 2. portfolio-daily-review — 포트폴리오 데일리 리뷰

포트폴리오를 등록해두면 하루 한 번, **정량 트리거가 발동한 종목만** 심층 평가합니다.

- **정량 트리거 (T1~T5)**: 급변동·한도 위반·중대 이벤트 등 "변동"의 정의를 규칙으로 고정
- **트리거 없으면 침묵**: "이상 없음" 한 줄로 종료 — 매일 쏟아지는 분석 노이즈 차단
- **3-소스 교차검증**: 퀀트 / 뉴스 / SNS를 독립 수집 후 매트릭스로 일치도 판정
- **액션 후보 + 반증 조건**: 유지/축소/확대/손절검토/관찰 중 후보 제시, 반대 논거와 반증 조건 필수
- **상태 저장**: `portfolio.json`에 보유 내역·리스크 한도·리뷰 로그 유지

→ **설치 및 상세 설명: [portfolio-daily-review_guide.md](./portfolio-daily-review_guide.md)**

### 함께 쓰기 (아침 루틴)

```
1. "오늘 시황 요약해줘"   → quant-market-brief가 레짐 판정
2. "포트폴리오 리뷰해줘"  → portfolio-daily-review가 같은 대화의
                            레짐 판정을 퀀트 소스로 재사용
```

레짐 판정 줄이 고정 형식이라 스킬 간 자동 연결됩니다. 브리핑이 없으면
리뷰 스킬이 약식 레짐 판정으로 대체합니다.

---

## 빠른 설치

### Claude.ai (웹/앱, 유료 플랜)

1. 이 폴더의 `.skill` 파일을 다운로드
2. **Settings → Capabilities → Skills** 에서 업로드
3. 새 대화에서 "오늘 시황 요약해줘" / "포트폴리오 리뷰해줘"로 발동 확인

### Claude Code

```bash
git clone https://github.com/gameworkerkim/vibe-investing.git
cd vibe-investing/TechDoc/claude_skill
# .skill은 zip 포맷이므로 압축 해제 후 개인 스킬 폴더로 복사
unzip quant-market-brief.skill -d ~/.claude/skills/
unzip portfolio-daily-review.skill -d ~/.claude/skills/
```

### Claude API

[Skills API Quickstart](https://docs.claude.com/en/api/skills-guide#creating-a-skill) 참고.
`.skill` 패키지를 그대로 업로드하면 됩니다.

>  **portfolio-daily-review 설치 후 필수**: `assets/portfolio.json`은 샘플입니다.
> 첫 대화에서 "포트폴리오 갱신해줘"라고 하거나 파일을 직접 수정해 본인 보유 내역으로
> 교체하세요. 자세한 스키마는 [설치 가이드 4장](./portfolio-daily-review_guide.md#4-초기-설정-중요) 참조.

---

## 왜 스킬인가? — 프롬프트 대비 장점

### 1. 재량을 제거한다

"많이 빠진 것 같으면 분석해줘"는 매번 다른 결과를 냅니다. 이 스킬들은
판단 기준을 파일로 고정합니다 — 트리거는 `trigger-rules.md`의 정량 규칙(±3%,
한도 위반 등)과 Python 스크립트로, 출력은 고정 템플릿으로. **같은 입력이면
같은 절차**가 보장됩니다. LLM을 오라클(신탁)이 아닌 엑셀(계산 절차)로 쓰는 방식입니다.

### 2. 프롬프트를 매번 다시 쓰지 않는다

잘 다듬은 워크플로우가 폴더에 저장되어 있으므로, 트리거 문구 한 마디면
전체 절차(웹 검색 → 팩터 판정 → 교차검증 → 액션 후보)가 자동 실행됩니다.
긴 프롬프트를 복사해 붙이거나 지난 대화를 뒤질 필요가 없습니다.

### 3. 상태가 유지된다

포트폴리오, 리스크 한도, 리뷰 로그가 `portfolio.json`에 저장됩니다.
매번 보유 내역을 재입력하지 않고, 리뷰 로그 덕분에 "어제와의 델타"를
추적할 수 있습니다. 대화가 바뀌어도 상태는 파일에 남습니다.

### 4. 컨텍스트를 아낀다 (Progressive Disclosure)

스킬의 이름·설명만 항상 로드되고, 본문과 참조 문서(팩터 체크리스트,
센티먼트 가이드 등)는 **필요할 때만** 읽힙니다. 긴 지침을 시스템 프롬프트에
욱여넣는 것보다 훨씬 효율적이며, 지침이 길어져도 대화 품질이 저하되지 않습니다.

### 5. 노이즈를 설계로 차단한다

LLM은 물어보면 항상 뭔가를 길게 답하려는 경향이 있습니다. 이 스킬은
"트리거 미발동 시 한 줄로 종료"를 제1 규칙으로 명시해, **분석이 필요 없는 날엔
분석하지 않습니다.** 시장 동조 필터(지수와 같이 움직인 변동은 약식 보고)도
같은 목적입니다. 매일 장문 리포트가 오는 것은 정보가 아니라 노이즈입니다.

### 6. 편향 방지 장치가 내장되어 있다

- 퀀트/뉴스/SNS를 **독립 수집 후 교차검증** — 한 소스가 결론을 지배하지 못함
- SNS 극단 쏠림은 **역지표 후보**로만 취급, 방향 신호로 쓰지 않음
- 모든 액션 후보에 **반대 논거 필수**, 모든 판정에 **반증 조건 필수**
- 가격보다 **투자 논거(thesis) 유효성을 먼저** 점검

### 7. 버전 관리와 공유가 된다

스킬은 텍스트 파일 폴더이므로 Git으로 diff·리뷰·롤백이 가능하고,
`.skill` 파일 하나로 다른 사람과 워크플로우 전체를 공유할 수 있습니다.
프롬프트 노하우가 개인 메모가 아닌 **버전 관리되는 자산**이 됩니다.

---

## 면책

- 두 스킬의 출력은 **투자 판단 재료이며 투자 자문이 아닙니다.** 최종 결정과 책임은 사용자에게 있습니다.
- 스킬은 데모/교육 목적으로 제공되며, 실제 사용 전 자신의 환경에서 충분히 테스트하세요.
- `portfolio.json`에 계좌번호·인증정보 등 민감정보를 넣지 마시고, 실제 포트폴리오 파일은 공개 저장소에 커밋하지 마세요 (`.gitignore` 권장).

---

## 참고 링크

- [anthropics/skills — 공식 Skills 저장소](https://github.com/anthropics/skills)
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [Creating custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Agent Skills 표준](http://agentskills.io)
