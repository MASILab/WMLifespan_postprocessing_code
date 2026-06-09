import pandas as pd
import json
from pathlib import Path
import numpy as np
import argparse

#### Part 1
def get_fswm_metrics(fswm_dir):
    """
    Given a fswm directory, get the measures
    """

        #get the nested dictionary values into a flat dictionary
    def flatten(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            if "dwmri%" in k:
                k2 = k.replace("dwmri%", "")
                k2 = k2.replace(".nii.gz", "")
                new_key = parent_key + sep + k2 if parent_key else k2
            else:
                new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    #get the sub,ses,scan
    #metrics_file = Path('/fs5/p_masi/kimm58/WMLifespan/data/FreesurferWhiteMatterMask/AOMIC/results/sub-ID1000x0001/FreesurferWhiteMatterMask/metrics.json')
    metrics_file = fswm_dir/'metrics.json'
    if not metrics_file.exists():
        print(f"The metrics file {str(metrics_file)} does not exist")
        return {}

    #read the json file
    row = {}
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)

    flat_metrics = flatten(metrics)
    row.update(flat_metrics)
    return row

#### Part 2
def get_DTI_jsons(tractseg_dir):
    """
    Given the path to a tractseg directory, return the paths to the DTI json files
    """

    measures_dir = tractseg_dir / "measures"
    #dti_measures_dir = tractseg_dir / "dti"
    measures = measures_dir.glob("*SHAPE.json")
    dti_measures = measures_dir.glob("*DTI.json")

    return list(measures), list(dti_measures)

def parse_DTI_json(json_file):
    """
    Given the path to a DTI json file, return a dictionary of the metrics
    """

    #print("parsing")

    try:
        with open(json_file, "r") as f:
            data = json.load(f)

    except:
        tract = json_file.name.split('-DTI.json')[0]
        row = {}
        for subkey in ['fa', 'md', 'ad', 'rd']:
            row[tract+'-'+subkey+'-mean'] = None
            row[tract+'-'+subkey+'-std'] = None
        return row

    #get the only key (the tract)
    tract = list(data.keys())[0]
    data = data[tract]
    #create the new dictionary
    row = {}
    for subkey in ['fa', 'md', 'ad', 'rd']:
        #print(data['dwmri_tensor_{}_1mm_iso'.format(subkey)])
        row[tract+'-'+subkey+'-mean'] = data['{}_1mm'.format(subkey)]['mean']
        row[tract+'-'+subkey+'-std'] = data['{}_1mm'.format(subkey)]['std']
    #print(row)
    return row

def parse_shape_json(json_file):

    #test_shape = "/nfs2/harmonization/THICKNESS/sub-HCA7410559/tractseg/measures/UF_right.json"
    tract = Path(json_file).name.split('-SHAPE.')[0]
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
            #print(data)

    except:
        row = {}
        for key in ['volume', 'volume_endpoints', 'streamlines_count', 'avg_length', 'std_length', 'min_length', 'max_length', 'span', 'curl', 'diameter', 'elongation', 'surface_area', 'end_surface_area_head', 'end_surface_area_tail', 'radius_head', 'radius_tail', 'irregularity', 'irregularity_of_end_surface_head', 'irregularity_of_end_surface_tail', 'mean_curvature', 'fractal_dimension']:
            row[tract+'-'+key] = None
        return row

    row = {}

    for key, value in data.items():
        try:
            row[tract+'-'+key] = value[0]
        except:
            print("Error with key: {}".format(key))
            print(json_file)
            print(value)
            row[tract+'-'+key] = value[0]
    
    return row

def get_tractseg_metrics(tractseg_dir):
    """
    Given a tractseg directory, get the DTI measures
    """

    rowdict = {}

    measures_jsons, dti_jsons = get_DTI_jsons(tractseg_dir)
    dti_data_dicts = [parse_DTI_json(x) for x in dti_jsons]
    #print(dti_data_dicts)
    shape_data_dicts = [parse_shape_json(x) for x in measures_jsons]
    #combine all dictionaries into a single one
    dti_data = {k: v for d in dti_data_dicts for k, v in d.items()}
    shape_data = {k: v for d in shape_data_dicts for k, v in d.items()}

    #combine the shape and dti data into a single dictionary
    rowdict.update(dti_data)
    #print(rowdict.keys())
    rowdict.update(shape_data)
    #print(rowdict.keys())

    return rowdict

