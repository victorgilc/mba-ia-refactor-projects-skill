const { Router } = require('express');

function checkoutRoutes(checkoutController) {
    const router = Router();

    router.post('/api/checkout', (req, res) => checkoutController.checkout(req, res));

    return router;
}

module.exports = checkoutRoutes;
