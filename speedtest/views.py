from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.http import HttpResponse
from .models import TestResult, Locations
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
import csv

# Create your views here.


class HomeView(TemplateView):
    template_name = "speedtest/base.html"


class PerformanceView(ListView):
    model = TestResult

    def get_queryset(self):
        return TestResult.objects.order_by("-test_datetime")[:10]


def FilterView(request):
    qs = TestResult.objects.all()
    locations = Locations.objects.values('location')
    template_name = "speedtest/recordview.html"
    location_selection = request.GET.get('location-list')
    start_datetime_ = request.GET.get('start-datetime')
    end_datetime_ = request.GET.get('end-datetime')
    page = request.GET.get('page', 1)
    if location_selection != 'All' and location_selection is not None:
        qs = qs.filter(alias__contains=location_selection)
    if location_selection == 'All':
        qs = TestResult.objects.all()
    if start_datetime_ != '' and start_datetime_ is not None:
        start_datetime = datetime.strptime(start_datetime_, '%Y-%m-%dT%H:%M')
        qs = qs.filter(test_datetime__gte=start_datetime)
    if end_datetime_ != '' and end_datetime_ is not None:
        end_datetime = datetime.strptime(end_datetime_, '%Y-%m-%dT%H:%M')
        qs = qs.filter(test_datetime__lte=end_datetime)
    paginator = Paginator(qs, 4)
    try:
        testresults = paginator.page(page)
    except PageNotAnInteger:
        testresults = paginator.page(1)
    except EmptyPage:
        testresults = paginator.page(paginator.num_pages)
    context = {
        'locations': locations,
        'testresult_list': testresults,
        'results': len(qs),
        'location_selection': location_selection,
        'start_date': start_datetime_,
        'end_date': end_datetime_,
    }
    return render(request, template_name, context)

def CSV_output(request):
    qs = TestResult.objects.values('alias', 'test_datetime', 'download', 'upload', 'ping').order_by('test_datetime')
    location_selection = request.GET.get('location-list')
    start_datetime_ = request.GET.get('start-datetime')
    end_datetime_ = request.GET.get('end-datetime')
    page = request.GET.get('page', 1)
    if location_selection != 'All' and location_selection is not None:
        qs = qs.filter(alias__contains=location_selection)
    if location_selection == 'All':
        qs = TestResult.objects.all()
    if start_datetime_ != '' and start_datetime_ is not None:
        start_datetime = datetime.strptime(start_datetime_, '%Y-%m-%dT%H:%M')
        qs = qs.filter(test_datetime__gte=start_datetime)
    if end_datetime_ != '' and end_datetime_ is not None:
        end_datetime = datetime.strptime(end_datetime_, '%Y-%m-%dT%H:%M')
        qs = qs.filter(test_datetime__lte=end_datetime)

    response = HttpResponse(content_type='text/csv')
    try:
        response['Content-Disposition'] = 'attachment; filename="Network_data-{}_{}_location={}.csv"'.format(start_datetime.strftime('%Y-%m-%d-%H-%M'), end_datetime.strftime('%Y-%m-%d-%H-%M'), location_selection)
    except Exception:
        response['Content-Disposition'] = 'attachment; filename="Network_data-location={}.csv"'.format(location_selection)
    writer = csv.writer(response)
    try:
        writer.writerow(["location: ", location_selection, 'Start Date: ', start_datetime.strftime('%B %d, %Y - %X'), 'End Date: ', end_datetime.strftime('%B %d, %Y - %X'), 'Retrieved: ', datetime.now().strftime('%B %d, %Y - %X')])
    except Exception:
        writer.writerow(["location: ", location_selection, 'Retrieved: ', datetime.now().strftime('%B %d, %Y - %X')])
    writer.writerow(['Location', 'Test Datetime', 'Download Speed', 'Upload Speed', 'Ping Time'])
    for i in qs.values():
        writer.writerow([i['alias'], i['test_datetime'].strftime('%c'), i['download'], i['upload'], i['ping']])
    return response

@api_view(['GET'])
def chart_data(request, format=None):
    num_of_sites = len(Locations.objects.values('location'))
    data = TestResult.objects.values('alias', 'test_datetime', 'download', 'upload', 'ping').order_by('test_datetime')[:num_of_sites * 96]
    chart_labels = []
    locations = []
    plotables = {}
    ping = []
    for i in data:
        ping.append(i['ping'])
        if i['alias'] in chart_labels:
            plotables[i['alias']].append((i['test_datetime'].strftime('%Y-%m-%d %X'), i['download'], i['upload'], i['ping']))
        else:
            chart_labels.append(i['alias'])
            chart_labels.append(i['alias'] + ' upload')
            locations.append(i['alias'])
            plotables[i['alias']] = []
            plotables[i['alias']].append((i['test_datetime'].strftime('%Y-%m-%d %X'), i['download'], i['upload'], i['ping']))
    labels = []
    for i in locations:
        for x in plotables.get(i):
            labels.append(x[0])
    list = []
    dict = {}
    color_q = Locations.objects.values('location', 'color')
    colors = {}
    for i in color_q:
        colors[i['location']] = i['color']
    for i, v in plotables.items():
        dict[i] = [{'x': x[0], 'y': x[1]} for x in v]
        dict[i + ' Upload'] = [{'x': x[0], 'y': x[2]} for x in v]
        dict[i + ' Ping'] = [{'x': x[0], 'y': x[3]} for x in v]
    for i, v in plotables.items():
        list.append(
            {
             'label': i,
             'data': dict[i],
             'YAxisID': 'A',
             'borderColor': colors[i],
             })
        list.append(
            {
             'label': i + ' Upload',
             'data': dict[i + ' Upload'],
             'yAxisID': 'A',
             'borderColor': colors[i],
             'borderDash': [10, 5]
             }
        )
        list.append(
            {
                'label': i + ' Ping',
                'data': dict[i + ' Ping'],
                'yAxisID': 'B',
                'borderColor': colors[i],
                'borderDash': [2, 10],
            }
        )
    axis = [
        {
            'id': 'A',
            'type': 'linear',
            'position': 'left',
            'ticks': {
                'beginAtZero': 'true'
            },
            'scaleLabel': {
                'display': 'true',
                'labelString': 'Bandwidth | Mb/S',
                'fontSize': 16,
            }
        },
        {
            'id': 'B',
            'type': 'linear',
            'position': 'right',
            'ticks': {
                'max': max(ping) + 10,
                'min': min(ping) - 10,
            },
            'scaleLabel': {
                'display': 'true',
                'labelString': 'Ping Time | Milliseconds',
                'fontSize': 16,
            }
        },
    ]
    context = {'labels': labels, 'datasets': list, 'axis_context': axis}

    return Response(context)

