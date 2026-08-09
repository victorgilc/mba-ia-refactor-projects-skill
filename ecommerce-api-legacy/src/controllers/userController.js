class UserController {
    constructor(userModel) {
        this.userModel = userModel;
    }

    deleteUser(req, res) {
        const id = req.params.id;
        try {
            this.userModel.delete(id);
        } catch (e) {
            // legado ignora erros de banco aqui e ainda responde a mensagem padrão
        }
        return res.send('Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.');
    }
}

module.exports = UserController;
