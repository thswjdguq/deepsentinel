const express = require('express');
const router = express.Router();
const BoardService = require('../services/boardService');
const upload = require('../config/multer');
const { asyncHandler } = require('../middleware/errorHandler');
const { HTTP_STATUS } = require('../config/constants');

/**
 * Board Controller
 * HTTP 요청/응답을 처리하는 컨트롤러 레이어
 */

/**
 * GET /api/boards/:type
 * 게시글 목록을 조회합니다.
 * @route GET /api/boards/:type
 * @param {string} type.path.required - 게시판 타입 ('detection-logs' | 'community-reports')
 * @param {number} page.query - 페이지 번호 (기본값: 1)
 * @param {number} limit.query - 페이지당 항목 수 (기본값: 20)
 * @returns {Object} 200 - 게시글 목록과 페이지네이션 정보
 * @returns {Object} 400 - 잘못된 요청
 */
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

/**
 * GET /api/boards/:type/:id
 * 게시글 상세 정보를 조회합니다.
 * @route GET /api/boards/:type/:id
 * @param {string} type.path.required - 게시판 타입
 * @param {number} id.path.required - 게시글 ID
 * @returns {Object} 200 - 게시글 상세 정보
 * @returns {Object} 404 - 게시글을 찾을 수 없음
 */
router.get('/:type/:id', asyncHandler(async (req, res) => {
    const { type, id } = req.params;

    const item = await BoardService.getById(type, id);

    res.status(HTTP_STATUS.OK).json({
        success: true,
        data: item,
    });
}));

/**
 * POST /api/boards/:type
 * 새로운 게시글을 작성합니다.
 * 파일 업로드를 지원합니다 (선택사항).
 * @route POST /api/boards/:type
 * @param {string} type.path.required - 게시판 타입
 * @param {Object} body.body.required - 게시글 데이터
 * @param {File} video.formData - 업로드할 비디오 파일 (선택)
 * @returns {Object} 201 - 생성된 게시글 정보
 * @returns {Object} 400 - 잘못된 요청
 */
router.post('/:type', upload.single('video'), asyncHandler(async (req, res) => {
    const { type } = req.params;

    const newItem = await BoardService.create(type, req.body, req.file);

    res.status(HTTP_STATUS.CREATED).json({
        success: true,
        data: newItem,
        message: 'Post created successfully',
    });
}));

/**
 * PUT /api/boards/:type/:id
 * 게시글을 수정합니다.
 * @route PUT /api/boards/:type/:id
 * @param {string} type.path.required - 게시판 타입
 * @param {number} id.path.required - 게시글 ID
 * @param {Object} body.body.required - 수정할 데이터
 * @returns {Object} 200 - 수정된 게시글 정보
 * @returns {Object} 404 - 게시글을 찾을 수 없음
 */
router.put('/:type/:id', asyncHandler(async (req, res) => {
    const { type, id } = req.params;

    const updatedItem = await BoardService.update(type, id, req.body);

    res.status(HTTP_STATUS.OK).json({
        success: true,
        data: updatedItem,
        message: 'Post updated successfully',
    });
}));

/**
 * DELETE /api/boards/:type/:id
 * 게시글을 삭제합니다.
 * 연결된 비디오 파일도 함께 삭제됩니다.
 * @route DELETE /api/boards/:type/:id
 * @param {string} type.path.required - 게시판 타입
 * @param {number} id.path.required - 게시글 ID
 * @returns {Object} 200 - 삭제 성공 메시지
 * @returns {Object} 404 - 게시글을 찾을 수 없음
 */
router.delete('/:type/:id', asyncHandler(async (req, res) => {
    const { type, id } = req.params;

    await BoardService.delete(type, id);

    res.status(HTTP_STATUS.OK).json({
        success: true,
        message: 'Post deleted successfully',
    });
}));

module.exports = router;
