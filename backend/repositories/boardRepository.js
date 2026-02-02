const { PrismaClient } = require('@prisma/client');
const { AppError } = require('../middleware/errorHandler');
const { BOARD_TYPES, ERROR_MESSAGES, HTTP_STATUS } = require('../config/constants');

const prisma = new PrismaClient();

/**
 * Board Repository
 * 데이터베이스와의 모든 상호작용을 담당하는 레포지토리 레이어
 */
class BoardRepository {
    /**
     * 게시판 타입에 따라 적절한 Prisma 모델을 반환합니다.
     * @param {string} type - 게시판 타입 ('detection-logs' | 'community-reports')
     * @returns {Object} Prisma 모델 객체
     * @throws {AppError} 유효하지 않은 게시판 타입일 경우
     */
    static getModelByType(type) {
        switch (type) {
            case BOARD_TYPES.DETECTION_LOGS:
                return prisma.detectionLog;
            case BOARD_TYPES.COMMUNITY_REPORTS:
                return prisma.communityReport;
            default:
                throw new AppError(ERROR_MESSAGES.INVALID_BOARD_TYPE, HTTP_STATUS.BAD_REQUEST);
        }
    }

    /**
     * 게시글 목록을 조회합니다.
     * @param {string} type - 게시판 타입
     * @param {number} skip - 건너뛸 항목 수
     * @param {number} take - 가져올 항목 수
     * @returns {Promise<Array>} 게시글 배열
     */
    static async findMany(type, skip, take) {
        const model = this.getModelByType(type);

        return await model.findMany({
            skip,
            take,
            orderBy: { createdAt: 'desc' },
            include: {
                user: {
                    select: {
                        id: true,
                        username: true,
                    },
                },
            },
        });
    }

    /**
     * 게시글 총 개수를 조회합니다.
     * @param {string} type - 게시판 타입
     * @returns {Promise<number>} 전체 게시글 수
     */
    static async count(type) {
        const model = this.getModelByType(type);
        return await model.count();
    }

    /**
     * ID로 게시글을 조회합니다.
     * @param {string} type - 게시판 타입
     * @param {number} id - 게시글 ID
     * @returns {Promise<Object|null>} 게시글 객체 또는 null
     */
    static async findById(type, id) {
        const model = this.getModelByType(type);

        return await model.findUnique({
            where: { id: parseInt(id) },
            include: {
                user: {
                    select: {
                        id: true,
                        username: true,
                        email: true,
                    },
                },
            },
        });
    }

    /**
     * 새로운 게시글을 생성합니다.
     * @param {string} type - 게시판 타입  
     * @param {Object} data - 생성할 게시글 데이터
     * @returns {Promise<Object>} 생성된 게시글 객체
     */
    static async create(type, data) {
        const model = this.getModelByType(type);

        return await model.create({
            data,
            include: {
                user: {
                    select: {
                        id: true,
                        username: true,
                    },
                },
            },
        });
    }

    /**
     * 게시글을 수정합니다.
     * @param {string} type - 게시판 타입
     * @param {number} id - 게시글 ID
     * @param {Object} data - 수정할 데이터
     * @returns {Promise<Object>} 수정된 게시글 객체
     */
    static async update(type, id, data) {
        const model = this.getModelByType(type);

        return await model.update({
            where: { id: parseInt(id) },
            data,
            include: {
                user: {
                    select: {
                        id: true,
                        username: true,
                    },
                },
            },
        });
    }

    /**
     * 게시글을 삭제합니다.
     * @param {string} type - 게시판 타입
     * @param {number} id - 게시글 ID
     * @returns {Promise<Object>} 삭제된 게시글 객체
     */
    static async delete(type, id) {
        const model = this.getModelByType(type);

        return await model.delete({
            where: { id: parseInt(id) },
        });
    }
}

module.exports = BoardRepository;
