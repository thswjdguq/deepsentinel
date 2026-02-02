# 백엔드 아키텍처 문서

## 📐 아키텍처 개요

DeepSentinel 백엔드는 **Controller-Service-Repository** 패턴을 따르는 계층형 아키텍처로 설계되었습니다.

```
┌─────────────────┐
│   Controller    │  ← HTTP 요청/응답 처리
└────────┬────────┘
         │
┌────────▼────────┐
│    Service      │  ← 비즈니스 로직
└────────┬────────┘
         │
┌────────▼────────┐
│   Repository    │  ← 데이터베이스 접근
└────────┬────────┘
         │
┌────────▼────────┐
│   Prisma ORM    │  ← ORM 레이어
└────────┬────────┘
         │
┌────────▼────────┐
│   MySQL DB      │  ← 데이터베이스
└─────────────────┘
```

---

## 📂 프로젝트 구조

```
backend/
├── config/                  # 설정 파일
│   ├── constants.js        # 상수 정의 (매직 넘버 제거)
│   └── multer.js           # 파일 업로드 설정
│
├── middleware/              # Express 미들웨어
│   └── errorHandler.js     # 전역 에러 핸들러
│
├── repositories/            # 데이터 접근 레이어
│   └── boardRepository.js  # 게시판 Repository
│
├── services/                # 비즈니스 로직 레이어
│   └── boardService.js     # 게시판 Service
│
├── routes/                  # 라우터 (Controller)
│   └── boards.js           # 게시판 API 라우터
│
├── prisma/                  # Prisma ORM
│   ├── schema.prisma       # 데이터베이스 스키마
│   └── seed.js             # 시드 데이터
│
├── uploads/                 # 파일 업로드 저장소
├── .env                     # 환경 변수
├── .env.example             # 환경 변수 템플릿
├── package.json             # 의존성 관리
└── server.js                # Express 서버 진입점
```

---

## 🏛️ 레이어별 책임

### 1. Controller (routes/)
**책임**: HTTP 요청/응답 처리
- 요청 파라미터 추출
- Service 레이어 호출
- HTTP 응답 형식 지정
- 라우팅 정의

**예시**: `routes/boards.js`
```javascript
router.get('/:type', asyncHandler(async (req, res) => {
  const { type } = req.params;
  const { page, limit } = req.query;
  
  const result = await BoardService.getList(type, page, limit);
  
  res.status(HTTP_STATUS.OK).json({
    success: true,
    data: result.items,
    pagination: result.pagination,
  });
}));
```

---

### 2. Service (services/)
**책임**: 비즈니스 로직 구현
- 데이터 검증
- 비즈니스 규칙 적용
- Repository 레이어 호출
- 트랜잭션 관리

**예시**: `services/boardService.js`
```javascript
static async create(type, requestData, file = null) {
  // 비즈니스 로직: 파일 처리, 데이터 검증
  let videoUrl = null;
  if (file) {
    videoUrl = `/uploads/${file.filename}`;
  }
  
  // Repository 호출
  return await BoardRepository.create(type, data);
}
```

---

### 3. Repository (repositories/)
**책임**: 데이터베이스 접근
- CRUD 연산
- Prisma 쿼리 실행
- 데이터 모델 변환
- 데이터베이스 에러 처리

**예시**: `repositories/boardRepository.js`
```javascript
static async findMany(type, skip, take) {
  const model = this.getModelByType(type);
  
  return await model.findMany({
    skip,
    take,
    orderBy: { createdAt: 'desc' },
    include: { user: { select: { id: true, username: true } } }
  });
}
```

---

## 🛡️ 에러 처리 전략

### 1. Custom Error Class
```javascript
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
  }
}
```

### 2. Async Handler Wrapper
모든 비동기 라우트 핸들러를 자동으로 에러 캐치:
```javascript
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};
```

### 3. 전역 에러 핸들러
- Prisma 에러 처리 (P2002, P2025 등)
- Multer 에러 처리 (LIMIT_FILE_SIZE)
- 일관된 에러 응답 형식
- 개발/프로덕션 환경별 스택 트레이스 제어

---

## 📋 상수 관리

모든 매직 넘버와 하드코딩된 값은 `config/constants.js`에서 중앙 관리:

```javascript
module.exports = {
  SERVER: { PORT: 5000, ENV: 'development' },
  UPLOAD: { MAX_FILE_SIZE: 524288000 },
  PAGINATION: { DEFAULT_PAGE: 1, DEFAULT_LIMIT: 20 },
  BOARD_TYPES: { DETECTION_LOGS: 'detection-logs' },
  HTTP_STATUS: { OK: 200, CREATED: 201, NOT_FOUND: 404 },
  ERROR_MESSAGES: { ITEM_NOT_FOUND: 'Item not found' }
};
```

**장점**:
- 유지보수성 향상
- 타입 안정성 강화
- 일관된 값 사용 보장

---

## 📝 JSDoc 표준

모든 함수와 클래스에 JSDoc 주석 작성:

```javascript
/**
 * 게시글 목록을 페이지네이션과 함께 조회합니다.
 * @param {string} type - 게시판 타입
 * @param {number} page - 페이지 번호 (1부터 시작)
 * @param {number} limit - 페이지당 항목 수
 * @returns {Promise<Object>} 게시글 목록과 페이지네이션 정보
 * @throws {AppError} 유효하지 않은 게시판 타입일 경우
 */
static async getList(type, page, limit) {
  // 구현...
}
```

---

## 🔄 데이터 흐름 예시

**게시글 생성 요청 흐름**:

```
1. Client
   ↓ POST /api/boards/community-reports
   
2. Controller (routes/boards.js)
   ↓ req.params, req.body, req.file 추출
   
3. Service (services/boardService.js)
   ↓ 비즈니스 로직: 파일 처리, 데이터 검증
   
4. Repository (repositories/boardRepository.js)
   ↓ Prisma 쿼리 실행
   
5. Prisma ORM
   ↓ SQL 쿼리 생성
   
6. MySQL Database
   ↓ 데이터 저장
   
7. Response
   ← 201 Created + 생성된 게시글 데이터
```

---

## 🔒 타입 안정성

### Prisma 스키마와 코드 동기화
- Prisma 스키마 정의 → `npx prisma generate` → TypeScript 타입 자동 생성
- Repository 레이어에서 Prisma Client 사용 → 타입 안정성 보장
- 상수 파일 활용으로 문자열 오타 방지

### 예시
```javascript
// ❌ 타입 불안정 (매직 스트링)
if (type === 'detection-logs') { ... }

// ✅ 타입 안정
if (type === BOARD_TYPES.DETECTION_LOGS) { ... }
```

---

## 🚀 확장 가능성

현재 아키텍처는 다음과 같은 확장을 쉽게 지원합니다:

1. **새로운 엔티티 추가**
   - Repository 생성 → Service 생성 → Controller 생성

2. **인증/권한 미들웨어**
   - `middleware/auth.js` 추가
   - Controller에서 미들웨어 적용

3. **캐싱 레이어**
   - Service와 Repository 사이에 캐시 레이어 추가

4. **로깅**
   - Winston/Pino 로거를 미들웨어로 추가

---

**작성일**: 2026-01-28  
**버전**: 1.0.0
