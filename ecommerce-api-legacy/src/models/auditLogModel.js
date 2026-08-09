class AuditLogModel {
    constructor(db) {
        this.db = db;
        this.insertStmt = db.prepare("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))");
    }

    create(action) {
        this.insertStmt.run(action);
    }
}

module.exports = AuditLogModel;
