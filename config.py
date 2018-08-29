# Комиссия фонда
FEE = .05
# Кофицент вознаграждения для реферера от общей суммы пополнения
REF_LEVELS = (0.015, 0.01, 0.005)
# ID аккаунта фонда в partners
FUND_ID = 32

# Запуск в режиме testnet
DEBUG = True

# Настройки RPC
RPCS = {
    'btc': {
        'user': 'sreda',
        'password': 'TuZ0GQ69C8wW',
        'host': '127.0.0.1',
        'port': f'{18332 if DEBUG else 8332}'
    },
    'bch': {
        'user': 'sreda',
        'password': 'txbZ3YI653PtVbulWZXZoFSbyXuJBrq5',
        'host': '127.0.0.1',
        'port': f'{18432 if DEBUG else 8432}'
    },
    'zec': {
        'user': 'sreda',
        'password': 'myhkwsH707qObV1592beEv6LvXXvancM',
        'host': '127.0.0.1',
        'port': f'{18232 if DEBUG else 8232}'
    }
}

# Уведомления
API_TOKEN = '533035104:AAFbwljq76fLd8gbOLJfan16DZIqSr7j8Zw' #  @simplefied_test_bot
GROUP_ID = -243615628  # Тесты уведомлений
# GROUP_ID = -1001104403081,  # Команда

# API_TOKEN = '428370285:AAEfjY1o6DyLp1ysrz-OQBtgFYBwlmS-d1g' бот продакшен
# API_TOKEN = '428474365:AAGhkCJc3_mhKALgMX-4my45w53yRpxwAk8' @mycryptotestobot
# GROUP_ID = -286567703  # группа разрабов

