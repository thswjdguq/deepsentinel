from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
import time
import random
import os
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(
    title="DeepSentinel AI Server",
    description="딥페이크 탐지 AI 분석 서버",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisMetrics(BaseModel):
    """
    분석 수치 모델
    """
    eye_blink_rate: float  # 눈 깜빡임 빈도 (0-100)
    lip_sync_score: float  # 입술 동기화 점수 (0-100)
    lighting_consistency: float  # 빛의 일관성 (0-100)
    facial_artifacts: float  # 얼굴 인공물 지수 (0-100)
    texture_quality: float  # 텍스처 품질 (0-100)
    motion_smoothness: float  # 동작 부드러움 (0-100)


class AnalysisResponse(BaseModel):
    """
    분석 결과 응답 모델
    """
    result: str  # 'real', 'fake', 'uncertain'
    confidence: float  # 신뢰도 (0-1)
    metrics: AnalysisMetrics
    report: str  # GPT 생성 리포트
    analysis_time: float  # 분석 소요 시간 (초)


def generate_analysis_metrics() -> AnalysisMetrics:
    """
    딥페이크 분석을 위한 임의의 메트릭을 생성합니다.
    실제 환경에서는 딥러닝 모델의 출력으로 대체됩니다.
    
    Returns:
        AnalysisMetrics: 생성된 분석 수치
    """
    # 진짜/가짜를 결정하는 랜덤 시드
    is_fake = random.random() < 0.4  # 40% 확률로 딥페이크
    
    if is_fake:
        # 딥페이크일 경우: 비정상적인 수치
        metrics = AnalysisMetrics(
            eye_blink_rate=random.uniform(15, 35),  # 비정상적으로 낮음
            lip_sync_score=random.uniform(50, 75),  # 동기화 문제
            lighting_consistency=random.uniform(40, 70),  # 빛의 불일치
            facial_artifacts=random.uniform(60, 90),  # 높은 인공물
            texture_quality=random.uniform(45, 70),  # 낮은 텍스처 품질
            motion_smoothness=random.uniform(50, 75),  # 부자연스러운 동작
        )
    else:
        # 진짜일 경우: 정상 수치
        metrics = AnalysisMetrics(
            eye_blink_rate=random.uniform(65, 95),  # 자연스러운 눈 깜빡임
            lip_sync_score=random.uniform(80, 98),  # 완벽한 동기화
            lighting_consistency=random.uniform(75, 95),  # 일관된 빛
            facial_artifacts=random.uniform(5, 25),  # 낮은 인공물
            texture_quality=random.uniform(80, 95),  # 높은 텍스처 품질
            motion_smoothness=random.uniform(85, 98),  # 자연스러운 동작
        )
    
    return metrics


def calculate_overall_score(metrics: AnalysisMetrics) -> tuple[str, float]:
    """
    메트릭을 기반으로 전체 점수와 결과를 계산합니다.
    
    Args:
        metrics: 분석 메트릭
        
    Returns:
        tuple: (result, confidence) - 결과와 신뢰도
    """
    # 가중치 적용 점수 계산
    score = (
        metrics.eye_blink_rate * 0.15 +
        metrics.lip_sync_score * 0.25 +
        metrics.lighting_consistency * 0.20 +
        (100 - metrics.facial_artifacts) * 0.25 +
        metrics.texture_quality * 0.10 +
        metrics.motion_smoothness * 0.05
    )
    
    # 결과 판정
    if score >= 75:
        result = "real"
        confidence = min(score / 100, 0.95)
    elif score >= 50:
        result = "uncertain"
        confidence = 0.5 + (score - 50) / 100
    else:
        result = "fake"
        confidence = min((100 - score) / 100, 0.95)
    
    return result, confidence


async def generate_gpt_report(
    metrics: AnalysisMetrics,
    result: str,
    confidence: float
) -> str:
    """
    OpenAI GPT-4o-mini를 사용하여 전문적인 분석 리포트를 생성합니다.
    
    Args:
        metrics: 분석 메트릭
        result: 분석 결과 ('real', 'fake', 'uncertain')
        confidence: 신뢰도 (0-1)
        
    Returns:
        str: 생성된 리포트
    """
    # 결과별 레이블
    result_labels = {
        "real": "안전",
        "fake": "위험",
        "uncertain": "주의"
    }
    
    # GPT 프롬프트 구성
    prompt = f"""너는 대한민국 사이버 수사대의 딥페이크 법의학 전문가야.

다음 영상 분석 수치를 바탕으로 전문적인 감정 보고서를 작성해줘:

[분석 수치]
- 눈 깜빡임 자연도: {metrics.eye_blink_rate:.1f}/100
- 음성-입술 동기화: {metrics.lip_sync_score:.1f}/100
- 조명 일관성: {metrics.lighting_consistency:.1f}/100
- 얼굴 인공물 지수: {metrics.facial_artifacts:.1f}/100
- 텍스처 품질: {metrics.texture_quality:.1f}/100
- 동작 부드러움: {metrics.motion_smoothness:.1f}/100

[종합 판정]
- 상태: {result_labels[result]}
- 신뢰도: {confidence*100:.1f}%

# 지침:
1. 3~4문장 이내로 작성
2. 전문 용어를 사용하되 이해하기 쉽게
3. 주요 근거를 명확히 제시
4. "이 영상은 [{result_labels[result]}] 상태이며..."로 시작
5. 존댓말 사용
6. 법의학적 객관성 유지

감정 보고서:"""

    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 대한민국 사이버 수사대의 딥페이크 감정 전문가입니다. 객관적이고 전문적인 분석 보고서를 작성합니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        report = response.choices[0].message.content.strip()
        return report
        
    except Exception as e:
        # OpenAI API 호출 실패 시 기본 리포트 반환
        print(f"OpenAI API Error: {e}")
        return f"이 영상은 [{result_labels[result]}] 상태이며, 분석 신뢰도는 {confidence*100:.1f}%입니다. 주요 분석 지표로는 입술 동기화({metrics.lip_sync_score:.1f}점), 조명 일관성({metrics.lighting_consistency:.1f}점), 얼굴 인공물 지수({metrics.facial_artifacts:.1f}점)가 종합적으로 검토되었습니다."


@app.get("/")
async def root():
    """
    루트 엔드포인트 - API 정보 제공
    """
    return {
        "service": "DeepSentinel AI Server",
        "version": "2.0.0",
        "status": "running",
        "features": ["deepfake_detection", "gpt_report_generation"]
    }


@app.get("/api/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    openai_status = "configured" if os.getenv("OPENAI_API_KEY") else "not_configured"
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "openai": openai_status
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_video(video: UploadFile = File(...)):
    """
    영상 딥페이크 분석 엔드포인트
    
    Args:
        video: 분석할 영상 파일
        
    Returns:
        AnalysisResponse: 분석 결과 및 GPT 리포트
    """
    start_time = time.time()
    
    try:
        # 파일 타입 검증
        if not video.content_type or not video.content_type.startswith("video/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only video files are supported."
            )
        
        # 임시 파일 읽기 (실제 분석 시뮬레이션)
        contents = await video.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        print(f"📹 Analyzing video: {video.filename} ({file_size_mb:.2f} MB)")
        
        # 분석 시뮬레이션 (짧은 대기)
        await asyncio.sleep(0.5)
        
        # 1. 메트릭 생성
        metrics = generate_analysis_metrics()
        
        # 2. 종합 점수 계산
        result, confidence = calculate_overall_score(metrics)
        
        # 3. GPT 리포트 생성
        report = await generate_gpt_report(metrics, result, confidence)
        
        # 분석 소요 시간
        analysis_time = time.time() - start_time
        
        print(f"✅ Analysis complete: {result} (confidence: {confidence:.2%})")
        
        return AnalysisResponse(
            result=result,
            confidence=confidence,
            metrics=metrics,
            report=report,
            analysis_time=analysis_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# asyncio import 추가
import asyncio


if __name__ == "__main__":
    port = int(os.getenv("AI_SERVER_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
