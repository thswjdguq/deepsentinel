"""
MediaPipe 기반 실시간 얼굴 분석 엔진
Eye blink, lip opening, facial angle 계산
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Optional


class FaceAnalyzer:
    """
    MediaPipe Face Mesh를 사용한 실시간 얼굴 분석기
    """
    
    def __init__(self):
        """
        MediaPipe Face Mesh 초기화
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 눈 깜빡임 감지용 랜드마크 인덱스
        self.LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        
        # 입술 분석용 랜드마크 인덱스
        self.UPPER_LIP_INDICES = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
        self.LOWER_LIP_INDICES = [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]
        
        # 얼굴 각도 계산용 주요 포인트
        self.NOSE_TIP = 1
        self.CHIN = 152
        self.LEFT_EYE_CORNER = 33
        self.RIGHT_EYE_CORNER = 263
        
        # 이전 프레임 데이터 (시계열 분석용)
        self.prev_ear = None
        self.blink_count = 0
        self.frame_count = 0
    
    def calculate_ear(self, eye_landmarks: np.ndarray) -> float:
        """
        Eye Aspect Ratio (EAR) 계산
        눈 깜빡임 감지를 위한 지표
        
        Args:
            eye_landmarks: 눈 랜드마크 좌표 배열
            
        Returns:
            float: EAR 값 (0에 가까울수록 눈을 감은 상태)
        """
        # 수직 거리 계산
        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # 수평 거리 계산
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # EAR 공식
        ear = (A + B) / (2.0 * C)
        return ear
    
    def calculate_mar(self, upper_lip: np.ndarray, lower_lip: np.ndarray) -> float:
        """
        Mouth Aspect Ratio (MAR) 계산
        입술 열림 정도를 측정
        
        Args:
            upper_lip: 윗입술 랜드마크
            lower_lip: 아랫입술 랜드마크
            
        Returns:
            float: MAR 값 (클수록 입이 많이 벌어진 상태)
        """
        # 입술 수직 거리들
        A = np.linalg.norm(upper_lip[2] - lower_lip[2])
        B = np.linalg.norm(upper_lip[5] - lower_lip[5])
        C = np.linalg.norm(upper_lip[8] - lower_lip[8])
        
        # 입 가로 길이
        D = np.linalg.norm(upper_lip[0] - upper_lip[-1])
        
        # MAR 공식
        mar = (A + B + C) / (3.0 * D)
        return mar
    
    def get_face_angle(self, landmarks: np.ndarray, img_shape: tuple) -> Dict[str, float]:
        """
        얼굴 각도 계산 (Pitch, Yaw, Roll)
        
        Args:
            landmarks: 전체 얼굴 랜드마크
            img_shape: 이미지 크기 (height, width, channels)
            
        Returns:
            dict: pitch, yaw, roll 각도
        """
        h, w = img_shape[:2]
        
        # 3D 모델 포인트 (정면 얼굴 기준)
        model_points = np.array([
            (0.0, 0.0, 0.0),             # 코끝
            (0.0, -330.0, -65.0),        # 턱
            (-225.0, 170.0, -135.0),     # 왼쪽 눈 코너
            (225.0, 170.0, -135.0),      # 오른쪽 눈 코너
        ])
        
        # 2D 이미지 포인트
        image_points = np.array([
            landmarks[self.NOSE_TIP],
            landmarks[self.CHIN],
            landmarks[self.LEFT_EYE_CORNER],
            landmarks[self.RIGHT_EYE_CORNER]
        ], dtype="double")
        
        # 카메라 매트릭스
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
        
        dist_coeffs = np.zeros((4, 1))
        
        # PnP 알고리즘으로 회전 벡터 계산
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        # 회전 벡터를 회전 행렬로 변환
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        
        # 오일러 각도 계산
        sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
        pitch = np.arctan2(-rotation_matrix[2, 0], sy)
        yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        roll = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        
        # 라디안을 각도로 변환
        return {
            'pitch': np.degrees(pitch),
            'yaw': np.degrees(yaw),
            'roll': np.degrees(roll)
        }
    
    def analyze_frame(self, frame: np.ndarray) -> Optional[Dict]:
        """
        단일 프레임 분석
        
        Args:
            frame: BGR 이미지 (OpenCV 형식)
            
        Returns:
            dict: 분석 결과 메트릭 또는 None (얼굴 미검출 시)
        """
        # BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None
        
        face_landmarks = results.multi_face_landmarks[0]
        h, w = frame.shape[:2]
        
        # 랜드마크를 픽셀 좌표로 변환
        landmarks = np.array([
            [lm.x * w, lm.y * h] for lm in face_landmarks.landmark
        ])
        
        # 왼쪽/오른쪽 눈 EAR 계산
        left_eye = landmarks[self.LEFT_EYE_INDICES]
        right_eye = landmarks[self.RIGHT_EYE_INDICES]
        
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # 눈 깜빡임 카운트 (EAR < 0.2일 때 감은 것으로 판단)
        if avg_ear < 0.2:
            if self.prev_ear is None or self.prev_ear >= 0.2:
                self.blink_count += 1
        
        self.prev_ear = avg_ear
        self.frame_count += 1
        
        # 깜빡임 빈도 (분당)
        blink_rate = (self.blink_count / max(self.frame_count, 1)) * 60 * 30  # 30fps 가정
        
        # 입술 분석
        upper_lip = landmarks[self.UPPER_LIP_INDICES]
        lower_lip = landmarks[self.LOWER_LIP_INDICES]
        mar = self.calculate_mar(upper_lip, lower_lip)
        
        # 얼굴 각도
        angles = self.get_face_angle(landmarks, frame.shape)
        
        # 조명 일관성 (프레임 밝기 분산으로 추정)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness_std = np.std(gray)
        lighting_score = min(100, max(0, 100 - brightness_std / 2))
        
        # 텍스처 품질 (Laplacian 분산으로 측정)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        texture_score = min(100, laplacian_var / 10)
        
        return {
            'eye_blink_rate': min(100, blink_rate),
            'lip_sync_score': min(100, (1 - mar) * 100),  # MAR이 낮을수록 자연스러움
            'lighting_consistency': lighting_score,
            'facial_artifacts': max(0, 100 - abs(angles['yaw']) - abs(angles['pitch'])),
            'texture_quality': texture_score,
            'motion_smoothness': min(100, 95 - abs(angles['roll'])),
            'face_detected': True,
            'angles': angles,
            'ear': avg_ear,
            'mar': mar
        }
    
    def reset(self):
        """
        분석기 상태 초기화
        """
        self.prev_ear = None
        self.blink_count = 0
        self.frame_count = 0
    
    def __del__(self):
        """
        리소스 정리
        """
        self.face_mesh.close()
