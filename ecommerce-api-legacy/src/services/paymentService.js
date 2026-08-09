const CARD_PREFIX_PAID = '4';
const PAYMENT_STATUS = { PAID: 'PAID', DENIED: 'DENIED' };

class PaymentService {
    processPayment(cardNumber) {
        return cardNumber.startsWith(CARD_PREFIX_PAID) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
    }
}

module.exports = { PaymentService, PAYMENT_STATUS };
