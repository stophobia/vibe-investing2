# Microsoft Qlib 시작 가이드 — 한국 개발자를 위한 완전판 (토스 Open API 연동 테스트 중)

> 최종 검증일: 2026-07-05 (microsoft/qlib main 브랜치 기준)
> 대상 독자: Python 개발 경험이 있고 퀀트/ML 백테스트 환경을 처음 구축하는 한국 개발자

---

## 1. Qlib 프로젝트 개요

**Qlib**는 마이크로소프트 리서치(MSRA)가 2020년 9월 오픈소스로 공개한 **AI 지향 퀀트 투자 플랫폼**(AI-oriented Quantitative Investment Platform)이다. 데이터 처리, 모델 훈련, 백테스트로 이어지는 전체 ML 파이프라인을 포함하며, 알파 발굴 → 리스크 모델링 → 포트폴리오 최적화 → 주문 집행에 이르는 퀀트 투자 전 과정을 커버한다.

지원하는 학습 패러다임은 세 가지로 정의 될 수 있다. 자비로운 마이크로소프트 리서치 팀에서 개발하다가 정말 올인원으로 확장한 케이스이다.

| 패러다임 | 용도 | 대표 구현 |
| :--- | :--- | :--- |
| 지도 학습 (Supervised Learning) | 복잡한 비선형 시장 패턴 발굴 | LightGBM, GRU, Transformer 등 25종+ |
| 시장 동적 모델링 (Market Dynamics) | 개념 표류(concept drift) 대응, 비정상성 적응 | DDG-DA, Rolling Retraining |
| 강화 학습 (Reinforcement Learning) | 연속적 매매 의사결정, 주문 집행 최적화 | PPO, OPDS (order execution) |

여기에 **RD-Agent**(LLM 기반 자율 R&D 에이전트)가 결합되어 팩터 발굴과 모델 최적화를 자동화하는 방향으로 진화 중이다. 관련 논문은 "R&D-Agent-Quant: A Multi-Agent Framework for Data-Centric Factors and Model Joint Optimization" (arXiv:2505.15155).

프로젝트 규모: GitHub Star 약 40,000+, Fork 6,000+ (2026년 기준). Python 퀀트 오픈소스 중 최상위권. 이 이하는 별로 볼 필요가 없다.

---

## 2. 핵심 장점

### 2.1 올인원(All-in-One) 파이프라인
데이터 처리 → 팩터 연산 → 모델 훈련 → 백테스트 → 리포트 분석 → 온라인 서빙까지 하나의 프레임워크에서 처리한다. zipline(백테스트만), backtrader(전략 실행만), 별도 팩터 라이브러리를 조합하던 기존 워크플로우 대비 통합 비용이 크게 줄어든다.

### 2.2 검증된 고성능 데이터 인프라
Qlib는 금융 시계열에 특화된 바이너리 저장 포맷과 2단 캐시(ExpressionCache, DatasetCache)를 자체 설계했다. 공식 벤치마크(800종목 × 14개 팩터, 2007–2020 일봉, 1 CPU 기준)


| 저장 방식 | 소요 시간(초) | Qlib 풀캐시 대비 |
| :--- | ---: | ---: |
| MySQL | 365.3 ± 7.5 | 약 49배 느림 |
| InfluxDB | 368.2 ± 3.6 | 약 50배 느림 |
| MongoDB | 253.6 ± 6.7 | 약 34배 느림 |
| HDF5 | 184.4 ± 3.7 | 약 25배 느림 |
| Qlib (캐시 없음) | 147.0 ± 8.8 | 약 20배 느림 |
| Qlib (+ExpressionCache) | 47.6 ± 1.0 | 약 6배 느림 |
| **Qlib (+Expression +Dataset 캐시)** | **7.4 ± 0.3** | 기준 |

64 CPU 병렬 환경에서는 캐시 없이도 8.8초, ExpressionCache만으로 4.2초까지 단축된다. 범용 DB는 다층 인터페이스와 불필요한 포맷 변환 때문에 금융 데이터 로딩에서 구조적으로 불리하다는 것이 MSRA의 분석이다.
이 지점은 나 역시 동의한다. ExpressionCache의 성능은 정말 금융 퀀트에서 압도적이다. 

