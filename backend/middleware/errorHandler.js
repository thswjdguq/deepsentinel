const { HTTP_STATUS } = require('../config/constants');

/**
 * 커스텀 에러 클래스
 * HTTP 상태 코드를 포함한 에러 객체를 생성합니다.
 */
class AppError extends Error {
    /**
     * @param {string} message - 에러 메시지
     * @param {number} statusCode - HTTP 상태 코드
     */
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
        this.isOperational = true;

        Error.captureStackTrace(this, this.constructor);
    }
}

/**
 * 전역 에러 핸들러 미들웨어
 * 모든 에러를 캐치하고 일관된 응답 형식으로 반환합니다.
 * @param {Error} err - 발생한 에러 객체
 * @param {Object} req - Express request 객체
 * @param {Object} res - Express response 객체
 * @param {Function} next - Express next 함수
 */
const errorHandler = (err, req, res, next) => {
    let { statusCode, message } = err;

    // 기본값 설정
    statusCode = statusCode || HTTP_STATUS.INTERNAL_SERVER_ERROR;
    message = message || 'Internal Server Error';

    // Prisma 에러 처리
    if (err.code === 'P2002') {
        statusCode = HTTP_STATUS.BAD_REQUEST;
        message = 'Duplicate entry. This record already exists.';
    }

    if (err.code === 'P2025') {
        statusCode = HTTP_STATUS.NOT_FOUND;
        message = 'Record not found.';
    }

    // Multer 에러 처리
    if (err.name === 'MulterError') {
        statusCode = HTTP_STATUS.BAD_REQUEST;
        if (err.code === 'LIMIT_FILE_SIZE') {
            message = 'File size is too large. Maximum size is 500MB.';
        }
    }

    // 에러 로깅
    console.error('Error:', {
        statusCode,
        message,
        path: req.path,
        method: req.method,
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
    });

    // 에러 응답
    res.status(statusCode).json({
        success: false,
        error: {
            message,
            statusCode,
            ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
        },
    });
};

/**
 * 404 Not Found 핸들러 미들웨어
 * 정의되지 않은 라우트에 대한 처리
 * @param {Object} req - Express request 객체
 * @param {Object} res - Express response 객체
 */
const notFoundHandler = (req, res) => {
    res.status(HTTP_STATUS.NOT_FOUND).json({
        success: false,
        error: {
            message: 'Route not found',
            statusCode: HTTP_STATUS.NOT_FOUND,
            path: req.path,
        },
    });
};

/**
 * 비동기 함수 에러 래퍼
 * async/await 함수에서 발생하는 에러를 자동으로 캐치합니다.
 * @param {Function} fn - 비동기 함수
 * @returns {Function} 에러 처리가 추가된 함수
 */
const asyncHandler = (fn) => (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
};

module.exports = {
    AppError,
    errorHandler,
    notFoundHandler,
    asyncHandler,
};