#### Part 3
def create_normalizing_metrics(df, column, prefix):
    """
    Given a dataframe and a column that represents a measure of volume, create new columns that represent the radius and surface area of the volume
    """

    vol_col = prefix + '_Volume'
    sa_col = prefix + '_SurfaceArea'
    r_col = prefix + '_Radius'

    #calcualte the normalizing metrics
    df[vol_col] = df[column]
    #df[r_col] = df[vol_col].apply(lambda x: (3*x/(4*np.pi))**(1/3))
    #df[sa_col] = df[r_col].apply(lambda x: 4*np.pi*x**2)
    df[r_col] = (3*df[vol_col]/(4*np.pi))**(1/3)
    df[sa_col] = 4*np.pi*df[r_col]**2
    return df

def normalize_column_values(df, normalizing_column, type='Volume'):
    """
    Given a dataframe, a column to normalize by, and a column to normalize, normalize the column by the normalizing column
    """

    def normalize_row(row, col, norm_col, new_col_name):
        row[new_col_name] = row[col]/row[norm_col]
        return row

    #based on the type, get the columns we need to normalize
    if type == 'Volume':
        #cols = [x for x in df.columns if x.endswith('-volume')]
        cols = [x for x in df if x.endswith('-volume')]
    elif type == 'SurfaceArea':
        cols = [x for x in df if x.endswith('-surface_area')]
    elif type == 'Radius':
        cols = [x for x in df if x.endswith('-avg_length')]
    
    #normalize the columns
    for col in cols:
        new_col_name = col + '_' + normalizing_column + '_normalized'
        #df[new_col_name] = df.apply(lambda x: normalize_row(x, col, normalizing_column), axis=1)
        df = normalize_row(df, col, normalizing_column, new_col_name)
    
    return df

def get_normalized_measurements(row):
    """
    Calculate normalized macrostructural measurements for all the tracts
    """
    normalizing_metrics = ['freesurfer_metrics_Estimated_Total_Intracranial_Volume', 'freesurfer_metrics_Total_cerebral_white_matter_volume', 'freesurfer_metrics_Brain_Segmentation_Volume_Without_Ventricles']
    normalizing_prefixes = ['TICV', 'WhiteMatter', 'BrainNoVentricles']
    for metric,prefix in zip(normalizing_metrics, normalizing_prefixes):
        row = create_normalizing_metrics(row, metric, prefix)

    #normalize the columns by the three different ways
    for metric,prefix in zip(normalizing_metrics, normalizing_prefixes):
        row = normalize_column_values(row, prefix + '_Volume', type='Volume')
        row = normalize_column_values(row, prefix + '_SurfaceArea', type='SurfaceArea')
        row = normalize_column_values(row, prefix + '_Radius', type='Radius')
    
    return row

### Main code

def pa():
    p = argparse.ArgumentParser()
    p.add_argument("--fswm_dir", type=str, default="/OUTPUTS/FreesurferWhiteMatterMask")
    p.add_argument("--tractseg_dir", type=str, default="/OUTPUTS/Tractseg")
    p.add_argument("--outfile", type=str, default="/OUTPUTS/measurements.csv")
    return p.parse_args()

args = pa()
fswm_dir = Path(args.fswm_dir)
tractseg_dir = Path(args.tractseg_dir)
outfile = Path(args.outfile)

#1.) Aggregate the global measurements
fswm_measures_dict = get_fswm_metrics(fswm_dir)
fswm_error=False
if fswm_measures_dict == {}:
    fswm_error=True

#2.) Aggregate the 72 tract measurements
tractseg_dict = get_tractseg_metrics(tractseg_dir)

#3.) Calculate the normalized macrostructural measurements
#combine the existing dicts
if not fswm_error:
    combined_dict = {**tractseg_dict, **fswm_measures_dict}
    combined_dict = get_normalized_measurements(combined_dict)
else:
    print("WARNING: Could not find FSWM mask measurements. Global and normalized measurements are likely missing.")
    combined_dict = tractseg_dict

#4.) Output the dict as a csv
df = pd.DataFrame.from_dict({'row': combined_dict}, orient='index')
df.to_csv(outfile, index=False)
