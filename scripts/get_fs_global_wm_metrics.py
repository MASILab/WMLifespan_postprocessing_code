#!/usr/local/bin/python3
import nibabel as nib
import numpy as np
import argparse
from pathlib import Path
import subprocess
import json
import os

def make_LAS(nii):
    """
    Given a nibabel image, return the LAS orientated image
    """
    #get the data
    data = nii.get_fdata()
    #get the affine
    aff = nii.affine
    #get the orientation
    orient = nib.aff2axcodes(aff)
    #if the orientation is not LAS, flip the data
    if orient != ('L', 'A', 'S'):
        data = np.flip(data, axis=0)
        data = np.flip(data, axis=1)
        aff = np.array(aff)
        aff[0,0] = -aff[0,0]
        aff[1,1] = -aff[1,1]
    #return the new image
    return nib.Nifti1Image(data, aff)

#aseg.presurf.mgz

def create_wm_mask(fs_wmseg, output_file):
    """
    Given the freesurfer aseg.presurf.mgz, create a binary mask of the WM
    """

    talaraich_wm_labels = {2: "Left-Cerebral-White-Matter", 7: "Left-Cerebellum-White-Matter", 41: "Right-Cerebral-White-Matter", 46: "Right-Cerebellum-White-Matter", 77: "WM_hypointensities", 78: "Left_WM_hypointensities", 79: "Right_WM_hypointensities",
                            251: "CC_Posterior", 252: "CC_Mid_Posterior", 253: "CC_Central", 254: "CC_Mid_Anterior", 255: "CC_Anterior", 16: "Brain_Stem", 28: "Left_Ventral_Dorsal_Column", 60: "Right_Ventral_Dorsal_Column",
                            250: "Fornix", 85: "Optic_Chiasm",
                            170: "brainstem", 171: "DCG", 172:"Vermis", 173: "Midbrain", 174: "Pons", 175: "Medulla"}

    #wm_mask = Path(fs_dir) / 'freesurfer'/'mri'/'wm.seg.mgz'
    assert Path(fs_wmseg).exists(), f'File {fs_wmseg} does not exist'
    #assert Path(t1).exists(), f'File {t1} does not exist'
    #t1_affine = nib.load(t1).affine
    wm_nii = nib.load(fs_wmseg)
    #wm_nii = make_LAS(wm_nii) #wont need because we need to run the mri_vol2vol command to get labels back into native space
    wm_data = wm_nii.get_fdata()

    #binarize based on the labels
    wm_mask = np.isin(wm_data, list(talaraich_wm_labels.keys())).astype(int)

    #save
    wm_mask_nii = nib.Nifti1Image(wm_mask.astype(int), wm_nii.affine, dtype=np.int8)
    nib.save(wm_mask_nii, output_file)

