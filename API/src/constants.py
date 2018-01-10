class AuthVerifyResultCode:
    success = 0
    password_mismatch = 1
    login_email_nonexistent = 2
    login_email_suspended = 3
    device_suspended = 4
    server_error = 5
    token_invalid = 6
    token_expired = 7
    token_missing = 8
    auth_code_invalid = 9


class AccessTokenStatusCode:
    valid = 0
    refreshed = 1
    blacklisted = 2


class TransactionStatusCode:
    open = 0
    completed = 1
