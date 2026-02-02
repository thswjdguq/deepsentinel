const BoardRepository = require('../repositories/boardRepository');
const { AppError } = require('../middleware/errorHandler');
const {
    ERROR_MESSAGES,
    HTTP_STATUS,
    PAGINATION,
    BOARD_TYPES,
    DETECTION_RESULTS,
    REPORT_STATUS
} = require('../config/constants');
const fs = require('fs');
const path = require('path');

/**
 * Board Service
 * 비즈니스 로직을 담당하는 서비스 레이어
 */
class BoardService {
    /**
     * 게시글 목록을 페이지네이션과 함께 조회합니다.
     * @param {string} type - 게시판 타입
     * @param {number} page - 페이지 번호 (1부터 시작)
     * @param {number} limit - 페이지당 항목 수
     * @returns {Promise<Object>} 게시글 목록과 페이지네이션 정보
     */
    static async getList(type, page = PAGINATION.DEFAULT_PAGE, limit = PAGINATION.DEFAULT_LIMIT) {
        // 페이지네이션 파라미터 검증 및 변환
        const pageNum = Math.max(1, parseInt(page));
        const limitNum = Math.min(PAGINATION.MAX_LIMIT, Math.max(1, parseInt(limit)));

        const skip = (pageNum - 1) * limitNum;
        const take = limitNum;

        // 병렬로 데이터와 전체 개수 조회
        const [items, total] = await Promise.all([
            BoardRepository.findMany(type, skip, take),
            BoardRepository.count(type),
        ]);

        return {
            items,
            pagination: {
                page: pageNum,
                limit: limitNum,
                total,
                totalPages: Math.ceil(total / limitNum),
            },
        };
    }

    /**
     * ID로 게시글 상세 정보를 조회합니다.
     * @param {string} type - 게시판 타입
     * @param {number} id - 게시글 ID
     * @returns {Promise<Object>} 게시글 상세 정보
     * @throws {AppError} 게시글을 찾을 수 없을 경우
     */
    static async getById(type, id) {
        const item = await BoardRepository.findById(type, id);

        if (!item) {
            throw new AppError(ERROR_MESSAGES.ITEM_NOT_FOUND, HTTP_STATUS.NOT_FOUND);
        }

        return item;
    }

    /**
     * 새로운 게시글을 생성합니다.
     * detection-logs의 경우 AI 서버에 자동으로 분석 요청을 보냅니다.
     * @param {string} type - 게시판 타입
     * @param {Object} requestData - 요청 데이터
     * @param {Object|null} file - 업로드된 파일 정보
     * @returns {Promise<Object>} 생성된 게시글 정보
     */
    static async create(type, requestData, file = null) {
        let data;

        // 비디오 URL 처리
        let videoUrl = null;
        if (file) {
            videoUrl = `/uploads/${file.filename}`;
        } else if (requestData.videoUrl) {
            videoUrl = requestData.videoUrl;
        }

        // 게시판 타입별 데이터 구성
        if (type === BOARD_TYPES.DETECTION_LOGS) {
            data = {
                userId: parseInt(requestData.userId) || 1, // TODO: JWT 인증으로 교체
                videoUrl: videoUrl || '',
                result: requestData.result || DETECTION_RESULTS.PENDING,
                confidence: parseFloat(requestData.confidence) || 0.0,
            };
        } else if (type === BOARD_TYPES.COMMUNITY_REPORTS) {
            data = {
                userId: parseInt(requestData.userId) || 1, // TODO: JWT 인증으로 교체
                title: requestData.title,
                content: requestData.content,
                videoUrl: videoUrl,
                status: REPORT_STATUS.PENDING,
            };
        }

        try {
            // DB에 먼저 저장
            const createdItem = await BoardRepository.create(type, data);

            // detection-logs이고 파일이 있으면 AI 분석 요청
            if (type === BOARD_TYPES.DETECTION_LOGS && file) {
                // 비동기로 AI 분석 트리거 (응답을 기다리지 않음)
                this.requestAIAnalysis(createdItem.id, file.path)
                    .catch(error => {
                        console.error(`AI analysis failed for post ${createdItem.id}:`, error.message);
                        // AI 분석 실패해도 업로드는 성공으로 처리
                    });
            }

            return createdItem;
        } catch (error) {
            // 파일 업로드가 실패했을 경우 업로드된 파일 삭제
            if (file && fs.existsSync(file.path)) {
                fs.unlinkSync(file.path);
            }
            throw error;
        }
    }

