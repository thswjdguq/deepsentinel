const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcrypt');
const { DETECTION_RESULTS, REPORT_STATUS } = require('../config/constants');

const prisma = new PrismaClient();

/**
 * 데이터베이스 시드 스크립트
 * 개발 및 테스트를 위한 더미 데이터를 생성합니다.
 */

/**
 * 더미 사용자를 생성합니다.
 * @returns {Promise<Array>} 생성된 사용자 배열
 */
async function seedUsers() {
    console.log('👤 Creating users...');

    // 비밀번호 해싱 (bcrypt, salt rounds: 10)
    const hashedPassword = await bcrypt.hash('password123', 10);

    const user1 = await prisma.user.upsert({
        where: { email: 'admin@deepsentinel.com' },
        update: {},
        create: {
            username: 'admin',
            email: 'admin@deepsentinel.com',
            passwordHash: hashedPassword,
        },
    });

    const user2 = await prisma.user.upsert({
        where: { email: 'test@deepsentinel.com' },
        update: {},
        create: {
            username: 'testuser',
            email: 'test@deepsentinel.com',
            passwordHash: hashedPassword,
        },
    });

    const user3 = await prisma.user.upsert({
        where: { email: 'demo@deepsentinel.com' },
        update: {},
        create: {
            username: 'demouser',
            email: 'demo@deepsentinel.com',
            passwordHash: hashedPassword,
        },
    });

    console.log('✅ Created users:', [user1.username, user2.username, user3.username]);
    return [user1, user2, user3];
}

/**
 * 더미 분석 기록을 생성합니다.
 * @param {Array} users - 생성된 사용자 배열
 * @returns {Promise<Array>} 생성된 분석 기록 배열
 */
async function seedDetectionLogs(users) {
    console.log('📊 Creating detection logs...');

    const logs = [];

    // User 1의 분석 기록
    logs.push(await prisma.detectionLog.create({
        data: {
            userId: users[0].id,
            videoUrl: 'https://example.com/videos/sample1.mp4',
            result: DETECTION_RESULTS.FAKE,
            confidence: 0.92,
        },
    }));

    logs.push(await prisma.detectionLog.create({
        data: {
            userId: users[0].id,
            videoUrl: 'https://example.com/videos/sample2.mp4',
            result: DETECTION_RESULTS.REAL,
            confidence: 0.87,
        },
    }));

    // User 2의 분석 기록
    logs.push(await prisma.detectionLog.create({
        data: {
            userId: users[1].id,
            videoUrl: 'https://example.com/videos/test-video.mp4',
            result: DETECTION_RESULTS.UNCERTAIN,
            confidence: 0.52,
        },
    }));

    // User 3의 분석 기록
    logs.push(await prisma.detectionLog.create({
        data: {
            userId: users[2].id,
            videoUrl: 'https://example.com/videos/demo.mp4',
            result: DETECTION_RESULTS.FAKE,
            confidence: 0.95,
        },
    }));

    console.log(`✅ Created ${logs.length} detection logs`);
    return logs;
}

/**
 * 더미 커뮤니티 제보를 생성합니다.
 * @param {Array} users - 생성된 사용자 배열
 * @returns {Promise<Array>} 생성된 제보 배열
 */
async function seedCommunityReports(users) {
    console.log('📝 Creating community reports...');

    const reports = [];

    reports.push(await prisma.communityReport.create({
        data: {
            userId: users[1].id,
            title: '의심스러운 정치인 연설 영상',
            content: '최근 SNS에서 화제가 된 정치인 발언 영상이 조작된 것 같습니다. 입 모양과 음성이 일치하지 않는 부분이 여러 군데 발견되었습니다. 확인 부탁드립니다.',
            videoUrl: 'https://example.com/reports/suspicious-speech.mp4',
            status: REPORT_STATUS.PENDING,
        },
    }));

    reports.push(await prisma.communityReport.create({
        data: {
            userId: users[0].id,
            title: '유명 연예인 딥페이크 영상 제보',
            content: '유튜브에서 발견한 유명 연예인의 딥페이크 영상입니다. 얼굴이 부자연스럽게 합성된 것으로 보입니다.',
            videoUrl: 'https://example.com/reports/celebrity-deepfake.mp4',
            status: REPORT_STATUS.VERIFIED,
        },
    }));

    reports.push(await prisma.communityReport.create({
        data: {
            userId: users[2].id,
            title: '허위 뉴스 영상 신고',
            content: '뉴스 앵커의 목소리와 얼굴이 합성된 가짜 뉴스 영상이 퍼지고 있습니다.',
            videoUrl: 'https://example.com/reports/fake-news.mp4',
            status: REPORT_STATUS.VERIFIED,
        },
    }));

    reports.push(await prisma.communityReport.create({
        data: {
            userId: users[1].id,
            title: 'SNS 광고 영상 조작 의심',
            content: 'SNS 광고에 사용된 인플루언서 영상이 딥페이크로 조작된 것 같습니다.',
            videoUrl: null, // 영상 URL이 없는 경우
            status: REPORT_STATUS.REJECTED,
        },
    }));

    console.log(`✅ Created ${reports.length} community reports`);
    return reports;
}

/**
 * 메인 시드 함수
 * 모든 더미 데이터를 순차적으로 생성합니다.
 */
async function main() {
    console.log('🌱 Starting database seeding...\n');

    try {
        // 1. 사용자 생성
        const users = await seedUsers();
        console.log('');

        // 2. 분석 기록 생성
        const logs = await seedDetectionLogs(users);
        console.log('');

        // 3. 커뮤니티 제보 생성
        const reports = await seedCommunityReports(users);
        console.log('');

        console.log('🎉 Database seeding completed successfully!');
        console.log(`📊 Summary:`);
        console.log(`   - Users: ${users.length}`);
        console.log(`   - Detection Logs: ${logs.length}`);
        console.log(`   - Community Reports: ${reports.length}`);
    } catch (error) {
        console.error('❌ Error during database seeding:', error);
        throw error;
    }
}

// 스크립트 실행
main()
    .catch((error) => {
        console.error('❌ Fatal error:', error);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
        console.log('\n✨ Database connection closed.');
    });