def create_wm_mask(fs_wmseg, output_file, mask_type='all'):
    """
    Given the freesurfer wmparc.mgz, create a binary mask of the WM
    """

    if mask_type == 'all':
        talaraich_wm_labels = {2: "Left-Cerebral-White-Matter", 7: "Left-Cerebellum-White-Matter", 41: "Right-Cerebral-White-Matter", 46: "Right-Cerebellum-White-Matter", 77: "WM_hypointensities", 78: "Left_WM_hypointensities", 79: "Right_WM_hypointensities",
                            251: "CC_Posterior", 252: "CC_Mid_Posterior", 253: "CC_Central", 254: "CC_Mid_Anterior", 255: "CC_Anterior", 16: "Brain_Stem", 28: "Left_Ventral_Dorsal_Column", 60: "Right_Ventral_Dorsal_Column",
                            250: "Fornix", 85: "Optic_Chiasm",
                            170: "brainstem", 171: "DCG", 172:"Vermis", 173: "Midbrain", 174: "Pons", 175: "Medulla"}
    elif mask_type == 'brainstem':
        talaraich_wm_labels = {16: "Brain_Stem", 171: "DCG", 172:"Vermis", 173: "Midbrain", 174: "Pons", 175: "Medulla", 170: "brainstem"} # brainstem only
    else:
        #no brainstem or cerebellum, but does include the ventral dorsal columns because the WM surface files from freesurfer include them
        talaraich_wm_labels = {2: "Left-Cerebral-White-Matter", 41: "Right-Cerebral-White-Matter", 77: "WM_hypointensities", 78: "Left_WM_hypointensities", 79: "Right_WM_hypointensities",
                            251: "CC_Posterior", 252: "CC_Mid_Posterior", 253: "CC_Central", 254: "CC_Mid_Anterior", 255: "CC_Anterior", 28: "Left_Ventral_Dorsal_Column", 60: "Right_Ventral_Dorsal_Column",
                            250: "Fornix", 85: "Optic_Chiasm",
                            } 

    #wm_mask = Path(fs_dir) / 'freesurfer'/'mri'/'wm.seg.mgz'
    assert Path(fs_wmseg).exists(), f'File {fs_wmseg} does not exist'
    #assert Path(t1).exists(), f'File {t1} does not exist'
    #t1_affine = nib.load(t1).affine
    wm_nii = nib.load(fs_wmseg)
    #wm_nii = make_LAS(wm_nii) #wont need because we need to run the mri_vol2vol command to get labels back into native space
    wm_data = wm_nii.get_fdata()

    #binarize based on the labels
    if mask_type == 'brainstem':
        wm_mask = np.isin(wm_data, list(talaraich_wm_labels.keys())).astype(int)
    else:
        wm_mask = (np.isin(wm_data, list(talaraich_wm_labels.keys())) | (wm_data > 2999)).astype(int)

    #save
    try:
        wm_mask_nii = nib.Nifti1Image(wm_mask.astype(int), wm_nii.affine, dtype=np.int8)
    except:
        wm_mask_nii = nib.Nifti1Image(wm_mask.astype(int), wm_nii.affine)
    nib.save(wm_mask_nii, output_file)

    #get the volume
    zooms = wm_nii.header.get_zooms()[:3]
    volume = np.sum(wm_mask) * np.prod(zooms)
    return volume

def get_average_metrics(mask, mask_cerebral, mask_brainstem, prequal_mask, metrics, aseg_stats, outfile, **kwargs):
    """
    Given a WM mask (and a cerebral only WM mask), a PreQual mask, and a list of scalar, outputs a json file that contains the average value of each metric in the WM mask
    - all voxels considered must be in the WM mask AND the PreQual mask (intersection between the two)

    Also gets the brain volume estimates from the aseg.stats file
    """

    def parse_aseg_stats(aseg_stats):
        #get only the lines that have "Measure" in them
        with open(aseg_stats, 'r') as f:
            aseg_stats = f.readlines()
        aseg_stats = [line.strip() for line in aseg_stats if 'Measure' in line]
        #now, split the lines by the comma
        aseg_stats = [line.split(',') for line in aseg_stats]
        #now, create a dictionary
        aseg_dict = {'_'.join(line[-3].strip().split(' ')): float(line[-2]) for line in aseg_stats}
        return {'freesurfer_metrics': aseg_dict}

    #get the brain volume estimates
    metrics_dict = parse_aseg_stats(aseg_stats)

    #load the masks
    wm_mask = nib.load(mask).get_fdata()
    wm_mask_cerebral = nib.load(mask_cerebral).get_fdata()
    wm_mask_brainstem = nib.load(mask_brainstem).get_fdata()
    pq_mask = nib.load(prequal_mask).get_fdata()

    #get the intersection
    mask = (wm_mask > 0) & (pq_mask > 0)
    mask_cerebral = (wm_mask_cerebral > 0) & (pq_mask > 0)
    mask_brainstem = (wm_mask_brainstem > 0) & (pq_mask > 0)

    #now, loop through the metrics and get the average value
    for mask_type, mask_data, volume in [('wm_all', mask, kwargs['all_wm_volume']), ('wm_cerebral', mask_cerebral, kwargs['cerebral_wm_volume']), ('wm_brainstem', mask_brainstem, kwargs['brainstem_volume'])]:
        mask_dict = {}
        for metric in metrics:
            metric_data = nib.load(metric).get_fdata()
            metric_data = metric_data[mask_data]
            for metric_suff, value in [('_mean',np.nanmean(metric_data)), ('_std',np.nanstd(metric_data)), ('_median', np.nanmedian(metric_data))]:
                metric_name = metric.name + metric_suff
                mask_dict[metric_name] = value
            #also the volume from the mask
            mask_dict['volume'] = volume
        metrics_dict[mask_type] = mask_dict

    #save the metrics dictionary to a json file
    with open(outfile, 'w') as f:
        json.dump(metrics_dict, f, indent=4)


