
echo "MAKE SURE that you have provided the freesurfer license at /usr/local/freesurfer/.license"

if [[ -z $1 || -z $2 ]]; then
    echo "Usage: $0 <t1> <out_dir>"
    exit 1
fi

t1=$(readlink -f $1)
outdir=$(readlink -f $2)

recon-all -i $t1 -subjid freesurfer -sd $outdir/ -all
