function notFoundHandler(req, res) {
    res.status(404).send('Not Found');
}

function errorHandler(err, req, res, next) {
    const status = err.status || err.statusCode || 500;
    if (status >= 500) {
        console.error(err);
    }
    if (res.headersSent) {
        return next(err);
    }
    if (status >= 500) {
        return res.status(status).send('Internal Server Error');
    }
    return res.status(status).send(err.message || 'Error');
}

module.exports = { notFoundHandler, errorHandler };