if __name__ == '__main__':

    print("MAKE SURE that you have provided the freesurfer license at /usr/local/freesurfer/.license")

    parser = argparse.ArgumentParser()
    #parser.add_argument('t1', help='t1 file')
    #parser.add_argument('input_dir', help='Input directory')
    parser.add_argument('fs_wmseg', help='Freesurfer wmseg file - wmparc.mgz')
    parser.add_argument('raw_avg_t1', help='raw t1 in native space - rawavg.mgz')
    parser.add_argument('t1_dwi_transform', help='t1 to dwi transform - dwmri%ANTS_t1tob0.txt')
    parser.add_argument('fa', help='FA map')
    parser.add_argument('md', help='MD map')
    parser.add_argument('ad', help='AD map')
    parser.add_argument('rd', help='RD map')
    parser.add_argument('PreQual_mask', help='PreQual mask file')
    parser.add_argument('aseg_stats', help='aseg.stats file for brain volume estimates')
    parser.add_argument('output_dir', help='Output directory')
    #parser.add_argument('--freesurfer_license_path', help='Path to the freesurfer license file', default='/nfs2/harmonization/singularities/FreesurferLicense.txt')
    args = parser.parse_args()

    #input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    #wmparc = Path(args.fs_wmseg).resolve()
    wmparc = Path(args.fs_wmseg)
    output_file = output_dir / 'metrics.json'
    #rawavg = Path(args.raw_avg_t1).resolve()
    #transform = Path(args.t1_dwi_transform).resolve()
    fa = Path(args.fa).resolve()
    md = Path(args.md).resolve()
    ad = Path(args.ad).resolve()
    rd = Path(args.rd).resolve()
    prequal_mask = Path(args.PreQual_mask).resolve()
    aseg_stats = Path(args.aseg_stats).resolve()
    rawavg = Path(args.raw_avg_t1)
    transform = Path(args.t1_dwi_transform)
    #fa = args.fa
    #md = args.md
    #ad = args.ad
    #rd = args.rd
    #prequal_mask = args.PreQual_mask
    #aseg_stats = args.aseg_stats
    #freesurfer_license = Path(args.freesurfer_license_path).resolve()

    assert output_dir.exists() and output_dir.is_dir(), f'Directory {output_dir} does not exist or is not a directory'
    assert wmparc.exists(), f'File {wmparc} does not exist'
    assert rawavg.exists(), f'File {rawavg} does not exist'
    assert transform.exists(), f'File {transform} does not exist'
    assert fa.exists(), f'File {fa} does not exist'
    assert md.exists(), f'File {md} does not exist'
    assert ad.exists(), f'File {ad} does not exist'
    assert rd.exists(), f'File {rd} does not exist'
    assert prequal_mask.exists(), f'File {prequal_mask} does not exist'
    assert aseg_stats.exists(), f'File {aseg_stats} does not exist'
    assert not output_file.exists(), f'File {output_file} already exists'
    #assert freesurfer_license.exists(), f'File {freesurfer_license} does not exist'

    #fs_license = f'-B {freesurfer_license.resolve()}:/usr/local/freesurfer/license.txt'
    outdir_bind = f"-B {output_dir}:{output_dir}"

    #Step 1: first, create the wm mask(s)
    temp = output_dir / 'wm_mask.mgz'
    all_wm_volume = create_wm_mask(wmparc, temp)
    temp_cerebral = output_dir / 'wm_mask_cerebralonly.mgz'
    cerebral_wm_volume = create_wm_mask(wmparc, temp_cerebral, mask_type='cerebral')
    temp_brainstem = output_dir / 'wm_mask_brainstem.mgz'
    brainstem_volume = create_wm_mask(wmparc, temp_brainstem, mask_type='brainstem')

    #Step 2: next, run the mri_vol2vol command to get the label(s) back into native space
    #
    temp_native = output_dir / 'wm_mask_native.nii.gz'
    cmd = f"mri_label2vol --seg {temp} --temp {rawavg} --o {temp_native} --regheader {temp}"
    #cmd = f"singularity exec -e --contain -B /tmp:/tmp {outdir_bind} {fs_license} /nfs2/harmonization/singularities/freesurfer_7.2.0.sif {cmd}"
    subprocess.run(cmd, shell=True, check=True)
    #
    temp_native_cerebral = output_dir / 'wm_mask_native_cerebralonly.nii.gz'
    cmd = f"mri_label2vol --seg {temp_cerebral} --temp {rawavg} --o {temp_native_cerebral} --regheader {temp_cerebral}"
    #cmd = f"singularity exec -e --contain -B /tmp:/tmp {outdir_bind} {fs_license} /nfs2/harmonization/singularities/freesurfer_7.2.0.sif {cmd}"
    subprocess.run(cmd, shell=True, check=True)
    #
    temp_native_brainstem = output_dir / 'wm_mask_native_brainstem.nii.gz'
    cmd = f"mri_label2vol --seg {temp_brainstem} --temp {rawavg} --o {temp_native_brainstem} --regheader {temp_brainstem}"
    #cmd = f"singularity exec -e --contain -B /tmp:/tmp {outdir_bind} {fs_license} /nfs2/harmonization/singularities/freesurfer_7.2.0.sif {cmd}"
    subprocess.run(cmd, shell=True, check=True)

    #remove the temp files from step 1
    os.remove(temp)
    os.remove(temp_cerebral)
    os.remove(temp_brainstem)

    #Step 3: apply the transform to the wm mask(s) to get it into the DWI space
    #
    dwi_wm_mask = output_dir / 'wm_mask_dwi.nii.gz'
    cmd = f"antsApplyTransforms -d 3 -i {temp_native} -r {fa} -n NearestNeighbor -t {transform} -o {dwi_wm_mask}"
    #cmd = f"singularity exec -e --contain -B /tmp:/tmp {outdir_bind} /nfs2/harmonization/singularities/WMAtlas_v1.3.simg {cmd}"
    subprocess.run(cmd, shell=True, check=True)
    #
    dwi_wm_mask_cerebral = output_dir / 'wm_mask_dwi_cerebralonly.nii.gz'
    cmd = f"antsApplyTransforms -d 3 -i {temp_native_cerebral} -r {fa} -n NearestNeighbor -t {transform} -o {dwi_wm_mask_cerebral}"
    #cmd = f"singularity exec -e --contain -B /tmp:/tmp {outdir_bind} /nfs2/harmonization/singularities/WMAtlas_v1.3.simg {cmd}"
    subprocess.run(cmd, shell=True, check=True)
    #
    dwi_wm_mask_brainstem = output_dir / 'wm_mask_dwi_brainstem.nii.gz'
    cmd = f"antsApplyTransforms -d 3 -i {temp_native_brainstem} -r {fa} -n NearestNeighbor -t {transform} -o {dwi_wm_mask_brainstem}"
    #cmd = f"singularity exec -e --contain -B /tmp:/tmp {outdir_bind} /nfs2/harmonization/singularities/WMAtlas_v1.3.simg {cmd}"
    subprocess.run(cmd, shell=True, check=True)

    #step 3.5: compute the brain volume estimates from the mask(s)
        #done in step 1

    #Step 4: get the metrics (including the brain volumes)
    get_average_metrics(dwi_wm_mask, dwi_wm_mask_cerebral, dwi_wm_mask_brainstem, prequal_mask, [fa, md, ad, rd], aseg_stats, output_file, all_wm_volume=all_wm_volume, cerebral_wm_volume=cerebral_wm_volume, brainstem_volume=brainstem_volume)

