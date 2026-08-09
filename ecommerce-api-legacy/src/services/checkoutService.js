const { hashPassword } = require('../utils/crypto');
const { PaymentService } = require('./paymentService');

const DEFAULT_PASSWORD = '123456';

class CheckoutService {
    constructor({ userModel, courseModel, enrollmentModel, paymentModel, auditLogModel }) {
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
        this.auditLogModel = auditLogModel;
        this.paymentService = new PaymentService();
    }

    checkout({ usr, eml, pwd, c_id, card }) {
        if (!usr || !eml || !c_id || !card) {
            return { status: 400, body: 'Bad Request' };
        }

        const course = this.courseModel.findActiveById(c_id);
        if (!course) {
            return { status: 404, body: 'Curso não encontrado' };
        }

        let user;
        try {
            user = this.userModel.findByEmail(eml);
        } catch (e) {
            return { status: 500, body: 'Erro DB' };
        }

        let userId;
        if (!user) {
            const passHash = hashPassword(pwd || DEFAULT_PASSWORD);
            try {
                userId = this.userModel.create(usr, eml, passHash);
            } catch (e) {
                return { status: 500, body: 'Erro ao criar usuário' };
            }
        } else {
            userId = user.id;
        }

        const status = this.paymentService.processPayment(card);
        if (status === 'DENIED') {
            return { status: 400, body: 'Pagamento recusado' };
        }

        let enrollmentId;
        try {
            enrollmentId = this.enrollmentModel.create(userId, c_id);
        } catch (e) {
            return { status: 500, body: 'Erro Matrícula' };
        }

        try {
            this.paymentModel.create(enrollmentId, course.price, status);
        } catch (e) {
            return { status: 500, body: 'Erro Pagamento' };
        }

        try {
            this.auditLogModel.create(`Checkout curso ${c_id} por ${userId}`);
        } catch (e) {
            // legado ignora falha no log de auditoria e ainda responde sucesso
        }

        return { status: 200, body: { msg: 'Sucesso', enrollment_id: enrollmentId } };
    }
}

module.exports = CheckoutService;
