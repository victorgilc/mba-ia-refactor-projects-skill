const { Router } = require('express');

function userRoutes(userController) {
    const router = Router();

    router.delete('/api/users/:id', (req, res) => userController.deleteUser(req, res));

    return router;
}

module.exports = userRoutes;
