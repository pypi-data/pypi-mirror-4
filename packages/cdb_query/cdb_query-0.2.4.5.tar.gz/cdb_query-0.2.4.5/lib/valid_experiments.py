import os
import json
import copy
import sqlalchemy
import sqlalchemy.orm

import numpy as np

from netCDF4 import Dataset
from netcdftime import utime
from datetime import  datetime

###### SUPPORT FUNCTIONS #######
class File_Expt(object):
    def __init__(self,diag_tree_desc):
        for tree_desc in diag_tree_desc:
            setattr(self,tree_desc,'')

def load_database(diag_tree_desc):

    engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=False)
    metadata = sqlalchemy.MetaData(bind=engine)

    time_db = sqlalchemy.Table('time_db',metadata,
            sqlalchemy.Column('case_id',sqlalchemy.Integer,primary_key=True),
            *(sqlalchemy.Column(diag_tree, sqlalchemy.String(255)) for diag_tree in diag_tree_desc)
            )
    metadata.create_all()
    sqlalchemy.orm.clear_mappers()
    sqlalchemy.orm.mapper(File_Expt,time_db)

    session = sqlalchemy.orm.create_session(bind=engine, autocommit=False, autoflush=True)
    return session, time_db

def descend_tree(session,file_expt,paths_dict,top_name,find_function):
    if isinstance(paths_dict,dict):
        for value in paths_dict.keys():
            if value[0] != '_':
                file_expt_copy = copy.deepcopy(file_expt)
                setattr(file_expt_copy,paths_dict['_name'],value)
                descend_tree(session,file_expt_copy,paths_dict[value],value,find_function)
    else:
        for value in paths_dict:
            file_expt_copy = copy.deepcopy(file_expt)
            find_function(session,file_expt_copy,value,top_name)

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
            if len(diag_tree_desc)>2:
                paths_dict[dict_name]={}
            else:
                paths_dict[dict_name]=[]
        #Recursively create tree:
        paths_dict[dict_name]=create_tree(item,diag_tree_desc[1:],paths_dict[dict_name])
    else:
        #The end of the recursion has been reached. This is 
        #to ensure a robust implementation.
        if isinstance(diag_tree_desc,list):
            paths_dict.append(getattr(item,diag_tree_desc[0]))
        else:
            paths_dict.append(item,diag_tree_desc)
    return paths_dict

def make_tuple_query_sqlite_compatible(query,tuple_list):
    for item_id, item in enumerate([item for sublist in tuple_list for item in sublist]):
        query=query.replace(':param_'+str(item_id+1),"'"+item+"'",1)
    return query

######## SPECIFIC FUNCTIONS ##########

##### PATH #####
def find_path(session,file_expt,path_name,top_name):
    setattr(file_expt,'path',path_name)
    session.add(file_expt)
    session.commit()
    return

