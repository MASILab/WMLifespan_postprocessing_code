
if [[ -z $1 || -z $2 || -z $3 ]]; then
    echo "Usage: $0 <inputs_dir> <fs_dir> <outputs_dir>"
    exit 1
fi

inputs=$(readlink -f $1) #/INPUTS
fsdir=$(readlink -f $2) #/OUTPUTS/freesurfer
outputsdir=$(readlink -f $3) #/OUTPUTS/REG

##inputs
t1=${inputs}/T1.nii.gz
dwi=${inputs}/dwmri.nii.gz
bval=${inputs}/dwmri.bval
bvec=${inputs}/dwmri.bvec
fsbet=${fsdir}/mri/brainmask.mgz
rawavg=${fsdir}/mri/rawavg.mgz

##temp
tempbrain=${outputsdir}/brain.nii.gz
fsmask=${outputsdir}/fs_mask.nii.gz
b0=${outputsdir}/b0.nii.gz
t1bet=${outputsdir}/T1_bet.nii.gz

##outputs
fsl_transform="${outputsdir}/dwmri%FSL_t1tob0.mat"
fsl_inv_transform="${outputsdir}/dwmri%FSL_b0tot1"
converted_transform="${outputsdir}/dwmri%ANTS_t1tob0.txt"

##get the freesurfer brain mask back to native space
#mri_label2vol --seg brainmask.mgz --temp rawavg.mgz --o temp/brain.nii.gz --regheader brainmask.mgz
mri_label2vol --seg $fsbet --temp $rawavg --o $tempbrain --regheader $fsbet
#fslmaths brain.nii.gz -div brain.nii.gz t1_mask.nii.gz
fslmaths $tempbrain -div $tempbrain $fsmask
##extract the skull stripped t1
fslmaths $t1 -mul $fsmask $t1bet

##get the b0 image from the dwi
dwiextract ${dwi} -fslgrad ${bvec} ${bval} - -bzero | mrmath - mean ${b0} -axis 3
##run epireg
epi_reg --epi=${b0} --t1=${t1} --t1brain=${t1bet} --out=${fsl_inv_transform}

##convert to ANTs format
convert_xfm -omat ${fsl_transform} -inverse ${fsl_inv_transform}.mat
c3d_affine_tool -ref ${b0} -src ${t1} ${fsl_transform} -fsl2ras -oitk ${converted_transform}
