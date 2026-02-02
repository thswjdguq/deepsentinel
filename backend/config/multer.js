const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const { UPLOAD, ERROR_MESSAGES } = require('./constants');

/**
 * Multer 파일 업로드 설정을 초기화합니다.
 * uploads 폴더가 없으면 자동으로 생성합니다.
 */
if (!fs.existsSync(UPLOAD.UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD.UPLOAD_DIR, { recursive: true });
}

/**
 * Multer 스토리지 설정
 * 업로드된 파일을 UUID 기반 파일명으로 저장합니다.
 */
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, UPLOAD.UPLOAD_DIR);
    },
    filename: (req, file, cb) => {
        const uniqueName = `${uuidv4()}${path.extname(file.originalname)}`;
        cb(null, uniqueName);
    },
});

/**
 * 파일 필터 함수
 * 영상 파일만 업로드를 허용합니다.
 * @param {Object} req - Express request 객체
 * @param {Object} file - 업로드된 파일 정보
 * @param {Function} cb - 콜백 함수
 */
const fileFilter = (req, file, cb) => {
    const extname = UPLOAD.ALLOWED_MIME_TYPES.test(
        path.extname(file.originalname).toLowerCase()
    );
    const mimetype = UPLOAD.ALLOWED_MIME_TYPES.test(file.mimetype);

    if (mimetype && extname) {
        return cb(null, true);
    } else {
        cb(new Error(ERROR_MESSAGES.INVALID_FILE_TYPE));
    }
};

/**
 * Multer 업로드 미들웨어 인스턴스
 */
const upload = multer({
    storage: storage,
    limits: {
        fileSize: UPLOAD.MAX_FILE_SIZE,
    },
    fileFilter: fileFilter,
});

module.exports = upload;
