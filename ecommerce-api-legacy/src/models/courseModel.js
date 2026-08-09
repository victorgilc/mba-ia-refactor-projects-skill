class CourseModel {
    constructor(db) {
        this.db = db;
        this.findActiveByIdStmt = db.prepare('SELECT * FROM courses WHERE id = ? AND active = 1');
    }

    findActiveById(id) {
        return this.findActiveByIdStmt.get(id) || null;
    }
}

module.exports = CourseModel;
