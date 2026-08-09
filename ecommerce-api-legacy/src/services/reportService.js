const PAYMENT_STATUS = { PAID: 'PAID' };

class ReportService {
    constructor(reportModel) {
        this.reportModel = reportModel;
    }

    getFinancialReport() {
        const rows = this.reportModel.getFinancialReportRows();
        const report = [];
        let current = null;

        for (const row of rows) {
            if (!current || current.courseId !== row.course_id) {
                current = {
                    courseId: row.course_id,
                    course: row.title,
                    revenue: 0,
                    students: []
                };
                report.push(current);
            }

            if (row.enrollment_id === null) {
                continue;
            }

            if (row.status === PAYMENT_STATUS.PAID) {
                current.revenue += row.amount;
            }

            current.students.push({
                student: row.student_name || 'Unknown',
                paid: row.amount !== null ? row.amount : 0
            });
        }

        return report.map(({ course, revenue, students }) => ({ course, revenue, students }));
    }
}

module.exports = ReportService;
