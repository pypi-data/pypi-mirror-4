import olap.xmla.xmla as xmla
import time
import simplejson
import types
from suds import WebFault
import memcache
import re
import random
import math
from django.conf import settings



# Nuevo metodo perteneciente a la clase XMLASource

def new_execute(self, command, dimformat="Multidimensional",axisFormat="ClusterFormat", **kwargs):

    """         
    *PARAMETERS* 

-A string with the mdx to execute 

    *USE*
- Is only used from CUBE.launch_query()

    *RETURN* 
- Return a xml file with the result of the mdx
    """
        
    if isinstance(command, types.StringTypes):
        command = {"Statement":command}
    props = {"Format":dimformat, "AxisFormat":axisFormat}
    props.update(kwargs)
    pl = {"PropertyList":props}
    try:
        medio_root =self.client.service.Execute(command, pl)    
        #root=medio_root.ExecuteResponse["return"].root
        #return TupleFormatReader(root)
        return medio_root
    except WebFault, fault:
        raise XMLAException(fault.message, listify(fault.fault))

class CUBE:

    """          
    *USE*
There are three parameters which are initialized when the method CUBE.connect() is used:
    -dimensiones
    -medidas
    -connect

    
    """

    dimensiones= {}
    medidas={}
    connection=''
    name='PosgrePago'


    
    # Conectar a un cubo pasando la direccion del mismo 
    def connect(self,ip,bbdd=[],cubes=[]):
        """         
    *PARAMETERS* 

-A string with the location of OLAP service like :   location="http://192.168.2.82/OLAP/msmdpump.dll"

    *USE*

>>> c=cube.CUBE()
>>> location="http://192.168.2.82/OLAP/msmdpump.dll" 
>>> c.connect(location=location)

    *RETURN* 
An object like <olap.xmla.xmla.XMLASource object at 0xa7ae5ac> : it`s the connection with OLAP service
        """
        "http://192.168.2.111/OLAP/msmdpump.dll"
        location="http://"+ip+"/OLAP/msmdpump.dll"
        def addDimension_Medidas(ide,value):
            if mc.get(ide) == None:
                return mc.set(ide,value,3200)
            return False
        def getDimension_Medidas(ide):
            value = mc.get(ide)
            return value[0],value[1]
        def isAdded(ide):
            return not (mc.get(ide) == None)

        t6=time.time()
        mc = memcache.Client([settings.MEMCACHE_IP], debug=0)

        p = xmla.XMLAProvider()
       
        self.connection = p.connect(location=location)
        
        t1=time.time()

        if not isAdded('dimYmed'):

            try:

                t2=time.time()
                # print '**************** CUBES',cubes
                # cubes=['Scint','ChannelUsage']
                # print '**************** CUBES',cubes
                self.medidas=self.__getMedidas(bbdd,cubes) 
                self.dimensiones=self.__getDimensiones(bbdd,cubes)

                value=[]
                value.append(self.medidas)
                value.append(self.dimensiones)
                addDimension_Medidas('dimYmed',value)
            except Exception, e:
                swslog('error','wrong location',e)
        else:

            self.medidas,self.dimensiones=getDimension_Medidas('dimYmed')

        return self.connection

    def getNamesBBDD (self):
        """         
    *PARAMETERS* 

-An object like <olap.xmla.xmla.XMLASource object at 0xa7ae5ac> :   get from CUBE.connect()

    *USE*

>>> c=cube.CUBE()
>>> location="http://192.168.2.82/OLAP/msmdpump.dll" 
>>> connect=c.connect(location=location)
>>> c.getNameBBDD()
>>> [u'test_cdr']


    *RETURN* 
An object like [u'test_cdr'] : it`s a list with the names of the BBDDs in that connection
        """
        row=[]
        try:
            catalogs=self.connection.getCatalogs()
        except Exception, e:
            swslog('repeat the connect() whith a goog location')
            return 'repeat the connect() whith a good location'
        #colocar de nuevo la option a false si no no deja acceder
        for i in catalogs:
            row.append(i.getUniqueName())
        return row 
    def __getDimensiones(self,bbdd=['PosgrePago'],cubes=['Scint']):
        dimensiones={}
        for catalogo in self.connection.getCatalogs():
          
            if catalogo.getUniqueName() in bbdd:
                for Cube in catalogo.getCubes():
                        if Cube.getUniqueName() in cubes:
                            for dim in Cube.getDimensions():
                                for jerar in dim.getHierarchies():
                                    for level in jerar.getLevels():
                                        name=level.getUniqueName()
                                        first_name=name[name.find('[')+1:name.find(']')]
                                        name_aux=name[name.find(']')+1:]
                                        second_name=name_aux[name_aux.find('[')+1:name_aux.find(']')]
                                        name_aux=name_aux[name_aux.find(']')+1:]
                                        third_name=name_aux[name_aux.find('[')+1:name_aux.find(']')]
                                        third_name=third_name.replace('(','').replace(')','')
                                        dimensiones[(first_name,second_name,third_name)]=level.getUniqueName()
        return dimensiones

    def name_dimension_replace(self,dict_replace):

        dimensiones=self.dimensiones

    def name_dimension(self,axis,complete_name):
        """         
    *PARAMETERS* 

-An list which has in each position an illegible name of dimension 


    *USE*

>>> axis=[[Tiempo 1].[Fecha].[Fecha],[Clients Reseller].[Reseller].[Reseller]]
>>> cuve=cube.name_dimension
>>> axis=cuve.name_dimension(axis)
>>> axis
>>> ['tiempo 1','reseller']


    *RETURN* 
-An list which has in each position an legible name of dimension 
        """ 
            
        dimensiones =self.dimensiones


        if dimensiones:
            nombres=[]            
            for dimension in axis:
                for dim in dimensiones:
                    if dimensiones[dim]==dimension: 
                       
                        if not complete_name:
                             
                            dim=str(dim[0])
                         
                            position_coma=dim.find(',')
                            
                            nombres.append(dim)
                        else:
                            dim=str(dim[0])+'*'+str(dim[1])
                          
                            position_coma=dim.find(',')
                           
                            nombres.append(dim)


            columnas=sorted(list(set(nombres)))
            return columnas
        else:
            return 'cube has not dimensions or it is not good connect'        
    def __getMedidas(self,bbdd=['PosgrePago'],cubes=['Scint']):
        medidas={}
        for catalogo in self.connection.getCatalogs():

            if catalogo.getUniqueName() in bbdd:
                for Cube in catalogo.getCubes():
                        if Cube.getUniqueName() in cubes:
                            for medida in Cube.getMeasures():
                               
                                name=medida.getUniqueName()
                                first_name=name[name.find('[')+1:name.find(']')]
                                name_aux=name[name.find(']')+1:]
                                second_name=name_aux[name_aux.find('[')+1:name_aux.find(']')]
                                name_aux=name_aux[name_aux.find(']')+1:]
                                medidas[(first_name,second_name)]=name
        return medidas

    def set_name_BBDD_to_use(self,name):
        """         
    *PARAMETERS* 

-A string which is the name of a BBDD where is our cube which you want connect


    *USE*

>>> name = '[Stoneworksolutions Dev]'
>>> cuve=cube.name_dimension
>>> cuve.set_name_BBDD_to_use(name)


    *RETURN* 
- Nothing
        """
        self.name=name

    def get_name_BBDD_used(self,name):
        """         
    *PARAMETERS* 

-A string which is the name of a BBDD where is our cube which you want connect


    *USE*

>>> name = '[Stoneworksolutions Dev]'
>>> cuve=cube.name_dimension
>>> cuve.set_name_BBDD_to_use(name)


    *RETURN* 
- Nothing
        """
        return self.name
        

    # Ejecutar una mdx contra el cubo del cual le pasamos la conexion y la mdx a ejecutar
    def launch_query(self,mdx=None):
        """         
    *PARAMETERS* 

-An object <olap.xmla.xmla.XMLASource object at 0xa7ae5ac> :   get from CUBE.connect() or CUBE.connect (after do CUBE.connect())
-A string which is a mdx
-And a string which is the name of the cube which we want make the query

    *USE*

>>> c=cube.CUBE()
>>> name="cube_name"
>>> mdx="select non empty ([Clients Client].[Client].[Client])  on rows,  {[Measures].[Calls]}  on columns from [stoneworksolutions dev]"
>>> result=c.launch_query(mdx,name)

    *RETURN* 
A xml object which has the result to make the query 

        """
        connexion=self.connection
 
        # if 'tiempo' in mdx.lower():
        #     mdx_class=MDX()
        #     mdx=mdx_class.tiempo_final(mdx)

        # mdx=mdx.upper()    
        connexion.client.set_options(retxml=True) 
        connexion.new = new_execute

        # Realiza la query al cubo y devuelve los resultados que se guardan en result
        result = connexion.new(connexion,mdx,Catalog=self.name)
        connexion.client.set_options(retxml=False)
        return result

