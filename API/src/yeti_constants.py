
class AccessTokenStatusCode:
    valid = 0
    refreshed = 1
    blacklisted = 2


class TransactionDirectionCode:
    i_pay_friend = 0
    friend_pays_me = 1


class TransactionStatusCode:
    open = 0
    closed = 1
    deactivated = 2


class TransactionUpdateActions:
    initial_creation = 0
    close_pending = 1
    close_complete = 2
    reopen_pending = 3
    reopen_complete = 4
    deactivate_pending = 5
    deactivate_complete = 6
    reactivate_pending = 7
    reactivate_complete = 8
