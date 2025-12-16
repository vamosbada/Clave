# Clave 🔑

**스페인어-영어 코드스위칭 감성분석 앱**

Hispanic-American SNS에서 사용되는 Spanglish 코드스위칭 텍스트의 문화적 맥락을 이해하고 정확한 감성분석을 제공하는 풀스택 애플리케이션입니다.

## 📋 프로젝트 개요

본 프로젝트는 KSC 2025 논문의 핵심 발견을 실제 애플리케이션으로 구현한 것입니다. 기존 AI 모델들이 코드스위칭 텍스트의 문화적 맥락을 놓치는 문제를 프롬프트 엔지니어링을 통해 해결합니다.

**핵심 문제**: "Me acostumbre ya a tenerte aqui 😢 Im depressed"와 같은 문장에서 기존 모델은 스페인어 부분만 보고 Neutral로 오판하지만, 실제로는 영어로 코드스위칭된 "Im depressed"가 핵심 감정을 표현합니다.

**해결 방법**: Gemini 2.5 Flash + 정교한 프롬프트 엔지니어링 (Role + Few-shot + Chain-of-Thought + Self-consistency)

---

## 🏗️ 시스템 아키텍처

```
    [Android Client - Java]
              |
              | POST /api/analyze
              v
    [FastAPI Server - 비동기]
      1. 프롬프트 엔지니어링
         (Role + Few-shot + CoT)
      2. Gemini API 병렬 호출 (x3)
      3. Self-consistency 집계
              |
              v
    [Gemini 2.5 Flash API]
```

---

## 🛠️ 기술 스택

| 구분 | 기술 | 버전/상세 |
|------|------|------|
| **Frontend** | Android (Java) | API Level 24+ (Android 7.0+) |
| | Material Design 3 | Latest |
| **Backend** | FastAPI | 0.104+ |
| **AI Model** | Gemini 2.5 Flash | Latest |
| **Language** | Python | 3.9+ |
| **API** | REST (JSON) | - |

**왜 FastAPI?**
- Self-Consistency를 위해 Gemini API 3회 **병렬 호출** 필요 → 비동기 필수
- 단순 API 서버 (DB 없음) → Django의 무거운 기능 불필요
- 자동 API 문서 생성 (`/docs`) → 테스트 편리

---

## 📁 프로젝트 구조

```
clave/
├── backend/                    # FastAPI 서버 (단일 파일 구조)
│   ├── main.py                 # 모든 로직이 포함된 FastAPI 앱
│   ├── requirements.txt        # Python 의존성
│   ├── .env.example            # 환경 변수 예시
│   └── .env                    # 실제 환경 변수 (gitignore)
│
├── android/                    # Android 앱 (Java + Material Design 3)
│   └── app/src/main/java/...   # MainActivity, ResultActivity, RetrofitClient 등
│
└── README.md
```

**Backend - 단일 파일 구조 채택:**
- FastAPI 초보자를 위해 모든 코드를 `main.py` 하나에 통합
- 프롬프트 엔지니어링, Gemini API 호출, Self-consistency 로직 모두 포함
- 파일 구조가 단순해 이해하기 쉽고 유지보수 용이

**Frontend - Android 앱:**
- Android Java + Material Design 3
- Retrofit + OkHttp (120초 타임아웃) REST API 통신
- 감성별 색상 카드 + 신뢰도 프로그레스 바 시각화

---

## 🚀 시작하기

### 1. 사전 준비

#### 필수 소프트웨어
- Python 3.9 이상
- Android Studio (최신 버전)
- VS Code (권장)
- JDK 11 이상

