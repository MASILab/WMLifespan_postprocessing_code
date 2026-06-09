#!/bin/bash

# Default values for flags
skip_dti=false
skip_tractseg=false
skip_scilpy=false
skip_freesurfer=false
skip_reg=false
skip_fswm=false
skip_aggregate=false

# Loop through all arguments and set flags
for arg in "$@"; do
case $arg in
    --skip-dti)
        skip_dti=true
        shift # Remove --skip-dti from the argument list
        ;;
    --skip-tractseg)
        skip_tractseg=true
        shift
        ;;
    --skip-scilpy)
        skip_scilpy=true
        shift
        ;;
    --skip-freesurfer)
        skip_freesurfer=true
        shift
        ;;
    --skip-reg)
        skip_reg=true
        shift
        ;;
    --skip-fswm)
        skip_fswm=true
        shift
        ;;
    --skip-aggregate)
        skip_aggregate=true
        shift
        ;;
    *)
        # Any other unrecognized arguments can be handled here
        echo "Unrecognized argument: '$1'. To shell into the Docker, run 'docker run -it --rm --entrypoint /bin/bash <IMAGE_NAME>'"
        exit 1
        ;;
esac
done

cd /OUTPUTS

##DTI
if [[ "$skip_dti" == false ]]; then
    echo "Starting DTI fitting..."
                                                                                            #### ADD OPTIONS FOR THE THRESHOLDING STEP ####
    /SCRIPTS/python3.10 extract_singleshell.py --outdir /OUTPUTS --inputdir /INPUTS
    bash /SCRIPTS/calc_scalars.sh /OUTPUTS dwmri%firstshell.nii.gz dwmri%firstshell.bval dwmri%firstshell.bvec /INPUTS/mask.nii.gz
    #move all outputs to a DTI directory
    mkdir -p /OUTPUTS/DTI
    mv /OUTPUTS/* /OUTPUTS/DTI/
    #check
    famap='/OUTPUTS/DTI/fa.nii.gz'
    if [[ ! -e $famap ]]; then
        echo "ERROR: ${famap} not found in outputs. Exiting..."
        exit 1
    fi
    echo "****FINISHED CALCULATING SCALARS****"
else
    echo "SKIPPING DTI"
fi


##Tractseg
if [[ "$skip_tractseg" == false ]]; then
    echo "Starting TractSeg..."
    bash /SCRIPTS/run_tractseg.sh
    #check
    tckdir=/OUTPUTS/Tractseg/TOM_trackings
    if [[ $(ls $tckdir | grep -E '*.tck' | wc -l) -ne 72 ]]; then
        echo "ERROR: Tractseg failed - 72 tracts not in ${tckdir}. Exiting..."
        exit 1
    fi
    echo "****FINISHED TRACTSEG****"
else
    echo "SKIPPING TRACTSEG"
fi


##Scilpy
if [[ "$skip_scilpy" == false ]]; then
    echo "Starting tract bundle feature extraction (scilpy)..."
    bash /SCRIPTS/get_bundle_measurements.sh
    #check
    measuresdir=/OUTPUTS/Tractseg/measures
    if [[ $(ls $measuresdir | grep DTI | wc -l) -ne 72 ]]; then
        echo "ERROR: Scilpy scripts failed - 72 tract DTI jsons not in ${measuresdir}. Exiting..."
        exit 1
    fi
    echo "****FINISHED CALCULATING BUNDLE MEASUREMENTS****"
else
    echo "Skipping calculation of bundle measurements..."
fi


## freesurfer
#mkdir /OUTPUTS/freesurfer
if [[ "$skip_freesurfer" == false ]]; then
    echo "Starting freesurfer..."
    fsfail='0'
    bash /SCRIPTS/run_freesurfer.sh /INPUTS/T1.nii.gz /OUTPUTS/
    rm -r /OUTPUTS/fsaverage
    echo "****FINISHED FREESURFER****"
else
    echo "Skipping freesurfer..."
fi
reconlog=/OUTPUTS/freesurfer/scripts/recon-all.log
if [[ -z $(cat $reconlog | grep "finished without error") ]]; then
    echo "WARNING: freesurfer may have exited with errors. Will try to continue running rest of pipeline, but it may fail and the outputs may be problematic."
    fsfail='1'
fi




## T1-b0 registration
#running t1-b0 registration
    #get the freesurfer brain mask
fsdir=/OUTPUTS/freesurfer
regdir=/OUTPUTS/REG
dtidir=/OUTPUTS/DTI
regfail='0'
if [[ "$skip_reg" == false ]]; then
    echo "Starting registration of b0 to T1..."
    mkdir -p $regdir
    bash /SCRIPTS/run_t1_b0_reg.sh /INPUTS ${fsdir} ${regdir}
    echo "****FINISHED DWI-T1 REGISTRATION****"
else
    echo "Skipping DWI-T1 registration..."
fi
#check
if [[ ! -e "${regdir}/dwmri%ANTS_t1tob0.txt" ]]; then
    regfail='1'
    if [[ $fsfail == '1' ]]; then #continue on if freesurfer failed
        echo "Registration failed likely due to freesurfer failure. Continuing on..."
    else
        echo "ERROR: Registration failed - ${regdir}/dwmri%ANTS_t1tob0.txt not in outputs. Exiting..."
        exit 1
    fi
fi




## FSWM mask
#calculating the metrics
maskfail='0'
if [[ "$skip_fswm" == false ]]; then
    fswmdir=/OUTPUTS/FreesurferWhiteMatterMask
    mkdir $fswmdir
    if [[ $regfail == '0' ]]; then
        echo "Starting calculation of global WM measurements..."
        python3.10 /SCRIPTS/get_fs_global_wm_metrics.py ${fsdir}/mri/wmparc.mgz ${fsdir}/mri/rawavg.mgz ${regdir}/dwmri%ANTS_t1tob0.txt \
        ${dtidir}/fa.nii.gz ${dtidir}/md.nii.gz ${dtidir}/ad.nii.gz ${dtidir}/rd.nii.gz /INPUTS/mask.nii.gz ${fsdir}/stats/aseg.stats \
        ${fswmdir}
        #check
        if [[ ! -e ${fswmdir}/metrics.json ]]; then
            maskfail='1'
            if [[ $fsfail == '1' ]]; then #continue on if freesurfer failed
                echo "FSWM masking failed likely due to freesurfer failure. Continuing on..."
            else
                echo "ERROR: FSWM masking failed - ${fswmdir}/metrics.json not in outputs. Exiting..."
                exit 1
            fi
        fi
        echo "****FINISHED CALCULATING GLOBAL WM measurements****"
    else
        echo "Skipping FSWM because registration failed."
        maskfail='1'
    fi
else
    echo "Skipping FSWM..."
fi



## Aggregate the measurements
if [[ "$skip_aggregate" == false ]]; then
    echo "Starting to aggregate all results..."
    python3.10 /SCRIPTS/aggregate_measurements.py
    #check
    if [[ ! -e /OUTPUTS/measurements.csv ]]; then
        echo "ERROR: Aggregating measurements failed - /OUTPUTS/measurements.csv not in outputs. Exiting..."
        exit 1
    fi
    if [[ $fsfail == '1' || $regfail == '1' || $maskfail == '1' ]]; then
        echo "****FINISHED AGGREGATING TRACTSEG RESULTS ONLY (not GLOBAL or NORMALIZED)****"
    else
        echo "****FINISHED AGGREGATING TRACTSEG, GLOBAL, AND NORMALIZED RESULTS****"
    fi
else
    echo "Skipping aggregation of results..."
fi


## Removal of intermediate files
echo "Now removing intermediate files..."
rm /OUTPUTS/dwmri_1mm.nii.gz /OUTPUTS/DTI/dwmri%firstshell.nii.gz /OUTPUTS/tmpmask.nii.gz
rm -r /OUTPUTS/dwi2response-tmp-*
