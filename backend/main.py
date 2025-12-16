"""
Clave Backend - FastAPI 애플리케이션
스페인어-영어 코드스위칭 감성분석 API

KSC 2025 논문 기반:
- 프롬프트 엔지니어링 (Role + Few-shot + CoT)
- Self-Consistency (다중 API 호출)
- Gemini 2.5 Flash 사용
"""

import os
import json
import asyncio
from typing import List, Dict
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


# ==================== 설정 ====================

# 환경 변수 로드
load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-exp")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
NUM_CALLS = int(os.getenv("NUM_CALLS", "3"))  # Self-consistency 호출 횟수

# 설정 검증
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set. "
        "Please set it in .env file or environment variables."
    )

# Gemini 초기화
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)


# ==================== Pydantic 모델 (Request/Response) ====================

class AnalyzeRequest(BaseModel):
    """감성 분석 요청 모델"""
    text: str

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Me acostumbre ya a tenerte aqui 😢 Im depressed"
            }
        }


class AnalysisDetail(BaseModel):
    """분석 세부사항"""
    analysis_focus: str
    cultural_context: str
    key_expression: str
    translation: str  # 한글 번역


class ConsistencyInfo(BaseModel):
    """Self-consistency 정보"""
    num_calls: int
    agreement: str
    all_results: list


class AnalyzeResponse(BaseModel):
    """감성 분석 응답 모델"""
    sentiment: str
    confidence: float
    analysis: AnalysisDetail
    consistency_info: ConsistencyInfo


# ==================== 핵심 로직: 프롬프트 엔지니어링 ====================

