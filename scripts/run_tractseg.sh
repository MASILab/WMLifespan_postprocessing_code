
##inputs
dwi=/INPUTS/dwmri.nii.gz
bval=/INPUTS/dwmri.bval
bvec=/INPUTS/dwmri.bvec
mask=/INPUTS/mask.nii.gz
#scalars
fa=/OUTPUTS/DTI/fa.nii.gz
md=/OUTPUTS/DTI/md.nii.gz
ad=/OUTPUTS/DTI/ad.nii.gz
rd=/OUTPUTS/DTI/rd.nii.gz

##temp
dwi1mm=/OUTPUTS/dwmri_1mm.nii.gz
fa1mm=/OUTPUTS/fa_1mm.nii.gz
md1mm=/OUTPUTS/md_1mm.nii.gz
ad1mm=/OUTPUTS/ad_1mm.nii.gz
rd1mm=/OUTPUTS/rd_1mm.nii.gz
tempmask1mm=/OUTPUTS/tmpmask.nii.gz
mask1mm=/OUTPUTS/nodif_brain_mask.nii.gz

##### Resample to 1mm isotropic #####
echo "Resampling to 1mm isotropic..."
mrgrid $dwi regrid $dwi1mm -voxel 1
mrgrid $fa regrid $fa1mm -voxel 1
mrgrid $md regrid $md1mm -voxel 1
mrgrid $ad regrid $ad1mm -voxel 1
mrgrid $rd regrid $rd1mm -voxel 1
mrgrid $mask regrid $tempmask1mm -voxel 1
fslmaths $tempmask1mm -bin $mask1mm

##### Run TractSeg #####
tractout=/OUTPUTS/Tractseg
echo "Running TractSeg..."
TractSeg -i $dwi1mm --raw_diffusion_input -o ${tractout} --bvals $bval --bvecs $bvec

#check
if [[ -f "${tractout}/peaks.nii.gz" ]]; then echo "Successfully created peaks.nii.gz"; error_flag=0; else echo "Improper bvalue/bvector distribution"; error_flag=1; fi
if [[ $error_flag -eq 1 ]]; then echo "Improper bvalue/bvector distribution" >> {}/report_bad_bvector.txt; fi
if [[ $error_flag -eq 1 ]]; then echo "Tractseg ran with error. Now exiting..."; exit 1; fi

TractSeg -i ${tractout}/peaks.nii.gz -o ${tractout} --output_type endings_segmentation
TractSeg -i ${tractout}/peaks.nii.gz -o ${tractout} --output_type TOM
Tracking -i ${tractout}/peaks.nii.gz -o ${tractout} --tracking_format tck

echo "Done running TractSeg..."