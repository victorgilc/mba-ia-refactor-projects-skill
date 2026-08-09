const { DatabaseSync } = require('node:sqlite');
const { hashPassword } = require('../utils/crypto');

function openDatabase(dbPath = ':memory:') {
    const db = new DatabaseSync(dbPath);

    db.exec(`
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT);
        CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER);
        CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER);
        CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT);
        CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME);
    `);

    seed(db);
    return db;
}

function seed(db) {
    const insertUser = db.prepare('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)');
    const insertCourse = db.prepare('INSERT INTO courses (title, price, active) VALUES (?, ?, ?)');
    const insertEnrollment = db.prepare('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)');
    const insertPayment = db.prepare('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)');

    insertUser.run('Leonan', 'leonan@fullcycle.com.br', hashPassword('123'));
    insertCourse.run('Clean Architecture', 997.00, 1);
    insertCourse.run('Docker', 497.00, 1);
    insertEnrollment.run(1, 1);
    insertPayment.run(1, 997.00, 'PAID');
}

module.exports = { openDatabase };
