from django.shortcuts import render
import pandas as pd
import numpy as np
from pandas import DataFrame

from django.views import generic
import re

import pymongo
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
from django.http import JsonResponse
from django.utils.safestring import mark_safe
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from pandas.plotting import register_matplotlib_converters
import seaborn as sns
from datetime import datetime, timedelta

def main(request):
    template_name = 'smartf/main.html'

    #return JsonResponse(dump)
    return render(request, template_name)

def predict(request):
    template_name = 'smartf/predict.html'
    connection = pymongo.MongoClient("113.198.137.140",27017)
    db = connection.exercise
    collection = db.exercise_collection

    results=collection.find()
    count=results.count()
    #relist=list(collection.find()))
    #dump=json.dumps(dumps(relist), default=json_util.default)
    vib = []
    sound = []
    gas = []
    obtemp = []
    amtemp = []
    date = []
    for js in results:
        vib.append((js['vib']))
        date.append((js['date']))
        sound.append((js['sound']))
        gas.append((js['gas']))
        obtemp.append((js['objectTemp']))
        amtemp.append((js['ambientTemp']))

    vib_d = {'vib':vib}
    vib_diff = pd.DataFrame(vib_d,index = date)
    obt_d = {'objectTemp':obtemp}
    df2 = pd.DataFrame(obt_d,index = date)
    abt_d = {'ambientTemp':amtemp}
    df3 = pd.DataFrame(abt_d,index = date)
    gas_d = {'gas':gas}
    gas_diff = pd.DataFrame(gas_d,index = date)
    sound_d = {'sound':sound}
    sound_diff = pd.DataFrame(sound_d,index = date)

    obt_diff = df2.diff(periods=1).iloc[1:]
    abt_diff = df3.diff(periods=1).iloc[1:]

    model = ARIMA(vib_diff, order=(1, 0, 0))
    results = model.fit(trend = 'nc', disp=-1)
    results.plot_predict(count-200,count+200)
    plt.savefig('/home/gac/smfp/mysite/smartf/static/smartf/foo1.png')

    model = ARIMA(obt_diff, order=(0, 0, 1))
    results = model.fit(trend = 'nc', disp=-1)
    results.plot_predict(count-200, count+200)
    plt.savefig('/home/gac/smfp/mysite/smartf/static/smartf/foo2.png')


    model = ARIMA(abt_diff, order=(0, 0, 1))
    results = model.fit(trend = 'nc', disp=-1)
    results.plot_predict(count-200, count+200)
    plt.savefig('/home/gac/smfp/mysite/smartf/static/smartf/foo3.png')


    model = ARIMA(gas_diff, order=(2, 0, 0))
    results = model.fit(trend = 'nc', disp=-1)
    results.plot_predict(count-200, count+200)
    plt.savefig('/home/gac/smfp/mysite/smartf/static/smartf/foo4.png')

    model = ARIMA(sound_diff, order=(0, 0, 1))
    results = model.fit(trend = 'nc', disp=-1)
    results.plot_predict(count-200, count+200)
    plt.savefig('/home/gac/smfp/mysite/smartf/static/smartf/foo5.png')

    #return JsonResponse(dump)
    return render(request, template_name)


    return render(request, template_name)

def chart_get(request):
    connection = pymongo.MongoClient("113.198.137.140",27017)
    db = connection.exercise
    collection = db.exercise_collection
    
    results=collection.find()
    
    data = []
    sdata = []
    gdata = []
    obtemp = []
    amtemp = []
    date = []
    dis = []
    for js in results:
        data.append((js['vib']))
        date.append((js['date']))
        sdata.append((js['sound']))
        gdata.append((js['gas']))
        obtemp.append((js['objectTemp']))
        amtemp.append((js['ambientTemp']))
        dis.append((js['dis']))


    #data=json.loads(gjson)
    
    vib_series ={
        'name': 'vib',
        'data': data,
        'color': 'green'
    }
    sound_series = {
            'name': 'sound',
            'data': sdata,
            'color': 'blue'
    }
    gas_series = {
            'name': 'gas',
            'data': gdata,
            'color': 'red'
    }
    ob_series = {
            'name': 'objectTemp',
            'data': obtemp,
            'color': 'yellow'
    }
    am_series = {
            'name': 'ambientTemp',
            'data': amtemp,
            'color': 'orange'
    }
    dis_series = {
            'name': 'distance',
            'data': dis,
            'color': 'purple'
    }


    chart ={
            'title': {'text' : 'example'},
            'xAxis': {'categories':date,'tickInterval': 500},
            'series': [vib_series,sound_series,gas_series,ob_series,am_series,dis_series]
            }
    #dump = json.dumps(chart)

    #return render(request,template_name,{'chart':dump})
    return JsonResponse(chart)

