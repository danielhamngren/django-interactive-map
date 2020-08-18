import datetime

def get_isoweekdays_btw_dates(d1, d2):
    if (d2 - d1).days >= 7:
        return list(range(1, 8))
    wd1, wd2 = d1.isoweekday(), d2.isoweekday()
    if wd1 <= wd2 :
        return list(range(wd1, wd2+1))
    else:
        return [j % 7 + 1 for j in range(wd1 - 1, wd2 + 7)]