import multiprocessing
import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
import re
from braingeneers.analysis import SpikeData, load_spike_data
from braingeneers.data import datasets_electrophysiology as ephys



if __name__ == '__main__':

    working_dir = '/Users/hunterschweiger/braingeneers/sakura/proj/base_ephys/analysis'
    save_dir = '/Users/hunterschweiger/braingeneers/sakura/proj/base_ephys/analysis'
    
    # s3_paths = [
    #     "s3://braingeneers/ephys/2024-05-04-e-sakura-day22and24/",
    #     "s3://braingeneers/ephys/2024-05-04-e-sakura-day22and24_dorothy/",
    #     "s3://braingeneers/ephys/2024-05-10-e-all_cell_lines_dorsal_pasca/",
    #     "s3://braingeneers/ephys/2024-05-17-e-all_cell_lines_dorsal_pasca/",
    #     "s3://braingeneers/ephys/2024-05-21-e-all_cell_lines_dorsal_pasca/",
    #     "s3://braingeneers/ephys/2024-05-07-e-c57bl6_dorsal_pasca/",
    #     "s3://braingeneers/ephys/2024-05-07-e-e14_dorsal_pasca/",
    #     "s3://braingeneers/ephys/2024-05-07-e-kh2_dorsal_pasca/"
    #     ]
    
    uuids = [
        "2024-05-04-e-sakura-day22and24",
        "2024-05-04-e-sakura-day22and24_dorothy",
        "2024-05-10-e-all_cell_lines_dorsal_pasca", 
        "2024-05-17-e-all_cell_lines_dorsal_pasca",
        "2024-05-21-e-all_cell_lines_dorsal_pasca", #sent job for new SNR params    # Downloaded some 
        "2024-05-07-e-c57bl6_dorsal_pasca",
        "2024-05-07-e-e14_dorsal_pasca",
        "2024-05-07-e-kh2_dorsal_pasca",
        "2024-05-24-e-all_cell_lines_dorsal_pasca",
        "2024-05-28-e-all_cell_lines_dorsal_pasca",
        "2024-05-31-e-all_cell_lines_dorsal_pasca",
        "2024-06-11-e-all_cell_lines_dorsal_pasca",
        "2024-06-14-e-all_cell_lines_dorsal_pasca",
        "2024-06-18-e-all_cell_lines_dorsal_pasca",
        "2024-06-19-e-sakura-ventral-day46", 
        "2024-06-21-e-all_cell_lines_dorsal_pasca", 
        "2024-06-21-e-cady-sakura-dorsal-ventral", 
        # "2024-06-21-e-sakura-dorsa-ventral/"  ###always breaks when sorting
        "2024-03-20-e-auto-mouse-slice-22542",
        "2024-02-06-e-auto-mouse-slice2",
        "2024-01-31-e-auto-mouse-slice",
        "2024-04-04-e-p001384-pharma-reupload",
        "2024-02-09-e-pharma1-20380-HS",
        "2024-07-01-e-sakura-drugs-22194",
        "2024-06-24-e-sakura-drugs-22097", 
        "2024-06-25-e-all_cell_lines_dorsal_pasca", 
        "2024-06-28-e-all_cell_lines_dorsal_pasca",
        "2024-07-01-e-sakura-drugs-22717",
        "2024-07-02-e-all_cell_lines_dorsal_pasca", 
        "2024-07-02-e-sakura-drugs-20174a",
        "2024-07-02-e-sakura-drugs-20264",
        "2024-07-03-e-sakura-drugs-21985",
        "2024-06-25-e-sakura-drugs-20247",
        "2024-07-05-e-all_cell_lines_dorsal_pasca",
        '2024-09-04-e-ventral_day48/', ##
        '2024-08-23-e-', ##ventral day 38 and 48 
        '2024-08-21-e-ventral_day36',
         '2024-08-23-e-ventral_day38',
         '2024-08-26-e-ventral_day41',
          '2024-08-30-e-ventral_day45',
          '2024-09-04-e-ventral_day48',
          '2024-09-04-e-ventral_day50',
          '2024-09-06-e-ventral_day52',
          '2024-09-13-e-ventral_day57',
          '2024-03-29-e-interneurons_44',
          '2024-04-10-e-interneurons_56',
          '2024-04-11-e-interneurons-pasca-57',
          '2024-11-04-e-ventral_day44',
          '2024-10-25-e-ventral-day33',
        #   '2023-02-20-ventOrg',
    ]


