/**
 * Application Constants
 * 모든 매직 넘버와 설정값을 중앙에서 관리합니다.
 */

module.exports = {
    // Server Configuration
    SERVER: {
        PORT: process.env.PORT || 5000,
        ENV: process.env.NODE_ENV || 'development',
    },

    // Database Configuration
    DATABASE: {
        URL: process.env.DATABASE_URL,
    },

    // File Upload Configuration
    UPLOAD: {
        MAX_FILE_SIZE: parseInt(process.env.MAX_FILE_SIZE) || 524288000, // 500MB
        UPLOAD_DIR: process.env.UPLOAD_PATH || './uploads',
        ALLOWED_VIDEO_EXTENSIONS: ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'],
        ALLOWED_MIME_TYPES: /mp4|avi|mov|mkv|webm|flv/,
    },

    // CORS Configuration
    CORS: {
        ORIGIN: process.env.FRONTEND_URL || 'http://localhost:3000',
        CREDENTIALS: true,
    },

    // JWT Configuration
    JWT: {
        SECRET: process.env.JWT_SECRET || 'deepsentinel-dev-secret-2026',
        EXPIRES_IN: '7d',
    },

    // Pagination Configuration
    PAGINATION: {
        DEFAULT_PAGE: 1,
        DEFAULT_LIMIT: 20,
        MAX_LIMIT: 100,
    },

    // Board Types
    BOARD_TYPES: {
        DETECTION_LOGS: 'detection-logs',
        COMMUNITY_REPORTS: 'community-reports',
    },

    // Detection Results
    DETECTION_RESULTS: {
        REAL: 'real',
        FAKE: 'fake',
        UNCERTAIN: 'uncertain',
        PENDING: 'pending',
    },

    // Report Status
    REPORT_STATUS: {
        PENDING: 'pending',
        VERIFIED: 'verified',
        REJECTED: 'rejected',
    },

    // HTTP Status Codes
    HTTP_STATUS: {
        OK: 200,
        CREATED: 201,
        BAD_REQUEST: 400,
        UNAUTHORIZED: 401,
        FORBIDDEN: 403,
        NOT_FOUND: 404,
        INTERNAL_SERVER_ERROR: 500,
    },

    // Error Messages
    ERROR_MESSAGES: {
        INVALID_BOARD_TYPE: 'Invalid board type',
        ITEM_NOT_FOUND: 'Item not found',
        DATABASE_ERROR: 'Database operation failed',
        FILE_UPLOAD_ERROR: 'File upload failed',
        INVALID_FILE_TYPE: 'Only video files are allowed',
        UNAUTHORIZED: 'Unauthorized access',
    },
};
