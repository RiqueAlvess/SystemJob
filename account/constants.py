class Routes:
    ADMIN_INDEX = "admin:index"
    ACCOUNT_PANEL = "account:panel"
    ACCOUNT_LOGIN = "account:login"
    ACCOUNT_FORGOT_PASSWORD = "account:forgot_password"        
    ACCOUNT_RESET_COMPLETE = "account:password_reset_complete"  

class Messages:
    LOGIN_SUCCESS = "Bem-vindo de volta, {}!"
    REGISTER_PCD_SUCCESS = "Bem-vindo à Plataforma PCD, {}!"
    REGISTER_COMPANY_SUCCESS = "Bem-vindo à Plataforma, {}! Sua conta será ativada após validação."
    LOGOUT_INFO = "Você saiu da sua conta. Até logo!"
    PASSWORD_RESET_EMAIL_SENT = "E-mail de redefinição enviado! Verifique sua caixa de entrada."
    PASSWORD_RESET_INVALID_LINK = "Link inválido ou expirado."
    PASSWORD_RESET_SUCCESS = "Senha alterada com sucesso!"
    PASSWORD_RESET_ERROR = "Erro ao alterar senha. Tente novamente."