class xml_result:
    """          
    *USE*
    This class is used to work with the xml result from launch a query on the cube
   
    """
   
    # Esta clase nos devuelve todos los valores resultantes pasandole el xml que se obtiene al realizar la consulta es solo de uso privado

    def getValues(self,xml1):

        """         
    *PARAMETERS* 

    -A string format in xml with the result from launch a query on the cube
    *USE*

    >>> c=cube.CUBE()
    >>> location="http://192.168.2.82/OLAP/msmdpump.dll" 
    >>> c.connect(location=location)
    >>> mdx =  "select NON EMPTY {[Clients Client].[Client].[Client]} on rows,{[Measures].[Calls],[Measures].[Minutes]} on columns from [Stoneworksolutions Dev] where [Clients Reseller].[Reseller].&[Sigotel]"
    >>> xml=c.launch_query(c.connect,mdx)
    >>> xml_class=cube.xml_result()
    >>> axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas = xml_result.getValues(xml)

        *RETURN* 
    An object like <olap.xmla.xmla.XMLASource object at 0xa7ae5ac> : it`s the connection with OLAP service
        """

        #axes = xml.getElementsByTagName('Axes')[0]
        NS = '{urn:schemas-microsoft-com:xml-analysis:mddataset}'
        import cElementTree
        xml = cElementTree.fromstring(xml1)
        try:
            axes = xml.findall('.//{0}Axes'.format(NS))[0]
        except Exception, e:
            swslog('error','findall',e) 

            error = xml1[xml1.find('<faultstring>')+13:xml1.find('</faultstring>')]
            axis_x_names=''
            axis_y_names=''
            axis_x_values=[]
            axis_y_values=[]
            numero_filas=0
            numero_dimensiones=0
            numero_celdas=0
            numero_medidas=0
            return axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas  
        axis_y= axes.getchildren()[1]


        numero_filas = len(axis_y.getchildren()[0].getchildren())

        if numero_filas == 0:
            axis_x_names=''
            axis_y_names=''
            axis_x_values=[]
            axis_y_values=[]
            numero_filas=0
            numero_dimensiones=0
            numero_celdas=0
            numero_medidas=0
            return axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas  
        numero_dimensiones = len(axis_y.getchildren()[0].getchildren()[0].getchildren())

        
        axis_y_names = [axis_y.findall('.//{0}Member'.format(NS))[i].findall('.//{0}LName'.format(NS))[0].text for i in range(0,numero_dimensiones) ]
        #axis_y = [i.childNodes[0].wholeText  for i in axis_y.getElementsByTagName('Caption')]
        
        axis_y_values = [i.text for i in axis_y.findall('.//{0}Caption'.format(NS))]
        
        #axis_x= axes.childNodes[0]
        axis_x= axes.getchildren()[0]
        #axis_x = [i.childNodes[0].wholeText  for i in axis_x.getElementsByTagName('Caption')]
        axis_x_names = [i.text for i in axis_x.findall('.//{0}Caption'.format(NS))]

        numero_medidas = len(axis_x_names)

        #axis_x_values
        
        axis_x_values = xml.findall('.//{0}CellData//{0}Value'.format(NS))
        axis_x_values = [i.text for i in axis_x_values]
        numero_celdas=len(axis_x_values)
        

        return (axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas)

