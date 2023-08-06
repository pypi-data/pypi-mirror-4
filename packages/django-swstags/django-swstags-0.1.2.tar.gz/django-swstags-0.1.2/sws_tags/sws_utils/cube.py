import olap.xmla.xmla as xmla
import time
import simplejson
import types
from suds import WebFault
import memcache
import json
import types
from types import *
import re
import string
from datetime import date, datetime, timedelta
import time
from django.conf import settings
from django.utils.datastructures import SortedDict

from sws_tags.sws_utils.cube_utils import *
from sws_tags.sws_utils.date import *
from sws_tags.sws_utils.__init__ import *



def requestCube(ip_connect,name_bbdd,name_cube,col_cube,med_cube,request_data,ifDate,dimension_filters,database_cube_dict,total_data = False,where_tupla=('Date','Id','Id'),request_date_previous = False,complete_name=False):
    cube=CUBE()
    mdx_class=MDX()
    cube.connect(ip_connect,name_bbdd,settings.CUBE_NAMES)
    exclude_rows={}
    where={}
    part_filter = filterWhere(dimension_filters,request_data,database_cube_dict)
    for i in part_filter:
        where[i]=part_filter[i]
    part_filter={}
    
    if ifDate==True:
        if request_date_previous == False:
            where[where_tupla]=(formatDateCube(request_data ['from_Date']),formatDateCube(request_data ['to_Date']))
        else:
            where[where_tupla]=(formatDateCube(request_data ['from_Date_previous']),formatDateCube(request_data ['to_Date_previous']))          

    if request_data['param_exclude'] == '1': 
        exclude_rows=[{('Hangupcode','Id','Id'):'34'},{('hangupcode','Id','Id'):'41'}]
        col_cube.append(('Hangupcode','Id','Id'))

    if request_data['sidx'] == request_data['sortname'] and request_data['sord'] == 'asc': # value of default
        mdx=mdx_class.mdx(cube,part_rows=col_cube,exclude_rows=exclude_rows,part_columns=med_cube,part_from=name_cube,part_where=where,part_filter=part_filter) #ASC or DESC  ('measure','calls')
   
    elif(col_cube[0][0] == 'Origin'):
        mdx=mdx_class.mdx(cube,part_rows=col_cube,exclude_rows=exclude_rows,part_columns=med_cube,part_from=name_cube,part_where=where,part_filter=part_filter) #ASC or DESC  ('measure','calls')
        try:
            if col_cube[1][0] == 'Origin':
                mdx=mdx_class.mdx(cube,part_rows=col_cube,exclude_rows=exclude_rows,part_columns=med_cube,part_from=name_cube,part_where=where,part_filter=part_filter) #ASC or DESC  ('measure','calls')
        except:
            ERROR = 'ERROR: list our range'

    else:
        sord = request_data['sord'].upper()
        sord = 'B'+sord
        data_order = ''
        part_order={}
        for i in col_cube:

            if i[0] == 'Time' or i[0] == 'Date':
                dato=i[1]
            else:
                dato=i[0]

            if request_data['sidx'] == dato:
                data_order= i

        for i in med_cube:
            if request_data['sidx'] == i[1]:
                data_order= i

        if 'Origin' in data_order:
            part_order={}
        else:
            part_order[data_order]=sord
        
        # print 'PART ORDER',part_order
        mdx=mdx_class.mdx(cube,part_rows=col_cube,exclude_rows=exclude_rows,part_columns=med_cube,part_from='[Scint]',part_where=where,part_order={data_order:sord},part_filter=part_filter) #ASC or DESC  ('measure','calls')

    # print mdx

    res=cube.launch_query(mdx)
      
    grid=Salida_Grid()

    json_data=grid.result_to_json(cube,res,database_cube_dict,False,request_data ['row_num'],request_data['page'],total_data,complete_name)

    return json_data