# potentially more org drug stuff if needed
# 2024-03-22-e-/



    add_s3_paths = True

    dfs = []  # list to hold individual dataframes
    if add_s3_paths== True:
        for uuid in uuids:  
            print(f"retrieving data for 'uuid': {uuid}")
            metadata = ephys.load_metadata(uuid)
            experiment_names = [exp['name'] for exp in metadata['ephys_experiments'].values()]
            experiment_dates = [exp['blocks'][0]['timestamp'] if 'blocks' in exp and len(exp['blocks']) > 0 and 'timestamp' in exp['blocks'][0] else None for exp in metadata['ephys_experiments'].values()]
            data = {
                'uuids': [uuid] * len(experiment_names),
                'experiment_name': experiment_names,
                'experiment_date': experiment_dates,
                'sample_type': [metadata['notes']['biology']['sample_type']] * len(experiment_names),
                'species': [metadata['notes']['biology']['species']] * len(experiment_names),
                'cell_line': [metadata['notes']['biology']['cell_line']] * len(experiment_names),
                'agg_date': [metadata['notes']['biology']['aggregation_date']] * len(experiment_names),
                'plating_date': [metadata['notes']['biology']['plating_date']] * len(experiment_names),
            }
            df = pd.DataFrame(data)
            dfs.append(df)

        # concatenate all the individual dataframes
        df = pd.concat(dfs, ignore_index=True)

    elif add_s3_paths == False:
        df = pd.read_csv('catalog_baseline.csv')
    



    
    # Convert 'experiment_date' and 'agg_date' to datetime
    df['experiment_date'] = pd.to_datetime(df['experiment_date'], errors='coerce')
    
    # Parse 'agg_date' with automatic format inference
    df['agg_date'] = pd.to_datetime(df['agg_date'], errors='coerce')
    
    # Create 'org_age' column
    df['org_age'] = df['experiment_date'] - df['agg_date']
    
    
    
    #code specific for the sakura baseline project
    
    # Define a dictionary where the keys are the uuids and the values are the correct agg_dates
    correct_agg_dates = {
        '2024-05-21-e-all_cell_lines_dorsal_pasca': '2024-04-09',
        '2024-05-10-e-all_cell_lines_dorsal_pasca': '2024-04-09',
        '2024-05-17-e-all_cell_lines_dorsal_pasca': '2024-04-09',
        '2024-05-24-e-all_cell_lines_dorsal_pasca': '2024-04-09',
        '2024-05-28-e-all_cell_lines_dorsal_pasca': '2024-04-09',
        '2024-05-31-e-all_cell_lines_dorsal_pasca': '2024-04-09',
    }
    
    # Convert the dates to datetime
    for uuid, date in correct_agg_dates.items():
        correct_agg_dates[uuid] = pd.to_datetime(date)
    
    # Update the agg_date for the specified uuids
    for uuid, date in correct_agg_dates.items():
        df.loc[df['uuids'] == uuid, 'agg_date'] = date
    
    # Recalculate the 'org_age' column
    df['org_age'] = df['experiment_date'] - df['agg_date']
    
    
    #correct the cell lines for specific uuids
    correct_cell_lines = {
        '2024-05-04-e-sakura-day22and24_dorothy': 'e14 and kh2',
    }
    # Update the cell_line for the specified uuids
    for uuid, cell_line in correct_cell_lines.items():
        df.loc[df['uuids'] == uuid, 'cell_line'] = cell_line
    
    #update the cell lines by parsing names
    df['cell_line'] = df['cell_line'].replace('e14', 'E14')
    df['cell_line'] = df['cell_line'].replace('kh2', 'KH2')
    df['cell_line'] = df['cell_line'].replace('c57bl6', 'C57BL6')
    df['cell_line'] = df['cell_line'].replace('c57', 'C57BL6')
    
    mask = df['experiment_name'].str.contains('c57bl6|C57BL6|"C57,|C57')
    df.loc[mask, 'cell_line'] = 'C57BL6'
    mask = df['experiment_name'].str.contains('e14|E14|E14"')
    df.loc[mask, 'cell_line'] = 'E14'
    mask = df['experiment_name'].str.contains('kh2|KH2|KH2,')
    df.loc[mask, 'cell_line'] = 'KH2'
    
    #individual fix for cell line
    df.loc[df['experiment_name'] == 'Trace_20240504_12_42_01_22064_day22_ventral', 'cell_line'] = 'KH2'
    
    #individual fix for age
    df.loc[df['experiment_name'] == 'Trace_20240510_11_55_52_20264_28_ventral_kh2', 'org_age'] = pd.to_timedelta('28 days')
    df.loc[df['experiment_name'] == 'Trace_20240510_11_19_56_22717_28_dorsa_kh2', 'org_age'] = pd.to_timedelta('28 days')
    
    #Change the sample type from "mouse organoid" to "organoid"
    df['sample_type'] = df['sample_type'].replace('mouse organoid', 'organoid')
    #if the string gfcdm is in sample_type add gfcdm to a new column: media 
    df.loc[df['sample_type'].str.contains('gfcdm'), 'media'] = 'gfcdm'
    #if slice is in the sample_type change species to mouse
    df.loc[df['sample_type'].str.contains('slice'), 'species'] = 'mouse'
    
    
    #if organoid string is in sample_type change to organoid
    df.loc[df['sample_type'].str.contains('organoid'), 'species'] = 'organoid'
    
    
    #Make a new column that has dorsal and ventral if dorsal or ventral is in experiment name 
    df['patterning'] = df['experiment_name'].apply(lambda x: 'dorsal' if 'dorsa' in x.lower() else 'ventral' if 'ventral' in x.lower() else 'unknown')

    
    #manually change patterning
    df.loc[df['experiment_name'] == 'Trace_20240510_11_19_56_22717_28_dorsal_kh2', 'patterning'] = 'dorsal'
    
    #manually change the uuid to mouse slice
    df.loc[df['uuids'] == '2024-01-31-e-auto-mouse-slice/', 'sample_type'] = 'P0 mouse slice'
    
    #if the string slice is in sample_type change to cell line to C57BL6
    df.loc[df['sample_type'].str.contains('slice'), 'cell_line'] = 'C57BL6'
    
    #if the string day26 is in experiment_name change age to 26 days
    df.loc[df['experiment_name'].str.contains('day26'), 'org_age'] = pd.to_timedelta('26 days')
    # df.loc[df['experiment_name'].str.contains('day27'), 'org_age'] = pd.to_datetime('27 days')

    # if the string day42 is in experiment_name change age to 42 days
    df.loc[df['experiment_name'].str.contains('day42'), 'org_age'] = pd.to_timedelta('42 days')
    
    #if this string is in the experiment name take out of the dataframe
    df = df[~df['experiment_name'].str.contains('Trace_20240327_13_09_43_p001384')]

    # if string 'pasca' is in the experiment name change the media to sakura
    df.loc[df['experiment_name'].str.contains('pasca'), 'media'] = 'sakura'

    # if string ventral is in experiment name change the media to sakura
    df.loc[df['experiment_name'].str.contains('ventral'), 'media'] = 'sakura'

    # if string nosynaptic is in experiment name chagne the drug to nbqx
    df.loc[df['experiment_name'].str.contains('nosynaptic'), 'drug'] = 'nbqx + apv + gabazine'


    # if string interneurons is in uuids change the media to sakura and the patterning to ventral 
    df.loc[df['uuids'].str.contains('interneurons'), 'media'] = 'sakura'
    df.loc[df['uuids'].str.contains('interneurons'), 'patterning'] = 'ventral'
    
    #add a drug column
    #if the drug contains upper or lower case gabazine put in drug column gabazine 
    df.loc[df['experiment_name'].str.contains('gabazine', case=False), 'drug'] = 'gabazine'
    #if the drug contains upper or lower case bicuculline put in drug column bicuculline
    df.loc[df['experiment_name'].str.contains('bicuculline', case=False), 'drug'] = 'bicuculine'
    #if the drug contains upper or lower case apv put in drug column apv
    df.loc[df['experiment_name'].str.contains('apv', case=False), 'drug'] = 'apv'
    #if the drug contains upper or lower case dmso put in drug column dmso
    df.loc[df['experiment_name'].str.contains('dmso', case=False), 'drug'] = 'dmso'
    #if the string contains upper or lower case cch put in drug column carbachol
    df.loc[df['experiment_name'].str.contains('cch', case=False), 'drug'] = 'carbachol'
    #if the string contains upper or lower case baseline or bl put in drug column baseline
    df.loc[df['experiment_name'].str.contains('baseline', case=False), 'drug'] = 'baseline'
    #if the string contains upper or lower case nbqx put in drug column nbqx
    df.loc[df['experiment_name'].str.contains('nbqx', case=False), 'drug'] = 'nbqx'
    #if the string contains upper or lower case dopamine put in drug column dopamine
    df.loc[df['experiment_name'].str.contains('dopamine', case=False), 'drug'] = 'dopamine'
    #if the string contains upper or lower case gaba put in drug column gaba
    df.loc[df['experiment_name'].str.contains('gaba', case=False), 'drug'] = 'gaba'
    df.loc[df['experiment_name'].str.contains('carbachol', case=False), 'drug'] = 'carbachol'
    
    
    #if it is a specific uuid change species to mouse
    df.loc[df['uuids'] == '2024-01-31-e-auto-mouse-slice/', 'species'] = 'mouse'
    df.loc[df['uuids'] == '2024-04-04-e-p001384-pharma-reupload/', 'species'] = 'mouse'
    
    #if the string gfcdm is in media change the patterning to dorsal 
    df.loc[df['media'] == 'gfcdm', 'patterning'] = 'dorsal'
    
    #if it is a specific uuid change the plating_date to 3/9/2024
    df.loc[df['uuids'] == '2024-03-20-e-auto-mouse-slice-22542/', 'plating_date'] = pd.to_datetime('2024-03-09')
    
    #add sakura to the media column
    df.loc[df['uuids'].str.contains('pasca|sakura', case=False), 'media'] = 'sakura'

    #if the chip in is the list to catch any that are not in the right naming convention 
    list_of_chips = ['21985', '22717', '20264', '22064', '22194', '20402', '23150', '23178', '23156', 
                    '23120', '23187', '23139','22710', '23141', '23137', '23215', '23179', '23124',
                    '22542', '20215', '20380', 'p001384', '20174a', 'p001354', '20247', '25244',
                    '25136', '23117b', '23117f', '23117F', '23117d', '25126d', '25158', '25123', '23154', 
                    '25126', '25122', '22064b', '22150b', '22097', '23119a', '22150a', '23196', 
                    '23119','23196', '23149']

    def extract_chip_number(experiment_name):
        # First, try to find the chip number using regex for patterns like "chip22542"
        match = re.search(r'chip(\d+)', experiment_name)
        if match:
            return match.group(1)
        
        # If that doesn't work, try to find any number from the list_of_chips
        for chip in list_of_chips:
            if chip in experiment_name:
                return chip
        
        # If still no match, try to find any number at the start of the string
        match = re.search(r'^\d+', experiment_name)
        if match:
            return match.group()
        
        # If no match is found, return None or a placeholder
        return None  # or 'N/A'
    

    # Apply the function to the 'experiment_name' column
    df['chip_number'] = df['experiment_name'].apply(extract_chip_number)

    # Fill None values in 'chip_number' with a placeholder
    df['chip_number'] = df['chip_number'].fillna('unknown')

    # Convert 'experiment_date' to datetime
    df['experiment_date'] = pd.to_datetime(df['experiment_date'])

    # Iterate through all the chips in the sakura catalog
    for chips in df['chip_number'].unique():
        chip_catalog = df[df['chip_number'] == chips]

        # Check if the chip number already ends with 'd' or 'e'
        if chips.endswith('d') or chips.endswith('e'):
            continue

        # If the chip has a date before 5/31/2024 it should be treated as a separate chip so add a 'd' to the end of the chip number
        # If the chip has a date after 5/31/2024 it should be treated as a separate chip so add a 'e' to the end of the chip number
        if chip_catalog['experiment_date'].max() < pd.to_datetime('2024-05-31'):
            df.loc[df['chip_number'] == chips, 'chip_number'] = chips + 'd'
        else:
            df.loc[df['chip_number'] == chips, 'chip_number'] = chips + 'e'

    # Display the first few rows of the result
    print(df[['experiment_name', 'chip_number']].head())

    

        
    
    # Save the DataFrame to a CSV file
    df.to_csv('../analysis/orgs/general_analysis/catalog_baseline.csv', index=False)
    
    