import requests

import config as cfg


class Notification:

    INVESTOR = "Инвестор: {amount:.6f} {token}"
    REFERRER = "Реферер: {amount:.6f} {token} ~ {percent:.1f}%"
    FUND = "Комиссия фонда: {fee:.6f} {token} ~ {percent:.1f}%"

    API_URL = 'https://api.telegram.org/bot'

    def __init__(self):
        self.output = None
        self.clear()

    def clear(self):
        self.output = ["💳  <b>Покупка токена</b>\n"]

    def send(self):
        # TODO: connect to telegram
        text = '\n'.join(self.output)
        requests.post(
            url=self.API_URL + cfg.API_TOKEN + '/sendMessage',
            data={
                'chat_id': cfg.GROUP_ID,
                'text': text,
                'parse_mode': 'HTML'
            }
        )

    def add_investor(self, amount, token):
        investor = self.INVESTOR.format(amount=amount, token=token.upper())
        self.output.insert(1, investor)

    def add_referrer(self, amount, token, percent):
        referrer = self.REFERRER.format(
            amount=amount, token=token.upper(), percent=percent)
        self.output.append(referrer)

    def add_fund(self, fee, token, percent):
        fund = self.FUND.format(fee=fee, token=token.upper(), percent=percent)
        self.output.append(fund)


notification = Notification()