def intersection_path(paths_dict,diag_tree_desc, diag_tree_desc_final):
    diag_tree_desc.append('file_type')
    diag_tree_desc.append('path')

    session, time_db = load_database(diag_tree_desc)
    file_expt = File_Expt(diag_tree_desc)

    top_name='data_pointers'
    descend_tree(session,file_expt,paths_dict[top_name],top_name,find_path)

    #Step one: find all the center / model tuples with all the requested variables
    model_list=session.query(
                             File_Expt.center,
                             File_Expt.model,
                             File_Expt.rip
                            ).distinct().all()

    for experiment in paths_dict['diagnostic']['experiment_list'].keys():
        for var_name in paths_dict['diagnostic']['variable_list'].keys():
            if paths_dict['diagnostic']['variable_list'][var_name][0]!='fx':
                #Do this without fx variables:
                conditions=[
                             File_Expt.var==var_name,
                             File_Expt.frequency==paths_dict['diagnostic']['variable_list'][var_name][0],
                             File_Expt.realm==paths_dict['diagnostic']['variable_list'][var_name][1],
                             File_Expt.mip==paths_dict['diagnostic']['variable_list'][var_name][2],
                             File_Expt.experiment==experiment,
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
    new_paths_dict['simulations_list']=[]

    for model in model_list:
        if model[:-1] in model_list_fx:
            new_paths_dict['simulations_list'].append('_'.join(model))

            runs_list=session.query(
                                      File_Expt
                                     ).filter(sqlalchemy.and_(
                                                                File_Expt.center==model[0],
                                                                File_Expt.model==model[1],
                                                             )).all()
            for item in runs_list:
                if item.var in paths_dict['diagnostic']['variable_list'].keys():
                    if [item.frequency,item.realm,item.mip]==paths_dict['diagnostic']['variable_list'][item.var]:
                        if item.frequency!='fx':
                            #Works if the variable is not fx:
                            new_paths_dict['data_pointers']=create_tree(item,diag_tree_desc_final,new_paths_dict['data_pointers'])
                        else:
                            #If fx, we create the time axis for easy retrieval:
                            new_paths_dict['data_pointers']=create_tree(item,diag_tree_desc_final,new_paths_dict['data_pointers'])
    return new_paths_dict

#### MONTHLY SEARCH ######

def find_months(session,file_expt,path_name,file_type):
    if file_type in ['HTTPServer','GridFTP']:
        find_months_file(session,file_expt,path_name)
    elif file_type in ['local_file','OPeNDAP']:
        find_months_opendap(session,file_expt,path_name)
    return
        
def find_months_file(session,file_expt,path_name):
    filename=os.path.basename(path_name)

    #Check if file has fixed frequency
    time_stamp=filename.replace('.nc','').split('_')[-1]
    if time_stamp == 'r0i0p0':
        file_expt_copy = copy.deepcopy(file_expt)
        setattr(file_expt_copy,'path',path_name)
        session.add(file_expt_copy)
        session.commit()
        return

    #Recover date range from filename:
    years_range = [int(date[:4]) for date in time_stamp.split('-')]
    #Check for yearly data
    if len(time_stamp.split('-')[0])>4:
        months_range=[int(date[4:6]) for date in time_stamp.split('-')]
    else:
        months_range=[1,12]
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
                #Check if local file. If yes, add indices to path, as for OPeNDAP:
                #if file_type == 'local_file':
                #    date_axis,year_axis=get_year_axis(path_name)
                #    if date_axis != None:
                #        month_id=[]
                #        for date_id, date in enumerate(date_axis):
                #            if date.year==year and date.month==month:
                #                month_id.append(date_id)
                #        setattr(file_expt_copy,'path',path_name+'|'+str(min(month_id))+'|'+str(max(month_id)))

                session.add(file_expt_copy)
                session.commit()
    return

def find_months_opendap(session,file_expt,path_name):
    date_axis, year_axis = get_year_axis(path_name)

    #Check if file has fixed frequency
    if date_axis is None:
        file_expt_copy = copy.deepcopy(file_expt)
        setattr(file_expt_copy,'path',path_name)
        session.add(file_expt_copy)
        session.commit()
        return

    for year in set(year_axis):
        month_axis=[]
        for date in date_axis:
            if date.year==year:
                month_axis.append(date.month)

        #Check for yearly data. If yearly create artificial month axis:
        if len(month_axis)==1:
            month_axis=range(1,13)
            
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
    return

def get_year_axis(path_name):
    try:
        data=Dataset(path_name)
    except:
        return None, None

    if 'time' not in data.dimensions.keys():
        return None, None
    time_axis = data.variables['time'][:]
    cdftime=utime(data.variables['time'].units)
    date_axis=cdftime.num2date(time_axis)
    year_axis=[date.year for date in date_axis]
    return date_axis, year_axis

def intersection_months(paths_dict,diag_tree_desc, diag_tree_desc_final):
    diag_tree_desc.append('file_type')
    diag_tree_desc.append('year')
    diag_tree_desc.append('month')
    diag_tree_desc.append('path')

    session, time_db = load_database(diag_tree_desc)
    file_expt = File_Expt(diag_tree_desc)

    top_name='data_pointers'
    descend_tree(session,file_expt,paths_dict[top_name],top_name,find_months)

    #Step one: find all the center / model tuples with all the requested variables
    #          for all months of all years for all experiments.
    model_list=session.query(
                             File_Expt.center,
                             File_Expt.model,
                             File_Expt.rip
                            ).distinct().all()

    for experiment in paths_dict['diagnostic']['experiment_list'].keys():
        period_list = paths_dict['diagnostic']['experiment_list'][experiment]
        if not isinstance(period_list,list): period_list=[period_list]
        for period in period_list:
            years_range=[int(year) for year in period.split(',')]
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

    #Step two: create the new paths dictionary:
    diag_tree_desc_final.append('path')
    new_paths_dict={}
    new_paths_dict['diagnostic']=paths_dict['diagnostic']
    new_paths_dict['data_pointers']={}

    variable_list_requested=[]
    for var_name in paths_dict['diagnostic']['variable_list'].keys():
        variable_list_requested.append((var_name,)+tuple(paths_dict['diagnostic']['variable_list'][var_name]))

    #Create a simulation list
    new_paths_dict['simulations_list']=[]

    for model in model_list:
        new_paths_dict['simulations_list'].append('_'.join(model))

        months_list=session.query(
                                  File_Expt
                                 ).filter(sqlalchemy.and_(
                                                            File_Expt.center==model[0],
                                                            File_Expt.model==model[1],
                                                         )).all()
        for item in months_list:
            if item.var in paths_dict['diagnostic']['variable_list'].keys():
                if [item.frequency,item.realm,item.mip]==paths_dict['diagnostic']['variable_list'][item.var]:
                    #Retrieve the demanded years list for this experiment
                    period_list = paths_dict['diagnostic']['experiment_list'][item.experiment]
                    if not isinstance(period_list,list): period_list=[period_list]
                    for period in period_list:
                        years_range=[int(year) for year in period.split(',')]
                        years_list=range(*years_range)
                        years_list.append(years_range[1])

                        if item.frequency!='fx':
                            #Works if the variable is not fx:
                            if int(item.year) in years_list:
                                if int(item.month) in range(1,13):
                                    new_paths_dict['data_pointers']=create_tree(item,diag_tree_desc_final,new_paths_dict['data_pointers'])
                        else:
                            #If fx, we create the time axis for easy retrieval:
                            for year in years_list:
                                for month in range(1,13):
                                    item.year=year
                                    item.month=month
                                    new_paths_dict['data_pointers']=create_tree(item,diag_tree_desc_final,new_paths_dict['data_pointers'])
    return new_paths_dict


