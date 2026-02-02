# DeepSentinel 실행 가이드

## 🚨 중요: MySQL 데이터베이스 설정 필수

DeepSentinel 백엔드를 실행하기 전에 **MySQL 서버가 실행 중이어야 합니다**.

### MySQL 설정 방법

1. **MySQL 서버 실행 확인**
   ```bash
   # MySQL 서비스가 실행 중인지 확인 (Windows)
   net start MySQL80  # MySQL 8.0 기준
   
   # 또는 서비스 관리자에서 확인
   services.msc
   ```

2. **데이터베이스 생성**
   ```bash
   # MySQL 콘솔 접속
   mysql -u root -p
   
   # 데이터베이스 생성
   CREATE DATABASE deepsentinel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   # 확인
   SHOW DATABASES;
   
   # 종료
   exit;
   ```

3. **Prisma 마이그레이션 실행**
   ```bash
   cd backend
   npx prisma migrate dev --name init
   ```

4. **더미 데이터 생성 (선택사항)**
   ```bash
   npm run prisma:seed
   ```

---

## 🚀 서버 실행 순서

### 1️⃣ 백엔드 서버 (필수)

```bash
cd backend

# 패키지 설치 (처음 한 번만)
npm install

# Prisma 클라이언트 생성 (처음 한 번만)
npx prisma generate

# 개발 서버 실행
npm run dev
```

**실행 확인**: http://localhost:5000
- 헬스 체크: http://localhost:5000/api/health

---

### 2️⃣ AI 서버 (선택사항)

```bash
cd ai_server

# 가상환경 생성 (처음 한 번만, 권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 패키지 설치 (처음 한 번만)
pip install -r requirements.txt

# 서버 실행
python main.py
```

**실행 확인**: http://localhost:8000
- 헬스 체크: http://localhost:8000/health
- API 문서: http://localhost:8000/docs

---

### 3️⃣ 프론트엔드 (미구현 - Phase 1-2에서 진행 예정)

```bash
cd frontend
npm install
npm run dev
```

**실행 확인**: http://localhost:3000

---

## 🔧 문제 해결

### MySQL 연결 실패 시

**증상**: `Can't reach database server at localhost:3306`

**해결 방법**:
1. MySQL 서버가 실행 중인지 확인
   ```bash
   net start MySQL80
   ```

2. .env 파일의 DATABASE_URL 확인
   ```env
   DATABASE_URL="mysql://root:@localhost:3306/deepsentinel"
   ```

3. MySQL 포트 및 비밀번호 확인
   - 기본 포트: 3306
   - 기본 사용자: root
   - 비밀번호가 있다면 DATABASE_URL을 수정: `mysql://root:YOUR_PASSWORD@localhost:3306/deepsentinel`

---

## 📡 API 테스트

### Postman 또는 curl로 테스트

```bash
# 헬스 체크
curl http://localhost:5000/api/health

# 게시글 목록 조회 (detection-logs)
curl http://localhost:5000/api/boards/detection-logs

# 게시글 목록 조회 (community-reports)
curl http://localhost:5000/api/boards/community-reports

# 게시글 작성 (community-reports)
curl -X POST http://localhost:5000/api/boards/community-reports \
  -H "Content-Type: application/json" \
  -d "{\"userId\":1,\"title\":\"테스트 제목\",\"content\":\"테스트 내용\"}"
```

---

## 🗄️ Prisma Studio (데이터베이스 GUI)

데이터베이스를 GUI로 관리하고 싶다면:

```bash
cd backend
npx prisma studio
```

브라우저에서 http://localhost:5555 접속

---

## 📝 다음 단계

- [ ] MySQL 서버 실행 및 데이터베이스 생성
- [ ] Prisma 마이그레이션 실행
- [ ] 백엔드 서버 실행 및 API 테스트
- [ ] (선택) AI 서버 실행 및 테스트
- [ ] Phase 1-2: 프론트엔드 구현 시작
