# 🛡️ DeepSentinel

**실시간 및 파일 기반 딥페이크 탐지 플랫폼**

DeepSentinel은 AI 기반 딥페이크 영상 탐지 솔루션입니다. 사용자는 의심스러운 영상을 업로드하고 실시간으로 분석 결과를 확인할 수 있으며, 커뮤니티 제보 기능을 통해 공익적인 딥페이크 정보를 공유할 수 있습니다.

## 🎯 주요 기능

- **영상 분석**: 업로드된 영상의 딥페이크 여부를 AI로 분석
- **분석 기록**: 사용자별 영상 분석 이력 관리
- **커뮤니티 제보**: 공익적 딥페이크 정보 공유 게시판
- **실시간 처리**: FastAPI 기반 고성능 AI 추론 서버

## 🏗️ 기술 스택

### Frontend
- **Next.js** (App Router) - React 프레임워크
- **Tailwind CSS** - 유틸리티 기반 CSS 프레임워크
- **Lucide React** - 아이콘 라이브러리
- **Axios** - HTTP 클라이언트

### Backend
- **Node.js** + **Express** - 백엔드 웹 프레임워크
- **Prisma ORM** - 타입세이프 데이터베이스 ORM
- **MySQL** - 관계형 데이터베이스
- **Multer** - 파일 업로드 미들웨어
- **JWT** - 사용자 인증 (예정)

### AI Server
- **FastAPI** - Python 비동기 웹 프레임워크
- **Uvicorn** - ASGI 서버
- **OpenCV** - 영상 처리
- **TensorFlow/PyTorch** - 딥러닝 모델 (Phase 2 예정)

## 📁 프로젝트 구조

```
deepsentinel/
├── backend/              # Express API 서버
│   ├── prisma/          # 데이터베이스 스키마
│   ├── routes/          # API 라우터
│   └── uploads/         # 업로드 파일 저장소
│
├── frontend/            # Next.js 프론트엔드
│   ├── app/            # App Router 페이지
│   └── components/     # 재사용 컴포넌트
│
└── ai_server/          # FastAPI AI 서버
    └── main.py         # AI 분석 엔드포인트
```

## 🚀 빠른 시작

### 사전 요구사항

- Node.js 18.x 이상
- Python 3.8 이상
- MySQL 8.0 이상

### 1. 백엔드 서버 실행

```bash
cd backend
npm install

# Prisma 클라이언트 생성
npx prisma generate

# 데이터베이스 마이그레이션
npx prisma migrate dev --name init

# 개발 서버 실행
npm run dev
```

백엔드 서버가 `http://localhost:5000`에서 실행됩니다.

### 2. AI 서버 실행

```bash
cd ai_server

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
```

AI 서버가 `http://localhost:8000`에서 실행됩니다.
- API 문서: `http://localhost:8000/docs`

### 3. 프론트엔드 실행 (예정)

```bash
cd frontend
npm install
npm run dev
```

프론트엔드가 `http://localhost:3000`에서 실행됩니다.

## 📡 API 엔드포인트

### 백엔드 API (Port 5000)

#### 게시판 API
- `GET /api/boards/:type` - 게시글 목록 조회
- `GET /api/boards/:type/:id` - 게시글 상세 조회
- `POST /api/boards/:type` - 게시글 작성 (파일 업로드 포함)
- `PUT /api/boards/:type/:id` - 게시글 수정
- `DELETE /api/boards/:type/:id` - 게시글 삭제

**게시판 타입**:
- `detection-logs` - 내 분석 기록
- `community-reports` - 공익 제보

### AI 서버 API (Port 8000)

- `GET /health` - 헬스 체크
- `POST /api/analyze` - 영상 딥페이크 분석
- `GET /api/models` - 사용 가능한 모델 목록

## 🗄️ 데이터베이스 스키마

### Users (사용자)
```sql
- id (PK)
- username (unique)
- email (unique)
- password_hash
- created_at
```

### DetectionLogs (분석 기록)
```sql
- id (PK)
- user_id (FK -> Users)
- video_url
- result (real/fake/uncertain)
- confidence (0.0 ~ 1.0)
- created_at
```

### CommunityReports (공익 제보)
```sql
- id (PK)
- user_id (FK -> Users)
- title
- content
- video_url
- status (pending/verified/rejected)
- created_at
```

## 🔐 환경 변수

백엔드 `.env` 파일:

```env
PORT=5000
NODE_ENV=development
DATABASE_URL="mysql://root:@localhost:3306/deepsentinel"
JWT_SECRET=your-secret-key
MAX_FILE_SIZE=524288000
UPLOAD_PATH=./uploads
FRONTEND_URL=http://localhost:3000
```

## 📝 개발 로드맵

- [x] **Phase 1**: 아키텍처 및 게시판 구축
  - [x] 프로젝트 구조 설정
  - [x] 데이터베이스 스키마 설계
  - [x] 백엔드 CRUD API
  - [x] AI 서버 스켈레톤
  - [ ] 프론트엔드 UI

- [ ] **Phase 2**: 딥페이크 탐지 AI 모델 통합
  - [ ] 딥페이크 탐지 모델 학습/통합
  - [ ] 실시간 분석 파이프라인
  - [ ] 결과 시각화

- [ ] **Phase 3**: 사용자 인증 및 고급 기능
  - [ ] JWT 기반 인증 시스템
  - [ ] 사용자 대시보드
  - [ ] 분석 결과 통계

- [ ] **Phase 4**: 배포 및 최적화
  - [ ] 프로덕션 배포
  - [ ] 성능 최적화
  - [ ] 모니터링 및 로깅

## 🤝 기여

이 프로젝트는 현재 개발 중입니다. 기여를 원하시면 이슈를 생성하거나 Pull Request를 제출해주세요.

## 📄 라이선스

MIT License

---

**DeepSentinel** - Protecting truth in the age of AI