### 2.3 표현식 기반 팩터 엔진
`Ref($close, 1)/$close - 1` 같은 문자열 표현식으로 팩터를 정의하면 엔진이 자동으로 벡터화 연산과 캐싱을 처리한다. pandas로 직접 rolling/shift를 조합하는 것보다 코드가 짧고, 캐시 재사용 덕분에 반복 실험에서 특히 빠르다.

### 2.4 논문 재현 가능한 모델 동물원 (Model Zoo)
LightGBM, XGBoost, CatBoost 같은 GBDT 계열부터 LSTM, GRU, ALSTM, GATs, Transformer, Localformer, TRA, TCN, ADARNN, ADD, IGMTF, HIST, KRNN, Sandwich, TabNet, DoubleEnsemble, TCTS, SFM, TFT까지 25종 이상의 SOTA 모델이 동일한 데이터셋(Alpha158/Alpha360)과 동일한 백테스트 조건에서 비교 가능한 형태로 구현되어 있다. "논문 수치를 직접 재현해볼 수 있는 유일한 퀀트 프레임워크"라는 평가가 과장이 아니다.

### 2.5 시장 비정상성(Non-stationarity) 대응 도구 내장
금융 데이터의 분포 변화(regime change)에 대응하는 Rolling Retraining과 메타러닝 기반 DDG-DA가 벤치마크와 함께 제공된다. 이 부분은 다른 오픈소스 백테스터에는 거의 없는 Qlib 고유 영역이다.

### 2.6 RD-Agent를 통한 자동화 R&D
LLM이 팩터 가설 생성 → 코드 구현 → 백테스트 → 결과 평가 → 개선 루프를 자율 수행한다. 리서치 리포트(PDF)에서 팩터를 추출해 구현하는 시나리오도 지원한다. 데모: rdagent.azurewebsites.net

---

## 3. 유사 프로젝트 비교

| 프로젝트 | 성격 | Qlib 대비 포지션 |
| :--- | :--- | :--- |
| **zipline / zipline-reloaded** | 이벤트 기반 백테스터 | 백테스트 전용. ML 파이프라인, 팩터 엔진 없음. Quantopian 폐쇄 후 커뮤니티 유지 |
| **backtrader** | 이벤트 기반 백테스터 | 전략 로직 구현에 강점, ML 통합은 수작업. 국내 사용자 많음 |
| **vectorbt** | 벡터화 백테스터 | 속도는 매우 빠르나 팩터 리서치·모델 훈련 프레임워크 아님 |
| **QuantConnect (LEAN)** | 클라우드 퀀트 플랫폼 | 실거래 연동 강점, C#/Python. 오픈 리서치 재현성은 Qlib 우위 |
| **Qbot / QuantMind / qlib-learning** | Qlib 기반 상위 응용 | Qlib를 코어 엔진으로 쓰는 파생 프로젝트. 빠른 체험용 |

정리하면 Qlib는 **"AI 모델 리서치 + 백테스트 통합"** 이라는 포지션에서 사실상 경쟁자가 없다. 반면 **실거래 주문 연동**(브로커 API)은 범위 밖이므로, 실전 매매까지 가려면 별도 집행 레이어를 직접 구축해야 한다.

---

## 4. 설치 (Getting Started)

### 4.1 환경 요구사항

| 항목 | 내용 |
| :--- | :--- |
| OS | Linux, Windows, macOS (Linux 권장 — `run_all_model.py` 등 일부 스크립트는 Linux 전용) |
| Python | **3.8 ~ 3.12** 공식 지원 |
| 패키지 관리 | Conda 강력 권장 (시스템 Python 사용 시 헤더 파일 누락으로 빌드 실패 가능) |
| 필수 의존성 | numpy, cython, lightgbm, pytorch(딥러닝 모델 사용 시) |

```bash
conda create -n qlib python=3.10
conda activate qlib
```

