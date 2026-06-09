
##inputs
dwi1mm=/OUTPUTS/dwmri_1mm.nii.gz
fa1mm=/OUTPUTS/fa_1mm.nii.gz
md1mm=/OUTPUTS/md_1mm.nii.gz
ad1mm=/OUTPUTS/ad_1mm.nii.gz
rd1mm=/OUTPUTS/rd_1mm.nii.gz

tractout=/OUTPUTS/Tractseg
TOMtrack=${tractout}/TOM_trackings

##output dirs
measuresdir=${tractout}/measures
mkdir $measuresdir

for i in ${TOMtrack}/*.tck; do
    echo "$i"; s=${i##*/}; s=${s%.tck}; echo $s
    scil_evaluate_bundles_individual_measures.py ${TOMtrack}/$s.tck ${measuresdir}/$s-SHAPE.json --reference ${dwi1mm}
    scil_compute_bundle_mean_std.py ${TOMtrack}/$s.tck ${fa1mm} ${md1mm} ${ad1mm} ${rd1mm} --density_weighting --reference=${dwi1mm} > ${measuresdir}/$s-DTI.json
done