def table_get(request):
    template_name = 'smartf/table.html'
    connection = pymongo.MongoClient("113.198.137.140",27017)
    db = connection.exercise
    collection = db.exercise_collection
    results=collection.find()
    data = []
    for js in results:
        data.append((js['vib']))

    return render(request,template_name,{'table':data})
def chart_search(request):
    template_name = 'smartf/graph.html'
    connection = pymongo.MongoClient("113.198.137.140",27017)
    db = connection.exercise
    collection = db.exercise_collection
    fdate = request.GET.get('fdate',None)
    if fdate=="" or fdate==None:
        results=collection.find()
    else:
        print(fdate)
        fdate=str(fdate)
        con_fd=datetime.strptime(fdate,"%Y-%m-%d").date()
        con_fd2=con_fd+timedelta(days=1)
        con_fd=str(con_fd)
        con_fd2=str(con_fd2)
        results=collection.find({'date':{'$lte':con_fd2,'$gte':con_fd}})

    vib = []
    date = []
    sound = []
    obtemp = []
    distance = []
    gas = []

    for js in results:
        vib.append((js['vib']))
        date.append((js['date']))
        sound.append((js['sound']))
        obtemp.append((js['objectTemp']))
        distance.append((js['dis']))
        gas.append((js['gas']))
    jvib = json.dumps(vib)
    jsound = json.dumps(sound)
    jdate = json.dumps(date)
    jobtemp = json.dumps(obtemp)
    jgas = json.dumps(gas)
    jdis = json.dumps(distance)

    print(jdate)
    return render(request, template_name,{'vib':jvib,'dats':jdate,'sound':jsound,'obtemp':obtemp,'gas':jgas,'dis':jdis})

def Correlation(request):
    template_name = 'smartf/correl.html'
    fdate=request.GET.get("Fdate",None)
    connection = pymongo.MongoClient("113.198.137.140",27017)
    db = connection.exercise
    collection = db.exercise_collection
    if fdate=="" or fdate==None:
        today=datetime.today().strftime("%Y-%m-%d")
        results=collection.find({'date':{'$gte':today}})
    else:
        print(fdate)
        fdate=str(fdate)
        con_fd=datetime.strptime(fdate,"%Y-%m-%d").date()
        con_fd2=con_fd+timedelta(days=1)
        con_fd=str(con_fd)
        con_fd2=str(con_fd2)
        results=collection.find({'date':{'$lte':con_fd2,'$gte':con_fd}})
    
    #results=collection.find({'date':{"$lte":"2020-02-16"}})
    vib = []
    sound = []
    gas = []
    obtemp = []
    amtemp = []
    date = []
    distance = []
    
    for js in results:
        vib.append((js['vib']))
        sound.append((js['sound']))
        date.append((js['date']))
        gas.append((js['gas']))
        obtemp.append((js['objectTemp']))
        amtemp.append((js['ambientTemp']))
        distance.append((js['dis']))
    
    datas= ({'vib':vib,'objecttemp':obtemp,'ambientTemp':amtemp,'gas':gas,'sound':sound,'distance':distance})
    print(datas)
    if vib:
        print("asda")
        df = pd.DataFrame(datas)
        plt.figure(figsize=(8,8))
        sns.heatmap(data = df.corr(), annot=True, fmt = '.2f', linewidths=.5, cmap='Blues')
        plt.savefig('/home/gac/smfp/mysite/smartf/static/smartf/co.png')
    
    return render(request,template_name)

def stability(request):
    template_name = 'smartf/stability.html'
    connection = pymongo.MongoClient("113.198.137.140",27017)
    db = connection.exercise
    collection = db.exercise_collection
    results=collection.find({})
    total_tag = []
    date = []
    for js in results:
        total_tag.append((js['total_tag']))
        date.append((js['date']))
    tag_series = {
	'name': 'tag',
	'data': total_tag,
	'color':'blue'
    }
    
    chart = {
	    'title': {'text':'stability'},
	    'xAxis': {'categories':date,'tickInterval': 500},
	    'series': [tag_series]
    }
    dump = json.dumps(chart)
    return render(request,template_name,{'chart':dump})
    




