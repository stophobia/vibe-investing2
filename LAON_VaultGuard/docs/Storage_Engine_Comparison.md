# Storage Engine Comparison — SQLite vs RocksDB

> 🇰🇷 LAON VaultGuard v0.4 → v0.5 스토리지 마이그레이션 검토.  
> 🇺🇸 Storage engine evaluation for migrating from JSON files to embedded DB.

> **현재 상태**: 파일 기반 JSON 저장소 (`readFileSync` / `writeFileSync`).  
> **문제점**: 동시성 제어 미비 — read-modify-write TOCTOU 경쟁 상태로 데이터 손실 위험 (§8.1 #1).  
> **목표**: 크로스플랫폼 임베디드 DB로 마이그레이션하여 동시성·무결성·성능 확보.

---

## 1. 현재 JSON 파일 저장소의 한계

| 문제 | 설명 | 심각도 |
|------|------|--------|
| **TOCTOU** | `readJson → modify → writeJson` 패턴이 원자적이지 않음. API 요청과 스케줄러가 동시에 `findings.json`에 쓰면 마지막 write만 살아남음 | 상 |
| **전체 파일 재작성** | finding 1건 추가에도 전체 `findings.json`(1,450+행)을 직렬화·재작성 → O(n) | 중 |
| **파일 락 없음** | Node.js `fs` 동기 호출은 프로세스 내 스레드 안전하지만, 외부 프로세스나 `fs.rename`과 경쟁 가능 | 하 |
| **질의(query) 불가** | 필터·집계·날짜 범위 검색 시 매번 전체 파일을 파싱해야 함 | 중 |
| **스키마 검증 없음** | JSON 파싱만 하고 필드 타입/필수값 검증 누락 → 손상된 파일 감지 불가 | 중 |

---

## 2. 후보 1: SQLite (`better-sqlite3`)

### 2.1 아키텍처

- **유형**: 관계형, 서버리스, 파일 기반
- **저장 구조**: B-Tree (기본) + WAL (Write-Ahead Log) 모드
- **트랜잭션**: ACID (Atomic, Consistent, Isolated, Durable)
- **동시성 모델**: WAL 모드 → **무제한 concurrent reader + 1 writer**. Writer는 queueing (serialized).

```
WAL 모드 동작:
  Reader ──→ 읽기: main DB file + WAL file 병합 조회
  Writer ──→ 쓰기: WAL file에 append-only → checkpoint 시 main DB에 병합
  동시 reader: 무제한 (blocking 없음)
  동시 writer: 1개 (SQLITE_BUSY 반환, 5ms default retry)
```

### 2.2 성능 특성

| 항목 | 수치 |
|------|------|
| **단일 INSERT** | ~10µs (메모리), ~0.1ms (디스크 WAL) |
| **단일 SELECT (PK)** | ~5µs (인덱스 룩업) |
| **범위 스캔 (100행)** | ~50µs (B-Tree 순회) |
| **초당 INSERT** | ~50,000~200,000 (batch, WAL) |
| **초당 SELECT** | ~200,000+ (인덱스 기준) |
| **동시 read 10개** | 거의 무제한 (WAL 모드), write는 직렬화 |
| **데이터 10MB → 디스크** | ~10MB (ZSTD 압축 미적용, 별도 설정) |

**LAON VaultGuard 부하 프로파일** (예측):
- 스캔당 finding: 0~100건
- 일일 스캔 횟수: 4~24회 (스케줄러 + 수동)
- 일일 INSERT: ~0~2,400건 → **SQLite WAL 모드로 자원 과잉 없이 충분히 처리 가능**

### 2.3 Node.js 바인딩: `better-sqlite3`

```typescript
// synchronous API — Node.js 이벤트 루프 차단 없음 (C++ addon, 빠름)
import Database from 'better-sqlite3';

const db = new Database('./data/vaultguard.db');
db.pragma('journal_mode = WAL');       // 동시성 활성화
db.pragma('busy_timeout = 5000');      // writer 대기 시간
db.pragma('foreign_keys = ON');        // 참조 무결성

// 트랜잭션으로 원자적 read-modify-write
const updateAck = db.transaction((id: string, note: string) => {
  const row = db.prepare('SELECT * FROM findings WHERE id = ?').get(id);
  if (!row) return;
  db.prepare('UPDATE findings SET acknowledged = 1, acknowledged_note = ? WHERE id = ?').run(note, id);
});
updateAck('F-abc123', 'false positive');
```

| 특성 | 설명 |
|------|------|
| **API** | 동기 (C++ addon, libuv 블로킹 아님) |
| **npm 주간 다운로드** | ~4M+ |
| **번들 크기** | 0 외부 의존성 (`prebuildify`로 바이너리 사전 빌드) |
| **Node.js 버전** | ≥14 |
| **TypeScript** | `@types/better-sqlite3` 공식 지원 |

### 2.4 크로스플랫폼 호환성

| OS | 아키텍처 | 사전 빌드 | 비고 |
|----|----------|-----------|------|
| **macOS** | arm64 (M1~M4) | ✅ | 사전 빌드 바이너리 |
| **macOS** | x64 (Intel) | ✅ | 사전 빌드 바이너리 |
| **Linux** | x64 (glibc) | ✅ | 사전 빌드 바이너리 |
| **Linux** | arm64 (glibc) | ✅ | 사전 빌드 바이너리 |
| **Linux** | musl (Alpine) | ✅ | 사전 빌드 바이너리 |
| **Windows** | x64 | ✅ | 사전 빌드 바이너리 (MSVC) |

> `npm install better-sqlite3` → `node-gyp` 자동 실행. C++17 컴파일러 필요 (Xcode CLT / gcc 8+ / MSVC 2017+).  
> 사전 빌드 바이너리가 있으면 컴파일 스킵. 모든 주요 플랫폼 커버.

### 2.5 LAON VaultGuard 적합성

| 장점 | 단점 |
|------|------|
| 이미 Database.md에 SQLite 마이그레이션 계획 명시 | writer 1개 제한 — 초당 수천 건 INSERT는 불가능 (LAON 사용량에서는 무관) |
| ACID 트랜잭션으로 TOCTOU 문제 완전 해결 | RDBMS — 스키마 설계 필요 (마이그레이션 비용) |
| SQL 질의로 대시보드 필터·집계 즉시 구현 | |
| 0 외부 의존성, 파일 하나로 백업 가능 | |
| WAL 모드로 읽기 논블로킹 | |
| 커뮤니티, 문서, 도구 생태계 최상 | |

---

## 3. 후보 2: RocksDB (`rocksdb` / `level-rocksdb`)

### 3.1 아키텍처

- **유형**: Key-Value, LSM-Tree (Log-Structured Merge)
- **저장 구조**: MemTable → SST files (Sorted String Table, level-compaction)
- **트랜잭션**: MVCC + Optimistic Transaction (Snapshot Isolation)
- **동시성 모델**: Multi-threaded 읽기·쓰기 (내부 동시성, writer 간 충돌은 optimistic lock)

```
LSM-Tree 구조:
  Write → MemTable (in-memory) → flush → Level 0 SST → compaction → Level 1, 2, ...
  Read  → MemTable + Level 0 SSTs (bloom filter 필터링) + Level 1+ SSTs
  Bloom Filter: 99.9% miss 제거, read 증폭 방지
```

### 3.2 성능 특성

| 항목 | 수치 |
|------|------|
| **단일 PUT** | ~5µs (MemTable write) |
| **단일 GET** | ~10µs (MemTable + bloom filter) |
| **범위 스캔 (100건)** | ~0.3ms (SST scan) |
| **초당 PUT** | ~200,000~1,000,000 (batch, SSD) |
| **초당 GET** | ~500,000+ (hot key in MemTable) |
| **동시 read 10개** | 병렬 (multi-threaded, MVCC snapshot) |
| **데이터 10MB → 디스크** | ~4MB (Snappy 압축, 기본 ON) |

**RocksDB의 강점은 write-heavy workload**. LAON VaultGuard는 read-dominant + write-rare → LSM-tree의 write 최적화가 오버스펙.

### 3.3 Node.js 바인딩

| 패키지 | API | 유지보수 |
|--------|-----|----------|
| `rocksdb` (Level/community) | LevelDB 호환 (async callback + promise) | 활발, Node ≥16 |
| `level-rocksdb` (Level org) | LevelDB 호환 | 중간 |
| `@aspect-build/rules_rocksdb` | Bazel 통합 | 특수 목적 |

```typescript
// level-rocksdb 예시 (LevelDB API 호환)
import { RocksDB } from 'level-rocksdb';

const db = new RocksDB('./data/vaultguard-rocks');
await db.open();

// Key-Value로만 접근
await db.put('finding:F-abc123', JSON.stringify(finding));
const row = JSON.parse(await db.get('finding:F-abc123'));

// 범위 스캔 (prefix scan)
for await (const [key, value] of db.iterator({ gte: 'finding:', lte: 'finding:\xff' })) {
  // ...
}

// Batch (atomic)
const batch = db.batch();
batch.put('finding:1', ...).put('finding:2', ...);
await batch.write();
```

### 3.4 크로스플랫폼 호환성

| OS | 아키텍처 | 사전 빌드 | 비고 |
|----|----------|-----------|------|
| **macOS** | arm64 | ⚠️ | `rocksdb` npm 패키지는 소스 컴파일 필요 (20~30분). Homebrew `rocksdb`로 우회 가능 |
| **macOS** | x64 | ⚠️ | 동일 |
| **Linux** | x64 | ⚠️ | `sudo apt install librocksdb-dev` 후 npm install |
| **Linux** | arm64 | ⚠️ | 크로스 컴파일 어려움 |
| **Windows** | x64 | ❌ | `vcpkg` + MSVC + CMake 필요. 공식 지원 미흡 |

> RocksDB npm 패키지는 **바이너리 사전 빌드를 제공하지 않음**.  
> 모든 플랫폼에서 C++17 + CMake + gflags + Snappy + ZSTD 전체 툴체인 컴파일 필요.  
> **CI/CD 파이프라인에서 빌드 시간 20~40분 추가**.  
> Windows 빌드는 특히 까다로움 (UTF-8 경로, long path, MSVC linker).

### 3.5 LAON VaultGuard 적합성

| 장점 | 단점 |
|------|------|
| 압축 내장 (Snappy/ZSTD) → 디스크 절약 | 빌드 복잡도 심각 — Node.js 프로젝트에 과도한 C++ 의존성 |
| 쓰기 처리량이 SQLite보다 훨씬 높음 | Key-Value 모델 — finding 필터·집계·조인 직접 구현 필요 (2차 인덱스 손수 관리) |
| 멀티스레드 읽기 (MVCC) → 동시성 우수 | npm 생태계 미성숙 — 문서·예제·커뮤니티 모두 SQLite보다 부족 |
| Meta/Google 수준의 엔지니어링 | **LAON VaultGuard의 작업부하에 완전한 오버킬** — 일일 2,400건 INSERT |
| | 스키마 마이그레이션 불가 — key prefix 재설계 필요 시 전체 DB 재작성 |
| | Windows 호환성 문제 (npm install 실패 가능성 높음) |

---

## 4. Head-to-Head 비교

| 평가 항목 | SQLite (better-sqlite3) | RocksDB (level-rocksdb) | JSON 파일 (현행) |
|------------|------------------------|------------------------|-------------------|
| **동시성** | WAL: 무제한 reader + 1 writer | MVCC: 다중 reader + optimistic writer | ❌ TOCTOU 경쟁 |
| **데이터 무결성** | ✅ ACID 트랜잭션 | ✅ Snapshot Isolation | ❌ 없음 |
| **쓰기 성능** | 충분 (50K/s) | 과잉 (200K+/s) | O(n) 전체 재작성 |
| **읽기 성능** | 우수 (200K/s) | 우수 (500K/s) | O(n) 전체 파싱 |
| **질의 능력** | ✅ SQL | ❌ Key-Value 직접 구현 | ❌ 없음 |
| **npm 설치** | ✅ 사전 빌드 (5초) | ❌ 소스 컴파일 (20~40분) | N/A |
| **파일 크기 (10MB)** | ~10MB | ~4MB (Snappy) | ~10MB |
| **메모리 사용** | ~2MB (기본 캐시) | ~50MB+ (MemTable + block cache + bloom) | 전체 파일 메모리 로드 |
| **macOS** | ✅✅ | ⚠️ |
| **Linux** | ✅✅ | ⚠️ |
| **Windows** | ✅ | ❌ |
| **스키마 마이그레이션** | ✅ `ALTER TABLE` | ❌ key prefix 재설계 |
| **백업** | `.dump` / 파일 복사 | Checkpoint + 파일 복사 | 파일 복사 |
| **생태계 성숙도** | ✅✅✅ (세계 최다 배포 DB) | ✅ (Meta/Google) | N/A |

---

## 5. 성능 벤치마크 (예측 시뮬레이션)

> LAON VaultGuard 시나리오: `findings` 테이블 10,000행, 동시 5 reader + 1 writer.

| 작업 | SQLite WAL | RocksDB | JSON 파일 |
|------|-----------|---------|-----------|
| finding 1건 저장 | 0.1ms | 0.05ms | 3~5ms (1,450행 파일 재작성) |
| finding 전체 조회 (100건) | 0.5ms | 1.2ms (prefix scan) | 2~4ms (JSON.parse) |
| finding acknowledge (UPDATE 1건) | 0.1ms (WAL write) | 0.1ms (PUT) | 3~5ms (전체 재작성) |
| finding 날짜 범위 검색 | 0.3ms (인덱스) | 1~3ms (prefix scan + filter) | 2~4ms (전체 파싱 → filter) |
| 동시 10 FINDING 저장 | 5~10ms (serialized) | 2~5ms (병렬) | ❌ 데이터 손실 가능 |
| 동시 100 FINDING 저장 | 50~100ms (serialized) | 20~50ms (병렬) | ❌ 데이터 손실 확정 |
| 동시 5 reader | 0.5ms×5 = 즉시 | 0.3ms×5 = 즉시 | 2ms×5 (경쟁만 무손실) |
| 디스크 10,000행 | ~1.5MB | ~0.6MB (Snappy) | ~2MB |

### 핵심 인사이트

1. **둘 다 JSON보다 10~100배 빠름** — 이건 기본 전제.
2. **SQLite와 RocksDB의 성능 차이는 LAON 규모에서 무의미** — 0.05ms vs 0.1ms는 사용자가 체감할 수 없음.
3. **RocksDB의 write 최적화는 LAON에 불필요** — LSM-tree는 초당 수만 건 write가 필요한 워크로드에서 빛을 발함. LAON은 초당 0.1건 미만의 write.
4. **SQLite의 SQL 질의 능력이 실질적 가치** — 대시보드에서 "최근 7일 critical finding", "레포지토리별 탐지 통계" 같은 쿼리를 코드 한 줄로 처리 가능.

---

## 6. 종합 평가 및 권장

### 권장: **SQLite (`better-sqlite3`)**

| 이유 | 설명 |
|------|------|
| **이미 계획됨** | Database.md v0.2 마이그레이션 로드맵에 명시. 팀이 이미 SQLite 방향에 합의. |
| **동시성 해결** | WAL 모드로 `findings.json` TOCTOU 문제 완전 해결. 동시 reader 무제한. |
| **npm 설치 5초** | 사전 빌드 바이너리. macOS/Linux/Windows 모두 `npm install` 한 번으로 완료. CI/CD 추가 설정 없음. |
| **SQL 질의** | 대시보드 필터·집계·통계를 코드 1~2줄로 구현. Key-Value DB는 인덱스 설계부터 직접 해야 함. |
| **파일 기반** | `data/vaultguard.db` 단일 파일. 현재 JSON 파일들과 동일한 백업·이관 전략 사용 가능. |
| **ACID** | 트랜잭션으로 `bulkAcknowledge` 같은 작업을 원자적으로 처리. 부분 실패 걱정 없음. |
| **생태계** | Drizzle ORM, Knex 마이그레이션, DB Browser for SQLite 등 도구 풍부. |
| **Windows** | ✅ 사전 빌드 바이너리로 즉시 사용 가능. RocksDB의 Windows 빌드는 CI에서 실패할 가능성이 높음. |

### RocksDB 선택이 유리한 경우 (LAON에는 해당 안 됨)

- 초당 10,000건 이상의 write가 지속되는 워크로드
- 100GB 이상의 대용량 데이터셋
- 이미 C++ 툴체인이 갖춰진 빌드 환경
- Key-Value 접근 패턴만으로 충분하고 SQL 질의가 필요 없는 경우

### 마이그레이션 전략

```bash
# 1. better-sqlite3 설치
npm install better-sqlite3
npm install --save-dev @types/better-sqlite3

# 2. 스키마 생성 (src/db-sqlite.ts)
#    - repositories, findings, scan_runs, alert_config, audit_log 테이블

# 3. 기존 JSON → SQLite 마이그레이션 스크립트
npx tsx src/migrate-json-to-sqlite.ts

# 4. API 라우트에서 JSON readJson/writeJson → db.prepare().run()으로 교체
# 5. npm run typecheck → npm run build → npm test
```

> 상세 스키마는 [Database.md §SQLite 마이그레이션 계획](./Database.md#sqlite-마이그레이션-계획-v02) 참고.

---

## 7. 추가 고려: RocksDB 없이 가는 대안

RocksDB는 Facebook/Meta 규모의 인프라를 위해 설계된 엔진입니다. LAON VaultGuard처럼 소규모 임베디드 도구에는 다음과 같은 이유로 과도합니다:

1. **빌드 복잡도** — `npm install` 한 번에 20~40분 컴파일. Windows에서는 `vcpkg` + MSVC + CMake 전체 툴체인이 필요하며, macOS/Linux에서도 `gflags`, `Snappy`, `lz4`, `zstd` 등 시스템 라이브러리를 사전 설치해야 함.
2. **Key-Value 한계** — finding을 `repoId` 기준으로 필터링하려면 복합 prefix key(`finding:${repoId}:${id}`)를 설계하고 2차 인덱스를 수동으로 유지해야 함. SQL이면 `SELECT * FROM findings WHERE repoId = ?` 한 줄.
3. **메모리 사용량** — RocksDB는 성능을 위해 MemTable(64MB 기본), Block Cache(8MB), Bloom Filter(10bit/key)가 필요. 최소 50~100MB. SQLite는 2MB 캐시로 시작.
4. **복구 난이도** — SST 파일이 손상되면 복구 도구가 제한적. SQLite는 `sqlite3 vaultguard.db ".recover"` 한 줄로 복구 가능.

### 결론: SQLite 단일 채택

RocksDB를 추가하면 유지보수 부담만 늘어납니다. **SQLite 하나로 모든 요구사항을 충족**할 수 있습니다. 두 엔진을 모두 지원하는 "플러그인 아키텍처"는 코드 복잡도 대비 실익이 없습니다.

---

> *"가장 좋은 도구는 가장 적합한 도구다. 가장 강력한 도구가 아니다."*
