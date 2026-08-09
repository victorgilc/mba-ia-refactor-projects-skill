class EnrollmentModel {
    constructor(db) {
        this.db = db;
        this.insertStmt = db.prepare('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)');
    }

    create(userId, courseId) {
        const result = this.insertStmt.run(userId, courseId);
        return Number(result.lastInsertRowid);
    }
}

module.exports = EnrollmentModel;
