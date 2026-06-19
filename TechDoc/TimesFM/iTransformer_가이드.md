# iTransformer 시작 가이드

> 칭화대 × 앤트그룹의 "뒤집힌 Transformer" — 다변량 시계열 예측의 새로운 패러다임

---

## 소개

iTransformer(Inverted Transformer)는 칭화대학교(Tsinghua University)와 앤트그룹(Alipay)이 공동 제안한 시계열 예측 모델로, **ICLR 2024 Spotlight**에 선정되었습니다.

이름의 핵심은 "Inverted(반전)" — Transformer 아키텍처 자체는 그대로 두고, **데이터를 집어넣는 방향을 180도 뒤집었습니다**. 이 단순한 발상의 전환이 다변량 시계열 예측에서 SOTA를 달성했습니다.

TimesFM이 "하나의 모델로 모든 도메인을 커버"하는 파운데이션 모델이라면, iTransformer는 "**변수 간 상관관계를 가장 잘 포착**"하는 다변량 특화 모델입니다. 두 모델은 목표가 달라 경쟁 관계이기도 하고, 상호 보완 관계이기도 합니다.

주식 종목 간 상관관계 포착하는 커플링 시그널을 잘 찾습니다. 그래서 가격의 비대칭, 시장의 비효율을 포착하여 불균형에서 균형으로 돌아오는 타이밍을 잡아 트레이딩할 때 효율적입니다. 섹터 로테이션을 포착하거나 종목 간 공분산 구조 예측으로 리밸런싱 트리거 생성할 때 유용합니다. 다만, 손이 많이 갑니다. TimesFM 대비한 장점이 있어 믹싱하여 사용하면 유용합니다.

한 줄 요약: 中原多俊杰，灿若江沙；天下尽英雄，壮如三国。

---

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 개발사 | 칭화대학교 + 앤트그룹(Alipay) |
| 발표 | ICLR 2024 Spotlight |
| 라이선스 | MIT 오픈소스 |
| GitHub | https://github.com/thuml/iTransformer |
| pip 패키지 | `pip install iTransformer` |
| 연관 라이브러리 | GluonTS(AWS), NeuralForecast(Nixtla), Time-Series-Library |

---

## 핵심 아이디어 - 무엇을 "뒤집었나"?

### 기존 Transformer의 문제

기존 Transformer가 다변량 시계열을 처리할 때는 **동일한 시점의 여러 변수**를 하나의 토큰(Temporal Token)으로 묶었습니다. 예를 들어 전력망 데이터에서 "오전 9시의 온도 + 습도 + 풍속"을 하나의 토큰으로 처리하는 방식입니다.

이 방식의 문제점
- 온도(°C)와 전력(kWh)처럼 **물리적 의미와 단위가 전혀 다른 값**을 강제로 합치면 의미 정보가 손실됩니다.
- 타임스탬프(시각) 자체는 자연어의 단어처럼 **독립적인 의미를 갖지 못합니다**.

### iTransformer의 해결책

| 구분 | 기존 Transformer | iTransformer |
|------|-----------------|--------------|
| **토큰 정의** | 각 시간 단계를 하나의 토큰 | **각 변수(채널)를 하나의 토큰** |
| **어텐션 역할** | 시간적 의존성 모델링 | **변수 간 다변량 상관관계** 모델링 |
| **피드포워드 역할** | 각 시점의 특징 인코딩 | **전체 시계열 표현** 인코딩 |

즉, iTransformer는 **전체 시계열을 특징(feature)**으로, **각 변수를 토큰**으로 간주합니다. 어텐션이 "변수 A와 변수 B는 어떤 관계인가?"를 학습하고, FFN이 "변수 A의 시계열 패턴은 무엇인가?"를 학습합니다.

---

## 장점 (Pros)

### 1. 다변량 예측 SOTA 성능
여러 실제 데이터셋에서 최첨단 성능을 달성했습니다.
- GNSS 고도 시계열: **RMSE 5.1mm, MAE 3.7mm** (PatchTST와 공동 1위)
- Traffic, ETTh1, Weather 등 표준 벤치마크에서 기존 Transformer 계열 모델 전반적 우위