def build_prompt(text: str) -> str:
    """
    KSC 2025 논문 결과를 기반으로 정교한 프롬프트 구성

    포함 내용:
    - Role Prompting (역할 부여)
    - Few-shot Examples (논문의 실제 예시)
    - Chain-of-Thought (단계별 추론)
    - Cultural context guidelines (문화적 맥락 가이드)
    """
    prompt = f"""당신은 Hispanic-American 코드스위칭 문화를 전문으로 하는 감성분석 전문가입니다. 소셜미디어에서 사용되는 Spanglish의 뉘앙스를 이해하며, 특히 강한 감정이 언어 전환을 통해 표현되는 문화적 패턴을 파악할 수 있습니다.

핵심 가이드라인 (연구 결과 기반):

1. 코드스위칭 지점 분석:
   - 코드스위칭 지점이 핵심 감정을 담고 있는 경우가 많음
   - 강한 감정을 표현할 때 다른 언어로 전환하는 패턴
   - 예: 스페인어 중립적 텍스트 + 영어 감정 표현 = 영어 부분에 집중

2. 문화적 표현 해석:
   - JAJAJAJA, jaja = 긍정 (스페인어 웃음 표현)
   - 해시태그는 Hispanic-American SNS에서 핵심 감정 지표 (단순 메타데이터가 아님)
   - "loco", "cabrón" = 맥락 의존적 (친구 사이는 친근함, 일반적으로는 부정적)

3. 과도한 분류 방지:
   - 키워드(happy, loco 등)만으로 Positive 분류하지 말 것
   - 전체 맥락과 코드스위칭 패턴 고려
   - 표면적으로 중립적인 스페인어 + 감정적 영어 = 영어 부분 신중히 분석

4. 숨겨진 감정 탐지:
   - 겉보기 중립 텍스트 + 이모티콘 + 코드스위칭 = 강한 감정 숨어있는 경우 많음
   - 부정적 감정 강도 과소평가하지 말 것

Few-shot 예시 (KSC 2025 논문):

예시 1 (긍정):
입력: "#selfie #goinghome #happy A descansar un poco! #weekend"
분석: 해시태그 #happy가 명확한 긍정 표현. "A descansar un poco" (조금 쉬러 가야지) + #weekend가 긍정적 맥락 형성. 스페인어-영어 코드스위칭이 자연스럽게 긍정적 분위기 형성.
출력: {{"sentiment": "positive", "confidence": 0.91, "analysis_focus": "해시태그 #happy가 명확한 긍정 표현이며 주말 휴식 맥락과 결합", "cultural_context": "Hispanic-American SNS에서 해시태그는 감정 표현의 핵심 수단", "key_expression": "#happy", "translation": "셀카 찍고 집에 가는 중 행복해 조금 쉬어야지! 주말이야"}}

예시 2 (부정 - 핵심 발견):
입력: "Me acostumbre ya a tenerte aqui 😢 Im depressed y estas lejos"
분석: 스페인어 부분 "Me acostumbre ya a tenerte aqui" (너가 여기 있는 게 익숙해졌어)는 표면적으로 중립적. 핵심 포인트: 진짜 감정은 영어 코드스위칭 "Im depressed"에서 폭발. 이모티콘 😢 + "y estas lejos" (그런데 넌 멀리 있어)가 부정적 감정 강화.
출력: {{"sentiment": "negative", "confidence": 0.88, "analysis_focus": "스페인어 부분은 표면적으로 중립적이나, 영어 코드스위칭 'Im depressed'에서 핵심 감정 표현", "cultural_context": "Hispanic-American은 강한 감정을 언어 전환을 통해 표현하는 문화적 패턴 - 코드스위칭 지점이 감정의 클라이맥스", "key_expression": "Im depressed", "translation": "너가 여기 있는 게 익숙해졌어 😢 우울해 그런데 넌 멀리 있잖아"}}

예시 3 (중립):
입력: "I think I'll buy me a loco burrito. I've never heard of that"
분석: "loco" 키워드가 포함되어 있지만 음식 이름 "loco burrito"의 일부일 뿐. 전체 맥락은 단순 정보 교환 대화. 감정 표현이 아닌 사실 진술.
출력: {{"sentiment": "neutral", "confidence": 0.82, "analysis_focus": "loco는 음식 이름의 일부이지 감정 표현이 아님. 맥락은 정보 전달 목적 대화", "cultural_context": "문화적 표현(loco, cabrón)은 맥락에 따라 의미가 완전히 달라짐", "key_expression": "loco burrito", "translation": "나 로코 부리또 사 먹을 것 같아. 그런 거 처음 들어봤네"}}

분석 단계 (Chain-of-Thought):
1. 스페인어와 영어 구간 식별
2. 코드스위칭 지점 찾기
3. 각 구간의 감성 개별 분석
4. 문화적 맥락 고려 (JAJAJAJA = 긍정, 해시태그 = 감정 마커 등)
5. 어느 구간이 핵심 감정을 담고 있는지 판단
6. 신뢰도 점수와 함께 최종 감성 제공

다음 텍스트를 분석하세요:
"{text}"

다음 JSON 형식으로만 응답하세요 (마크다운, 코드블록 없이):
{{"sentiment": "positive" | "negative" | "neutral", "confidence": 0.0-1.0, "analysis_focus": "어디에 주목했는지 1-2문장 요약", "cultural_context": "왜 그렇게 해석했는지 문화적 배경", "key_expression": "핵심 표현", "translation": "입력 문장의 자연스러운 한글 번역"}}"""

    return prompt


# ==================== Gemini API 호출 ====================

