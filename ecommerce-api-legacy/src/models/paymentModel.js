class PaymentModel {
    constructor(db) {
        this.db = db;
        this.insertStmt = db.prepare('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)');
        this.findByEnrollmentStmt = db.prepare('SELECT amount, status FROM payments WHERE enrollment_id = ?');
    }

    create(enrollmentId, amount, status) {
        this.insertStmt.run(enrollmentId, amount, status);
    }

    findByEnrollment(enrollmentId) {
        return this.findByEnrollmentStmt.get(enrollmentId) || null;
    }
}

module.exports = PaymentModel;
