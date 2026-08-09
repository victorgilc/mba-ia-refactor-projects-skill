class UserModel {
    constructor(db) {
        this.db = db;
        this.findByIdStmt = db.prepare('SELECT id, name, email FROM users WHERE id = ?');
        this.findByEmailStmt = db.prepare('SELECT id, name, email FROM users WHERE email = ?');
        this.insertStmt = db.prepare('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)');
        this.deleteStmt = db.prepare('DELETE FROM users WHERE id = ?');
    }

    findById(id) {
        return this.findByIdStmt.get(id) || null;
    }

    findByEmail(email) {
        return this.findByEmailStmt.get(email) || null;
    }

    create(name, email, passHash) {
        const result = this.insertStmt.run(name, email, passHash);
        return Number(result.lastInsertRowid);
    }

    delete(id) {
        this.deleteStmt.run(id);
    }

    toPublic(row) {
        return { id: row.id, name: row.name, email: row.email };
    }
}

module.exports = UserModel;