async def analyze_sentiment_single(text: str) -> dict:
    """
    Gemini를 사용하여 코드스위칭 텍스트의 감성 분석 (단일 호출)

    Args:
        text: 스페인어-영어 코드스위칭 입력 텍스트

    Returns:
        감성, 신뢰도, 분석 세부사항을 포함한 dict
    """
    try:
        prompt = build_prompt(text)

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": TEMPERATURE,
                "max_output_tokens": MAX_TOKENS,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        # 디버깅: response 전체 구조 확인 (필요시 주석 해제)
        # print(f"🔍 Response finish_reason: {response.candidates[0].finish_reason if response.candidates else 'No candidates'}")
        # print(f"🔍 Safety ratings: {response.candidates[0].safety_ratings if response.candidates else 'No candidates'}")

        # finish_reason=2 (SAFETY) 처리
        if response.candidates and response.candidates[0].finish_reason == 2:
            # print(f"⚠️  Safety filter triggered. Prompt was:\n{prompt[:200]}...")
            # Safety filter 무시하고 neutral 반환
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "analysis_focus": "Safety filter triggered - returning neutral",
                "cultural_context": "Response blocked by safety filter",
                "key_expression": "N/A"
            }

        # JSON 응답 파싱
        result_text = response.text.strip()

        # 마크다운 코드블록 제거 (있을 경우)
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:].strip()

        result = json.loads(result_text)

        # 결과 검증
        if "sentiment" not in result or "confidence" not in result:
            raise ValueError("Gemini로부터 잘못된 응답 형식")

        # 필드명 확인 및 기본값 설정
        if "analysis_focus" not in result:
            result["analysis_focus"] = result.get("process", "")
        if "cultural_context" not in result:
            result["cultural_context"] = result.get("cultural_reason", "")
        if "translation" not in result:
            result["translation"] = "번역 정보 없음"

        return result

    except json.JSONDecodeError as e:
        # 폴백: 텍스트에서 감성 추출 시도
        result_text = response.text.lower()
        if "positive" in result_text or "긍정" in result_text:
            sentiment = "positive"
        elif "negative" in result_text or "부정" in result_text:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "confidence": 0.5,
            "process": "JSON 파싱 실패, 폴백 사용",
            "cultural_reason": "N/A",
            "key_expression": "N/A",
            "error": str(e)
        }

    except Exception as e:
        print(f"❌ Gemini API 에러: {type(e).__name__}: {str(e)}")  # 로그 출력
        import traceback
        traceback.print_exc()  # 전체 에러 스택 출력
        raise Exception(f"Gemini API 호출 실패: {str(e)}")


# ==================== Self-Consistency 로직 ====================

def aggregate_results(results: List[Dict]) -> dict:
    """
    여러 감성 분석 결과 집계

    로직:
    1. 감성 발생 횟수 카운트
    2. 다수(2개 이상 동일)가 존재하면 → 다수 사용, 신뢰도 평균
    3. 모두 다르면 → 가장 높은 신뢰도 결과 사용
    """
    # 감성 발생 횟수 카운트
    sentiment_counts = {}
    sentiment_confidences = {}

    for result in results:
        sentiment = result["sentiment"]
        confidence = result["confidence"]

        if sentiment not in sentiment_counts:
            sentiment_counts[sentiment] = 0
            sentiment_confidences[sentiment] = []

        sentiment_counts[sentiment] += 1
        sentiment_confidences[sentiment].append(confidence)

    # 다수 찾기 (2개 이상 같은 감성)
    max_count = max(sentiment_counts.values())

    if max_count >= 2:
        # 다수 존재 - 다수 사용
        majority_sentiment = [
            s for s, c in sentiment_counts.items() if c == max_count
        ][0]

        avg_confidence = sum(sentiment_confidences[majority_sentiment]) / len(
            sentiment_confidences[majority_sentiment]
        )

        # 다수 결과 중 confidence가 가장 높은 것에서 상세 분석 가져오기
        majority_result = max(
            (r for r in results if r["sentiment"] == majority_sentiment),
            key=lambda r: r["confidence"]
        )

        return {
            "sentiment": majority_sentiment,
            "confidence": round(avg_confidence, 2),
            "analysis": {
                "analysis_focus": majority_result.get("analysis_focus", majority_result.get("process", "")),
                "cultural_context": majority_result.get("cultural_context", majority_result.get("cultural_reason", "")),
                "key_expression": majority_result.get("key_expression", ""),
                "translation": majority_result.get("translation", "번역 정보 없음"),
            },
            "consistency_info": {
                "num_calls": len(results),
                "agreement": f"{max_count}/{len(results)}",
                "all_results": [
                    {
                        "sentiment": r["sentiment"],
                        "confidence": r["confidence"]
                    }
                    for r in results
                ]
            }
        }
    else:
        # 모두 다름 - 가장 높은 신뢰도 사용
        best_result = max(results, key=lambda r: r["confidence"])

        return {
            "sentiment": best_result["sentiment"],
            "confidence": best_result["confidence"],
            "analysis": {
                "analysis_focus": best_result.get("analysis_focus", best_result.get("process", "")),
                "cultural_context": best_result.get("cultural_context", best_result.get("cultural_reason", "")),
                "key_expression": best_result.get("key_expression", ""),
                "translation": best_result.get("translation", "번역 정보 없음"),
            },
            "consistency_info": {
                "num_calls": len(results),
                "agreement": f"1/{len(results)} (used highest confidence)",
                "all_results": [
                    {
                        "sentiment": r["sentiment"],
                        "confidence": r["confidence"]
                    }
                    for r in results
                ]
            }
        }


