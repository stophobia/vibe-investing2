# Claude Skill System — 아키텍처 분석

## 개요

Anthropic의 "스킬" 시스템은 특정 작업 유형에 대한 베스트 프랙티스를 모듈화한 RAG 유사 패턴이다.

## 아키텍처

```
/mnt/skills/
├── public/           ← Anthropic 제공 내장 스킬
│   ├── docx/SKILL.md
│   ├── pdf/SKILL.md
│   ├── pptx/SKILL.md
│   ├── xlsx/SKILL.md
│   ├── frontend-design/SKILL.md
│   └── product-self-knowledge/SKILL.md
├── user/             ← 사용자 업로드 커스텀 스킬
│   └── imagegen/SKILL.md (예시)
├── examples/         ← 예제 스킬
│   └── skill-creator/SKILL.md
└── private/          ← 비공개 스킬 (읽기 전용)
```

## 작동 방식

### 1. 트리거
```
Before creating any file, writing any code, or running any bash command, 
first view the relevant SKILL.md files.

This check is unconditional: don't first decide whether the task "needs" 
a skill; the skills themselves define what they cover.
```

### 2. 매핑
```
Task → Skill:
- presentations / slide decks → pptx/SKILL.md
- spreadsheets / financial models → xlsx/SKILL.md
- reports / essays / Word documents → docx/SKILL.md
- creating or filling PDFs → pdf/SKILL.md
- React / Vue / frontend components → frontend-design/SKILL.md
- Anthropic product questions → product-self-knowledge/SKILL.md
- creating new skills → skill-creator/SKILL.md
```

### 3. 실행
```
1. {available_skills} 목록 스캔
2. 모든 관련 가능성 있는 SKILL.md 읽기 (복수 가능)
3. skill의 지침에 따라 작업 수행
```

## 왜 스킬 시스템이 필요한가?

```
skills encode environment-specific constraints (available libraries, 
rendering quirks, output paths) that aren't in Claude's training data, 
so skipping the skill read lowers output quality even on formats Claude 
already knows well.
```

→ 모델의 학습 데이터에 없는 환경별 제약사항(라이브러리 버전, 렌더링 특이사항, 출력 경로 등)을 보완.

## 디자인 원칙

1. **선제적 읽기 (Preemptive Reading)**: 작업 전 무조건 읽기. "필요한가?" 판단하지 않음
2. **복수 스킬 조합**: 하나의 작업에 여러 스킬이 필요할 수 있음
3. **무조건적(Unconditional)**: 모든 파일 생성/코드 작성/bash 실행 전 체크
4. **사용자 스킬 우선**: `/mnt/skills/user/`의 사용자 스킬은 매우 높은 관련성

## Agent 개발에 적용할 점

이 스킬 시스템은 다음과 같이 일반화할 수 있다:

```
1. 작업 유형별 "플레이북" 작성 (SKILL.md)
   - 환경별 제약사항 명시
   - 트라이얼앤에러로 축적된 베스트 프랙티스
   - 구체적인 라이브러리 버전, 명령어 예시

2. 작업 전 자동 로딩
   - 작업 의도를 분석하여 관련 플레이북 식별
   - 프롬프트에 주입

3. 지속적 개선
   - 새로운 실패 사례 발견 시 플레이북 업데이트
   - skill-creator 패턴으로 셀프 개선 가능
```

## Skill Creator 패턴

Claude는 자신의 스킬을 생성하는 메타 스킬도 가지고 있다:
```
skill-creator → 새로운 스킬 생성/업데이트 가이드
```
→ 자기 개선이 가능한 폐쇄 루프 시스템.