def requestCubeHighcharts(ip_connect,name_bbdd,name_cube,col_cube,med_cube,request_data,ifDate,dimension_filters,database_cube_dict,total_data = True,where_tupla=('Date','Id','Id'),request_date_previous = False):
    
    cube=CUBE()
    mdx_class=MDX()
    cube.connect(ip_connect,name_bbdd,settings.CUBE_NAMES)
    exclude_rows={}
    where={}
    part_filter = filterWhere(dimension_filters,request_data,database_cube_dict)

    for i in part_filter:
        where[i]=part_filter[i]
    
    if ifDate==True:
        if request_date_previous == False:
            where[where_tupla]=(formatDateCube(request_data['from_Date']),formatDateCube(request_data['to_Date']))
        else:
            where[where_tupla]=(formatDateCube(request_data['from_Date_previous']),formatDateCube(request_data['to_Date_previous']))

    part_filter={}

    if request_data['param_exclude'] == '1': 
        exclude_rows=[{('Hangupcode','Id','Id'):'34'},{('hangupcode','Id','Id'):'41'}]
        col_cube.append(('Hangupcode','Id','Id'))
    else : 
        exclude_rows=[]

    range_rows={}
    if request_data['sidx']!='NULL':
        sord = request_data['sord'].upper()
        data_order = ''
        for i in col_cube:
            if request_data['sidx'] == i[0]:
                data_order= i
        for i in med_cube:
            if request_data['sidx'] == i[1]:
                data_order= i
    else:
        part_order=[]
    new_col_cube=[]
    for i in col_cube:
        new_col_cube.append((i[0],i[1],i[2]))
    col_cube=new_col_cube
        
    med_cube = filterMed(med_cube,request_data['int_asr_acd'])
    
    # mdx=mdx_class.mdx(cube,part_rows=col_cube,range_rows=range_rows,exclude_rows=exclude_rows,part_columns=med_cube,part_from='[Scint]',part_where=where,part_order=part_order,part_filter=part_filter) 
    mdx=mdx_class.mdx(cube,part_rows=col_cube,exclude_rows=exclude_rows,part_columns=med_cube,part_from=name_cube,part_where=where,part_filter=part_filter,request_data=request_data) #ASC or DESC  ('measure','calls')

    # print 'MDX--> ',mdx
    res=cube.launch_query(mdx)
   
    high=Salida_Highcharts()

    types = request_data['representation_type']

    if request_data['button']=='ALL':
        json_data=high.result_to_json(cube,res,types,dimension_v_name='Client',request_data=request_data)
    else:
        json_data=high.result_to_json(cube,res,types,dimension_v_name=request_data['button'],exclude=exclude_rows,request_data=request_data)

    return json_data

def requestCubeFilters(ip_connect,name_bbdd,name_cube,col_cube,med_cube,request_data,ifDate,dimension_filters,database_cube_dict=False,where_tupla=('Date','Id','Id')):
    

    # dimension_filters_new = []
    # for d in dimension_filters:
    #     if d[0].find('_')>0:
    #         index = d[0].find('_')
    #         dimension_filters_new.append((d[0][0:index],d[1],d[2]))
    #     else:
    #         dimension_filters_new.append((d[0],d[1],d[2]))

    # dimension_filters = dimension_filters_new

    cube=CUBE()
    mdx_class=MDX()
    cube.connect(ip_connect,name_bbdd,settings.CUBE_NAMES)
    
    where = filterWhere(dimension_filters,request_data,database_cube_dict)
    
    exclude_rows={}
    
    if request_data[request_data['types']]!='NULL':
        key=(str(request_data['types']),'Id','Id')
        col_cube.append(key)

        exclude_rows[key]=where[key]
        where_aux={}
        for i in where:
            if i!=key:
                where_aux[i]=where[i]
        where=where_aux
        exclude_rows=[exclude_rows]

    else:
        exclude_rows={}

    if ifDate==True:
        where[('Date','Id','Id')]=(formatDateCubeDate(request_data ['from_Date']),formatDateCubeDate(request_data ['to_Date']))
   

    mdx=mdx_class.mdx(cube,part_rows=col_cube,exclude_rows=exclude_rows,part_columns=med_cube,part_from=name_cube,part_where=where)

    grid=Salida_Grid()
    
    dimension_filter=filterDimensionCube(dimension_filters,request_data['types'])
    
    if dimension_filter[0][0].find('_')>0:  # especial case two atributes same dimension, delete charts after '_'
        dimension_filter_new = []
        index = dimension_filter[0][0].find('_')
        dimension_filter_new.append((dimension_filter[0][0][0:index],dimension_filter[0][1],dimension_filter[0][2]))
        dimension_filter = dimension_filter_new

    filters_cube = grid.filters(mdx,cube,database_cube_dict,dimension_filter,exclude_rows)

    json_data = json_encode({
        'more':False,
        'results': filters_cube
        })

    return json_data




