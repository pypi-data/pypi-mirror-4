import os
import json
import copy
import sqlalchemy
import sqlalchemy.orm

import numpy as np

from netCDF4 import Dataset
from netcdftime import utime
from datetime import  datetime

class File_Expt(object):
    def __init__(self,diag_tree_desc):
        for tree_desc in diag_tree_desc:
            setattr(self,tree_desc,'')
        self.path=''
        self.month=''
        self.year=''

def load_database(diag_tree_desc):

    engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=False)
    metadata = sqlalchemy.MetaData(bind=engine)

    time_db = sqlalchemy.Table('time_db',metadata,
            sqlalchemy.Column('case_id',sqlalchemy.Integer,primary_key=True),
            sqlalchemy.Column('year',sqlalchemy.Integer),
            sqlalchemy.Column('month',sqlalchemy.Integer),
            sqlalchemy.Column('path',sqlalchemy.String(255)),
            *(sqlalchemy.Column(diag_tree, sqlalchemy.String(255)) for diag_tree in diag_tree_desc)
            )
    metadata.create_all()
    sqlalchemy.orm.mapper(File_Expt,time_db)

    session = sqlalchemy.orm.create_session(bind=engine, autocommit=False, autoflush=True)
    return session, time_db

def descend_tree(session,file_expt,paths_dict,top_name,frequency):
    if isinstance(paths_dict,dict):
        for value in paths_dict.keys():
            if value[0] != '_':
                file_expt_copy = copy.deepcopy(file_expt)
                setattr(file_expt_copy,paths_dict['_name'],value)
                if paths_dict['_name']=='frequency':
                    frequency=value
                descend_tree(session,file_expt_copy,paths_dict[value],value,frequency)
    else:
        for value in paths_dict:
            file_expt_copy = copy.deepcopy(file_expt)
            find_months(session,file_expt_copy,value,top_name,frequency)

def find_months(session,file_expt,path_name,file_type,frequency):
    if frequency=='fx':
        file_expt_copy = copy.deepcopy(file_expt)
        if file_type=='OPeNDAP': 
            setattr(file_expt_copy,'path',path_name+'|0|0')
        else:
            setattr(file_expt_copy,'path',path_name)
        session.add(file_expt_copy)
        session.commit()
    elif file_type in ['local_file','HTTPServer','GridFTP']:
        year_indexing={'yr':12,'mon':16,'day':20,'6hr':32,'3hr':32}
        filename=os.path.basename(path_name)

        #Recover date range from filename:
        years_range = [int(date[:4]) for date in filename[-year_indexing[frequency]:-3].split('-')]
        months_range = [int(date[4:6]) for date in filename[-year_indexing[frequency]:-3].split('-')]
        years_list=range(*years_range)
        years_list.append(years_range[1])

        for year in years_list:
            for month in range(1,13):
                if not ( (year==years_range[0] and month<months_range[0]) or
                         (year==years_range[1] and month>months_range[1])   ):
                    file_expt_copy = copy.deepcopy(file_expt)
                    setattr(file_expt_copy,'year',year)
                    setattr(file_expt_copy,'month',month)
                    setattr(file_expt_copy,'path',path_name)
                    session.add(file_expt_copy)
                    session.commit()

    elif file_type == 'OPeNDAP':
        try:
            data=Dataset(path_name)
        except:
            return

        time_axis = data.variables['time'][:]
        cdftime=utime(data.variables['time'].units)
        date_axis=cdftime.num2date(time_axis)
        year_axis=[date.year for date in date_axis]
        for year in set(year_axis):
            month_axis=[]
            for date in date_axis:
                if date.year==year:
                    month_axis.append(date.month)
            for month in month_axis:
                month_id=[]
                for date_id, date in enumerate(date_axis):
                    if date.year==year and date.month==month:
                        month_id.append(date_id)
                file_expt_copy = copy.deepcopy(file_expt)
                setattr(file_expt_copy,'year',year)
                setattr(file_expt_copy,'month',month)
                setattr(file_expt_copy,'path',path_name+'|'+str(min(month_id))+'|'+str(max(month_id)))
                session.add(file_expt_copy)
                session.commit()

def make_tuple_query_sqlite_compatible(query,tuple_list):
    for item_id, item in enumerate([item for sublist in tuple_list for item in sublist]):
        query=query.replace(':param_'+str(item_id+1),"'"+item+"'",1)
    return query

