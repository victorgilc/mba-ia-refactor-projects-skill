const crypto = require('crypto');

const KEY_LENGTH = 64;
const SALT_LENGTH = 16;

function hashPassword(password) {
    const salt = crypto.randomBytes(SALT_LENGTH).toString('hex');
    const hash = crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex');
    return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
    const [salt, hash] = String(stored || '').split(':');
    if (!salt || !hash) return false;
    const candidate = crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex');
    return crypto.timingSafeEqual(Buffer.from(candidate), Buffer.from(hash));
}

module.exports = { hashPassword, verifyPassword };