### 2. Transformer 모듈 수정 불필요
어텐션, 피드포워드, 레이어 정규화 등 **Transformer 기본 모듈을 전혀 수정하지 않았습니다**. 데이터 구성 방식만 재설계했기 때문에:
- FlashAttention 등 효율적인 어텐션 메커니즘을 그대로 플러그인 가능
- 향후 Transformer 개선 사항을 즉시 흡수 가능

### 3. 보지 못한 변수에 대한 일반화
입력 토큰 수가 유연하여 **변수 채널 수에 제한이 없습니다**. 일부 변수만으로 학습한 후 학습 시 보지 못한 새로운 변수로 일반화 가능합니다.

### 4. 긴 룩백 윈도우 활용
룩백 윈도우가 길어져도 성능 저하가 적습니다. 기존 Temporal Transformer는 컨텍스트가 길어지면 오히려 노이즈가 증가하는 문제가 있었습니다.

### 5. 풍부한 생태계 통합
- **GluonTS** (AWS) — 클라우드 시계열 파이프라인
- **NeuralForecast** (Nixtla) — TimeGPT와 같은 생태계
- **Time-Series-Library** (칭화대) — 공식 벤치마크 라이브러리

---

## 단점 (Cons)

### 1. O(N²) 계산 복잡도
변수 수 N에 대해 **O(N²)** 복잡도를 가집니다. 수천 개의 IoT 센서처럼 변수가 매우 많은 경우 메모리와 연산 비용이 기하급수적으로 증가합니다.

### 2. 시간적 국소 정보 약화
반전된 프레임워크는 변수 간 상관관계를 잘 포착하는 반면, 인접한 시점 간의 의존성(temporal locality)이 약화될 수 있습니다. 단변량 시계열이나 시간적 패턴이 중요한 경우 일반 Transformer보다 불리할 수 있습니다.

### 3. 계절성 노이즈에 민감
연구에 따르면 iTransformer는 **계절성 노이즈(Seasonality Noise)**에 비교적 민감합니다. 강한 계절 패턴이 있는 데이터(관광, 소매 등)에서는 전처리가 중요합니다.

### 4. 잠재 표현의 시계열 구조 부족
일부 연구에서 표준 iTransformer가 학습한 잠재 표현이 **명확한 시계열 국소성**을 결여할 수 있다고 지적합니다. 이웃한 시점의 표현이 잠재 공간에서 멀리 흩어질 수 있습니다.

### 5. 파운데이션 모델 아님
TimesFM과 달리 iTransformer는 **새로운 도메인마다 학습이 필요합니다**. 제로샷 예측을 지원하지 않으며, 각 데이터셋에 맞는 파인튜닝이 필요합니다.

---

## 설치 및 구성

### 환경 요구사항
- Python 3.7 이상
- PyTorch 2.3+ 권장
- CUDA 지원 GPU (대규모 데이터셋 권장)

### 방법 1: pip 설치 (빠른 시작)

```bash
pip install iTransformer
```

### 방법 2: 소스 코드 설치 (공식 구현)

```bash
git clone https://github.com/thuml/iTransformer.git
cd iTransformer

conda create --name itransformer python=3.7
conda activate itransformer
pip install -r requirements.txt
```

### 설치 확인

```python
import torch
from iTransformer import iTransformer

print("iTransformer 설치 성공!")
print(f"PyTorch 버전: {torch.__version__}")
```

---

## 사용 예제

### 기본 단변량 예측

```python
import torch
from iTransformer import iTransformer

model = iTransformer(
    num_variates=1,           # 변수 개수
    lookback_len=96,          # 과거 데이터 길이
    dim=256,                  # 모델 차원
    depth=6,                  # Transformer 레이어 수
    heads=8,                  # 어텐션 헤드 수
    dim_head=64,              # 각 헤드의 차원
    pred_length=24,           # 예측 길이
    use_reversible_instance_norm=True
)

# 입력: (배치, 과거 길이, 변수 수)
time_series = torch.randn(2, 96, 1)
predictions = model(time_series)
print(f"예측 결과: {predictions.shape}")  # (2, 24, 1)
```