class Salida_Highcharts:
    # def __init__(self,request_data):
    """          
    *USE*
This class is used to get  a string format in json for a HighChart
   
    """

    def result_to_json(self,cube,result,types={},xAxis=['Time','Date'],dimension_v_name='client',exclude=[],request_data={},complete_name=False):
        """         
    *PARAMETERS*

-The cube object which has been used to make the query
-A xml object :   get from CUBE.launch_query() 
-A list with types to the dimensions : types=['spline','column']


    *USE*

>>> cu=cube.CUBE()
>>> connect=c.connect()
>>> name="cube_name"
>>> mdx="select non empty ([Clients Client].[Client].[Client])  on rows,  {[Measures].[Calls]}  on columns from [stoneworksolutions dev]"
>>> xml=c.launch_query(mdx,name)
>>> chart=cube.Salida_Highcharts()
>>> json=chart.xml_to_json(xml,cu)

    *RETURN* 
- A string in json format 
        """
        import time
        t0 = time.time()
        
        t1 = time.time()
        
        xml_class=xml_result()

        # concordancia_types={'spline':0,'column':1,'line':2,'areaspline':3}
      
        types2={}
        for i in types:
            types2[i.upper()]=types[i]

        types=types2

        c={}
        for i in exclude:
            c[i.keys()[0]]=0



        axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas = xml_class.getValues(result)
        axis_y_names = cube.name_dimension(axis_y_names,complete_name)

        # print 'axis_ynames',axis_y_names
        # print 'axis_y_values',axis_y_values
        value_type=[]
        for i in range(0, len(axis_y_values)):
            value =  axis_y_values[i]
            name = axis_y_names[int(math.fmod(i,len(axis_y_names)))]
            if name == 'Date' and  len(value) ==1:
                value = '0'+value
            # print name,'->',value
            value_type.append((name,value))

        new_date = []

        dim = ''
        for d in axis_y_names:
            if d != 'Time' and d != 'Date':
                dim = d

        if len(axis_y_names) == 3:
            for i in range(0,len(value_type)):
                # print 'V->',value_type[i]
                if value_type[i][0] == 'Date':
                    part_Date = value_type[i][1]
                    part_Date = part_Date[0:4]+'-'+part_Date[4:6]+'-'+part_Date[6:8]

                    try: 
                        if value_type[i+1][0] == 'Time':
                            part_Time = value_type[i+1][1]
                        elif value_type[i+2][0] == 'Time':
                            part_Time = value_type[i+2][1]
                    except Exception, e:
                        part_Time = '00:00'
                        swslog('error','index out of range',e)
                        # print error
                        # print 'VALUETYPE',value_type[i]
                    
                    date = part_Date +' '+ part_Time
                    new_date.append(date)
                elif value_type[i][0] ==dim:
                    new_date.append(value_type[i][1])

            axis_y_values = new_date

            axis_y_names.remove('Time')
            numero_dimensiones = 2

        elif len(axis_y_names) == 2:
            for i in range(0,len(value_type)):
                if value_type[i][0] == 'Date':  
                    part_Date = value_type[i][1]
                    part_Date = part_Date[0:4]+'-'+part_Date[4:6]+'-'+part_Date[6:8]
                    new_date.append(part_Date) 

                elif value_type[i][0] ==dim:
                    new_date.append(value_type[i][1])
            axis_y_values = new_date


        if c:
            for i in c.keys():
                axis_y_names.remove(i[0])
            position=0
            for i in range(0,len(axis_y_names)):

                if axis_y_names[i]==c.keys()[0][0]:
                    position=i
            part_Dates_y=[]
            for i in range(0,len(axis_y_values)):
                if i%numero_dimensiones != position:
                    part_Dates_y.append(axis_y_values[i])                


            axis_y_values=part_Dates_y
            numero_dimensiones=numero_dimensiones - len(c.keys())

        
        position_dimension_v_name=0

        for i in range(0,len(axis_y_names)):
            if axis_y_names[i] == xAxis[0] :
                position_dimension_v_name=i
                xAxis=xAxis[0]
            elif axis_y_names[i] == xAxis[1]:
                position_dimension_v_name=i
                xAxis=xAxis[1]
        ##GENERALIZAR 
        todo={}


        v_xAxis=[axis_y_values[i*numero_dimensiones+position_dimension_v_name] for i in range(0,len(axis_y_values)/2)]
      
        v_xAxis=sorted(list(set(v_xAxis)))
                   
        
        for j in range(0,numero_dimensiones):

            todo[axis_y_names[j]]=[axis_y_values[i*numero_dimensiones+j] for i in range(0,len(axis_y_values)/numero_dimensiones)]
            todo[axis_y_names[j]]=sorted(list(set(todo[axis_y_names[j]])))

        if todo:
            new_xAxis = []
            for r in todo[xAxis]:
                if len(r)==1:
                    r = '0'+r
                new_xAxis.append(r)



            v_xAxis=new_xAxis

            v_xAxis=sorted(new_xAxis)

            value_xAxis=todo[dimension_v_name]
           

            
            v_name=[]
            
            for i in axis_x_names:
                for j in value_xAxis:
                    v_name.append(str(j)+i.upper())
            
            v_name= sorted(list(set(v_name)))
            v_type=[]
            v_yAxis=[]
           
            cont = 0
            for i in v_name:
                for j in types:  
                    
                    if j in i:
                        v_type.append(types[j])
                        v_yAxis.append(cont)
                        if cont == 0:
                            cont = 1
                        else:
                            cont = 0
           

            index1=0
            index2=numero_filas
            rows=[]
            for fila in range(index1,index2):
                    row={}
                    for i in axis_y_names:
                        row[i]=''
                    for i in axis_x_names:
                        row[i.lower().replace(' ','_')]=''

                    for measure in range(0,numero_medidas):
                        row[axis_x_names[measure].lower().replace(' ','_')] = str(axis_x_values[(fila*numero_medidas)+measure])
                        
                    for dimension in range(0,numero_dimensiones):

                        if isinstance(axis_y_values[(fila*numero_dimensiones)+dimension],unicode):
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension].encode('utf-8'))
                        else:
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension])
                    rows.append(row)
            v_data={}
            for i in v_name:
                v_data[i]=[]

            for row in rows:
                if row[dimension_v_name] in  str(v_name):
                    for i in axis_x_names:
                        v_data[str(row[dimension_v_name])+i.upper()].append(float(row[i.lower()]))
                
            
            ## Para rellenar cada fila hasta el maximo 
            v_data2=[]
            mayor=0
           
            for i in  sorted(list(set(v_data.keys()))):
                if len(v_data[i])>mayor:
                    mayor=len(v_data[i])
                v_data2.append(v_data[i])

            for i in v_data2:
                while len(i)<mayor:
                    i.append(0)
            v_data= v_data2

            dict_higcharts={}
            dict_higcharts['v_data']=v_data
            dict_higcharts['v_name']=v_name
            dict_higcharts['v_type']=v_type
            dict_higcharts['v_yAxis']=v_yAxis
            dict_higcharts['v_xAxis']=v_xAxis


            
            return dict_higcharts
        else:
            dict_higcharts={}
            dict_higcharts['v_data']=[]
            dict_higcharts['v_name']=[]
            dict_higcharts['v_type']=[]
            dict_higcharts['v_yAxis']=[]
            dict_higcharts['v_xAxis']=[]
            return dict_higcharts
      


