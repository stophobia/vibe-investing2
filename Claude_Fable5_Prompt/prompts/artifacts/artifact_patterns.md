# Claude Fable 5 — Artifacts 패턴

## Persistent Storage API (window.storage)

Claude Fable 5에서 아티팩트는 `window.storage` API를 통해 세션 간 데이터 지속성을 제공한다.

### API 메서드
```javascript
await window.storage.get(key, shared?)   // → {key, value, shared} | null
await window.storage.set(key, value, shared?)  // → {key, value, shared} | null
await window.storage.delete(key, shared?)  // → {key, deleted, shared} | null
await window.storage.list(prefix?, shared?)  // → {keys, prefix?, shared} | null
```

### 사용 예시
```javascript
// 개인 데이터 저장 (shared=false, 기본값)
await window.storage.set('entries:123', JSON.stringify(entry));

// 공유 데이터 저장 (모든 사용자에게 표시)
await window.storage.set('leaderboard:alice', JSON.stringify(score), true);

// 데이터 조회
const result = await window.storage.get('entries:123');
const entry = result ? JSON.parse(result.value) : null;

// 프리픽스로 키 목록 조회
const keys = await window.storage.list('entries:');
```

### 키 설계 패턴
```
계층적 키: table_name:record_id (예: "todos:todo_1")
- 200자 미만
- 공백, 경로 구분자(/ \), 따옴표(' ") 금지
- 함께 업데이트되는 데이터는 단일 키로 결합
  예: cards, benefits, completion → cards-and-benefits 단일 키
```

### 에러 처리
```javascript
// 저장 작업 (성공해야 함)
try {
  const result = await window.storage.set('key', data);
  if (!result) console.error('Storage operation failed');
} catch (error) {
  console.error('Storage error:', error);
}

// 키 존재 확인
try {
  const result = await window.storage.get('might-not-exist');
  // 키 존재, result.value 사용
} catch (error) {
  console.log('Key not found:', error);
}
```

### 제한 사항
```
- 텍스트/JSON 데이터만 (파일 업로드 불가)
- 키 200자 미만, 공백/슬래시/따옴표 금지
- 값당 5MB 제한
- 속도 제한 있음 (관련 데이터는 단일 키로 배치)
- 동시 업데이트는 last-write-wins
- shared 파라미터 항상 명시
```

## CRITICAL: Browser Storage 제한

```
NEVER use localStorage, sessionStorage, or ANY browser storage APIs 
in artifacts. These APIs are NOT supported.

대신 사용:
- React: useState, useReducer
- HTML: JavaScript variables/objects
- 모든 데이터는 세션 중 메모리에 유지
```

## React 아티팩트 라이브러리

```javascript
// 사용 가능한 라이브러리 (Claude Fable 5 기준)
import { useState } from "react";
import { Camera } from "lucide-react";          // lucide-react@0.383.0
import { LineChart, XAxis } from "recharts";
import * as math from 'mathjs';
import _ from 'lodash';
import * as d3 from 'd3';
import * as Plotly from 'plotly';
import * as THREE from 'three';                 // r128
import Papa from 'papaparse';
import * as XLSX from 'xlsx';
import { Alert } from '@/components/ui/alert';  // shadcn/ui
import * as Chart from 'chart.js';
import * as Tone from 'tone';
import * as mammoth from 'mammoth';
import * as tf from 'tensorflow';
```

### Three.js 주의사항
```
- THREE.OrbitControls 사용 불가 (CDN 미호스팅)
- THREE.CapsuleGeometry 사용 불가 (r142+ 기능, r128에서는 CylinderGeometry 등으로 대체)
```

## Claude Completions in Artifacts

아티팩트 내에서 Anthropic API를 직접 호출 가능 ("Claude in Claude"):

```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",  // 항상 Sonnet 4 사용
    max_tokens: 1000,
    messages: [
      { role: "user", content: "Your prompt here" }
    ]
  })
});
const data = await response.json();
const claudeResponse = data.content[0].text;
```

### 대화 이력 유지 (중요)
```
Claude는 완료 간 메모리가 없으므로, 모든 이전 메시지를 포함해야 함:

const history = [
  { role: "user", content: "Hello" },
  { role: "assistant", content: "Hi!" },
];
const newMsg = { role: "user", content: "New question" };
messages: [...history, newMsg];
```

### MCP 서버 사용
```javascript
body: JSON.stringify({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1000,
  messages: [...],
  mcp_servers: [
    {
      type: "url",
      url: "https://mcp.asana.com/sse",
      name: "asana-mcp"
    }
  ]
})
```

### 웹 검색 도구 사용
```javascript
body: JSON.stringify({
  ...
  tools: [
    {
      type: "web_search_20250305",
      name: "web_search"
    }
  ]
})
```