### 다변량 다중 스텝 예측

```python
multi_model = iTransformer(
    num_variates=137,         # Solar 데이터셋의 137개 변수
    lookback_len=96,
    dim=256,
    depth=6,
    heads=8,
    dim_head=64,
    pred_length=(12, 24, 36, 48),  # 여러 예측 길이를 동시에 출력
    use_reversible_instance_norm=True
)

multi_input = torch.randn(2, 96, 137)
multi_predictions = multi_model(multi_input)

for pred_len, pred in multi_predictions.items():
    print(f"{pred_len}스텝 예측: {pred.shape}")
```

### iTransformer2D: 시공간 이중 어텐션

변수 관계와 시계열 패턴을 **동시에** 고려해야 하는 경우 (예: 공간적으로 분산된 센서):

```python
from iTransformer import iTransformer2D

model_2d = iTransformer2D(
    num_variates=137,
    num_time_tokens=16,       # 시계열을 16개의 시간 토큰으로 분할
    lookback_len=96,
    dim=256,
    depth=6,
    heads=8,
    dim_head=64,
    pred_length=(12, 24, 36, 48)
)

input_data = torch.randn(2, 96, 137)
predictions_2d = model_2d(input_data)
```

> **iTransformer2D를 선택해야 하는 경우**: 기상 관측소처럼 공간적으로 인접한 센서들의 시계열을 예측할 때. 변수 간 어텐션과 시간적 어텐션을 모두 활용하여 표준 iTransformer보다 더 풍부한 표현을 학습합니다.

### 공식 스크립트로 학습

```bash
# 다변량 예측 (Traffic 데이터셋)
bash ./scripts/multivariate_forecasting/Traffic/iTransformer.sh

# Transformer vs iTransformer 성능 비교
bash ./scripts/boost_performance/Weather/iTransformer.sh

# 보지 못한 변수 일반화 테스트
bash ./scripts/variate_generalization/ECL/iTransformer.sh

# 룩백 윈도우 증가 효과 테스트
bash ./scripts/increasing_lookback/Traffic/iTransformer.sh

# FlashAttention 가속 버전
bash ./scripts/efficient_attentions/iFlashTransformer.sh
```

### 데이터셋