    /**
     * AI 서버에 영상 분석을 요청하고 결과를 DB에 업데이트합니다.
     * @param {number} postId - 게시글 ID
     * @param {string} videoPath - 영상 파일 경로
     * @returns {Promise<void>}
     */
    static async requestAIAnalysis(postId, videoPath) {
        const FormData = require('form-data');
        const axios = require('axios');
        const AI_SERVER_URL = process.env.AI_SERVER_URL || 'http://localhost:8000';

        try {
            console.log(`🤖 Requesting AI analysis for post ${postId}...`);

            // FormData 생성
            const formData = new FormData();
            formData.append('video', fs.createReadStream(videoPath));

            // AI 서버에 분석 요청
            const response = await axios.post(
                `${AI_SERVER_URL}/api/analyze`,
                formData,
                {
                    headers: formData.getHeaders(),
                    timeout: 60000, // 60초 타임아웃
                }
            );

            const analysisResult = response.data;

            console.log(`✅ AI analysis complete for post ${postId}: ${analysisResult.result} (${(analysisResult.confidence * 100).toFixed(1)}%)`);

            // DB 업데이트 데이터 구성
            const updateData = {
                result: analysisResult.result,
                confidence: analysisResult.confidence,
                metrics: analysisResult.metrics,  // 6가지 메트릭 JSON 저장
                report: analysisResult.report,    // GPT 리포트 텍스트 저장
            };

            // DB 업데이트
            await BoardRepository.update(BOARD_TYPES.DETECTION_LOGS, postId, updateData);

            console.log(`💾 Database updated for post ${postId}`);

        } catch (error) {
            // AI 서버 연결 실패 또는 분석 실패
            console.error(`❌ AI analysis failed for post ${postId}:`, error.message);

            // 에러 상태로 DB 업데이트 (선택사항)
            try {
                await BoardRepository.update(BOARD_TYPES.DETECTION_LOGS, postId, {
                    result: DETECTION_RESULTS.UNCERTAIN,
                    confidence: 0.0,
                });
            } catch (dbError) {
                console.error(`Failed to update error state for post ${postId}:`, dbError.message);
            }

            throw error;
        }
    }

    /**
     * 게시글을 수정합니다.
     * @param {string} type - 게시판 타입
     * @param {number} id - 게시글 ID
     * @param {Object} requestData - 수정할 데이터
     * @returns {Promise<Object>} 수정된 게시글 정보
     * @throws {AppError} 게시글을 찾을 수 없을 경우
     */
    static async update(type, id, requestData) {
        // 기존 게시글 존재 여부 확인
        const existingItem = await BoardRepository.findById(type, id);
        if (!existingItem) {
            throw new AppError(ERROR_MESSAGES.ITEM_NOT_FOUND, HTTP_STATUS.NOT_FOUND);
        }

        let updateData;

        // 게시판 타입별 수정 데이터 구성
        if (type === BOARD_TYPES.DETECTION_LOGS) {
            updateData = {
                result: requestData.result || existingItem.result,
                confidence: requestData.confidence !== undefined
                    ? parseFloat(requestData.confidence)
                    : existingItem.confidence,
            };
        } else if (type === BOARD_TYPES.COMMUNITY_REPORTS) {
            updateData = {
                title: requestData.title || existingItem.title,
                content: requestData.content || existingItem.content,
                status: requestData.status || existingItem.status,
            };
        }

        return await BoardRepository.update(type, id, updateData);
    }

    /**
     * 게시글을 삭제합니다.
     * 연결된 비디오 파일도 함께 삭제합니다.
     * @param {string} type - 게시판 타입
     * @param {number} id - 게시글 ID
     * @returns {Promise<void>}
     * @throws {AppError} 게시글을 찾을 수 없을 경우
     */
    static async delete(type, id) {
        // 기존 게시글 존재 여부 확인
        const existingItem = await BoardRepository.findById(type, id);
        if (!existingItem) {
            throw new AppError(ERROR_MESSAGES.ITEM_NOT_FOUND, HTTP_STATUS.NOT_FOUND);
        }

        // 비디오 파일이 서버에 업로드된 경우 파일도 삭제
        if (existingItem.videoUrl && existingItem.videoUrl.startsWith('/uploads/')) {
            const filePath = path.join(__dirname, '..', existingItem.videoUrl);
            if (fs.existsSync(filePath)) {
                fs.unlinkSync(filePath);
            }
        }

        await BoardRepository.delete(type, id);
    }
}

module.exports = BoardService;
