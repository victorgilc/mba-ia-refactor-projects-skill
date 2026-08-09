const express = require('express');
const { config } = require('./config');
const { openDatabase } = require('./models/database');
const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const ReportModel = require('./models/reportModel');
const CheckoutService = require('./services/checkoutService');
const ReportService = require('./services/reportService');
const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');
const { notFoundHandler, errorHandler } = require('./middlewares/errorHandler');

function createApp() {
    const db = openDatabase(':memory:');

    const userModel = new UserModel(db);
    const courseModel = new CourseModel(db);
    const enrollmentModel = new EnrollmentModel(db);
    const paymentModel = new PaymentModel(db);
    const auditLogModel = new AuditLogModel(db);
    const reportModel = new ReportModel(db);

    const checkoutService = new CheckoutService({
        userModel,
        courseModel,
        enrollmentModel,
        paymentModel,
        auditLogModel
    });
    const reportService = new ReportService(reportModel);

    const checkoutController = new CheckoutController(checkoutService);
    const reportController = new ReportController(reportService);
    const userController = new UserController(userModel);

    const app = express();
    app.use(express.json());

    app.use(checkoutRoutes(checkoutController));
    app.use(reportRoutes(reportController));
    app.use(userRoutes(userController));

    app.use(notFoundHandler);
    app.use(errorHandler);

    return app;
}

const app = createApp();

app.listen(config.port, () => {
    console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
});
