import os
import json
import gzip
import filesystem_query
import experiment_years
import esgf_query
import copy

def union_headers(diag_headers):
    #Create the diagnostic description dictionary:
    diag_desc={}
    #Find all the requested realms, frequencies and variables:
    variable_list=['var_list','frequency_list','realm_list','mip_list']
    for list_name in variable_list: diag_desc[list_name]=[]
    for var_name in diag_headers['variable_list'].keys():
        diag_desc['var_list'].append(var_name)
        for list_id, list_name in enumerate(list(variable_list[1:])):
            diag_desc[list_name].append(diag_headers['variable_list'][var_name][list_id])

    #Find all the requested experiments and years:
    experiment_list=['experiment_list','years_list']
    for list_name in experiment_list: diag_desc[list_name]=[]
    for experiment_name in diag_headers['experiment_list'].keys():
        diag_desc['experiment_list'].append(experiment_name)
        for list_name in list(experiment_list[1:]):
            diag_desc[list_name].append(diag_headers['experiment_list'][experiment_name])
            
    #Find the unique members:
    for list_name in diag_desc.keys(): diag_desc[list_name]=list(set(diag_desc[list_name]))
    return diag_desc

def find_optimset(diagnostic_headers_file, diagnostic_paths_file, gzip_flag):
    #Tree description following the CMIP5 DRS:
    diag_tree_desc=['search',
                    'center',
                    'model',
                    'experiment',
                    'frequency',
                    'realm',
                    'mip',
                    'rip',
                    'version',
                    'var'
                    ]

    #Load the diagnostic header file:
    paths_dict={}
    paths_dict['diagnostic']=json.load(diagnostic_headers_file)
    
    #Create the diagnostic description dictionary with the union of all the requirements.
    #This will make the description easier and allow to appply the intersection of requirements
    #offline.
    diag_desc=union_headers(paths_dict['diagnostic'])

    #Build the simple pointers to files:
    paths_dict['data_pointers']={}
    paths_dict['data_pointers']['_name']='search'
    for search_path in paths_dict['diagnostic']['search_list']:
        top_path=os.path.expanduser(os.path.expandvars(search_path))
        if os.path.exists(top_path):
            #Local filesystem archive
            paths_dict['data_pointers'][search_path]=search_filesystem(
                                                                       diag_desc,
                                                                       diag_tree_desc[1:],
                                                                       top_path
                                                                       )
        else:
            #ESGF search
            paths_dict['data_pointers'][search_path]=search_esgf(search_path,
                                                                 paths_dict['diagnostic']['file_type_list'],
                                                                 paths_dict['diagnostic']['variable_list'],
                                                                 paths_dict['diagnostic']['experiment_list'],
                                                                 diag_tree_desc[1:]
                                                                 )
    #Define the tree strucuture in the output file
    diag_tree_desc_final=[  
                            'center',
                            'model',
                            'experiment',
                            'frequency',
                            'realm',
                            'mip',
                            'rip',
                            'var',
                            'year',
                            'month',
                            'version',
                            'file_type',
                            'search',
                         ]
    #Find the list of center / model with all the months for all the years / experiments and variables requested:
    paths_dict=experiment_years.intersection(paths_dict,diag_tree_desc,diag_tree_desc_final)
    
    #Write dictionary to file using JSON encoding. If the gzip flag was used,
    #output directly to a compressed file:
    if gzip_flag:
        outfile = gzip.open(diagnostic_paths_file+'.gz','w')
    else:
        outfile = open(diagnostic_paths_file,'w')
    json.dump(paths_dict,outfile)

    outfile.close()

def search_filesystem(diag_desc,diag_tree_desc,top_path):
    return filesystem_query.descend_tree(diag_desc,diag_tree_desc,top_path)

def search_esgf(search_path,file_type_list,variable_list,experiment_list,diag_tree_desc):
    return esgf_query.create_dict(search_path,file_type_list,variable_list,experiment_list,diag_tree_desc)


def retrieval(retrieval_desc):
    #Reads the file created by find_optimset and gives the path to file:
    if retrieval_desc.in_diagnostic_pointers_file[-3:]=='.gz':
        infile=gzip.open(retrieval_desc.in_diagnostic_pointers_file,'r')
    else:
        infile=open(retrieval_desc.in_diagnostic_pointers_file,'r')
    paths_dict=json.load(infile)

    tree_retrieval(retrieval_desc,paths_dict['diagnostic'],paths_dict['data_pointers'])
    return