def filterColCube(col_cube,col_group_by,col_and_by):
    col_cube_new = []
    if col_group_by!='ALL':
        for c in col_cube:
            if c[0]== col_group_by:
                col_cube_new.append((c[0],c[1],c[2]))
            if c[0]=='Date'and (c[1]==col_group_by or c[1]==col_and_by) :
                col_cube_new.append((c[0],c[1],c[2]))
            if c[0] == col_and_by and col_and_by != col_group_by:
                col_cube_new.append(c[0:3])
    else:
        col_cube_new.append(('Client', 'Client', 'All'))
    col_cube=[]
    for c in col_cube_new:
        index = c[0].find('_')
        if index>0:
            col_cube.append((c[0][0:index],c[1],c[2]))
        else:
            col_cube.append((c[0],c[1],c[2]))

    return col_cube


def adjustementData(dict_higcharts,value_adjustement):

    list_index = []
    i=0

    for data in dict_higcharts['v_name']:
        for name in value_adjustement:
            if data.find(name[0]) > 0:
                list_index.append((data,i,name[1]))
                i = i+1

    list_data = []
    list_aux = []

    j = 0
    for data in dict_higcharts['v_data']:

        for i in range(0,len(data)):
            list_aux.append(data[i]*list_index[j][2])
        j = j+1
        list_data.append(list_aux)
        list_aux = []


    dict_higcharts['v_data'] = list_data

    return dict_higcharts


#return tuple with column and id of the dimemsion selected
def filterDimensionCube(dimension_filters,dimension):
    new_dimension_filters=[]
    for d in dimension_filters:
        if d[0]== dimension:
            new_dimension_filters.append(d[0:3])
    return new_dimension_filters



def filterWhere(filters,request_data,database_cube_dict): 
    
    where={}
 
    for f in filters:
   
        if f[0]!='calldate':
       
            if f[0] in request_data:
                if  request_data[f[0]]!='NULL':
                    where[(f[0],'Id','Id')]=request_data[f[0]]
          
  
    return where   

def filterDataCube(filters,request,database_cube_dict): 
    where={}
    for f in filters:
        if f[0]!='calldate':
            if f[0] in request.GET:
                if  request.GET[f[0]]!='NULL':
                    where[(f[0],'id')]=request.GET[f[0]]
    return where

def filterMed(med_cube,select_med):

    if select_med.lower() == 'asr':
        med_cube=[('Measures','Calls'),('Measures','ASR')]
        return med_cube
    elif select_med.lower() == 'acd' :
        med_cube=[('Measures','Calls'),('Measures','ACD')]
        return med_cube
    else:
        return med_cube


def atributeAdjustement(json_data,col_cube,request_data):
    json_data = json_data.replace('Date*','')
    
    #especial case when the query have two atributtes of the same dimension
    if request_data['group_by'].find('_')>0 :
        group_by_plus= request_data['group_by'].replace('_','*')
        json_data = json_data.replace(group_by_plus,request_data['group_by'])

    try:
        if request_data['and_by'].find('_')>0:
            and_by_plus = request_data['and_by'].replace('_','*')
            json_data = json_data.replace(and_by_plus,request_data['and_by'])
    except:
        ERROR = 'ERROR: non request_data[and_by] '



    for name in col_cube:
        json_data = json_data.replace('*'+name[1]+'"','"')
   
    return json_data


def obtainMargin(json_data):
    json_data_dict = json.loads(json_data)
    
    for data in json_data_dict['rows']:
        if float(data['Total Income']) != 0:
            benefit = float(data['Total Income']) - float(data['Total Cost'])
            margin = benefit / float(data['Total Income']) * 100
            dif = random.randrange(0,9)
            data['Margin'] = dif
        else:
            data['Margin'] = 0
    json_data = json.dumps(json_data_dict)

    return json_data


