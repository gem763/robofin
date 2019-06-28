import requests
import pandas as pd


class CoinAPI:
    def __init__(self, *, symbol, ccy, exchange):
        self.symbol = symbol
        self.ccy = ccy
        self.exchange = exchange

    class NotProperResponseError(Exception):
        pass

    class SomethingWrongError(Exception):
        pass


    def _int(self, num_s):
        try:
            return int(num_s)
        except ValueError:
            return int(float(num_s))


    def _request(self, *, nbars, utc_to, freq='h'):
        # 참고: 종료시점(utc_to)이 반드시 시간(h)으로 나누어 떨어질 필요는 없다

        # 종료시점(utc_to)이 utc timestamp(integer/float 또는 숫자로 된 문자열)로 주어진 경우
        if str(utc_to).isdigit():
            utc_to = self._int(utc_to)

        # 시간 문자열(ex. 2019-06-12 05:00:45)로 주어진 경우
        else:
            utc_to = int(pd.Timestamp(utc_to).timestamp())

        if freq == 'h':
            endpoint = 'histohour'

        elif freq == 'd':
            endpoint = 'histoday'


        baseurl = ('https://min-api.cryptocompare.com/data/{endpoint}?'
                   'fsym={fsym}'
                   '&tsym={tsym}'
                   '&e={e}'
                   '&limit={limit}'
                   '&toTs={toTs}')

        url = baseurl.format(endpoint=endpoint, fsym=self.symbol, tsym=self.ccy, e=self.exchange, limit=nbars, toTs=utc_to)
        resp = requests.get(url).json()
        msg = resp['Response']

        if msg == 'Success':
            truncated = True
            utc_from = None

            data = {str(pd.to_datetime(_r.pop('time'), unit='s')):_r for _r in resp['Data'] if _r['close'] != 0}

            if len(data) > 0:
                n_del = max(0, len(data) - nbars)
                keys = sorted(data)
                keys_del = keys[:n_del]
                [data.pop(k) for k in keys_del]

                utc_from = keys[n_del]

                if len(data) == nbars:
                    truncated = False


            return {
                'data': data,
                'truncated': truncated,
                'utc_from': utc_from,
            }

        elif msg == 'Error':
            raise self.NotProperResponseError()

        else:
            raise self.SomethingWrongError()


    def market_history(self, *, utc_from=None, utc_to=None, freq='h'):
        # 시작시점(utc_from)이나 종료시점(utc_to)이 주어지지 않았다면,
        # 해당 코인 가격정보를 가장 최근 시점까지 가져온다
        # 참고: 입력 파라미터에서의 시작시점(utc_from)와 종료시점(utc_to)이 반드시 시간(h)으로 나누어 떨어질 필요는 없다

        data = {}

        if utc_from is None:
            utc_from = pd.Timestamp('2000-01-01')
        else:
            utc_from = pd.Timestamp(utc_from).ceil('h')

        if utc_to is None:
            utc_to = pd.Timestamp.utcnow().floor('h') + pd.Timedelta(-1, unit='h')
        else:
            utc_to = pd.Timestamp(utc_to).floor('h')


        # nbar 구하기: 시작시점(_from)을 포함해야 하기에 +1
        _nbars_h = lambda _from, _to: int((_to.timestamp() - _from.timestamp()) / 3600) + 1

        while True:
            nbars = _nbars_h(utc_from, utc_to)
            nbars = min(2000, nbars)
            req = self._request(nbars=nbars, utc_to=utc_to, freq=freq)
            data.update(req['data'])

            print(req['utc_from'] + ' - ' + str(utc_to))

            if req['truncated'] or (nbars < 2000):
                print('completed')
                break

            # 루프를 계속 돌려야된다면, 전 response의 (시작시점-1초)를 다음 루프의 종료시점으로 둔다
            else:
                utc_to = pd.Timestamp(req['utc_from']) + pd.Timedelta(-1, unit='s')


        return data
