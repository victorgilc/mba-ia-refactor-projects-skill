class ReportController {
    constructor(reportService) {
        this.reportService = reportService;
    }

    getFinancialReport(req, res) {
        let report;
        try {
            report = this.reportService.getFinancialReport();
        } catch (e) {
            return res.status(500).send('Erro DB');
        }
        return res.json(report);
    }
}

module.exports = ReportController;