def orderDataCube(request,json_data):
    json_data_dict = json.loads(json_data)
    name_order = request['sidx']
    if request['sord'] == 'asc':
        rev = False
    else:
        rev = True
    sorted_json = sorted(json_data_dict['rows'], key=lambda d: d[name_order],reverse = rev)
    json_data_dict['rows'] = sorted_json
    json_data_dict = json.dumps(json_data_dict)

    return json_data_dict


def accuratelyAdjustment(json_data,med_cube_prec):
    if len(med_cube_prec[0])==3:
        ind = 0
    else:
        ind = 1

    json_data_dict = json.loads(json_data)
    new_list_data = []
    for i in range(len(json_data_dict['rows'])):
        new_dict = {}
        for k,v in json_data_dict['rows'][i].items():
            for m in med_cube_prec:


                if m[ind] == k:
                    v = str(v)
                    if v.find('.')>0:
                        index = v.find('.');
                        if m[ind+1] != 0:
                            v = v[0:index+1+m[ind+1]]
                        else:
                            v = v[0:index]
                    try:
                        v = v + m[ind+2]
                    except:
                        error = 'ERROR: in add type data for measure cube'

            new_dict[k] = v
        new_list_data.append(new_dict)
    json_data_dict['rows'] = new_list_data
    json_data = json.dumps(json_data_dict)  

    # else:

    #     for i in range(0,len(queryset_detail)):
    #         for j in field_query_detail:
    #             # print j[0]
    #             data = str(queryset_detail[i][j[0]])
    #             if data.find('.')>0:
    #                 index = data.find('.')
    #                 queryset_detail[i][j[0]] = data[0:index+1+j[1]]+j[2]



    return json_data



def getTableDict(json_data, title_dict, value_group_by_data):
    # table_dict = SortedDict({'titles_table':title_dict})
    json_data_dict = json.loads(json_data)  
    data = json_data_dict['rows']

    first_element = True
    for key,value in title_dict.items():
        if first_element == True:
            title_dict.pop(key)
            title_dict.insert(0,value_group_by_data,value_group_by_data.capitalize())
            first_element = False

    table_dict = SortedDict({'titles_table':title_dict})
    cont = 0
    series_dict = SortedDict()
    for d in data:
        exists = False
        for key,value in series_dict.items():
            if value_group_by_data == 'ALL':
                value_group_by_data = 'Client'
            if(value[value_group_by_data] == d[value_group_by_data]):
                row_dict = SortedDict()
                for v in value:
                    element = series_dict.get(key)
                    if v == value_group_by_data:
                        element_value = d[v]
                    elif v == 'ASR':
                        # try:
                        #     element_value = float(element[v]) + float(d[v])
                        #     element_value = str(round(element_value,3))
                        # except:
                        element_value = str(float(element[v]) + float(d[v]))

                    elif v == 'ACD':
                        element_value = str(float(element[v]) + float(d[v]))
                    elif v == 'answer_calls':

                        # element_value = element[v]
                        if value['ASR'] == '0.0' or value['Calls'] == '0.0':
                            element_value = '0'
                        else:
                            if float (value['Calls']) != 0:
                                element_value = str(float(value['ASR']) / float(value['Calls'])) 
                            else:
                                element_value = '0';
                    elif v == 'calls':
                        element_value = str(int(element[v]) + int(d[v]))
                    
                    row_dict[v] = element_value
                
                series_dict[serie] = row_dict
                exists = True

        if not(exists):
            cont = cont + 1
            serie = 'serie' + str(cont)

            row_dict = SortedDict()
            for e in title_dict.keys():
                if e == 'answer_calls':
                    row_dict[e] = '0'
                else:
                    if e == 'ALL':
                        e = 'Client'


                    row_dict[e] = d[e]
            series_dict[serie] = row_dict
    
    table_dict['series'] = series_dict

    table_dict_result = SortedDict()
    for key,value in table_dict.items():
        values_list = []
        series_dict = SortedDict()
        for name,val in value.items():
            if key == 'series':
                values_list = []
                for k,v in val.items():
                    v = str(v)
                    if v.find('.')>0:
                        i = v.find('.');
                        v = v[0:i+3]
                    values_list.append(v)
                series_dict[name] = values_list
            elif key == 'titles_table':
                values_list.append(val)
        if key == 'series':
            table_dict_result[key] = series_dict
        elif key == 'titles_table':
            table_dict_result[key] = values_list

    return table_dict_result