### 4.2 설치 방법 3가지

**방법 1: pip (안정 버전, 권장)**
```bash
pip install pyqlib
```

**방법 2: 소스 설치 (main 브랜치 최신 기능 필요 시)**
```bash
pip install numpy
pip install --upgrade cython

git clone https://github.com/microsoft/qlib.git && cd qlib
pip install .            # 개발 참여 시: pip install -e ".[dev]"
```
> 주의: 과거 문서의 `python setup.py install` 방식은 deprecated 되었다. 반드시 `pip install .`을 사용할 것.

**방법 3: Docker (환경 격리)**
```bash
docker pull pyqlib/qlib_image_stable:stable
docker run -it --name qlib -v <로컬 디렉토리>:/app pyqlib/qlib_image_stable:stable
```

**Apple Silicon (M1/M2/M3) Mac 사용자**: LightGBM 빌드가 OpenMP 의존성 누락으로 실패할 수 있다. 먼저 `brew install libomp` 실행 후 설치할 것.

**설치 확인**:
```python
import qlib
print(qlib.__version__)   # 0.9.x
```

### 4.3 데이터 준비 — 중요 변경사항

> **[2026년 현재 상태]** 데이터 보안 정책 강화로 **공식 데이터 다운로드 스크립트가 일시 중단**되었다. 공식 README가 안내하는 대체 경로는 커뮤니티(chenditc)가 유지하는 investment_data 저장소이다. 구버전 문서의 `python scripts/get_data.py qlib_data_cn ...` 명령은 더 이상 작동을 보장하지 않는다.

**권장: 커뮤니티 데이터셋 (중국 A주, TuShare 기반, 일 단위 갱신)**
```bash
wget https://github.com/chenditc/investment_data/releases/latest/download/qlib_bin.tar.gz
mkdir -p ~/.qlib/qlib_data/cn_data
tar -zxvf qlib_bin.tar.gz -C ~/.qlib/qlib_data/cn_data --strip-components=1
rm -f qlib_bin.tar.gz
```

**공식 스크립트 (복구 시 사용 가능, Yahoo Finance 크롤러 기반)**
```bash
# 일봉
python -m qlib.cli.data qlib_data --target_dir ~/.qlib/qlib_data/cn_data --region cn
# 1분봉
python -m qlib.cli.data qlib_data --target_dir ~/.qlib/qlib_data/cn_data_1min --region cn --interval 1min
```

**데이터 무결성 검사** (필수 습관으로 권장):
```bash
python scripts/check_data_health.py check_data --qlib_dir ~/.qlib/qlib_data/cn_data
```

### 4.4 초기화

```python
import qlib
from qlib.constant import REG_CN   # 구버전: qlib.config — 현재는 qlib.constant

provider_uri = "~/.qlib/qlib_data/cn_data"
qlib.init(provider_uri=provider_uri, region=REG_CN)
```

`region`은 `REG_CN`(중국), `REG_US`(미국), `REG_TW`(대만)를 지원한다. region 설정은 데이터 경로뿐 아니라 **거래 제약 규칙**(중국의 상하한가, T+1, 최소 거래단위 등)에도 영향을 미치므로, 커스텀 시장 데이터를 쓸 때는 백테스트 설정에서 거래 규칙을 반드시 별도 검토해야 한다.

---

## 5. 첫 번째 워크플로우 실행

### 5.1 qrun으로 자동 실행 (설정 파일 기반)

`qrun`은 데이터셋 구축 → 모델 학습 → 시그널 생성 → 백테스트 → 평가를 YAML 하나로 자동화한다.

```bash
cd examples    # 주의: qlib 소스 루트 디렉토리에서 실행하면 import 충돌 발생
qrun benchmarks/LightGBM/workflow_config_lightgbm_Alpha158.yaml
```

실행 결과 예시 (CSI300 + Alpha158 + LightGBM, 공식 README 기준):

