const { Router } = require('express');

function reportRoutes(reportController) {
    const router = Router();

    router.get('/api/admin/financial-report', (req, res) => reportController.getFinancialReport(req, res));

    return router;
}

module.exports = reportRoutes;
