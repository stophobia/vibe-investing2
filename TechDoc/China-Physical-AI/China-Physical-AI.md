# 중국 피지컬 AI(Physical AI) 및 임베디드 AI(Embodied AI) 오픈소스 생태계

최종 갱신: 2026-07-06

## 0. 왜 지금 중국은 피지컬 AI를 전면 오픈소스화하는가?

2026년 1월 말 앤트그룹(Robbyant/LingBot)의 연쇄 오픈소스 공개를 기점으로, 알리바바 다모원(RynnBrain), 가오더(ABot 시리즈), 텐센트(Hunyuan World Model), 유니트리(UnifoLM), 갤럭시아(GalaxeaVLA), 엑스스퀘어로봇(WALL 시리즈), 위안리링지(Dexbotic/DM0), 주지둥리(FluxVLA) 등 주요 플랫폼·로봇 기업들이 거의 동시다발적으로 파운데이션 모델과 데이터셋을 무료 공개했다. 이는 개별 기업의 홍보 이벤트가 아니라 다음 세 가지 구조적 흐름이 겹친 결과로 해석해야 한다.
지금 한국에게 중국의 피지컬 AI는 기회와 도전이 되고 있다. 단기간에 중국의 오픈소스 생태계에 

1. **데이터 병목 해소를 위한 연합 전략**: 로봇 실물 데이터는 텍스트·이미지 데이터에 비해 수집 비용이 압도적으로 높다. 개별 기업이 각자 데이터를 쌓는 대신, 모델 아키텍처와 파이프라인 자체를 공개해 전 세계 개발자의 피드백·파생 데이터를 흡수하는 것이 더 빠른 길이라는 판단이 확산됐다(가오더 ABot-M0의 "isolated silo 통합" 논리, 갤럭시아 제너럴의 저품질 데이터 재활용 전략 등).
2. **정부 주도 산업 정책과의 결합**: 중국 정부는 로봇·휴머노이드를 전략 산업으로 지정했고, 2025년 전 세계 휴머노이드 출하량의 상당 부분이 중국에서 이뤄졌다. 상하이 소재 국유기업 '휴머노이드로봇상하이유한회사'가 주도하는 OpenLoong처럼 국가급 혁신센터가 오픈소스 커뮤니티를 직접 조성하는 사례도 있다.
3. **미·중 기술 패권 경쟁 구도에서의 개방형 표준 선점**: 블룸버그 등 외신은 알리바바 RynnBrain 공개를 두고 "중국의 오픈소스 전략이 서방의 폐쇄형 기술 우위를 약화시킬 수 있다"고 평가했다. 구글 딥마인드(Gemini Robotics-ER), 엔비디아(Cosmos), 피지컬 인텔리전스(π0 계열) 등 미국 진영의 폐쇄적·부분공개 전략과 대비되는 완전 오픈소스 노선이다.

아래는 원본 참고자료의 기업별 프로젝트 목록에 최신 뉴스, 전략 코멘터리를 더하고, 원본에 없던 주요 플레이어(갤럭시아 제너럴/갈봇, BAAI, 스피릿 AI)를 추가한 갱신판이다.

## 기회와 도전

1. 많은 한국과 미국 기업이 중국의 플랫폼을 두려워하고 있다. 그래서 보안, 파트너쉽, 레귤레이션, 사용의 확장성에서 오픈소스로 신뢰의 문제를 돌파하려고 하는 것이다.
2. 그럼에도 문제는 많은 공장들이 '암묵지'로 구성되어 있어, 이 학습된 결과가 중국의 클라우드와 경쟁 회사에 들어간다는 두려움이 남아 있다.
3. 핵심 과제는 우리는 달리는 호랑이의 등에 올라탈 용기가 필요하다.

---

## 1. 인터넷 및 테크 대기업

### 1.1 앤트그룹(Ant Group) — 링보 테크(Ant LingBo / Robbyant)

