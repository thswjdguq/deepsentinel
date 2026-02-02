require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { CORS, SERVER } = require('./config/constants');
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');

const app = express();

/**
 * ===== Middleware Configuration =====
 */

/**
 * CORS 설정
 * 프론트엔드 애플리케이션과의 통신을 허용합니다.
 */
app.use(cors({
  origin: CORS.ORIGIN,
  credentials: CORS.CREDENTIALS,
}));

/**
 * Body Parser
 * JSON 및 URL-encoded 요청 본문을 파싱합니다.
 */
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

/**
 * 정적 파일 제공
 * 업로드된 영상 파일을 제공합니다.
 */
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

/**
 * ===== Routes Configuration =====
 */
const boardsRouter = require('./routes/boards');

app.use('/api/boards', boardsRouter);

/**
 * 헬스 체크 엔드포인트
 * 서버 상태를 확인합니다.
 * @route GET /api/health
 * @returns {Object} 200 - 서버 상태 정보
 */
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    message: 'DeepSentinel Backend Server is running',
    timestamp: new Date().toISOString(),
    environment: SERVER.ENV,
  });
});

/**
 * 루트 엔드포인트
 * API 정보를 제공합니다.
 * @route GET /
 * @returns {Object} 200 - API 정보
 */
app.get('/', (req, res) => {
  res.json({
    name: 'DeepSentinel API',
    version: '1.0.0',
    description: 'Deepfake Detection Platform Backend',
    endpoints: {
      health: '/api/health',
      boards: {
        detectionLogs: '/api/boards/detection-logs',
        communityReports: '/api/boards/community-reports',
      },
    },
  });
});

/**
 * ===== Error Handling =====
 */

// 404 핸들러 (정의되지 않은 라우트)
app.use(notFoundHandler);

// 전역 에러 핸들러
app.use(errorHandler);

/**
 * ===== Server Start =====
 */
app.listen(SERVER.PORT, () => {
  console.log('🚀 DeepSentinel Backend Server Started');
  console.log(`📍 Port: ${SERVER.PORT}`);
  console.log(`🌍 Environment: ${SERVER.ENV}`);
  console.log(`🔗 API Base URL: http://localhost:${SERVER.PORT}`);
  console.log(`💾 Database: ${process.env.DATABASE_URL ? 'Configured' : 'Not configured'}`);
  console.log('✨ Ready to accept requests');
});

module.exports = app;