#### API 키 발급
1. [Google AI Studio](https://aistudio.google.com/apikey)에서 Gemini API 키 발급
2. Google Cloud 프로젝트에 결제 계정 연결 필요 (무료 크레딧 사용 가능)

---

### 2. Backend 설정

#### 2.1 가상환경 생성 및 활성화
```bash
# 프로젝트 루트에서
cd backend

# 가상환경 생성
python -m venv venv

# 활성화 (macOS/Linux)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate
```

#### 2.2 의존성 설치
```bash
pip install -r requirements.txt
```

#### 2.3 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 수정
# GEMINI_API_KEY=your_api_key_here
```

#### 2.4 서버 실행
```bash
# 개발 모드 (핫 리로드)
uvicorn main:app --reload
```

서버가 `http://localhost:8000`에서 실행됩니다.

**서버 실행 확인:**
```bash
# 브라우저에서 http://localhost:8000 접속
# 또는 curl로 확인
curl http://localhost:8000
```

---

## 📱 Android 앱 UI/UX

### 디자인 컨셉

**문화적 정체성**: Hispanic-American 문화를 반영한 멕시코 색상 브랜딩

**색상 전략**:
- **브랜딩 요소** (로고, 앱바, 아이콘): 멕시코 국기 색상
  - 초록: `#006847` (0, 104, 71)
  - 빨강: `#CE1127` (206, 17, 39)
  - 흰색: `#FFFFFF` (255, 255, 255)

- **감성 표시** (직관적 UX): Material Design 표준 색상
  - Positive: `#4CAF50` (Material Green)
  - Negative: `#F44336` (Material Red)
  - Neutral: `#9E9E9E` (Material Grey)

**디자인 철학**: 멕시코 색상으로 문화적 정체성을 강조하면서도, 감성 표시는 사용자에게 직관적인 표준 색상 사용

---

### 화면 설계

#### 화면 1: 메인 (입력)
- 앱바: Clave 🔑 (멕시코 초록 배경)
- 텍스트 입력창 + 글자수 카운터
- [분석하기] 버튼
- 예시 칩: [Positive] [Negative] [Neutral]

#### 화면 2: 결과
- 입력 텍스트 표시
- 감성 결과 카드 (색상별 배경)
  - 😔 Negative / 88% / 일치도 3/3 ✓
- 핵심 표현 칩
- 분석 상세 (Analysis Focus, Cultural Context)

---

### 주요 기능

- ✅ **실시간 감성 분석**: FastAPI 서버와 REST API 통신
- 🎨 **감성별 색상 차별화**: Positive(초록), Negative(빨강), Neutral(회색)
- 📊 **Self-consistency 시각화**: 3번 호출 결과 일치도 표시 (예: 3/3 ✓)
- ⚡ **예시 문장 빠른 입력**: 칩 형식으로 Positive/Negative/Neutral 예시 제공
- 🔄 **로딩 상태 표시**: 분석 중 프로그레스 인디케이터
- ⚠️ **에러 처리**: 서버 연결 실패, 빈 입력 등 사용자 친화적 메시지

---

### 테스트용 예시 문장

**Positive:**
```
Ayer fue amazing, la pasé super bien con mis amigos y we had so much fun!
```

**Negative:**
```
Estoy so tired of this, siempre the same problems y nadie helps me.
```

**Neutral:**
```
I need to go al supermercado porque no hay milk en la casa.
```

---

### Android 앱 설정

**요구사항:**
- Android Studio (최신 버전)
- API Level 24 (Android 7.0) 이상
- 인터넷 연결 필수

**실행 방법:**
1. Android Studio에서 프로젝트 열기
2. Backend 서버 먼저 실행 (`http://localhost:8000`)
3. 에뮬레이터 실행 시 서버 주소: `http://10.0.2.2:8000`
4. 실제 기기 실행 시 서버 주소: `http://{PC_IP}:8000`

**주요 의존성:**
- Retrofit (REST API 통신)
- Gson (JSON 파싱)
- Material Components (UI)

---

## 📡 API 명세

### POST /api/analyze

코드스위칭 텍스트의 감성을 분석합니다.

**Endpoint:** `http://localhost:8000/api/analyze`

#### Request
```json
{
  "text": "Estoy so tired of this, siempre the same problems y nadie helps me."
}
```

#### Response
```json
{
  "sentiment": "negative",
  "confidence": 0.88,
  "analysis": {
    "analysis_focus": "스페인어 부분 'Estoy so tired of this, siempre the same problems'는 불만을 내포하고 있으며, 영어 코드스위칭 'y nadie helps me'에서 좌절감과 무력감이 증폭됨.",
    "cultural_context": "강한 감정을 영어로 표현하는 Hispanic-American 코드스위칭 패턴이 나타남. 문제 해결에 대한 좌절감을 토로하며, 도움을 받지 못하는 상황에 대한 불만이 두드러짐.",
    "key_expression": "nadie helps me"
  },
  "consistency_info": {
    "num_calls": 3,
    "agreement": "3/3",
    "all_results": [
      {"sentiment": "negative", "confidence": 0.9},
      {"sentiment": "negative", "confidence": 0.9},
      {"sentiment": "negative", "confidence": 0.85}
    ]
  }
}
```

#### 응답 필드 설명
- `sentiment`: 감성 분류 (positive/negative/neutral)
- `confidence`: 신뢰도 (0.0-1.0)
- `analysis`:
  - `analysis_focus`: 어디에 주목했는지 (핵심 분석 요약)
  - `cultural_context`: 왜 그렇게 해석했는지 (문화적 배경 설명)
  - `key_expression`: 핵심 감정 표현
- `consistency_info`: Self-consistency 정보
  - `num_calls`: API 호출 횟수 (기본 3회)
  - `agreement`: 일치도 (예: "3/3")
  - `all_results`: 각 호출의 감성과 신뢰도

#### 감성 분류
- `positive`: 긍정적 감정
- `negative`: 부정적 감정
- `neutral`: 중립적 감정

---

## 🔬 핵심 기술

### 1. Self-Consistency 메커니즘

신뢰도 향상을 위해 Gemini API를 3번 병렬 호출하여 결과를 집계합니다.

**집계 로직**:
- 2개 이상 같은 감성 → 해당 감성 채택, confidence 평균
- 3개 모두 다른 감성 → 가장 높은 confidence 값 채택

**예시**:
```
호출 1: Negative (0.85)
호출 2: Negative (0.89)
호출 3: Neutral (0.72)
→ 결과: Negative, confidence = 0.87
```

### 2. 프롬프트 엔지니어링 전략

#### Role Prompting
```
You are an expert sentiment analyst specializing in
Hispanic-American code-switching culture.
```

#### Few-shot Learning (논문 기반)
KSC 2025 논문에서 검증된 실제 예시 3개 포함

#### Chain-of-Thought
단계별 분석 프로세스:
1. 스페인어/영어 구간 식별
2. 코드스위칭 포인트 찾기
3. 각 구간의 감성 분석
4. 문화적 맥락 고려 (JAJAJAJA = positive 등)
5. 핵심 감정 판단
6. 최종 결과 도출

---

## 💡 사용 예시 (논문 기반 실제 사례)

### 예시 1: 긍정적 감성 (Positive)
**입력**:
```
#selfie #goinghome #happy A descansar un poco! #weekend
```

**출력**:
- Sentiment: `positive`
- Confidence: `0.91`

**분석 과정**:
- 해시태그 #happy가 명확한 긍정 표현
- "A descansar un poco" (조금 쉬러 가야지) + #weekend의 긍정적 맥락
- 스페인어-영어 코드스위칭이 자연스럽게 긍정적 분위기 형성

**왜 이 사례가 중요한가?**
기존 모델들은 해시태그를 단순 메타데이터로 처리하여 Neutral로 오판했으나, Hispanic-American SNS 문화에서 해시태그는 감정 표현의 핵심 수단입니다.

---

### 예시 2: 부정적 감성 (Negative) ⭐ **논문의 핵심 발견**
**입력**:
```
Me acostumbre ya a tenerte aqui 😢 Im depressed y estas lejos
```

**출력**:
- Sentiment: `negative`
- Confidence: `0.88`

**분석 과정**:
- 스페인어 부분 "Me acostumbre ya a tenerte aqui" (너가 여기 있는 게 익숙해졌어)는 표면적으로 중립적
- **핵심 포인트**: 영어로 코드스위칭된 "Im depressed"에서 진짜 감정이 폭발
- 😢 이모지 + "y estas lejos" (그런데 넌 멀리 있어)가 부정적 감정 강화

**왜 이 사례가 중요한가?**
이것이 **논문의 핵심 발견**입니다. 기존 AI 모델들은 스페인어 부분만 보고 Neutral로 오판했으나, 실제로 Hispanic-American은 **강한 감정을 다른 언어로 코드스위칭하여 표현하는 문화적 패턴**이 있습니다. 코드스위칭 지점이 감정의 클라이맥스입니다.

---

### 예시 3: 중립적 감성 (Neutral)
**입력**:
```
I think I'll buy me a loco burrito.
I've never heard of that.
```

**출력**:
- Sentiment: `neutral`
- Confidence: `0.82`

**분석 과정**:
- "loco" 키워드가 포함되어 있지만 음식 이름 "loco burrito"의 일부일 뿐
- 전체 맥락은 단순 정보 전달 목적의 대화
- 감정 표현이 아닌 사실 진술

**왜 이 사례가 중요한가?**
기존 모델들은 "loco"(미친) 키워드만 보고 Positive나 Negative로 오판했습니다. 이 사례는 **맥락 기반 판단의 중요성**을 보여줍니다. 문화적 표현(loco, cabrón 등)은 맥락에 따라 의미가 완전히 달라집니다.

---

### 📊 논문에서 발견한 주요 오류 패턴

KSC 2025 논문 분석 결과, 기존 데이터셋의 **17% 라벨링 오류** 중:

1. **Positive ↔ Neutral 혼동** (65%):
   - 과도한 Positive 분류 또는 숨겨진 Positive 맥락 미탐지

2. **Negative 감정 미탐지** (17.4%):
   - 코드스위칭 지점의 부정적 감정 표현 놓침

3. **문화적 맥락 누락**:
   - JAJAJAJA (긍정적 웃음), cabrón/loco (맥락 의존) 등 오해

본 앱은 이러한 오류 패턴을 **프롬프트 엔지니어링으로 해결**합니다.

---

## ✅ 실제 테스트 결과 (`gemini-2.5-flash`)

아래는 개발 완료 후 실제 API로 테스트한 결과입니다. 모든 케이스에서 **3/3 일치**를 달성했습니다.

### Test Case 1: Positive 감성
**입력:**
```
Ayer fue amazing, la pasé super bien con mis amigos y we had so much fun!
```

**결과:**
- ✅ Sentiment: `positive`
- ✅ Confidence: `0.94`
- ✅ Agreement: `3/3` (완벽한 일치)
- **Analysis Focus**: "스페인어 'Ayer fue amazing, la pasé super bien con mis amigos'와 영어 'we had so much fun!' 모두 긍정적인 감정을 표현하며, 두 언어의 조합이 긍정적인 분위기를 강화합니다."
- **Cultural Context**: "스페인어와 영어의 코드스위칭이 자연스럽게 이루어지며, 긍정적인 경험을 강조하는 일반적인 Hispanic-American 소셜 미디어 사용 패턴을 보여줍니다."

---

### Test Case 2: Neutral 감성
**입력:**
```
I need to go al supermercado porque no hay milk en la casa.
```

**결과:**
- ✅ Sentiment: `neutral`
- ✅ Confidence: `0.85`
- ✅ Agreement: `3/3` (완벽한 일치)
- **Analysis Focus**: "텍스트는 슈퍼마켓에 가야 하는 이유를 설명하는 단순한 진술입니다. 감정적인 표현이나 강한 감정을 나타내는 코멘트가 없습니다."
- **Cultural Context**: "코드 스위칭이 발생했지만, 이는 일상적인 대화에서 흔히 나타나는 현상이며, 특정 감정을 강조하기 위한 의도적인 사용으로 보이지 않습니다."

---

### Test Case 3: Negative 감성
**입력:**
```
Estoy so tired of this, siempre the same problems y nadie helps me.
```

**결과:**
- ✅ Sentiment: `negative`
- ✅ Confidence: `0.88`
- ✅ Agreement: `3/3` (완벽한 일치)
- **Analysis Focus**: "스페인어 부분 'Estoy so tired of this, siempre the same problems'는 불만을 내포하고 있으며, 영어 코드스위칭 'y nadie helps me'에서 좌절감과 무력감이 증폭됨."
- **Cultural Context**: "강한 감정을 영어로 표현하는 Hispanic-American 코드스위칭 패턴이 나타남. 문제 해결에 대한 좌절감을 토로하며, 도움을 받지 못하는 상황에 대한 불만이 두드러짐."

**핵심 성과:**
- 🎯 **100% 일치율**: 모든 테스트에서 Self-Consistency 3/3 달성
- 📊 **높은 신뢰도**: 평균 confidence 0.89 (0.85-0.94)
- 🧠 **문화적 맥락 이해**: 코드스위칭 지점을 정확히 파악

---

## 🧪 테스트

### Backend 테스트
```bash
cd backend

# API 테스트 (서버 실행 후)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Estoy muy happy hoy"}'

# 또는 브라우저에서 자동 생성된 API 문서 확인
# http://localhost:8000/docs (Swagger UI)
```

---

## 📚 개발 워크플로우

### Backend 개발 (VS Code)
```bash
# 1. Backend 디렉토리에서 작업
cd backend

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 서버 실행 (터미널)
uvicorn main:app --reload

# 4. 자동 생성된 API 문서 확인
# http://localhost:8000/docs
```

### main.py 코드 구조
```python
# 1. 설정 (Config) - 환경 변수 로드
# 2. Pydantic 모델 - Request/Response 정의
# 3. 프롬프트 엔지니어링 - build_prompt()
# 4. Gemini API 호출 - analyze_sentiment_single()
# 5. Self-Consistency - aggregate_results(), analyze_with_consistency()
# 6. FastAPI 앱 - app 초기화, CORS 설정
# 7. API 엔드포인트 - /api/analyze
```

---

## 🎯 핵심 차별점

1. **논문 기반**: KSC 2025 논문의 연구 결과를 실제 API로 구현
   - **논문 접근법**: 데이터 재라벨링 + mBERT-XLM-R 앙상블 (67.15%)
   - **API 접근법**: 프롬프트 엔지니어링 + Self-consistency (데이터 재라벨링 없이 동일한 효과 목표)
2. **단일 파일 구조**: 모든 로직이 main.py 하나에 통합되어 이해하기 쉬움
3. **정교한 프롬프트**: Role + Few-shot + CoT + Self-consistency 조합
4. **도메인 전문성**: 스페인어 능력을 활용한 문화적 맥락 반영
5. **비동기 병렬 처리**: FastAPI의 async를 활용한 빠른 응답 (3회 호출 동시 처리)

---

## 🔧 트러블슈팅

### ⚠️ Gemini API Quota 이슈 (해결됨)

개발 중 `gemini-2.5-flash` 모델에서 **429 Quota Exceeded** 에러가 발생했습니다.

**문제:**
- API 키만 발급받고 결제 계정 미연결 시 quota limit: 0
- 무료 tier만으로는 API 호출 불가

**원인 분석:**
1. **결제 계정 필수**: Google Cloud 프로젝트에 결제 계정이 연결되어야 API 사용 가능
2. **무료 크레딧**: 결제 계정 연결해도 무료 크레딧 범위 내에서는 과금 없음

**해결 방법:**
```bash
# Google Cloud 프로젝트에 결제 계정 연결 후 gemini-2.5-flash 사용 가능
GEMINI_MODEL=gemini-2.5-flash  # ✅ 결제 계정 연결 시 작동
```

**결과:**
- ✅ 결제 계정 연결 후 `gemini-2.5-flash` 정상 작동
- ✅ Safety filter 이슈 해결
- ✅ 논문의 핵심 예시 ("Im depressed") 정상 처리

---

## 🔮 향후 개선 사항 (TODO)

### 성능 최적화

**현재 상황:**
- Self-Consistency로 Gemini API 3번 병렬 호출
- 응답 시간: 평균 2-4초 (가장 느린 API 응답 기준)

**최적화 방안:**

1. **NUM_CALLS 조정**
   ```bash
   # .env에서 NUM_CALLS=2로 줄이기
   # 장점: 응답 속도 33% 향상
   # 단점: Self-consistency 신뢰도 약간 감소
   ```

2. **Streaming 응답 구현**
   ```python
   # Gemini의 generate_content_stream() 사용
   # 부분 응답을 실시간으로 클라이언트에 전송 (UX 개선)
   ```

3. **응답 캐싱**
   ```python
   # 동일한 텍스트 재요청 시 캐시에서 즉시 반환
   from functools import lru_cache
   # 또는 Redis 사용
   ```

4. **Timeout 설정**
   ```python
   # 5초 이상 걸리는 API 호출은 포기
   asyncio.wait_for(task, timeout=5.0)
   # 2개 결과로만 판단
   ```

5. **경량 모델 테스트**
   ```bash
   # gemini-2.5-flash-lite 등 경량 모델 시도
   # 더 빠른 응답, 정확도 trade-off 확인 필요
   ```

---

## 👥 저자

**Bada**
- KSC 2025 논문 저자
- 스페인어-영어 코드스위칭 감성분석 연구

---

**Made with 🔑 by Bada**