class Salida_Grid:

    """          
    *USE*
This class is used to get the filter and a string format in json for a grid
   
    """

    # Formatea los resultados obtenidos ejecutar una mdx en el paso anterior a json
    def result_to_json(self,cube,result,database_cube_dict=[],isfilter=False,rowNum=200,page=0,total=False,complete_name=False):
        """         
    *PARAMETERS* 

-A xml object :   get from CUBE.launch_query() 
-The cube object which has been used to make the query

    *USE*

>>> cu=cube.CUBE()
>>> connect=c.connect()
>>> name="cube_name"
>>> mdx="select non empty ([Clients Client].[Client].[Client])  on rows,  {[Measures].[Calls]}  on columns from [stoneworksolutions dev]"
>>> xml=c.launch_query(mdx,name)
>>> grid=cube.Salida_Grid()
>>> json=grid.xml_to_json(xml,cu)

    *RETURN* 
A string in json format 
        """
        
        
        import time
        t0 = time.time()
        
        t1 = time.time()

        #comprobar si el result es bueno o a lanzado algun fallo
       
        xml_class=xml_result()
        #axis_x,axis_x_names,axis_y,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas = self.__getValues(xml)
        axis_x_names,axis_y_names,axis_x_values,axis_y_values,numero_filas,numero_dimensiones,numero_celdas,numero_medidas = xml_class.getValues(result)
        
        ##axis_x_names al hacer el json salen duplicados y uno de ellos vacio 
        ##axis_ynames al hacer el json deberia de salir el nombre mejor 
       
        
        t2 = time.time()

        
        t3=time.time()
        axis_y_names = cube.name_dimension(axis_y_names,complete_name)

        if isfilter:
            list_dict = []
            list_dict.append({'text':'----','id':'NULL'})

            for i in range(0,len(axis_y_values)/2):

                list_dict.append({'id': str(axis_y_values[(i*2)+1]),'text':axis_y_values[i*2]})



            return list_dict
        else:
            t4=time.time()

            data = {}
            rows = []

            if page==0:
                data['total']=numero_filas
            else:
                numero_filas=numero_filas+0.0
                total = numero_filas / rowNum
                if total.is_integer():
                    data['total'] = total
                else:
                    if int(str(total)[str(total).find('.')+1])>5:
                        data['total']=int(str(total)[str(total).find('.')-1])+1
                    else:
                        data['total']=int(str(total)[str(total).find('.')-1])

            numero_filas = int(numero_filas)
            data['records'] = numero_filas

            if page==0:
                index1=0
                index2=numero_filas
            else:
                page = int(page)
                index1 = int((page-1) * rowNum)
                index2 = int(page*rowNum)
                if numero_filas<index2:
                    index2 = numero_filas
            if total:
                totales={}
                for i in axis_x_names:
                    # totales[i.replace(' ','_')]=0
                    totales[i]=0
              

            cont_ACD_NAN=0
            for fila in range(0,numero_filas):


                row={}
                for i in axis_y_names:
                    row[i]=''
                for i in axis_x_names:
                    # row[i.replace(' ','_')]=''
                    row[i]=''

                
                for measure in range(0,numero_medidas):

                    # row[axis_x_names[measure].replace(' ','_')] = str(axis_x_values[(fila*numero_medidas)+measure])
                    if fila < index2 and fila >= index1:
                        if axis_x_values[(fila*numero_medidas)+measure]!='NaN':
                            row[axis_x_names[measure]] = str(round(float(axis_x_values[(fila*numero_medidas)+measure]),4))
                        else:
                            row[axis_x_names[measure]] = '0'

                    if total:

                        # totales[axis_x_names[measure].replace(' ','_')]+=float(axis_x_values[(fila*numero_medidas)+measure])

                        # print 'aa',axis_x_values[(fila*numero_medidas)+measure]
                        # print axis_x_names[measure]

                        if axis_x_values[(fila*numero_medidas)+measure] != 'NaN':
                            totales[axis_x_names[measure]]+=round(float(axis_x_values[(fila*numero_medidas)+measure]),4)
                        else:
                            cont_ACD_NAN = cont_ACD_NAN +1

                        # print measure,totales[axis_x_names[measure]]

                # for r in totales:
                #     print '---->',r

                if fila < index2 and fila >= index1:

                    for dimension in range(0,numero_dimensiones):
                        if database_cube_dict:
                            for key,value in database_cube_dict.items():
                                if axis_y_names[dimension] == key:
                                    axis_y_names[dimension] = value



                        #### TODO_MAS EL KEY DE DATABASA_CUBE DICT VIENE CON UNA COMA AL PRINCIPIO
                        axis_y_names[dimension]=axis_y_names[dimension].lstrip("'")
                        if isinstance(axis_y_values[(fila*numero_dimensiones)+dimension],unicode):
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension].encode('utf-8'))
                        else:
                            row[axis_y_names[dimension]] = str(axis_y_values[(fila*numero_dimensiones)+dimension])
                    rows.append(row)
            
            # print 'totales',totales
            if total:
                json_data_new={}
                for k,v in totales.items():
                    v=str(v)
                    p = re.compile('\d+')
                    c= p.findall(v)
                    if len(c)>1:
                        v= str(c[0])+'.'+str(c[1])[0:2]
                    
                    if (k.find('Avg')>0) or (k == 'ASR') or (k=='ACD'):
                        try:
                            if (k!='ACD'):
                                v = str(float(v)/len(rows))
                            else:
                                div = len(rows)-cont_ACD_NAN
                                v = str(float(v)/div)

                            v = v[0:6] + '~'

                        except Exception, e:
                            swslog('error','div for 0',e)

                    json_data_new[k]=v
                data['footerData']=json_data_new
            data['rows']=rows
            data['page'] = page
            obj=simplejson.dumps(data,sort_keys=True, indent=4)
    #############################
            return obj
        


    # Obtenemos los nombres de las dimensiones de modo legible, pasandole un array de valores los cuales se usan en la mdx
    



    # Pasando una query obtenemos los filtros necesarios para esta, uno a uno 
    def filters(self,query,cube,database_cube_dict,dimensiones=[],exclude_rows=[]):

        """         
    *PARAMETERS* 

-A string which is a mdx
-The cube object which has been used 
- Optional: a list of dimensions which calculate the mdx to get the filters if it isnt used the filters will be calculated with all filters

    *USE*

>>> cu=cube.CUBE()
>>> connect=c.connect() 
>>> name='test_cdr'
>>> cu.set_name_cube_using(name)
>>> mdx="select non empty ([Clients Client].[Client].[Client])  on rows,  {[Measures].[Calls]}  on columns from [stoneworksolutions dev]"
>>> filters=c.filters(connect,mdx)


    *RETURN* 
A dict key:value.The key is the name of the dimension used to make the query and the value is a string in json format which is the result to make the query of that dimension
        """

        t1=time.time()
        if not dimensiones:
            dimensiones= cube.dimensiones
       

        cmd=''
        row=''
        p=0

        for dim in dimensiones:
                row=self.filter(query,cube,dim,database_cube_dict,exclude_rows)
        return row
        
    def filter(self,query,cube,dimension,database_cube_dict=[],exclude_rows=[]):

        """         
    *PARAMETERS* 

-A string which is a mdx
-The cube object which has been used 
-The dimension which is used to make the filter

    *USE*

>>> cuve=cube.CUBE()
>>> cuve.connect()
>>> salida=cube.Salida_Grid()
>>> mdx=cube.MDX()
>>> mdx="select non empty ([Clients Client].[Client].[Client])  on rows,  {[Measures].[Calls]}  on columns from [stoneworksolutions dev]"
>>> dimension=('client','client')
>>> salida.filter(mdx,cuve,dimension)


    *RETURN* 
A string format in json which has the result for one filter
        """
        mdx_class=MDX()
        query_without_select,measure=mdx_class.without_select(query)
        
        
        json=''
        on_rows=[]

        on_rows.append(dimension)
        dimension_id=(dimension[0],'Id','Id')
        on_rows.append(dimension_id)
        select=mdx_class.select_for_filter(cube,on_rows=on_rows,medida=measure,exclude_rows=exclude_rows)
        query =select + query_without_select

        res=cube.launch_query(mdx=query.upper())
        json=self.result_to_json(cube,res,database_cube_dict,isfilter=True)
        return json
