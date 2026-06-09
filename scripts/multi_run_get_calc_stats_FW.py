from pathlib import Path
import os
from tqdm import tqdm
import subprocess
from multiprocessing import Pool, cpu_count


def run_scripts(line):
    #PQdir = Path(line.strip())
    FW_dir = Path(line)
    sub = FW_dir.parent.parent.name
    ses = FW_dir.parent.name
    suffix = FW_dir.name.split('freewater')[1]

    #get the path to the FW directory
    dataset_name = FW_dir.parent.parent.parent.parent.name
    dataset_name_FW = dataset_name
    # if dataset_name == "ADNI_DTI":
    #     dataset_name_FW = "ADNI"
    #FW_dir = Path("/nfs2/harmonization/raw/{}_Freewater/{}/{}{}/Pasternak_Freewater{}".format(dataset_name_FW, sub, ses, suffix, suffix))
    #if not FW_dir.exists():
    #    #try adding the suffix within another level
    #    FW_dir = Path("/nfs2/harmonization/raw/{}_Freewater/{}/{}/Pasternak_Freewater{}".format(dataset_name_FW, sub, ses, suffix))
    #    #print(FW_dir)
    
    #FW_dirs.append(str(FW_dir))

    #get the path to the EVE reg
    derivs = Path("/nfs2/harmonization/BIDS/{}/derivatives".format(dataset_name))
    EVEdir = derivs/(sub)/(ses)/("WMAtlasEVE3{}".format(suffix))
    if not EVEdir.exists():
        DNE.append(str(FW_dir))
        return

    #inputs:
# p.add_argument('reg_atlas', type=str, help="Path to regisistered EVE3 atlas")
# p.add_argument('reg_slant', type=str, help="Path to registered SLANT labels")
# p.add_argument("FW_map_dir", type=str, help="Path to FW-corrected DTI maps")
# p.add_argument('atlas_labels', type=str, help="Path to regisistered EVE3 atlas LUT")
# p.add_argument('slant_labels', type=str, help="Path to registered SLANT LUT")
# p.add_argument('output_dir', type=str, help="Path to directory for outputs")

    atlas = EVEdir/("dwmri%Atlas_JHU_MNI_SS_WMPM_Type-III.nii.gz")
    slant = EVEdir/("dwmri%T1_seg_to_dwi.nii.gz")
    #FW_dir
    #atlas_labels
    #slant_labels
    output_dir = FW_dir.parent/("FW_DTI_scalars{}".format(suffix))
    if not output_dir.exists():
        os.mkdir(output_dir)

    fa = FW_dir/('freewater_single_fa.nii.gz') #FW_dir/("Pasternak_FW_corr_{}.nii.gz".format('FA'))
    md = FW_dir/('freewater_single_md.nii.gz') #FW_dir/("Pasternak_FW_corr_{}.nii.gz".format('MD'))
    ad = FW_dir/('freewater_single_ad.nii.gz') #FW_dir/("Pasternak_FW_corr_{}.nii.gz".format('AD'))
    rd = FW_dir/('freewater_single_rd.nii.gz') #FW_dir/("Pasternak_FW_corr_{}.nii.gz".format('RD'))
    fw = FW_dir/('freewater_single.nii.gz') #FW_dir/("Pasternak_FW.nii.gz")
    allexist = True
    for x in [fa, md, ad, rd, fw]:
        if not x.exists():
            allexist = False
            break
    
    if not allexist:
        DNE.append(str(FW_dir))
        return 

    FW_dirs.append(str(FW_dir))

    arguments = "{} {} {} {} {} {}".format(atlas, slant, FW_dir, atlas_labels, slant_labels, output_dir)
    cmd1 = "python3 FW-FA_calc_metrics_per_roi.py {}".format(arguments)
    #print(cmd1)
    #cmd2 = "python3 create_QA_png.py {}".format(arguments)

    #if not (output_dir/("dwmri_FWcorrected_wFreewater%diffusionmetrics.csv")).exists():
    if not (output_dir/('dwmri_FWcorrected%diffusionmetrics.csv')).exists():
        res1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True).stdout
        stdout1 = res1.strip().splitlines()
    else:
        stdout1 = []

    #if not (output_dir/("Atlas_JHU_MNI_SS_WMPM_Type-III.png")).exists():
    #    res2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True).stdout
    #    stdout2 = res2.strip().splitlines()
    #else:
    #    stdout2 = []

    stdout = stdout1 #+ stdout2
    with open(output_dir/('logs.txt'), 'w') as f:
        for item in stdout:
            f.write(item+"\n")

    #print(PQdir)
    #print(FW_dir)
    #print(EVEdir)
    #print(cmd1)
    #print(cmd2)
    #print(output_dir)

    #break
atlas_labels = "/nfs2/kimm58/AtlasInputs/Labels_JHU_MNI_SS_WMPM_Type-III.txt"
slant_labels = "/nfs2/kimm58/T1_TICV_seg.txt"

DNE = []
FW_dirs = []


### For freeze 3 (2025)

root = '/nfs2/harmonization/BIDS/'
subdirs = ['ADNI_DTI', 'FloridaADRC', 'Indiana']
deriv_dirs = [root + x + '/derivatives' for x in subdirs]
for deriv_dir,dataset in zip(deriv_dirs,subdirs):

    print(f"Running calculation of FW for {dataset}...")
    cmd = "find {} -mindepth 3 -maxdepth 3 -type d -name 'freewater*'".format(deriv_dir)
    fw_dirs = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip().splitlines()

    #dirs = dirs[200:220]
        
    with Pool(processes=19) as pool:
        results = list(tqdm(pool.imap(run_scripts, fw_dirs, chunksize=1), total=len(fw_dirs)))

    #write FW dirs to file
    with open(f'{dataset}_FW_dirs.txt', 'w') as f:
        for item in FW_dirs:
            f.write(item+"\n")

    #write missing ses to file
    with open(f'{dataset}_missing_FW.txt', 'w') as f:
        for item in DNE:
            f.write(item+"\n")

### For HABSHD (second freeze)

# habshd_derivs = Path("/nfs2/harmonization/BIDS/HABSHD/derivatives")

# cmd = "find {} -mindepth 3 -maxdepth 3 -type d -name 'freewater*'".format(habshd_derivs)
# fw_dirs = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip().splitlines()

#### For the First Freeze:

# whitelist = Path("/nfs2/liz79/adsp/QA/step4_whitelist.txt")
# #files = [(str(scriptsdir/("{}.sh".format(x))),str(logsdir/("{}.txt".format(x)))) for x in range(1, int(res)+1)]
# with open(whitelist, 'r') as f:
#     dirs = [x for x in f]

# #dirs = dirs[200:220]
    
# with Pool(processes=20) as pool:
#     results = list(tqdm(pool.imap(run_scripts, dirs, chunksize=1), total=len(dirs)))

# #write FW dirs to file
# with open('FW_dirs.txt', 'w') as f:
#     for item in FW_dirs:
#         f.write(item+"\n")

# #write missing ses to file
# with open('missing_FW.txt', 'w') as f:
#     for item in DNE:
#         f.write(item+"\n")

#/nfs2/kimm58/Freeze_10_1_24