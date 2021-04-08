from django import template
from speedtest.models import TestResult, Locations
from decimal import Decimal, getcontext
from datetime import timedelta, datetime
register = template.Library()


@register.simple_tag(name='summary_stats')
def summary_stats():
    data = TestResult.objects.values('alias', 'download', 'upload', 'ping')[:96]
    locations = Locations.objects.values_list('location')
    sumstats = []
    context = {}
    for i in data:
        sumstats.append((i['alias'], i['download'], i['upload'], i['ping']))
    for i in locations:
        counter = 0
        tempdsum = Decimal(0.00)
        tempupsum = Decimal(0.00)
        tempingsum = Decimal(0.00)
        for d in sumstats:
            if d[0] == i[0]:
                tempdsum = tempdsum + Decimal(d[1])
                tempupsum = tempupsum + Decimal(d[2])
                tempingsum = tempingsum + Decimal(d[3])
                counter += 1
        ilist = [tempdsum, tempupsum, tempingsum]
        try:
            flist = ['{0:.2f}'.format(Decimal(x / counter)) for x in ilist]
        except Exception:
            flist = ['N/A', 'N/A', 'N/A']
        flist.append(counter)
        context[i[0]] = flist
    return context

@register.simple_tag(name='tdelta')
def time_delta():
    return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')