class MDX:

    """          
    *USE*
This class is used to create mdx and work with then
   
    """

    # Esta funcion decuelve la misma query que se le pasa como parametro pero sin la parte select de la misma
    def without_select(self,query):
        """         
    *PARAMETERS* 

-A string which is a mdx : 
 

    *USE*

>>> mdx=cube.MDX()
>>> mdx="select non empty ([Clients Client].[Client].[Client])  on rows,  {[Measures].[Calls]}  on columns from [stoneworksolutions dev]"
>>> mdx.without_select(mdx)
>>> ',  {[Measures].[Calls]}  on columns from [stoneworksolutions dev]''

    *RETURN* 
A string which is a mdx without on rows in select
        """
        query=query.lower()
        inicio=query.find('rows')+4
        medida=query[inicio:]
        inicio=medida.find('[')
        medida=medida[inicio:]
        final = medida.find('.')
        medida_aux=medida[final:]
        final+=medida_aux.find(']')
        medida=medida[:final+1]
        position_rows=query.find('from')
        query=query[position_rows:]
        return query,medida

    

    def __non_empty(self,part_NON_EMPTY):
        if part_NON_EMPTY:
            return ' non empty '
        else:
            return' '

    def __rows_or_columns(self,cube,rows,part=[],range_rows={},exclude_rows={},part_order={}):
        dimensiones=cube.dimensiones
        medidas=cube.medidas
 

        mdx=''
        order='null'
        dim_concrete=''
        
        for i in part_order:
            if i in dimensiones:
                order='dim'
                dim_concrete=i
            elif i in medidas:
                order='med'
                med_concrete=i
            else:
                order='null'
        if part:
            if  order=='med' and med_concrete in medidas:
                mdx+='order('

            if (part_order) and (order=='dim'):
                        mdx+='(order('
            if rows:
                mdx+=' ('
            else:
                mdx+=' {' 
            for on_row in part:
                if on_row in dimensiones:
                    
                    
                    
                    if on_row in range_rows:
                        position=dimensiones[on_row].find('.')+1
                        dim=dimensiones[on_row][position:]
                        position+=dim.find('.')+1
                        mdx+=dimensiones[on_row][:position]+'&['+range_rows[on_row][0]+']:'
                        mdx+=dimensiones[on_row][:position]+'&['+range_rows[on_row][1]+']'
                        if on_row in exclude_rows:
                            for dim in exclude_rows[on_row]:

                                mdx+='-'+dimensiones[on_row][:position]+'&['+dim+']'
                        mdx+=','
                    else:
                        position=dimensiones[on_row].find('.')+1
                        dim=dimensiones[on_row][position:]
                        position+=dim.find('.')+1
                        mdx+= dimensiones[on_row]
                        for exclude in exclude_rows:
                            if on_row in exclude: 
                                mdx+='-'+dimensiones[on_row][:position]+'&['+ exclude[on_row]+']'
                        mdx+=','
                    
                    if (part_order) and (order=='dim') and (dim_concrete == on_row):
                        position=dimensiones[dim_concrete].find('.')+1
                        dim=dimensiones[dim_concrete][position:]
                        position+=dim.find('.')+1
                        mdx=mdx[0:len(mdx)-1]
                        mdx+='),'+dimensiones[dim_concrete][:position]+'membervalue , '+ part_order[dim_concrete] +'),'
                elif on_row in medidas:
                    mdx+= medidas[on_row]+','
                else:

                    mdx+='<<error in {0} >>'.format(str(on_row))

            mdx=mdx[0:len(mdx)-1]
            if rows:    
                mdx+=') '
            else:
                mdx+='} ' 

            if  order=='med' and med_concrete in medidas:
                mdx+= ','+medidas[med_concrete]+','+part_order[med_concrete]+')'
                
            

            
        
        return mdx

    def partDate(self,part_where,fecha,cube):
        mdx=''
        dimensiones=cube.dimensiones
        for i in part_where:
            if 'Date' in i:
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    mdx+='('+w[:position_value]+'&['+str(fecha)+'] ) *'
        for i in part_where:
            if 'Date' in i:
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    # join=''
                    # w= dimension
                    # position_value=w.find('.')+1
                    # w2=w[position_value:]
                    # position_value+=w2.find('.')+1
                    # mdx+='('+w[:position_value]+'&['+str(fecha)+'] ) *'
                    # print 'DIMENSIONNNNNN',dimension
            elif 'Time' in i:
                if i in dimensiones:

                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    mdx+='('+w[:position_value]+'&['+str(part_where[i][0])+'] : '+w[:position_value]+'&['+str(part_where[i][1])+']) *'

                    
            else:
                 
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    mdx+='('+w[:position_value]+'&['+str(part_where[i])+'] ) *'
        mdx= mdx[:-1]
        return mdx

    def partComplete(self,part_where,cube,nuevas_fechas):
        mdx=''
        dimensiones=cube.dimensiones
        for i in part_where:
            if 'Date' in i:
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    mdx+='('+w[:position_value]+'&['+nuevas_fechas[0]+'] : '+w[:position_value]+'&['+nuevas_fechas[1]+']) *'

        for i in part_where:
            if 'Date' in i:
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    # join=''
                    # w= dimension
                    # position_value=w.find('.')+1
                    # w2=w[position_value:]
                    # position_value+=w2.find('.')+1
                    # mdx+='('+w[:position_value]+'&['+nuevas_fechas[0]+'] : '+w[:position_value]+'&['+nuevas_fechas[1]+']) *'

            elif 'Time' in i:
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')
                    mdx+='('+w[:position_value]+ ' ) *'
            else:
                
                if i in dimensiones:
                    dimension=dimensiones[i]        
                    join=''
                    w= dimension
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    mdx+='('+w[:position_value]+'&['+str(part_where[i])+'] ) *'
        mdx= mdx[:-1]
        return mdx
    def __where_dict2(self,cube,part_where={},request_data={}):  

        # print 'PART_WHERE----->',part_where

        dimensiones=cube.dimensiones
        medidas=cube.medidas
        mdx=''
        dimension_members=''
        tiempo={'Time':False,'Date':False}
        for i in part_where:
            if i[0]in tiempo:
                tiempo[i[0]]=i
                dim_time=i
        nuevas_fechas=(part_where[dim_time][0][:-6],part_where[dim_time][1][:-6])
        
        if not 'int_all_time' in request_data:
            request_data['int_all_time']=0
        if not request_data['int_all_time']:
            if part_where:
                ## PARA VER QUE CASO DEL WHERE ES
                
                if tiempo['Date']:
                    fecha_comienzo=int(part_where[dim_time][0][8:-2])==0
                    fecha_fin=int(part_where[dim_time][1][8:-2])==2359

                #### SI LAS FECHAS SON COMPLETAS
                if fecha_comienzo and fecha_fin:
                    mdx+='{'+self.partComplete(part_where,cube,nuevas_fechas)+'} +'

                ###### Si las fechas no son completas por el final 
                elif fecha_comienzo:
                    nuevas_horas=(0,int(part_where[dim_time][1][8:-2]))
                    part_where[('Time','Time Field','Time Field')]=nuevas_horas
                    #no son completas por el final
                    

                    mdx+='{'+self.partDate(part_where,nuevas_fechas[1],cube)+'} +'

                    nueva=int(nuevas_fechas[1])-1
                    nuevas_fechas=(nuevas_fechas[0],str(nueva))

                    mdx+='{'+self.partComplete(part_where,cube,nuevas_fechas)+'} +'


                ###### Si las fechas no son completas por el principio 
                elif fecha_fin:
                    nuevas_horas=(int(part_where[dim_time][0][8:-2]),2359)
                    part_where[('Time','Time Field','Time Field')]=nuevas_horas
                   
                    mdx+='{'+self.partDate(part_where,nuevas_fechas[0],cube)+'} +'


                    nueva=int(nuevas_fechas[0])+1
                    nuevas_fechas=(str(nueva),nuevas_fechas[1])


                    mdx+='{'+self.partComplete(part_where,cube,nuevas_fechas)+'} '
                ########################
                ###### Si las fechas no son completas por ninguno de los extremos
                else:
                    
                    # print 'no son completas por ninguno de los extremos'
                    nuevas_horas=(int(part_where[dim_time][0][8:-2]),int(part_where[dim_time][1][8:-2]))
                    part_where[('Time','Time Field','Time Field')]=nuevas_horas
                    
                    if int(nuevas_fechas[1])-int(nuevas_fechas[0])==1:
                        
                        part_where_aux={}
                        for i in part_where:
                            if 'Time' in i :
                                aux=(0,part_where[i][1])
                                part_where_aux[i]=aux
                            else:
                                part_where_aux[i]=part_where[i]
                        
                        mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[1],cube)+'} +'
                        part_where_aux={}
                        for i in part_where:
                            if 'Time' in i :
                                aux=(part_where[i][0],2359)
                                part_where_aux[i]=aux
                            else:
                                part_where_aux[i]=part_where[i]

                        mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[0],cube)+'} +'
                    elif int(nuevas_fechas[1])-int(nuevas_fechas[0])==0:
                        

                        mdx+='{'+self.partDate(part_where,nuevas_fechas[0],cube)+'} +'

                    else:
                        part_where_aux={}
                        for i in part_where:
                            if 'Time' in i :
                                aux=(0,part_where[i][1])
                                part_where_aux[i]=aux
                            else:
                                part_where_aux[i]=part_where[i]

                        mdx+='{'+self.partDate(part_where_aux,nuevas_fechas[1],cube)+'} +'
                        if nuevas_fechas[0]!=nuevas_fechas[1]:
                            mdx+='{'+self.partDate(part_where,nuevas_fechas[0],cube)+'} +'

                            nueva1=int(nuevas_fechas[1])-1
                            nueva0=int(nuevas_fechas[0])+1
                            nuevas_fechas=(str(nueva0),str(nueva1))
                            
                            part_where_aux={}
                            for i in part_where:
                                if 'Time' in i :
                                    aux=(part_where[i][0],2359)
                                    part_where_aux[i]=aux
                                else:
                                    part_where_aux[i]=part_where[i]

                            mdx+='{'+self.partComplete(part_where_aux,cube,nuevas_fechas)+'} '
                mdx=' where ( ' + mdx[:-1] + ' )'  
        else:
            nuevas_horas=(int(part_where[dim_time][0][8:-2]),int(part_where[dim_time][1][8:-2]))
            mdx = ' where ( ' + '{([Time].[Time Field].&[' + str(nuevas_horas[0])+ '] : [Time].[Time Field].&['+str(nuevas_horas[1])+']) *([Date].[Id].&['+str(nuevas_fechas[0])+'] : [Date].[Id].&['+str(nuevas_fechas[1])+'])} *'
            for i in part_where:
                if 'Date' in i:
                    dimension=dimensiones[i]        

                elif 'Time' in i:
                    dimension=dimensiones[i]        
                else:
                    if i in dimensiones:
                        dimension=dimensiones[i]        
                        join=''
                        w= dimension
                        position_value=w.find('.')+1
                        w2=w[position_value:]
                        position_value+=w2.find('.')+1
                        mdx+='{('+w[:position_value]+'&['+str(part_where[i])+'] )} *'
            mdx= mdx[:-1] + ')'

        # part_where[('Time','Time Field','Time Field')]=nuevas_horas
        #no son completas por el final


        # mdx+='{'+self.partDate(part_where,nuevas_fechas[1],cube)+'} +'

        # mdx+='{'+self.partComplete(part_where,cube,nuevas_fechas)+'} +'

 
         


 # # where ( {([Time].[Time Field].&[0] : [Time].[Time Field].&[0]) *([Date].[Id].&[20130212] ) } +{([Time].[Time Field] ) *([Date].[Id].&[20130211] : [Date].[Id].&[20130212]) }  )

 # #    where ( {([Time].[Time Field].&[1000] : [Time].[Time Field].&[2305]) *([Date].[Id].&[20130211] : [Date].[Id].&[20130213]) }  )


 #        print 'ESTOOOOOOOOOO',mdx
        return mdx




    def __where_dict(self,cube,part_where={}):

        # print 'where de unooo'
        dimensiones=cube.dimensiones
        medidas=cube.medidas
        mdx=''
        if part_where:
            mdx +=' where filter ('
            for where in part_where:
                if where in dimensiones:
                    join=''
                    w= dimensiones[where]
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    join+=w+'.Members '
                    mdx+=join

                elif where in medidas:
                    mdx+='<<error in where {0}>> filtrar medidas en select'.format(str())
                else:
                    mdx+='<<error in where {0}>>'.format(str())
            mdx= mdx[:len(mdx)-1]+', '
            # ya_aniadido=False
            
         
            for where in part_where:
               

                if where in dimensiones:
                    
                    w= dimensiones[where]
                    position_value=w.find('.')+1
                    w2=w[position_value:]
                    position_value+=w2.find('.')+1
                    if not isinstance(part_where[where], types.StringTypes):
                        if len(part_where[where])>1:
                            #w2=w[0:position_value] +'&['+str(part_where[where][0])+'] : '+w[0:position_value] +'&['+str(part_where[where][1])+']'
                            w2=w[0:position_value] +'CurrentMember.Properties(\'Key\') >= \''+ str(part_where[where][0])+ '\' and '+w[0:position_value] +'CurrentMember.Properties(\'Key\') <= \''+str(part_where[where][1])+'\' '
                            mdx+=w2

                elif where in medidas:
                    mdx+='<<error in where {0}>> filtrar medidas en select'.format(str())
                else:
                    mdx+='<<error in where {0}>>'.format(str())

            mdx=mdx[:len(mdx)-1]+')'
       
        return mdx

    

    def __order(self,cube,order,part_order):
        dimensiones=cube.dimensiones
        medidas=cube.medidas
        mdx=', '
        if order in dimensiones:
            dimension = dimensiones[order]
            p_pto=dimension.find('.')+1
            d=dimension[p_pto:]
            p_pto+=d.find('.')
            dimension=dimension[0:p_pto+1]+'membervalue'

            mdx+= dimension+', '+part_order[order]

        elif order in medidas:
            mdx+= medidas[order]+', '+part_order[order]
        else:
            mdx+='<<error in order {0}>> '.format(str(order))
        mdx+=' ) '
        return mdx

    def __part_order(self,cube,part_on_rows,range_rows,exclude_rows,part_order,part_filter):

        dimensiones=cube.dimensiones
        medidas=cube.medidas
        mdx=''
        for order in part_order:
            # mdx+= 'order('
            if  part_order[order]=='ASC' or part_order[order] == 'DESC' or part_order[order]=='BASC' or part_order[order] == 'BDESC' :
                if part_filter:
                    mdx+= self.__filter(cube,part_filter,part_on_rows,range_rows,exclude_rows)
                else:
                    mdx+= self.__rows_or_columns(cube,True,part_on_rows,range_rows,exclude_rows,part_order)
                # mdx+=self.__order(cube,order,part_order)
            else:
                if part_filter:
                    mdx+= self.__filter(cube,part_filter,part_on_rows,range_rows,exclude_rows)
                else:
                    mdx+= self.__rows_or_columns(cube,True,part_on_rows,range_rows,exclude_rows)
                mdx+= '<<{0} in order is incorrect >> '.format(part_order[order])
        return mdx


    def __filter(self,cube,part_filter,part_on_rows,range_rows,exclude_rows):
        mdx=''
        medidas=cube.medidas
        filtrada=False
        dimensiones=cube.dimensiones
        
        mdx+= 'filter( '
        mdx+= self.__rows_or_columns(cube,True,part_on_rows,range_rows,exclude_rows)+', '
        
        for filte in part_filter:
           
            #key=filte.keys()[0]
           
            if filtrada:
                mdx+=' and '
            if filte in dimensiones:
               #print filte
                dimension=dimensiones[filte]
                position=dimension.find('.')
                dimension=dimension[position+1:]
                position+=dimension.find('.')+1
                dimension=dimensiones[filte][:position]

                mdx+= dimension+'.&['+part_filter[filte]+']'

            elif key in medidas:
                mdx+= medidas[key]+filte[filte][0] + filte[filte][1]
            else: 
                mdx+='<<error in filter {0}>> '.format(str(filte))

            filtrada=True


        return mdx+'  ) '

    def __on_row(self,cube,part_on_rows,range_rows,exclude_rows,part_order,part_filter):
        medidas=cube.medidas
        dimensiones=cube.dimensiones
        mdx=''
        if part_order :
            if len(part_order)==1:
                mdx+=self.__part_order(cube,part_on_rows,range_rows,exclude_rows,part_order,part_filter)
            else:
                mdx+='<< part_order must be like {0}>>'.format(str({('Measures','Calls'):'ASC'}))
        else:
            if part_filter:
                
                mdx+= self.__filter(cube,part_filter,part_on_rows,range_rows,exclude_rows)
                
            else:   

                mdx+= self.__rows_or_columns(cube,True,part_on_rows,range_rows,exclude_rows)
        
        return mdx

    # Pasandole unos parametros se forma la mdx
    # [('client','client'),('client','id'),...] part_on_rows y part_on_columns del mismo tipo 
    # range rows= {('client','fechask'):[('value1'),('value2')]}
    # part_from un string indicando el nombre del cubo 
    # part_where {('cdrfint','fechask'):('20130101000000','20130125000000'),('client','id'):'54'...}
    # part_order {('measure','calls'):'ASC'} ASC , DESC , BASC , BDESC
    # part_filter {('measure','calls'):'>1000'}
    # NON_EMPTY es un boolean para indicar si se quiere ese campo  
    def mdx (self,cube,part_rows=[],range_rows=[],exclude_rows={},part_columns=[],part_from='',part_where={},part_order=[],part_filter={},part_NON_EMPTY=True,total_data=False,request_data={}):
        
        """         
    *PARAMETERS* 

-A cube instance
-part_rows A list of tuples for the rows : [('client','client'),('client','id'),...]
-part_columns A list of tuples for the columns : [('client','client'),('client','id'),...]
-part_exclude A list of dict for the columns and value to exclude: [{('client','client'):2345},{('client','id'):...}]
-part_from  A string with the name of the cube :'[stoneworksolutions dev]'
-part_where  A dict. The key is the dimension and the value is the value which want put in the where :{('client','client'):'Aryans',('cdrfint','fecha'):('2013101010101010','2013101110101010')....}
-A dict with only one key.The key is the measure and the value indicate the order to do ('ASC','DESC','BASC','BDESC') :{('measure','calls'):'ASC'}
-A dict with only one key.The key is the measure and the value is a string with the expression to filter : {('measure','calls'):(>,1000),...}
-A booleann that indicate if is True that we want non empty in the mdx , by contrast we don`t want non empty in the mdx

    *USE*

>>> cuve=cube.CUBE()
>>> cuve.connect()
>>> mdx=cube.MDX()
>>> rows=[('client','client')]
>>> columns=[('measure','calls')]
>>> where ={('destination','destination'):'Austria A1'}
>>> order={('measure','calls'):'ASC'}
>>> fromo='[stoneworksolutions dev]'
>>> filter={('measure','calls'):'<100'}
>>> mdx.mdx(cuve,rows,columns,fromo,where,order,filter)

    *RETURN* 
A string which is a mdx 
        """
        #select
    
        part_rows=sorted(list(set(part_rows)))
        if cube.dimensiones:
            
            mdx='select'
            mdx+= self.__non_empty(part_NON_EMPTY)

            # on rows
            mdx+= self.__on_row(cube,part_rows,range_rows,exclude_rows,part_order,part_filter)
            if total_data==True:
                mdx='select non empty ([Destination].[Destination].[Destination])'
            mdx+= 'on rows, '

            # on columns
            mdx+= self.__rows_or_columns(cube,False,part_columns,range_rows,exclude_rows)
            mdx+=' on columns'
            
           
            #from 
            mdx+=' from '+ part_from
            #where
            mdx+=self.__where_dict2(cube,part_where,request_data)
          

            # print 'MDX',mdx

            return mdx
        else:
            return 'cube has not dimensions or it is not good connect'



    def tiempo_final(self,mdx):
        """         
    *PARAMETERS* 

-A string which represent a mdx


    *USE*

>>> mdx="select non empty([Tiempo 1].[Fecha].[Fecha]) on rows, {[Measures].[Calls],[Measures].[Minutes]} on columns from [Stoneworksolutions Dev]"
>>> mdx_class=cube.MDX()
>>> mdx_class.tiempo_final(mdx)
>>> select non empty([Tiempo 1].[Fecha].[Fecha]) on rows, {[Measures].[Calls],[Measures].[Minutes]} on columns from [Stoneworksolutions Dev]


>>> mdx="select NON EMPTY ([Clients Client].[Client].[Client], [Tiempo 1].[Fecha].[Fecha]) on rows,{[Measures].[Calls]}  on columns from [Stoneworksolutions Dev] where [Tiempo 1].[Semestre].&[2012-01-01T00:00:00]"
>>> mdx_class.tiempo_final(mdx)
>>> select NON EMPTY ([Clients Client].[Client].[Client], [Tiempo 1].[Fecha].[Fecha]) on rows,{[Measures].[Calls]}  on columns from [Stoneworksolutions Dev] where [Tiempo 1].[Semestre].&[2012-01-01T00:00:00]


>>> mdx="select NON EMPTY ([Tiempo 1].[Fecha].[Fecha],[Clients Client].[Client].[Client]) on rows,{[Measures].[Calls]}  on columns from [Stoneworksolutions Dev] where [Tiempo 1].[Semestre].&[2012-01-01T00:00:00]"
>>> mdx_class.tiempo_final(mdx)
>>> select NON EMPTY ([Clients Client].[Client].[Client], [Tiempo 1].[Fecha].[Fecha]) on rows,{[Measures].[Calls]}  on columns from [Stoneworksolutions Dev] where [Tiempo 1].[Semestre].&[2012-01-01T00:00:00]

    *RETURN* 
A string which is a mdx but if the mdx of input has a dimension time in rows this will appear at the end
        """
        selec = mdx[:mdx.find('(')]
        resto = mdx[mdx.find(')')+1:]
        dimensiones=mdx[mdx.find('(')+1:mdx.find(')')]
        if dimensiones.find(',')>0:
            lista_dimensiones=[]
            tiempo=''
            while dimensiones.find(',')>0:

                dimension=dimensiones[:dimensiones.find(',')]

                dimensiones=dimensiones[dimensiones.find(',')+1:]

                if 'tiempo' in dimension.lower():

                    tiempo=dimension
                else:

                    lista_dimensiones.append(dimension)

            if 'tiempo' in dimensiones.lower():

                    tiempo=dimensiones
            else:

                lista_dimensiones.append(dimensiones)


            dimens='( ' 

            for i in lista_dimensiones:
                dimens+=i+','
            
            if tiempo:
                dimens+= tiempo +')'
            else:
                dimens = dimens[:len(dimens)-1] +')'

            return selec + dimens + resto
        else:
            return mdx
    def convert_list_rows_columns(self,cube,col_order):

        dimensiones=cube.dimensiones
        medidas=cube.medidas
        rows=[]
        columns=[]
        alone=[]
        col=col_order[0]
        col_order_string=[]

        if not (type(col)==types.StringType):
            for i in col_order:
                col_order_string.append(i[0])
            col_order=col_order_string
        for col in col_order:
            not_found=True
            for dim in dimensiones:
               
                dim_key=dim[0]
                
                if col in dim_key :
                    rows.append(dim_key)
                    not_found=False
            
            if  not_found:
                for med in medidas:
                    med_key=med[0]
                    
                    if col in med_key:
                        not_found=False
                        columns.append(med_key)      
            if  not_found:
                alone.append(col)

        return rows,columns,alone

    #def aniadir_on_rows(self,cube,rows=[]):


    def select_for_filter(self,cube,on_rows=[],medida='',exclude_rows={}):
        """         
    *PARAMETERS* 

-A cube instance
-A list of tuples for the rows : [('client','client'),('client','id'),...]


    *USE*

>>> cuve=cube.CUBE()
>>> cuve.connect()
>>> mdx=cube.MDX()
>>> rows=[('client','client')]
>>> mdx.select_for_filter(cuve,rows)

    *RETURN* 
A string which is a mdx but only the select
        """

        selects= cube.dimensiones
        select='select non empty'

        select+=self.__rows_or_columns(cube,True,part=on_rows,range_rows={},exclude_rows=exclude_rows)

        select+=' on rows, {'+medida+'} on columns '
        return select

################################################################################################################################################
################################################################################################################################################