```
'The following are analysis results of the excess return without cost.'
annualized_return   0.178316    # 연 환산 초과수익 17.83%
information_ratio   1.996555
max_drawdown       -0.081806

'The following are analysis results of the excess return with cost.'
annualized_return   0.128982    # 거래비용 반영 시 12.90%
information_ratio   1.444287
max_drawdown       -0.091078
```

거래비용 반영 전후로 연 수익률이 약 5%p 차이 나는 것에 주목할 것. **비용 미반영 백테스트 수치를 그대로 믿으면 안 되는 이유**를 프레임워크가 기본 출력으로 보여준다.

### 5.2 코드 기반 커스텀 워크플로우

qrun의 자동 워크플로우가 맞지 않으면 모듈 단위로 직접 조립할 수 있다. 최소 예제:

```python
import qlib
from qlib.constant import REG_CN
from qlib.utils import init_instance_by_config
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, PortAnaRecord

qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region=REG_CN)

market = "csi300"
benchmark = "SH000300"

data_handler_config = {
    "start_time": "2008-01-01",
    "end_time": "2020-08-01",
    "fit_start_time": "2008-01-01",
    "fit_end_time": "2014-12-31",
    "instruments": market,
}

task = {
    "model": {
        "class": "LGBModel",
        "module_path": "qlib.contrib.model.gbdt",
        "kwargs": {"loss": "mse", "num_leaves": 210, "learning_rate": 0.05},
    },
    "dataset": {
        "class": "DatasetH",
        "module_path": "qlib.data.dataset",
        "kwargs": {
            "handler": {
                "class": "Alpha158",
                "module_path": "qlib.contrib.data.handler",
                "kwargs": data_handler_config,
            },
            "segments": {
                "train": ("2008-01-01", "2014-12-31"),
                "valid": ("2015-01-01", "2016-12-31"),
                "test":  ("2017-01-01", "2020-08-01"),
            },
        },
    },
}

model = init_instance_by_config(task["model"])
dataset = init_instance_by_config(task["dataset"])

with R.start(experiment_name="my_first_workflow"):
    model.fit(dataset)
    R.save_objects(trained_model=model)
    rec = R.get_recorder()
    SignalRecord(model, dataset, rec).generate()   # 예측 시그널 저장
```

### 5.3 표현식 엔진으로 데이터 직접 조회

```python
from qlib.data import D

# 단순 조회
df = D.features(
    ["SH600000"],
    ["$close", "$volume"],
    start_time="2020-01-01", end_time="2020-12-31", freq="day",
)

# 표현식으로 팩터 즉석 정의: 5일 모멘텀, 20일 변동성
df = D.features(
    D.instruments("csi300"),
    ["Ref($close, 5)/$close - 1", "Std($close/Ref($close,1)-1, 20)"],
    start_time="2019-01-01", end_time="2020-12-31",
)
```

이 표현식 문자열이 곧 팩터 정의이며, 결과는 ExpressionCache에 캐시되어 두 번째 호출부터 극적으로 빨라진다.

### 5.4 그래픽 리포트

```bash
python -m pip install ".[analysis]"
jupyter notebook examples/workflow_by_code.ipynb
```
> 구버전 문서의 `examples/estimator/analyze_from_estimator.ipynb` 경로는 폐기되었다.

노트북에서 확인 가능한 리포트: 그룹별 누적수익, 롱숏 수익 분포, IC/월별 IC, 시그널 자기상관, 포트폴리오 백테스트 수익 곡선.

---

## 6. 벤치마크 — 모델별 성능 비교

### 6.1 데이터셋 이해: Alpha158 vs Alpha360

| 데이터셋 | 특징 | 적합 모델 |
| :--- | :--- | :--- |
| **Alpha158** | 사람이 설계한 158개 팩터 (전형적 피처 엔지니어링). 피처 간 공간적 관계 약함 | GBDT 계열 (LightGBM, CatBoost 등) |
| **Alpha360** | 최근 60일 원시 가격/거래량 그대로 (피처 엔지니어링 최소). 시간축 공간 관계 강함 | 딥러닝 계열 (GRU, ALSTM, TRA 등) |

