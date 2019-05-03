from django.conf import settings
import pandas as pd
import os


info_path = os.path.join(settings.BASE_DIR, 'info.pkl')
fin_path = os.path.join(settings.BASE_DIR, 'fin.pkl')
mc_path = os.path.join(settings.BASE_DIR, 'mc.pkl')

info = pd.read_pickle(info_path)
fin = pd.read_pickle(fin_path)
mc = pd.read_pickle(mc_path)


def backtest(model, n):
    bt = Backtest(model=model, bm=BM, fin=fin, mc=mc, info=info, n=n)
    bt.run()
    return bt


def get_fisyear(date):
    if type(date)==str:
        date = pd.Timestamp(date)

    if date.month >= 6:
        return date.year - 1

    else:
        return date.year - 2


def 매출상위(date, fin=None, mc=None, n=10):
    fisyear = get_fisyear(date)
    univ = mc.columns[mc.loc[date]>0]
    position = fin['매출액'].xs(fisyear, level=1).loc[univ].nlargest(n)
    position[:] = 1/len(position)
    return position


def 시총상위PB저평가(date, fin=None, mc=None, n=10):
    fisyear = get_fisyear(date)
    marketcap = mc.loc[date].nlargest(100)
    univ = marketcap.index
    bv = fin['자본총계'].xs(fisyear, level=1).loc[univ]
    bp = bv / marketcap
    position = bp.nlargest(n)
    position[:] = 1/len(position)
    return position


def 슈퍼밸류(date, fin=None, mc=None, n=10):
    fisyear = get_fisyear(date)
    marketcap = mc.loc[date].nlargest(100)
    univ = marketcap.index
    _ni = fin['순익(단순)'].xs(fisyear, level=1)>0
    _bv = fin['자본총계'].xs(fisyear, level=1)>0
    _ocf = fin['영활현흐'].xs(fisyear, level=1)>0
    _ebitda = fin['EBITDA'].xs(fisyear, level=1)>0
    _dvd = fin['DPS'].xs(fisyear, level=1)>0
    screen = (_ni & _bv & _ocf & _ebitda & _dvd).loc[univ]
    univ = screen.index[screen]
    marketcap = marketcap.loc[univ]
    ni = fin['순익(단순)'].xs(fisyear, level=1).loc[univ]
    bv = fin['자본총계'].xs(fisyear, level=1).loc[univ]
    ocf = fin['영활현흐'].xs(fisyear, level=1).loc[univ]
    sales = fin['매출액'].xs(fisyear, level=1).loc[univ]
    ebitda = fin['EBITDA'].xs(fisyear, level=1).loc[univ]
    ev = fin['EV'].xs(fisyear, level=1).loc[univ]

    r_per = (ni/marketcap).rank()
    r_pbr = (bv/marketcap).rank()
    r_pcr = (ocf/marketcap).rank()
    r_psr = (sales/marketcap).rank()
    r_ee = (ebitda/ev).rank()

    r_total = r_per + r_pbr + r_pcr + r_psr + r_ee
    position = r_total.nlargest(n)
    position[:] = 1/len(position)

    return position


def BM(date, fin=None, mc=None, n=200):
    position = mc.loc[date].nlargest(n)
    position /= position.sum()
    return position



class Backtest:
    def __init__(self, model=None, bm=None, fin=None, mc=None, info=None, n=10):
        self.model = model
        self.bm = bm
        self.fin = fin
        self.mc = mc
        self.info = info
        self.n = n

    def run(self):
        dates = self.mc.index[8:]
        pos = {}
        nav = {}
        pos_bm = {}
        nav_bm = {}

        for i,date in enumerate(dates):
            pos[date] = self.model(date, fin=self.fin, mc=self.mc, n=self.n)
            pos_bm[date] = self.bm(date, fin=self.fin, mc=self.mc)

            if i==0:
                nav[date] = 1
                nav_bm[date] = 1

            else:
                date_prev = dates[i-1]
                nav[date] = self.evaluate(nav, pos, date_prev, date)
                nav_bm[date] = self.evaluate(nav_bm, pos_bm, date_prev, date)

        self.nav = nav
        self.pos = pos
        self.nav_bm = nav_bm
        self.pos_bm = pos_bm


    def evaluate(self, nav, pos, date_prev, date):
        nav_prev = nav[date_prev]
        pos_prev = pos[date_prev]
        assets_prev = pos_prev.index
        pos_update = self.mc.loc[date, assets_prev] / self.mc.loc[date_prev, assets_prev] * pos_prev
        return nav_prev * pos_update.sum()

    def navs(self):
        return pd.DataFrame({'Model':self.nav, 'BM':self.nav_bm})

    def plot_perf(self):
        self.navs().plot()

    def stats(self):
        _navs = self.navs()
        days_all = (_navs.index[-1]-_navs.index[0]).days
        ann_rtn = (_navs.iloc[-1]**(365/days_all))-1
        vol = _navs.pct_change().std() * 4**0.5
        return pd.DataFrame({'Annual return':ann_rtn, 'Volatility':vol, 'Sharpe':ann_rtn/vol})

    def position(self, date=None, what='model'):
        if what=='model':
            pos = self.pos
        elif what=='bm':
            pos = self.pos_bm

        if date is None:
            return pd.DataFrame(pos).T
        else:
            return pos[pd.Timestamp(date)]

    def position_mapped(self):
        pos_kr = self.position().rename(columns=self.info['name'].to_dict())*100
        return {str(k.date()):pos_kr.loc[k].dropna().to_dict() for k in pos_kr.index}
