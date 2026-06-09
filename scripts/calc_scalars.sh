
if [[ -z $1 || -z $2 || -z $3 || -z $4 || -z $5 ]]; then
    echo "Usage: $0 <data_dir> <nii> <bval> <bvec> <mask>"
    exit 1
fi


data_dir=$(readlink -f $1)
#inputs
dwi_firstshell=${data_dir}/$2 #dwmri$firstshell.nii.gz
bval=${data_dir}/$3 #dwmri$firstshell.bval
bvec=${data_dir}/$4 #dwmri$firstshell.bvec
mask=$(readlink -f $5) #mask.nii.gz
#outputs
tensors=${data_dir}/tensor.nii.gz
fa=${data_dir}/fa.nii.gz
md=${data_dir}/md.nii.gz
ad=${data_dir}/ad.nii.gz
rd=${data_dir}/rd.nii.gz

#tensors
echo "dwi2tensor ${dwi_firstshell} ${tensors} -fslgrad ${bvec} ${bval} -mask ${mask}"
dwi2tensor ${dwi_firstshell} ${tensors} -fslgrad ${bvec} ${bval} -mask ${mask}
tensor2metric ${tensors} -fa ${fa} -adc ${md} -ad ${ad} -rd ${rd} -mask ${mask}