| 프로젝트명 | 유형 | 설명 | 링크 |
|---|---|---|---|
| LingBot-VLA | 임베디드 대형 모델(VLA) | 9종 듀얼암 로봇, 2만 시간 실물 데이터로 사전학습된 "범용 두뇌" | [GitHub](https://github.com/Robbyant) · [Hugging Face](https://huggingface.co/robbyant) |
| LingBot-Depth | 공간 인식 모델 | 희소·노이즈 깊이 데이터에서 정밀 3D 깊이 복원(Masked Depth Modeling) | 오픈소스 공개 완료 |
| LingBot-World | 세계 모델 | 16fps·지연 1초 이내 실시간 인터랙티브 시뮬레이션, 최대 약 1분 연속성 확보 | Apache 2.0 라이선스 |
| LingBot-Map | 스트리밍 3D 재구성 | 단일 RGB 카메라만으로 실시간 SLAM급 3D 지도 생성, ETH3D 벤치마크 1위 | [GitHub](https://github.com/Robbyant/lingbot-map) · [arXiv](https://arxiv.org/abs/2604.14141) |

**최신 뉴스 및 전략(2026)**
- 2026년 1월 28~30일 "Evolution of Embodied AI Week" 기간 중 LingBot-VLA·Depth·World를 연쇄 공개하며 앤트그룹 최초의 오픈소스 임베디드 AI 모델 시리즈를 완성했다. 로비언트 CEO 주싱(Zhu Xing)은 이를 "AGI 전략을 디지털 영역에서 물리적 지각으로 확장하는 것"이라고 규정했다.
- LingBot-VLA는 이미 갈락시아 다이내믹스(Galaxea Dynamics), 애자일X(AgileX Robotics), 애지봇(AgiBot) 등 타사 하드웨어에 이식되어 크로스 모피(cross-morphology) 이식성을 검증받았으며, 상하이교통대가 공개한 GM-100 벤치마크에서 SOTA를 기록했다.
- 4월 16일 공개한 LingBot-Map까지 더해 지각(Depth·Map)–행동(VLA)–상상(World)을 아우르는 "체화지능 풀스택"을 완성했다는 점이 핵심 전략 메시지다. 다만 앤트그룹 스스로도 기술문서에서 2만 시간 데이터로는 미국 Physical Intelligence의 π*0.6과 비슷한 수준에 그친다고 인정, 데이터 확충이 다음 과제로 지목됐다.
- 오르벡(Orbbec)과 전략적 파트너십을 체결해 LingBot-Depth를 자사 심도 카메라(Gemini 330)와 칩(MX6800) 레벨에서 공동 최적화하는 하드웨어 연계 전략도 병행 중이다.

### 1.2 알리바바(Alibaba) — 다모원(DAMO Academy)

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| RynnBrain | 2B/4B/8B Dense + 30B-A3B MoE 임베디드 파운데이션 모델, Qwen3-VL 기반 | [GitHub](https://github.com/alibaba-damo-academy/RynnBrain) · [Hugging Face](https://huggingface.co/Alibaba-DAMO-Academy) |
| RynnBrain-Plan/Nav/CoP | 작업계획·비전언어내비게이션·포인트 단위 추론에 특화된 사후학습 모델 | 위 저장소 포함 |
| RynnEC / RynnScale / RynnVLA-001,002 | MLLM의 임베디드 세계 연결, 확장형 임베디드 모델, VLA·세계모델 통합 | 알리바바 다모원 GitHub |

**최신 뉴스 및 전략(2026)**
- 2026년 2월 10일 공개. 구글 딥마인드 Gemini Robotics-ER 1.5, 엔비디아 Cosmos-Reason2를 능가하는 성능을 주장하며 16개 오픈소스 벤치마크에서 신기록을 세웠다고 발표했다. 시공간 기억(episodic memory)과 물리 세계 추론을 결합한 것이 핵심 차별점이다.
- 알리바바 CTO 제프 장(Jeff Zhang)이 다모원을 직접 총괄하며, 베이징·항저우·산마테오·벨뷰·모스크바·텔아비브·싱가포르 7개 연구소를 신설하는 등 조직적 투자를 병행하고 있다.
- 전략적으로 알리바바는 RynnBrain 오픈소스화와 동시에 휴머노이드 스타트업 엑스스퀘어로봇에 대규모 투자(A+ 라운드 주도, 약 1억~1.4억 달러)를 단행해, "두뇌(모델)는 오픈소스로 생태계를 넓히고, 하드웨어는 지분투자로 수직 계열화한다"는 이원 전략을 취하고 있다. 자사 LLM 브랜드 Qwen과 함께 피지컬 AI를 알리바바 AI 전략의 핵심 축으로 명시했다.
- 4월 13일 RynnBrain-4B를 추가 출시하며 지속적인 모델 라인업 확장을 이어가고 있다.

### 1.3 텐센트(Tencent) — 혼원(Hunyuan)

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| Hunyuan World Model 1.5(WorldPlay) | 텍스트/이미지 1장으로 실시간 인터랙티브 3D 월드 생성, 업계 최초 전체 파이프라인(데이터·학습·스트리밍 추론) 오픈소스 | [Tencent Hunyuan](https://3d-models.hunyuan.tencent.com/world/) |
| Hunyuan3D World 1.0 | 13억 파라미터, 3D VAE + Diffusion Transformer, 최대 16초 클립 생성 | 오픈소스 공개 완료 |
| HunyuanVideo 1.5 | 8.3B 경량 DiT 기반 오픈소스 영상 생성 모델 | [arXiv](https://arxiv.org/pdf/2511.18870) |

**최신 뉴스 및 전략(2026)**
- 2025년 12월 17일 Hunyuan World Model 1.5(WorldPlay)를 공식 출시하며 "업계에서 가장 체계적이고 포괄적인 실시간 세계 모델 프레임워크"를 데이터·학습·스트리밍 추론 배포까지 전 과정 오픈소스로 공개했다고 밝혔다. Next-Frames-Prediction 방식의 시각적 자기회귀 태스크로 실시간성과 기하학적 일관성의 상충 문제를 해결했다고 주장한다.
- 텐센트의 전략은 게임·콘텐츠 제작(WorldPlay, GameCraft)과 로봇 시뮬레이션 양쪽에 동일한 세계모델 기술을 적용하는 "일석이조" 접근으로, 앤트그룹의 LingBot-World와 사실상 경쟁 관계에 있다.
- Hunyuan3D 시리즈는 2024년 11월 최초 오픈소스화 이후 허깅페이스 누적 다운로드 300만 건을 돌파했으며, 유니티 차이나·뱀부랩 등 150개 이상 기업이 텐센트 클라우드를 통해 도입했다. 로봇 전용 브랜드보다는 3D 콘텐츠·게임 자산 생성 축이 아직 더 강하다는 점이 링보/다모원과의 차이다.

### 1.4 가오더(Amap, 알리바바 계열) — ABot

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| ABot-M0 | UniACT-dataset(600만+ 궤적, 9,500시간, 6개 오픈소스 데이터셋 통합) 기반 VLA, Action Manifold Learning(AML) 제안 | [GitHub](https://github.com/amap-cvlab) · [프로젝트 페이지](https://amap-cvlab.github.io/ABot-Manipulation/) · [arXiv](https://arxiv.org/abs/2602.11236) |
| ABot-N0 | 1,690만 전문가 궤적 기반 임베디드 내비게이션 VLA, 7개 벤치마크 SOTA | [프로젝트 페이지](https://amap-cvlab.github.io/ABot-Navigation/ABot-NO/) |
| ABot-PhysWorld | 물리 정합형 인터랙티브 세계 파운데이션 모델, Veo 3.1·Sora v2 Pro 대비 물리적 타당성 우위 주장 | [GitHub](https://github.com/amap-cvlab/ABot-PhysWorld) |
| UniACT-dataset | 6개 공개 데이터셋 통합, 600만+ 궤적, 20+ 로봇 형태 커버 | ABot-M0와 함께 공개 |

**최신 뉴스 및 전략(2026)**
- 가오더(아마프, 고덕지도)는 알리바바 그룹 산하 지도·내비게이션 계열사로, "체화지능은 폐쇄적 독점 시스템이 아니라 이종 데이터의 통합과 점진적 역량 축적을 통해 발전해야 한다"는 명시적 오픈소스 철학을 논문 서두에 밝히고 있다.
- ABot-M0의 핵심 기술은 Action Manifold Learning(AML)으로, 노이즈 제거(diffusion) 대신 저차원 매니폴드로의 투사(projection)를 통해 행동을 직접 예측, 디코딩 속도와 안정성을 동시에 개선했다고 주장한다.
- 2026년 2~3월 사이 ABot-M0(조작), ABot-N0(내비게이션), ABot-PhysWorld(세계모델)까지 3종 세트를 순차 공개하며 조작·이동·시뮬레이션 전 영역을 아우르는 로드맵을 완성했다. 알리바바 다모원(RynnBrain)과는 별도 조직이지만 동일한 알리바바 그룹 오픈소스 전략의 한 축으로 움직인다.

---

## 2. 로봇 기업

### 2.1 유니트리(Unitree Robotics)

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| UnifoLM-WMA-0 | 크로스 임보디먼트 세계모델-액션 아키텍처, 시뮬레이션 엔진 겸 정책 강화 모듈 | [GitHub](https://github.com/unitreerobotics/unifolm-world-model-action) · [Hugging Face](https://huggingface.co/unitreerobotics/UnifoLM-WMA-0-Base) |
| UnifoLM-VLA-0 | 범용 휴머노이드 조작을 위한 VLA 대형모델 | [GitHub](https://github.com/unitreerobotics) |
| Qmini / UniArmL1 | 3D 프린팅 가능한 저비용 이족보행 로봇, 경량 6-DOF 오픈소스 로봇팔 | GitHub |

**최신 뉴스 및 전략(2026)**
- 2025년 9월(WMA-0), 2026년 1월(VLA-0)에 각각 오픈소스화. G1 휴머노이드(1.3m)에 UnifoLM-WMA-0을 통합해 비전·언어·행동을 결합했다.
- 2026년 7월 초 상하이증권거래소 상장 승인(CSRC 승인, 기업가치 약 9.5조 원 규모)을 받아 IPO를 목전에 두고 있다. 이는 창립 10주년과 맞물린 이벤트로, "풀스택 자체개발 + 대량생산 + 오픈소스 생태계"의 선순환 구조가 IPO 스토리텔링의 핵심으로 제시되고 있다.
- 다롄해사대 개러이(Pioneer Technology Lab) 연구자는 "UnifoLM-WMA-0은 로봇이 웅덩이 등 장애물을 밀리초 단위로 예측해 보폭을 조정하게 해준다"고 평가했으며, 업계 관계자는 "유니트리 매출의 상당 부분이 교육·연구용 로봇에서 나오는 만큼 개발자 생태계 확보가 핵심 비즈니스"라고 분석했다. 실제로 4족보행·휴머노이드 모델의 약 80%가 연구·교육·소비자 시장에 배치되고 있다.

### 2.2 즈핑팡(Zhipingfang) — AlphaBrain

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| AlphaBrain Platform | 세계 최초 원스톱 임베디드 AI 모델 오픈소스 커뮤니티 표방 | 공식 발표 |
| NeuroVLA | 뇌과학 기반 VLA 모델(세계 최초 오픈소스 표방) | AlphaBrain Platform 경유 공개 |

**참고**: 즈핑팡/AlphaBrain은 다른 대기업 계열 프로젝트에 비해 영문·국제 매체 보도가 제한적이며, 검증 가능한 GitHub 저장소 링크가 아직 널리 확인되지 않는다. 원본 자료의 "세계 최초" 표현은 회사측 공식 발표에 근거한 것으로, 교차 검증이 추가로 필요한 항목이다. 최신 활동 확인을 위해서는 회사 공식 채널 모니터링을 권장한다.

### 2.3 갤럭시아 다이내믹스(Galaxea Dynamics / Galaxea AI)

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| G0.5(GalaxeaVLA) | 자기회귀 방식으로 추론·행동 토큰을 하나의 트랜스포머 디코더에서 생성하는 VLA | [GitHub](https://github.com/OpenGalaxea/GalaxeaVLA) |
| Galaxea Open-World Dataset | 50개 이상 실제 환경, 누적 500시간·10TB 초과, 공개 2개월 만에 다운로드 40만 건 | Hugging Face · ModelScope |
| G0Tiny | 250M 경량 모델, R1 Pro Orin 온디바이스 추론(최대 10Hz) | Hugging Face |

**최신 뉴스 및 전략(2026)**
- 2023년 9월 창업(창업자 가오지양, 전 웨이모·모멘타 출신), 알고리즘과 하드웨어를 함께 개발하는 "풀스택" 전략을 표방한다. 2025년 8월 G0 공개 이후 2026년 1월 G0Plus, 6월 G0.5로 빠르게 반복 출시하고 있다.
- 휠형 로봇 R1 Pro는 앤트그룹 LingBot-VLA의 공식 하드웨어 파트너로 채택되는 등, 대기업 오픈소스 모델의 "레퍼런스 하드웨어" 지위를 전략적으로 확보하고 있다.
- 2026년 2월 시리즈B에서 10억 위안(약 1,450억 원)을 조달했으며, Galaxea Open-World Dataset의 흥행(다운로드 40만 건)을 데이터 생태계 확장의 핵심 성과로 내세우고 있다.
- 유사한 이름의 별도 회사인 **갤럭시아 제너럴(Galaxea General/銀河通用, Galbot)**은 베이징대·칭화대와 공동으로 LDA-1B(Latent Dynamics Action Model)를 개발해 2026년 4월 RSS(Robotics: Science and Systems)에 정식 채택됐다. DINO 기반 잠재 표현으로 저품질·비정제 데이터까지 학습에 활용, "저품질 데이터 30% 추가 시 성공률 10%p 상승"이라는 결과로 주목받았으며 기업가치 200억 위안을 기록 중이다. Galbot G1은 2026년 춘절 CCTV 무대에 출연했고, 약국 100곳에 배치돼 30만 건 이상의 의약품 판매를 처리, 중국 최초 "로봇 약사" 자격을 획득했다. **두 회사는 이름이 유사하나 별개 법인이므로 문서 인용 시 혼동에 유의해야 한다.**

### 2.4 주지둥리(LimX Dynamics)

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| FluxVLA Engine | VLA 전 주기(데이터→학습→평가→실물 배포) 표준화 엔지니어링 플랫폼, Apache 2.0 | [GitHub](https://github.com/limxdynamics/FluxVLA) · [문서](https://fluxvla.limxdynamics.com/) |
| LimX COSA / VGM / DreamActor | 임베디드 에이전틱 OS, 조작 알고리즘, 임베디드 학습 신패러다임 | 공식 홈페이지 |

**최신 뉴스 및 전략(2026)**
- 2026년 4월 30일 FluxVLA Engine 오픈소스 발표. OpenVLA·LlavaVLA·GR00T·Pi0·Pi0.5 등 주요 VLA 알고리즘을 단일 설정 파일로 관리할 수 있는 표준화 플랫폼을 표방하며, 서드파티 서빙 프레임워크(Reflex 등)에도 이미 통합되고 있다.
- 알리바바(2024년)와 징둥닷컴(2025년)으로부터 전략적 투자를 유치했으며, TRON 1/2(연구용) → Oli(완전체 휴머노이드)로 이어지는 제품 사다리와 소프트웨어 스택(COSA, VGM, DreamActor, FluxVLA)을 결합한 "하드웨어+소프트웨어 플랫폼 기업" 포지셔닝을 취하고 있다.
- 2026년 2월 기준 약 2억 달러 규모 최신 투자 라운드를 유치했으며(갤럭시아·스피릿 AI 등과 함께 대형 라운드 그룹에 포함), GitHub 이슈 외에 mason@limxdynamics.com·wayne@limxdynamics.com을 통한 직접 기술지원 창구를 공개해 개발자 커뮤니티와의 접점을 강화하고 있다.

### 2.5 엑스스퀘어로봇(X Square Robot, 自变量机器人)

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| WALL-OSS-0.5 | 4B 파라미터 VLA, 제로샷 실물 로봇 조작, 업계 최초 임베디드 AI 오픈소스 표방 | GitHub · Hugging Face |
| WALL-B / WALL-WM | World Unified Model 아키텍처 기반 파운데이션 모델 / 월드모델 확장판 | 공개 완료 |
| XRZero-G0 | 로봇 없이 데이터 수집·훈련 가능한 오픈소스 프레임워크, 공개 1주 만에 AlphaXiv 트렌드 톱10 진입 | 공개 완료 |

**최신 뉴스 및 전략(2026)**
- 2023년 12월 창업(2년이 채 되지 않은 시점 기준) 이후 2025년 9월 A+ 라운드(알리바바 클라우드·CAS 인베스트먼트 주도, 1억 달러)를 포함해 8차례 연속 투자 유치, 누적 조달액 약 2억 8천만 달러(20억 위안)를 기록했다. 이후 2026년 초 두 달간 4연속 라운드로 30개 이상 투자자를 유치하며 기업가치 200억 위안(약 4.5조 원)을 돌파, 갈봇·갤럭시아 AI·스피릿 AI·링커봇과 함께 "200억 위안대 클럽"에 이름을 올렸다.
- CEO 왕첸(Wang Qian, 창업 당시 COO는 양첸)은 "창업 첫날부터 자체 파운데이션 모델에 집중했다"고 강조하며, 하드웨어(청소로봇 Quanta X2)와 모델(WALL 시리즈)을 동시에 오픈소스·상용화하는 이중 전략을 취한다.
- 2026년 4월 WALL-B 공개 시 기존 모듈형 VLA와 달리 인지·언어·행동·물리적 예측을 단일 네트워크에서 학습하는 "World Unified Model" 아키텍처를 표방했다. IPO 준비에도 착수했으나 상장 지역은 미정이다.

### 2.6 위안리링지(Dexmal, 原力灵机)

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| Dexbotic 2.0 | PyTorch 기반 VLA 개발 툴박스, π0·CogACT 등 주요 알고리즘 재현·미세조정 지원, MIT 라이선스 | [GitHub](https://github.com/dexmal/dexbotic) |
| DM0 | 2.4B 파라미터 "Embodied-Native" VLA, RoboChallenge Table30 벤치마크 1위 | [GitHub](https://github.com/dexmal/dexbotic/blob/main/docs/DM0.md) · [arXiv](https://arxiv.org/html/2602.14974v1) |

**최신 뉴스 및 전략(2026)**
- 2025년 10월 Dexbotic 최초 공개, 2026년 2월 10일 DM0 공개와 동시에 StepFun과 공동 개발 사실을 명시했다. RLinf 팀과도 VLA+강화학습 연구를 위한 전략적 협력을 발표하는 등 오픈소스 생태계 간 연합이 활발하다.
- DM0의 핵심 주장은 "인터넷 사전학습 모델을 물리 작업에 사후 적응시키는 기존 방식"에서 벗어나, 사전학습 단계부터 주행·임베디드 상호작용 데이터를 통합 학습하는 "Embodied-Native" 접근이다. 3단계(Pretraining-Mid-Training-Post-Training) 파이프라인과 Flow Matching 액션 전문가를 결합했다.
- 베이징 소재 스타트업으로, Dexbotic 2.0을 "임베디드 AI의 PyTorch급 인프라"로 포지셔닝하며 표준 개발 프레임워크 지위 선점을 노리고 있다.

---

## 3. 오픈소스 커뮤니티 및 국가 주도 프로젝트

### 3.1 OpenLoong

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| OpenLoong | 인체형 로봇 임베디드 AI 조작 시스템 오픈소스 커뮤니티 | [GitHub](https://github.com/loongOpen) |
| OpenLoong-Dyn-Control | MPC·WBC 기반 전신 동역학 제어 소프트웨어 | GitHub |
| OpenLoong-Hardware | 인체형 로봇 하드웨어 오픈소스 | GitHub |

**최신 뉴스 및 전략(2026)**
- 2024년 5월 출범. 국유기업 '휴머노이드로봇상하이유한회사(人形机器人上海有限公司)'가 연구개발을 주도하며, 국가급 혁신센터(상하이 휴머노이드 로봇 혁신센터)가 직접 운영하는 관제탑형 오픈소스 커뮤니티라는 점에서 민간기업 주도 프로젝트들과 성격이 다르다.
- 혁신센터 총경리 쉬빈(許彬)은 "휴머노이드 '칭룽(靑龍)'의 오픈소스 버전을 기반으로 공통 기술 플랫폼을 구축해 핵심 분야 기술 돌파와 대규모 상업화를 동시에 실현하겠다"고 밝혔다. 즉 OpenLoong은 개별 기업의 생태계 확장 도구가 아니라 **중국 로봇 산업 전체의 공통 인프라를 국가가 조성**하는 성격이 강하다.
- 2025~2026년 정부·국유기업 주도의 대량 조달이 로봇 스타트업의 현금흐름과 규모의 경제를 견인하는 구조 속에서, OpenLoong은 그 기술적 표준화 축을 담당하고 있다는 분석이 나온다(2025년 전 세계 휴머노이드 출하량의 약 87%가 중국산이라는 통계가 이런 흐름을 뒷받침한다).

### 3.2 OpenJiuwen

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| JiuwenSwarm | 멀티 에이전트 협업 시스템 | GitHub |
| Agent-Core | LLM 애플리케이션용 Python SDK | GitHub |
| Agent-Protocol | 에이전트 상호운용 프로토콜 SDK | GitHub |

**참고**: OpenJiuwen은 로봇 본체보다 에이전트·SDK 계층에 초점을 맞춘 프로젝트로, 검색 시점 기준 국제 매체의 별도 보도가 제한적이다. GitHub 저장소를 통한 직접 확인과 커밋 히스토리 추적을 권장한다.

### 3.3 [신규 추가] BAAI(북경통용인공지능연구원) — RoboBrain 2.0

| 프로젝트명 | 설명 | 링크 |
|---|---|---|
| RoboBrain 2.0 | 언어모델 능력과 공간 추론을 결합한 오픈소스 로보틱스 모델, 도우인(TikTok 중국판) 영상에서 인간 동작을 직접 관찰·학습하는 방식 채택 | BAAI 공식 |

**최신 뉴스 및 전략(2026)**
- BAAI(원장 겸 로보틱스 연구책임자 중위안 왕)는 대학·정부 연구소 계열의 대표적 오픈소스 축으로, 기업 계열(앤트·알리바바·텐센트)과는 결이 다른 학술-국가연구소 하이브리드 모델이다. 인터넷에 존재하는 방대한 인간 동작 영상(SNS 댄스 영상 등)을 직접 학습 데이터로 활용하는 접근이 특징적으로 보도됐다.

### 3.4 [신규 추가] 스피릿 AI(Spirit AI)

**개요 및 전략(2026)**: '중국판 Physical Intelligence'로 불리며, 정제된 데이터 대신 "더티 데이터(dirty data)" 대규모 학습이 VLA 확장의 핵심이라는 차별화된 철학을 내세운다. 자체 웨어러블 데이터 수집 장치를 5세대까지 발전시켜 텔레오퍼레이션 대비 데이터 수집 비용을 90% 절감했다고 주장하며, 20만 시간 이상의 실세계 상호작용 데이터를 확보(연내 100만 시간 목표)했다. 2026년 1월 오픈소스 공개한 '스피릿 v1.5'는 RoboChallenge 글로벌 리더보드에서 미국 Physical Intelligence의 π0.5를 능가하는 성적을 기록했다고 보도됐다. CATL·화웨이·샤오미·징둥닷컴 등 산업 전략 투자자와 충칭·항저우 국유펀드가 함께 참여해 부품(상류)·유통(하류) 양측을 주주로 확보, 실세계 배치 데이터를 빠르게 축적할 수 있는 구조를 갖췄다는 평가다.

---

## 4. 요약: 중국 물리 AI 오픈소스 생태계 계층 구조(갱신판)

| 계층 | 대표 기업/프로젝트 | 성격 | 핵심 링크 |
|---|---|---|---|
| 기초 모델층 | 앤트(LingBot-VLA), 다모원(RynnBrain), 가오더(ABot-M0), 위안리링지(DM0), 스피릿 AI(v1.5) | 범용 VLA "두뇌" | lingbot-vla · RynnBrain · ABot-Manipulation |
| 세계 모델층 | 유니트리(UnifoLM-WMA-0), 텐센트(Hunyuan World 1.5), 앤트(LingBot-World), 가오더(ABot-PhysWorld) | 시뮬레이션·데이터 생성 엔진 | UnifoLM-WMA-0 |
| 프레임워크·툴체인층 | 위안리링지(Dexbotic 2.0), 주지둥리(FluxVLA), 즈핑팡(AlphaBrain) | 개발 인프라 표준화 | FluxVLA · Dexbotic |
| 데이터셋층 | 갤럭시아(Open-World Dataset), 가오더(UniACT-dataset), 엑스스퀘어로봇(XRZero-G0), 갤럭시아 제너럴(LDA-1B 학습셋) | 대규모 실물/합성 데이터 | X-Square-Robot |
| 운영체제·하드웨어층 | OpenLoong(국가주도), 유니트리(UnifoLM 통합 G1), 주지둥리(COSA) | 로봇 본체·OS 표준 | OpenLoong |
| 국가/학술 인프라층 | OpenLoong(국유기업 주도), BAAI(RoboBrain 2.0), OpenJiuwen | 산업 공통 표준·정책 연계 | 상하이 휴머노이드 혁신센터 |

---

## 5. 전체 전략 지형 요약

1. **대기업(앤트·알리바바·텐센트)**: 모델을 완전 오픈소스화해 "글로벌 개발자 생태계 흡수 → 자사 클라우드/하드웨어 파트너 락인"이라는 2단계 전략을 공유한다. 알리바바는 오픈소스(RynnBrain)와 지분투자(엑스스퀘어로봇)를 병행하는 점이 특히 뚜렷하다.
2. **로봇 하드웨어 기업(유니트리·갤럭시아·엑스스퀘어로봇·주지둥리)**: 오픈소스는 매출보다 개발자 저변 확대와 IPO/투자 스토리텔링에 방점이 있다. 유니트리의 임박한 상장, 엑스스퀘어로봇·갤럭시아의 연쇄 대형 투자 유치가 이를 뒷받침한다.
3. **순수 AI 스타트업(위안리링지·스피릿 AI)**: 하드웨어 없이 모델·데이터·프레임워크만으로 승부하며, 벤치마크(RoboChallenge, GM-100) 1위 경쟁이 곧 마케팅이자 투자 유치 수단이다.
4. **국가/학술 축(OpenLoong·BAAI)**: 개별 기업 경쟁과 별개로 산업 전체의 공통 표준·데이터 인프라를 구축하는 역할을 하며, 정부의 대량 조달 정책과 직접 연동된다.

이 네 축이 서로 경쟁하면서도 데이터·인재·투자 측면에서 상호 얽혀 있다는 점(예: LingBot-VLA를 갤럭시아·애자일X 하드웨어에서 검증, 알리바바가 RynnBrain과 엑스스퀘어로봇 지분을 동시에 보유)이 2026년 중국 피지컬 AI 생태계의 구조적 특징이다.

---

## 6. 주요 출처

- RoboHorizon, "앤트그룹, 로봇 AI 풀스택 전격 공개", 2026-01-29
- 로봇신문, "오르벡–로비언트, LingBot-Depth 공개", 2026-01-30
- BusinessWire/FinancialContent, "Robbyant Open-Sources LingBot-World", 2026-01-29
- Las Vegas Sun/BusinessWire, "Robbyant Unveils LingBot-Map", 2026-04-16
- MarkTechPost, "Ant Group Releases LingBot-VLA", 2026-01-29
- MS투데이, "알리바바, 로봇용 오픈소스 AI '린브레인' 공개", 2026-02-11
- 로봇신문, "中 알리바바, 로봇용 오픈소스 AI 모델 '린브레인' 공개", 2026-02-11
- GitHub, alibaba-damo-academy/RynnBrain
- ai타임스, "알리바바, 오픈소스 로봇 모델 출시로 '피지컬 AI' 진출", 2026-02-11
- CIP Lawyer / Futubull, "Tencent Hunyuan World Model 1.5 Officially Launched", 2025-12-16~17
- arXiv 2602.11236, "ABot-M0: VLA Foundation Model for Robotic Manipulation with Action Manifold Learning"
- arXiv 2603.23376, "ABot-PhysWorld"
- arXiv 2602.11598, "ABot-N0"
- Gasgoo, "Unitree Robotics IPO Reaches Key Milestone", 2026-03-23
- Yicai, "China's Unitree Open-Sources World Model to Advance Robotics Ecosystem", 2025-09-16
- 글로벌이코노믹, "유니트리 상장 승인…기업가치 9.5조 육박", 2026-07
- 오마이뉴스, "피 튀기는 중국 로봇 3파전", 2026-04-30
- GitHub, OpenGalaxea/GalaxeaVLA
- 로봇신문, "2026년 로봇 데이터 전쟁, 이미 시작됐다", 2026-01-26
- 와우테일, "로봇 두뇌부터 자율주행 칩까지, 2월 주목해야 할 중국 스타트업 4곳", 2026-03-16
- LimX Dynamics 공식 뉴스센터·GitHub(limxdynamics/FluxVLA)
- RobotsAsia, "LimX Dynamics: Humanoid Robots, Oli & TRON Platforms"
- Cryptopolitan, "알리바바, 로봇 회사 X 스퀘어에 1억 달러 투자 지원", 2025-09-08
- 로봇신문, "中 휴머노이드 스타트업 '엑스스퀘어로봇', 기업가치 28억달러 돌파"
- GitHub, dexmal/dexbotic · Pandaily, "Dexmal Unveils DM0", 2026-02-10
- iting.co.kr, "2025년 중국은 휴머노이드 로봇 산업 육성중", 2025-03-07(OpenLoong 개요)
- 로봇신문, "[기획] 휴머노이드 로봇 강국 '중국'의 미래를 엿보다(3)", 2025-09-17(OpenLoong·상하이혁신센터)
- GQ Korea, "인간과 공존할 첫 로봇, 그 출발지는 중국", 2026-04-15(BAAI RoboBrain 2.0)
- inuglr.com, "중국 국가주도형 AI 로봇 정책: 데이터 확보와 오픈소스 표준화", 2026-03-13

*참고: 일부 프로젝트(즈핑팡/AlphaBrain, OpenJiuwen)는 국제 매체·영문 GitHub 상 교차 검증 자료가 상대적으로 제한적이므로, 최신 동향은 회사·커뮤니티 공식 채널을 통해 재확인할 것을 권장한다.*