async def analyze_with_consistency(text: str) -> dict:
    """
    자기 일관성을 활용한 텍스트 분석 (다중 병렬 호출)

    집계 로직 (논문 기반):
    - 2개 이상 같은 감성 → 해당 감성 사용, 신뢰도 평균
    - 3개 모두 다른 감성 → 가장 높은 신뢰도 사용

    Args:
        text: 분석할 입력 텍스트

    Returns:
        집계된 감성 분석 결과를 포함한 dict
    """
    # Gemini API를 병렬로 여러 번 호출
    tasks = [
        analyze_sentiment_single(text)
        for _ in range(NUM_CALLS)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 예외 필터링
    valid_results = [
        r for r in results
        if not isinstance(r, Exception) and "sentiment" in r
    ]

    if not valid_results:
        raise Exception("모든 API 호출 실패")

    # 결과 집계
    return aggregate_results(valid_results)


# ==================== FastAPI 애플리케이션 ====================

# FastAPI 앱 초기화
app = FastAPI(
    title="Clave API",
    description="Spanish-English Code-switching Sentiment Analysis API",
    version="1.0.0",
)

# CORS 설정 (Android 앱 통신용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용: 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API 엔드포인트 ====================

@app.get("/")
async def root():
    """루트 엔드포인트 - 서버 상태 확인"""
    return {
        "message": "Clave API is running",
        "version": "1.0.0",
        "status": "healthy",
        "model": GEMINI_MODEL,
        "endpoints": {
            "analyze": "POST /api/analyze",
            "health": "GET /api/health"
        }
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_sentiment_endpoint(request: AnalyzeRequest):
    """
    스페인어-영어 코드스위칭 텍스트의 감성 분석

    **KSC 2025 논문 기반 프롬프트 엔지니어링 사용:**
    - Role Prompting (Hispanic-American 전문가)
    - Few-shot Learning (논문의 실제 예시)
    - Chain-of-Thought (단계별 분석)
    - Self-Consistency (3회 병렬 호출)

    **Parameters:**
    - text: 분석할 스페인어-영어 코드스위칭 텍스트

    **Returns:**
    - sentiment: "positive" | "negative" | "neutral"
    - confidence: 0.0 ~ 1.0 (신뢰도)
    - analysis: 분석 과정, 문화적 이유, 핵심 표현
    - consistency_info: Self-consistency 결과 상세
    """

    # 입력 검증
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="텍스트가 비어있습니다. 'text' 필드를 제공해주세요."
        )

    if len(request.text) > 1000:
        raise HTTPException(
            status_code=400,
            detail="텍스트가 너무 깁니다 (최대 1000자)."
        )

    try:
        # Self-consistency를 사용한 감성 분석
        result = await analyze_with_consistency(request.text)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"감성 분석 중 오류 발생: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """API 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "service": "Clave Sentiment Analysis API",
        "model": GEMINI_MODEL,
        "num_calls": NUM_CALLS
    }


# ==================== 서버 시작 이벤트 ====================

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    print("=" * 60)
    print("🔑 Clave API Server Starting...")
    print(f"📍 Model: {GEMINI_MODEL}")
    print(f"🔄 Self-consistency calls: {NUM_CALLS}")
    print(f"🌡️  Temperature: {TEMPERATURE}")
    print("=" * 60)