공식 실험 데이터셋 다운로드:
- [Google Drive](https://drive.google.com/drive/folders/1ZOYpTUa82_jCcxIdTmyr0LXQfvaM9vIy)
- [Tsinghua Cloud](https://cloud.tsinghua.edu.cn/f/84fbc752d0e94980a610/)

---

## 주요 하이퍼파라미터

| 파라미터 | 설명 | 대표값 |
|----------|------|--------|
| `num_variates` | 변수(채널) 개수 | 데이터셋 특성 수 |
| `lookback_len` | 룩백 윈도우 길이 | 96, 192, 336, 720 |
| `dim` | 모델 은닉 차원 | 256, 512 |
| `depth` | Transformer 레이어 수 | 2, 3, 6 |
| `heads` | 어텐션 헤드 수 | 4, 8 |
| `dim_head` | 각 헤드 차원 | 64 |
| `pred_length` | 예측 길이 (튜플로 복수 지정 가능) | 24, 48, 96, 192 |
| `use_reversible_instance_norm` | 가역 인스턴스 정규화 | True 권장 |

---

## 대표 활용 사례

| 분야 | 설명 | iTransformer 적합성 |
|------|------|---------------------|
| GNSS 고도 시계열 | 위성 항법 데이터 처리 | ★★★★★ (공동 1위) |
| 전력 가격 예측 | 실시간 전력 시장 예측 | ★★★★☆ |
| 태양광 발전 예측 | 일일 발전량 예측 | ★★★★☆ |
| 고속도로 통행량 예측 | 교통 흐름 예측 | ★★★★★ |
| 석탄층 메탄 생산 예측 | 에너지 시추 생산량 | ★★★★☆ |
| 해수면 온도 예측 | 전이 학습 결합 활용 | ★★★★☆ |
| 이상 탐지 | 다변량 시계열 이상 감지 | ★★★☆☆ |
| 주식 포트폴리오 분석 | 종목 간 상관관계 포착 | ★★★★☆ |

---

## TimesFM vs iTransformer 비교

두 모델은 목적이 달라 상황에 따라 선택이 달라집니다.

| 기준 | TimesFM | iTransformer |
|------|---------|--------------|
| **모델 타입** | 파운데이션 모델 | 특화 아키텍처 |
| **제로샷 예측** | ✅ | ❌ (학습 필요) |
| **다변량 지원** | 제한적 | ✅ (핵심 강점) |
| **단변량 성능** | ✅ | 상대적 열위 |
| **변수 간 관계 포착** | ❌ | ✅ |
| **Google 생태계 통합** | ✅ | ❌ |
| **AWS 생태계 통합** | ❌ | ✅ (GluonTS) |
| **설치 난이도** | 높음 (JAX 의존성) | 낮음 (pip 한 줄) |
| **즉시 사용 가능성** | ✅ | ❌ |

**선택 가이드:**
- 새로운 도메인, 데이터 부족 → **TimesFM** (제로샷)
- 센서/금융 변수 간 상관관계가 중요 → **iTransformer** (다변량)
- 두 접근 결합: iTransformer로 파인튜닝 전 TimesFM으로 기준선 확인

---

## 주식 및 예측 시장 활용 가능성

### 주식 시장에서의 iTransformer

iTransformer의 **변수 간 상관관계 학습**은 금융 데이터에 특히 유용합니다.

**강점이 발휘되는 시나리오:**
- **섹터 로테이션 분석**: 기술주/에너지주/금융주 간 상관관계 변화 포착
- **팩터 모델 보완**: PBR, PER, ROE 등 여러 팩터의 상호 관계 학습
- **포트폴리오 최적화**: 종목 간 공분산 구조 예측으로 리밸런싱 트리거 생성
- **쌍 거래(Pair Trading)**: 동일 섹터 두 종목의 스프레드 예측

**활용 예시:**
```python
# 코스피 200 종목의 30일 수익률 예측
model = iTransformer(
    num_variates=200,    # 200개 종목
    lookback_len=252,    # 1년 거래일
    pred_length=20,      # 20 거래일(1개월) 예측
    dim=512,
    depth=4,
    heads=8,
    dim_head=64,
    use_reversible_instance_norm=True
)
```

### Polymarket에서의 활용

iTransformer는 **복수의 경제 지표를 동시에 고려**할 수 있어 Polymarket의 복합 마켓에 유리합니다.

예: "2025년 말 미국 경기침체 여부" 마켓
```
입력 변수 (num_variates=6):
- 실업률
- 10년물 금리
- 2년물 금리 (yield curve)
- ISM 제조업 PMI
- 소비자신뢰지수
- S&P 500 수익률

→ iTransformer가 6개 변수 간 상관관계 학습 후 경기침체 확률 추정
→ Polymarket 현재 가격과 비교하여 차익 기회 탐색
```

---

## 참고 자료

- **논문**: [iTransformer: Inverted Transformers Are Effective for Time Series Forecasting (ICLR 2024)](https://arxiv.org/abs/2310.06625)
- **공식 코드**: https://github.com/thuml/iTransformer
- **발표 슬라이드**: https://cloud.tsinghua.edu.cn/f/175ff98f7e2d44fbbe8e/
- **포스터**: https://cloud.tsinghua.edu.cn/f/36a2ae6c132d44c0bd8c/
- **Time-Series-Library** (칭화대 공식 벤치마크): https://github.com/thuml/Time-Series-Library

---

*최종 업데이트: 2025년 6월 | 작성: Vibe Investing Research*