def intersection(paths_dict,diag_tree_desc, diag_tree_desc_final):
    diag_tree_desc.append('file_type')

    session, time_db = load_database(diag_tree_desc)
    file_expt = File_Expt(diag_tree_desc)

    top_name='data_pointers'
    descend_tree(session,file_expt,paths_dict[top_name],top_name,None)

    #Step one: find all the center / model tuples with all the requested variables
    #          for all months of all years for all experiments.
    model_list=session.query(
                             File_Expt.center,
                             File_Expt.model,
                             File_Expt.rip
                            ).distinct().all()

    for experiment in paths_dict['diagnostic']['experiment_list'].keys():
        years_range=[int(year) for year in paths_dict['diagnostic']['experiment_list'][experiment].split(',')]
        years_list=range(*years_range)
        years_list.append(years_range[1])
        for year in years_list:
            for month in range(1,13):
                for var_name in paths_dict['diagnostic']['variable_list'].keys():
                    if paths_dict['diagnostic']['variable_list'][var_name][0]!='fx':
                        #Do this without fx variables:
                        conditions=[
                                     File_Expt.var==var_name,
                                     File_Expt.frequency==paths_dict['diagnostic']['variable_list'][var_name][0],
                                     File_Expt.realm==paths_dict['diagnostic']['variable_list'][var_name][1],
                                     File_Expt.mip==paths_dict['diagnostic']['variable_list'][var_name][2],
                                     File_Expt.experiment==experiment,
                                     File_Expt.year==year,
                                     File_Expt.month==month
                                   ]
                        model_list_var=session.query(
                                                 File_Expt.center,
                                                 File_Expt.model,
                                                 File_Expt.rip
                                                ).filter(sqlalchemy.and_(*conditions)).distinct().all()
                        model_list=set(model_list).intersection(set(model_list_var))

        #Do it for fx variables:
        model_list_fx=[model[:-1] for model in model_list]
        for var_name in paths_dict['diagnostic']['variable_list'].keys():
            if paths_dict['diagnostic']['variable_list'][var_name][0]=='fx':
                conditions=[
                             File_Expt.var==var_name,
                             File_Expt.frequency==paths_dict['diagnostic']['variable_list'][var_name][0],
                             File_Expt.realm==paths_dict['diagnostic']['variable_list'][var_name][1],
                             File_Expt.mip==paths_dict['diagnostic']['variable_list'][var_name][2],
                             File_Expt.experiment==experiment
                           ]
                model_list_var=session.query(
                                         File_Expt.center,
                                         File_Expt.model,
                                           ).filter(sqlalchemy.and_(*conditions)).distinct().all()
                model_list_fx=set(model_list_fx).intersection(set(model_list_var))


    #Step two: create the new paths dictionary:
    diag_tree_desc_final.append('path')
    new_paths_dict={}
    new_paths_dict['diagnostic']=paths_dict['diagnostic']
    new_paths_dict['data_pointers']={}

    variable_list_requested=[]
    for var_name in paths_dict['diagnostic']['variable_list'].keys():
        variable_list_requested.append((var_name,)+tuple(paths_dict['diagnostic']['variable_list'][var_name]))

    #Create a simulation list
    new_paths_dict['simulation_list']=[]

    for model in model_list:
        if model[:-1] in model_list_fx:
            new_paths_dict['simulation_list'].append(list(model))

            months_list=session.query(
                                      File_Expt
                                     ).filter(sqlalchemy.and_(
                                                                File_Expt.center==model[0],
                                                                File_Expt.model==model[1],
                                                             )).all()
            for item in months_list:
                if item.var in paths_dict['diagnostic']['variable_list'].keys():
                    if [item.frequency,item.realm,item.mip]==paths_dict['diagnostic']['variable_list'][item.var]:
                        if item.frequency!='fx':
                            #Works if the variable is not fx:
                            if item.year in years_list:
                                if item.month in range(1,13):
                                    new_paths_dict['data_pointers']=create_tree(item,diag_tree_desc_final,new_paths_dict['data_pointers'])
                        else:
                            #If fx, we create the time axis for easy retrieval:
                            for year in years_list:
                                for month in range(1,13):
                                    item.year=year
                                    item.month=month
                                    new_paths_dict['data_pointers']=create_tree(item,diag_tree_desc_final,new_paths_dict['data_pointers'])
    return new_paths_dict

def create_tree(item,diag_tree_desc,paths_dict):
    #This function adds to the tree defined by paths_dict
    #It calls itself recursively.

    if len(diag_tree_desc)>1 and isinstance(diag_tree_desc,list):
        #At each call, diag_tree_desc is reduced by one element.
        #If it is a list of more than one element, we continue the recursion.
        if '_name' not in paths_dict.keys():
            #This branch has not been created yet, so create it:
            paths_dict['_name']=diag_tree_desc[0]
        dict_name=getattr(item,diag_tree_desc[0])
        if dict_name not in paths_dict.keys():
            #This branch name has not been created it, so create it:
            paths_dict[dict_name]={}
        #Recursively create tree:
        paths_dict[dict_name]=create_tree(item,diag_tree_desc[1:],paths_dict[dict_name])
    else:
        #The end of the recursion has been reached. This if is just 
        #to ensure a robust implementation.
        if isinstance(diag_tree_desc,list):
            paths_dict=getattr(item,diag_tree_desc[0])
        else:
            paths_dict=getattr(item,diag_tree_desc)
    return paths_dict