이 구분이 중요한 이유: **테이블 데이터에서는 GBDT가, 원시 시계열에서는 신경망이 유리**하다는 일반 ML 상식이 Qlib 벤치마크에서도 그대로 재현된다. 자신의 팩터 성격에 따라 모델 계열을 골라야지, "요즘 뜨는 모델"을 무조건 쓰는 것은 비효율적이다.

### 6.2 시장 동적 적응 벤치마크 (CSI500, Alpha158, 2017.01–2020.08 롤링)

공식 benchmarks_dynamic 수치:

| 모델 | IC | ICIR | Rank IC | 연환산 수익 | IR | MDD |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| RR[Linear] (롤링 재학습) | 0.0945 | 0.5989 | 0.1069 | 8.57% | 1.368 | -9.86% |
| DDG-DA[Linear] | 0.0983 | 0.6157 | 0.1108 | 7.64% | 1.190 | -7.69% |
| RR[LightGBM] | 0.0816 | 0.5887 | 0.0912 | 7.71% | 1.320 | -9.09% |
| **DDG-DA[LightGBM]** | **0.0878** | **0.6185** | **0.0975** | **12.61%** | **2.010** | **-7.44%** |

포인트: DDG-DA(메타러닝 기반 분포 적응)를 LightGBM에 결합하면 단순 롤링 재학습 대비 연 수익 +4.9%p, IR 1.32 → 2.01로 개선된다. **동일 모델이라도 시장 변화 적응 전략에 따라 성과가 크게 갈린다**는 것이 Qlib 벤치마크의 핵심 교훈이다.

### 6.3 전체 모델 비교표

25개+ 모델의 Alpha158/Alpha360 성능 비교표는 다음에서 유지·갱신된다:
`https://github.com/microsoft/qlib/blob/main/examples/benchmarks/README.md`

여러 모델을 한 번에 돌려 직접 비교하려면 (Linux 전용)
```bash
python run_all_model.py run 10          # 전체 모델 10회 반복
python run_all_model.py run 3 lightgbm Alpha158 csi500   # 특정 모델/데이터셋/유니버스
```
랜덤성이 있는 딥러닝 모델은 최소 20회 반복 후 평균을 볼 것을 공식 문서가 권장한다. **단일 실행 결과로 모델 우열을 판단하는 것은 통계적으로 무의미하다.**

---

## 7. 한국 개발자를 위한 실전 섹션: KRX 데이터 연동

Qlib는 한국 시장을 공식 지원하지 않는다(region은 CN/US/TW만 존재). 그러나 CSV → Qlib 바이너리 변환 도구(`dump_bin.py`)가 있어 KOSPI/KOSDAQ 데이터를 붙이는 것은 어렵지 않다.
토스 Open API를 붙이는 것은 그리 어렵지 않다. 

### 7.1 pykrx로 데이터 수집 → CSV 생성

```python
# pip install pykrx
from pykrx import stock
import pandas as pd, os

os.makedirs("csv_kr", exist_ok=True)
tickers = stock.get_market_ticker_list(market="KOSPI")

for t in tickers[:50]:   # 예시: 상위 50종목
    df = stock.get_market_ohlcv("20180101", "20260630", t)
    df = df.reset_index().rename(columns={
        "날짜": "date", "시가": "open", "고가": "high",
        "저가": "low", "종가": "close", "거래량": "volume",
    })
    df["symbol"] = t
    # Qlib 관례: 수정주가 계산용 factor 컬럼 (미수정 데이터면 1.0)
    df["factor"] = 1.0
    df.to_csv(f"csv_kr/{t}.csv", index=False)
```

### 7.2 Qlib 바이너리로 변환

```bash
python scripts/dump_bin.py dump_all \
    --csv_path ./csv_kr \
    --qlib_dir ~/.qlib/qlib_data/kr_data \
    --include_fields open,close,high,low,volume,factor \
    --date_field_name date --symbol_field_name symbol
```

### 7.3 한국 데이터 사용 시 필수 체크리스트

