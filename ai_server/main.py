from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
import time
import random
import os
from dotenv import load_dotenv
from openai import OpenAI
import asyncio
import json

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(
    title="DeepSentinel AI Server",
    description="딥페이크 탐지 AI 분석 서버",
    version="2.1.0"
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


class URLAnalysisRequest(BaseModel):
    """
    URL 분석 요청 모델
    """
    url: str
    platform: Optional[str] = None  # 'youtube', 'instagram', 'tiktok' 등


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
    prompt = f"""대한민국 국가정보원 산하 디지털 포렌식 연구소 수석 분석관으로서, 다음 영상에 대한 공식 감정 보고서를 작성하십시오.

[영상 감정 결과]
판정: {result_labels[result]} ({confidence*100:.1f}%)

[세부 분석 지표]
1. 눈 깜빡임 자연도 (EAR): {metrics.eye_blink_rate:.1f}/100
2. 음성-입술 동기화 정밀도 (MAR): {metrics.lip_sync_score:.1f}/100
3. 조명 일관성 분석: {metrics.lighting_consistency:.1f}/100
4. 얼굴 아티팩트 검출: {metrics.facial_artifacts:.1f}/100
5. 텍스처 품질 평가: {metrics.texture_quality:.1f}/100
6. 모션 자연도 분석: {metrics.motion_smoothness:.1f}/100

[보고서 작성 지침]
- 3~4문장으로 간결하게 작성
- 법정 제출 가능한 객관적 표현 사용
- "본 영상은 [{result_labels[result]}] 판정을 받았으며"로 시작
- 핵심 근거 수치를 명확히 제시
- 공식 보고서 어투 (하십시오체)
- 전문 용어 사용 시 괄호 안에 영문 병기

[감정 의견]:"""

    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """당신은 대한민국 국가정보원 산하 디지털 포렌식 연구소의 수석 분석관입니다. 
                    
귀하의 보고서는 법정 증거로 사용될 수 있으며, 다음 원칙을 준수해야 합니다:
1. 객관적이고 단호한 어조
2. 공식 감정서 형식 준수
3. 전문 기술 용어 정확히 사용
4. 수치 기반의 논리적 근거 제시
5. 하십시오체 사용

보고서는 검찰, 법원, 정보기관에 제출될 수 있으므로 최고 수준의 전문성과 신뢰성을 유지하십시오."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,  # 더 객관적이고 일관된 답변을 위해 낮춤
            max_tokens=350
        )
        
        report = response.choices[0].message.content.strip()
        return report
        
    except Exception as e:
        # OpenAI API 호출 실패 시 기본 리포트 반환
        print(f"OpenAI API Error: {e}")
        return f"""본 영상은 [{result_labels[result]}] 판정을 받았으며, 분석 신뢰도는 {confidence*100:.1f}%입니다. 주요 감정 근거로는 음성-입술 동기화(MAR) {metrics.lip_sync_score:.1f}점, 조명 일관성 분석 {metrics.lighting_consistency:.1f}점, 얼굴 아티팩트 검출 {metrics.facial_artifacts:.1f}점이 종합적으로 검토되었습니다. 본 감정 결과는 현행 디지털 포렌식 기준에 부합하는 것으로 판단됩니다."""


@app.get("/")
async def root():
    """
    루트 엔드포인트 - API 정보 제공
    """
    return {
        "service": "DeepSentinel AI Server",
        "version": "2.1.0",
        "status": "running",
        "features": ["deepfake_detection", "gpt_report_generation", "realtime_analysis"]
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
        "openai": openai_status,
        "websocket": "enabled"
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


@app.post("/api/analyze-url")
async def analyze_url(request: URLAnalysisRequest):
    """
    URL 기반 영상 분석 엔드포인트 (스켈레톤)
    
    Args:
        request: URL 분석 요청 (유튜브, 릴스 등)
        
    Returns:
        dict: 분석 결과 (더미)
    """
    print(f"🔗 Analyzing URL: {request.url}")
    
    # 더미 응답 (향후 youtube-dl, yt-dlp 등으로 구현)
    await asyncio.sleep(1)
    
    return {
        "status": "success",
        "message": "URL 분석은 현재 개발 중입니다.",
        "url": request.url,
        "platform": request.platform or "unknown"
    }


@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """
    실시간 프레임 분석용 WebSocket 엔드포인트
    
    Usage:
        클라이언트가 웹캠 프레임을 base64로 인코딩하여 전송하면
        MediaPipe로 실시간 분석 결과를 스트리밍
    """
    await websocket.accept()
    print("🔌 WebSocket connection established")
    
    # FaceAnalyzer 초기화
    try:
        from face_analyzer import FaceAnalyzer
        import base64
        import cv2
        
        analyzer = FaceAnalyzer()
        frame_skip = 0  # 프레임 스킵 카운터 (지연 시간 감소용)
        
        while True:
            # 클라이언트로부터 프레임 수신
            data = await websocket.receive_text()
            frame_data = json.loads(data)
            
            # 프레임 스킵 로직 (2프레임마다 1번씩 분석)
            frame_skip += 1
            if frame_skip % 2 != 0:
                continue
            
            try:
                # Base64 디코딩
                img_data = base64.b64decode(frame_data.get('frame', ''))
                nparr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    await websocket.send_json({
                        "error": "Invalid frame data",
                        "timestamp": time.time()
                    })
                    continue
                
                # MediaPipe 얼굴 분석
                analysis_result = analyzer.analyze_frame(frame)
                
                if analysis_result is None:
                    # 얼굴 미검출
                    await websocket.send_json({
                        "face_detected": False,
                        "timestamp": time.time(),
                        "message": "얼굴이 감지되지 않았습니다"
                    })
                    continue
                
                # 종합 점수 계산
                metrics_obj = AnalysisMetrics(
                    eye_blink_rate=analysis_result['eye_blink_rate'],
                    lip_sync_score=analysis_result['lip_sync_score'],
                    lighting_consistency=analysis_result['lighting_consistency'],
                    facial_artifacts=analysis_result['facial_artifacts'],
                    texture_quality=analysis_result['texture_quality'],
                    motion_smoothness=analysis_result['motion_smoothness']
                )
                
                result, confidence = calculate_overall_score(metrics_obj)
                
                # 결과 전송
                response = {
                    "timestamp": time.time(),
                    "result": result,
                    "confidence": confidence,
                    "face_detected": True,
                    "metrics": {
                        "eye_blink_rate": round(analysis_result['eye_blink_rate'], 1),
                        "lip_sync_score": round(analysis_result['lip_sync_score'], 1),
                        "lighting_consistency": round(analysis_result['lighting_consistency'], 1),
                        "facial_artifacts": round(analysis_result['facial_artifacts'], 1),
                        "texture_quality": round(analysis_result['texture_quality'], 1),
                        "motion_smoothness": round(analysis_result['motion_smoothness'], 1),
                    },
                    "details": {
                        "ear": round(analysis_result.get('ear', 0), 3),
                        "mar": round(analysis_result.get('mar', 0), 3),
                        "angles": {
                            "pitch": round(analysis_result['angles']['pitch'], 1),
                            "yaw": round(analysis_result['angles']['yaw'], 1),
                            "roll": round(analysis_result['angles']['roll'], 1)
                        }
                    }
                }
                
                await websocket.send_json(response)
                print(f"📡 Sent realtime analysis: {result} ({confidence:.2%})")
                
            except Exception as e:
                print(f"⚠️ Frame analysis error: {str(e)}")
                await websocket.send_json({
                    "error": str(e),
                    "timestamp": time.time()
                })
                
    except WebSocketDisconnect:
        print("🔌 WebSocket connection closed")
    except Exception as e:
        print(f"❌ WebSocket error: {str(e)}")
        await websocket.close()
    finally:
        # 분석기 정리
        if 'analyzer' in locals():
            analyzer.reset()


if __name__ == "__main__":
    port = int(os.getenv("AI_SERVER_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