def tree_retrieval(retrieval_desc,diag_desc,paths_dict):
    #Reads the tree recursively:
    if isinstance(paths_dict,dict):
        #Read the level name:
        level_name=paths_dict['_name']
        if level_name in dir(retrieval_desc):
            #If the level name was specified in the retrieval, use this specification:
            tree_retrieval(retrieval_desc,diag_desc,paths_dict[str(getattr(retrieval_desc,level_name))])
        elif level_name=='version':
            #the 'version' field is perculiar. Here, we use the most recent, or largest version number:
            version_list=[]
            for version in paths_dict.keys():
                if version[0]!='_':
                    version_list.append(int(version[1:]))
            version='v'+str(max(version_list))
            tree_retrieval(retrieval_desc,diag_desc,paths_dict[version])
        else:
            #The level was not specified but an ordered list was provided in the diagnostic header.
            #Go through the list and pick the first avilable one:
            level_ordering=diag_desc[level_name+'_list']
            for level in level_ordering:
                if level in paths_dict.keys():
                    if level_name=='file_type' and retrieval_desc.file_type_flag:
                        #if the file_type_flag was used, the script outputs only the file_type
                        print level
                        return
                    tree_retrieval(retrieval_desc,diag_desc,paths_dict[level])
                    break
    else:
        print paths_dict
    return

def simulations(simulations_desc):
    #Reads the file created by find_optimset and gives the path to file:
    if simulations_desc.in_diagnostic_pointers_file[-3:]=='.gz':
        infile=gzip.open(simulations_desc.in_diagnostic_pointers_file,'r')
    else:
        infile=open(simulations_desc.in_diagnostic_pointers_file,'r')
    paths_dict=json.load(infile)

    print paths_dict['simulations_list']
    return


def main():
    import sys
    import argparse 
    import shutil
    import textwrap

    #Option parser
    description=textwrap.dedent('''\
    This script queries an ESGF archive. It can query a
    local POSIX-based archive following the CMIP5 DRS
    filename convention and directory structure.

    In the future it should become able to query the THREDDS
    catalog of the ESGF and provide a simple interface to
    the OPEnDAP services.
    ''')
    epilog='Frederic Laliberte, Paul Kushner 10/2012'
    version_num='0.2'
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                            description=description,
                            version='%(prog)s '+version_num,
                            epilog=epilog)

    subparsers = parser.add_subparsers(help='commands',dest='command')

    #Find Optimset
    epilog_optimset=textwrap.dedent(epilog+'\n\nThe output can be pretty printed by using:\n\
                          cat out_paths_file | python -mjson.tool')
    optimset_parser=subparsers.add_parser('optimset',
                                           help='Find the optimal set of models for a diagnostic',
                                           epilog=epilog_optimset,
                                           formatter_class=argparse.RawTextHelpFormatter
                                         )
    optimset_parser.add_argument('in_diagnostic_headers_file',
                                 type=argparse.FileType('r'),
                                 help='Diagnostic headers file (input)')
    optimset_parser.add_argument('out_paths_file',
                                 help='Diagnostic paths file (output)')
    optimset_parser.add_argument('-z','--gzip',
                                 default=False, action='store_true',
                                 help='Compress the output using gzip. Because the output is mostly repeated text, this leads to large compression.')

    #Retrieve data
    retrieve_parser=subparsers.add_parser('retrieve',
                                           help='Retrieve a path (on file system or url) to files containing:\n\
                                                 a set of variables from a single month, year, model, experiment.\n\
                                                 It retrieves the latest version.',
                                           )
    retrieve_parser.add_argument('center',type=str,help='Modelling center name')
    retrieve_parser.add_argument('model',type=str,help='Model name')
    retrieve_parser.add_argument('experiment',type=str,help='Experiment name')
    retrieve_parser.add_argument('rip',type=str,help='RIP identifier, e.g. r1i1p1')
    retrieve_parser.add_argument('var',type=str,help='Variable name, e.g. tas')
    retrieve_parser.add_argument('frequency',type=str,help='Frequency, e.g. day')
    retrieve_parser.add_argument('realm',type=str,help='Realm, e.g. atmos')
    retrieve_parser.add_argument('mip',type=str,help='MIP table name, e.g. day')
    retrieve_parser.add_argument('year',type=int,help='Year')
    retrieve_parser.add_argument('month',type=int,help='Month as an integer ranging from 1 to 12')
    retrieve_parser.add_argument('in_diagnostic_pointers_file',
                                 help='Diagnostic headers file with data pointers (input)')

    retrieve_parser.add_argument('-f','--file_type_flag',
                                 default=False,
                                 action='store_true',
                                 help='prints only the file_type if selected')

    #Retrieve data
    simulations_parser=subparsers.add_parser('simulations',
                                           help='Prints the (center,model,rip) triples available in the pointers file.'
                                           )
    simulations_parser.add_argument('in_diagnostic_pointers_file',
                                 help='Diagnostic headers file with data pointers (input)')

    options=parser.parse_args()

    if options.command=='optimset':
        find_optimset(options.in_diagnostic_headers_file, options.out_paths_file, options.gzip)
    elif options.command=='retrieve':
        retrieval(options)
    elif options.command=='simulations':
        simulations(options)

if __name__ == "__main__":
    main()