| 항목 | 내용 |
| :--- | :--- |
| **수정주가(factor)** | pykrx 기본 OHLCV는 수정주가 반영 방식 확인 필요. 액면분할/배당락 미반영 데이터로 백테스트하면 수익률이 왜곡된다 |
| **거래 규칙** | region=REG_CN을 쓰면 중국 상하한가(±10%)와 T+1 규칙이 적용된다. 한국(±30% 가격제한, T+0 회전 가능)과 다르므로 백테스트 executor 설정을 커스터마이즈할 것 |
| **거래정지/상장폐지** | 생존 편향(survivorship bias) 방지를 위해 상장폐지 종목 포함 데이터 확보가 이상적. pykrx는 현재 상장 종목 중심이므로 한계 인지 필요 |
| **캘린더** | 한국 휴장일 캘린더가 자동 생성되는지 `~/.qlib/qlib_data/kr_data/calendars/day.txt` 확인 |
| **벤치마크 지수** | KOSPI200 지수를 별도 심볼로 넣어 백테스트 benchmark로 지정 |
| **Alpha158 팩터** | 팩터 정의 자체는 시장 중립적이므로 한국 데이터에도 그대로 적용 가능. 단, 검증은 한국 시장에서 다시 해야 함 (중국 CSI300 IC가 한국에서 재현된다는 보장 없음) |

---

## 8. 주의점 (Pitfalls) — 실전에서 반드시 만나는 문제들

### 8.1 환경/설치 관련

1. **소스 루트에서 import 금지**: qlib 저장소 루트 디렉토리에서 `import qlib`를 실행하면 로컬 폴더가 패키지를 가려 `ModuleNotFoundError: No module named 'qlib.data._libs.rolling'` 오류가 난다. 반드시 `cd examples` 후 실행하거나 다른 경로에서 작업할 것.
2. **pandas 2.x 호환성**: pandas 1.5 → 2.0에서 `groupby`의 `group_key` 기본값이 변경되어 일부 예제(TRA dataset, TFT, RL order execution 스크립트)가 오류를 낼 수 있다. 공식 대응이 있지만 완전하지 않으므로, 문제가 생기면 pandas 버전을 고정(`pandas<2.0`)하는 것이 빠른 우회책이다.
3. **TFT 모델은 Python 3.6~3.7 + tensorflow 1.15 전용**: 최신 환경에서 돌아가지 않는다. 벤치마크별로 requirements.txt가 다르므로 모델마다 확인할 것.
4. **Redis 없어도 동작**: Redis 미연결 시 캐시 일부가 비활성화될 뿐 핵심 기능은 정상이다. 단, 이미 Redis를 쓰다가 락이 꼬이면 `QlibCacheException` 발생 — Redis 키 삭제로 해결.
5. **multiprocessing 오류 (Windows)**: `RuntimeError: An attempt has been made to start a new process...`는 Windows에서 `if __name__ == "__main__":` 가드 없이 실행할 때 발생하는 전형적 문제.

### 8.2 데이터 품질 관련

6. **Yahoo Finance 데이터의 한계**: 공식 크롤러 데이터는 Yahoo 소스라 결측/오류가 존재한다는 것을 공식 문서 스스로 명시한다. 고품질 데이터가 있다면 자체 데이터 사용이 공식 권장사항이다. `check_data_health.py`를 파이프라인에 상시 포함할 것.
7. **오프라인 데이터의 증분 갱신 불가**: 공식 배포 데이터는 용량 절감을 위해 일부 필드가 제거되어 있어 증분 업데이트가 안 된다. 지속 갱신이 필요하면 collector로 처음부터 수집 후 증분 갱신 체계를 구축해야 한다.

### 8.3 방법론 관련 — 가장 중요

