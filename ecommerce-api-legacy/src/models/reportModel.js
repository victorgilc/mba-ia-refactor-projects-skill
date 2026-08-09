class ReportModel {
    constructor(db) {
        this.db = db;
        this.financialReportStmt = db.prepare(`
            SELECT
                c.id AS course_id,
                c.title,
                e.id AS enrollment_id,
                u.name AS student_name,
                p.amount AS amount,
                p.status AS status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            ORDER BY c.id, e.id
        `);
    }

    getFinancialReportRows() {
        return this.financialReportStmt.all();
    }
}

module.exports = ReportModel;
