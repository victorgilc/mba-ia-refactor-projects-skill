class CheckoutController {
    constructor(checkoutService) {
        this.checkoutService = checkoutService;
    }

    checkout(req, res) {
        const result = this.checkoutService.checkout(req.body || {});
        if (typeof result.body === 'string') {
            return res.status(result.status).send(result.body);
        }
        return res.status(result.status).json(result.body);
    }
}

module.exports = CheckoutController;