8. **미래 참조(look-ahead bias)**: 커스텀 팩터를 만들 때 `Ref($close, -1)` 같은 음수 Ref는 미래 데이터 참조다. 라벨 정의에는 필요하지만 피처에 들어가면 백테스트가 무의미해진다.
9. **거래비용·슬리피지**: 위 5.1 예시처럼 비용 반영 여부로 연 수익률이 17.8% → 12.9%로 바뀐다. 한국 시장 적용 시 거래세(0.18%~), 수수료, 호가 슬리피지를 executor 설정에 반드시 반영할 것.
10. **과최적화(overfitting)**: Alpha158 위에서 하이퍼파라미터를 valid 구간에 맞춰 반복 튜닝하면 test 성과는 필연적으로 부풀려진다. 롤링 검증(benchmarks_dynamic 방식)이 단일 train/valid/test 분할보다 신뢰할 만하다.
11. **IC 0.05는 "좋은" 수치가 아니라 "출발점"**: 일간 IC 0.03~0.05 수준의 시그널은 거래비용과 용량 제약을 넘지 못하는 경우가 대부분이다. IC보다 ICIR(안정성)과 비용 반영 IR을 보라.
12. **백테스트는 집행이 아니다**: Qlib의 백테스트 성과가 실거래 성과를 보장하지 않는다. 호가창 깊이, 체결 지연, 시장 충격은 별개 문제이며, Qlib RL order execution 모듈이 이 간극 일부를 다루지만 완전하지 않다.

> 이 지점에서 한 문장으로 요약하면: **Qlib는 계산기이지 신탁이 아니다.** 프레임워크가 아무리 정교해도 입력 데이터 품질과 방법론 규율이 결과를 결정한다.

---

## 9. RD-Agent 연동 (선택)

```bash
pip install rdagent
# LLM API 키 설정 후
rdagent fin_factor    # 팩터 발굴 루프
rdagent fin_model     # 모델 최적화 루프
rdagent fin_factor_report --report_folder=<PDF 폴더>   # 리포트 기반 팩터 추출
```

주의점: RD-Agent는 LLM API 호출 비용이 상당하고(팩터 루프 1회에 수십~수백 회 호출), 생성된 팩터의 통계적 유의성은 사람이 별도 검증해야 한다. 자동화가 검증을 대체하지 않는다.

---

## 10. 추천 학습 경로

| 단계 | 할 일 | 예상 소요 |
| :--- | :--- | :--- |
| 1 | 설치 + 커뮤니티 데이터 다운로드 + `qrun` LightGBM 벤치마크 1회 실행 | 반나절 |
| 2 | `workflow_by_code.ipynb`로 리포트 해석 (IC, 그룹 수익, 백테스트 곡선) | 1일 |
| 3 | 표현식 엔진으로 자기만의 팩터 3개 정의 → Alpha158에 추가 → 성능 비교 | 2~3일 |
| 4 | KRX 데이터 변환 + 한국 시장 백테스트 파이프라인 구축 | 1주 |
| 5 | 롤링 재학습(benchmarks_dynamic) 도입 → 단일 분할과 결과 비교 | 1주 |
| 6 | (선택) RL order execution / RD-Agent 실험 | 이후 |

---

## 11. 참고 자료

| 자료 | 링크 |
| :--- | :--- |
| GitHub 저장소 | https://github.com/microsoft/qlib |
| 공식 문서 | https://qlib.readthedocs.io |
| 모델 벤치마크 표 | https://github.com/microsoft/qlib/blob/main/examples/benchmarks/README.md |
| 동적 적응 벤치마크 | https://github.com/microsoft/qlib/tree/main/examples/benchmarks_dynamic |
| 커뮤니티 데이터 (CN) | https://github.com/chenditc/investment_data/releases |
| RD-Agent | https://github.com/microsoft/RD-Agent |
| Qlib 논문 | https://arxiv.org/abs/2009.11189 |
| R&D-Agent-Quant 논문 | https://arxiv.org/abs/2505.15155 |
| Qlib-Server (온라인 모드) | https://github.com/microsoft/qlib-server |

---

*본 문서는 2026-07-05 기준 microsoft/qlib main 브랜치와 공식 문서를 대조 검증하여 작성되었다. 수치(벤치마크, 성능 비교)는 모두 공식 저장소 공개 자료 출처이며, 실행 환경에 따라 재현 결과는 달라질 수 있다.*
