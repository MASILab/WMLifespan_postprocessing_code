import numpy as np
import pandas as pd
import nibabel as nib
from pathlib import Path
import re
import argparse

def pa():
    parser = argparse.ArgumentParser(description="Extract volumes with bvals between thresholds from a diffusion image.")
    parser.add_argument("--inputdir", type=str, default="/INPUTS", help="Path to input directory containing dwmri.nii.gz, dwmri.bval, dwmri.bvec")
    parser.add_argument("--outdir", type=str, required=True, help="Path to output the extracted data")
    parser.add_argument("--high_threshold", type=int, default=1500, help="Threshold for bvals to extract (default: 1500)")
    parser.add_argument("--low_threshold", type=int, default=500, help="Lower threshold for bvals to extract (default: 500)")
    args = parser.parse_args()
    return args

def get_new_bvecs(new_bvec):
    bdirs = []      #bdirs will be the new bvec list
    for x in new_bvec:
        r = x[0]
        l = []
        for y in r:
            l.append(str(y))
        bdirs.append(l)

    #nbdirs will be the new bvec list with the zeroes as '0' not '0.0'
    nbdirs = []
    for x in bdirs:
        a = []
        for d in x:
                f = float(d)
                if f == 0:
                        a.append('0')
                else:
                        a.append(str(f))
        nbdirs.append(a)
    return nbdirs

#at the end of EVERY value (even terminal ones) there are 2 spaces
    #at the end of EVERY line, there is a newline
def get_new_bvec_txt(new_bvec):
    bvectxt = ''
    for line in new_bvec:
        s = "  ".join(line)
        s = s + '\n'
        bvectxt = bvectxt + s
    return bvectxt

def get_bval_str(new_bval):
    e = []
    for x in new_bval:
        f = float(x)
        if f == 0:
                e.append('0')
        else:
                e.append(str(f))
    s = ' '.join(e)
    s = s + '\n'
    return s

def round(num, base):
    """
    Taken from Leon Cai's PreQual
    """

    d = num / base
    if d % 1 >= 0.5:
        return base*np.ceil(d)
    else:
        return base*np.floor(d)

args = pa()
LOW_THRESHOLD = args.low_threshold
HIGH_THRESHOLD = args.high_threshold
outdir = Path(args.outdir)
indir = Path(args.inputdir)
assert LOW_THRESHOLD < HIGH_THRESHOLD, "Low threshold must be less than high threshold"

#inputs
name='dwmri'
indir = Path(indir)
dwi = indir/"{}.nii.gz".format(name)
bval_file = indir/"{}.bval".format(name)
bvec_file = indir/"{}.bvec".format(name)

#outputs
output_file = outdir/"{}%firstshell.nii.gz".format(name)
bval_new_file = outdir/"{}%firstshell.bval".format(name)
bvec_new_file = outdir/"{}%firstshell.bvec".format(name)

#dwi = Path("/home-local/kimm58/AtlasToDiffusionReg/data/BLSA_test/inputs/dwmri.nii.gz")
#bval_file = Path("/home-local/kimm58/AtlasToDiffusionReg/data/BLSA_test/inputs/dwmri.bval")
#bvec_file = Path("/home-local/kimm58/AtlasToDiffusionReg/data/BLSA_test/inputs/dwmri.bvec")

#must extract the volumes less than 1500 bval from the diffusion image
nii = nib.load(dwi)
img = nii.get_fdata()

bval = np.loadtxt(bval_file)
bvec = np.loadtxt(bvec_file)

#round the bvals
rounded_bvals = np.array([round(b, 100) for b in bval])

#get indices of volumes to extract
indices = np.where(((rounded_bvals<=HIGH_THRESHOLD) & (rounded_bvals>=LOW_THRESHOLD))| (rounded_bvals==0))
#indices = np.where(rounded_bvals<=THRESHOLD)

#extract the volumes
new_bval = rounded_bvals[indices]
#new_bval = rounded_bvals[rounded_bvals<=THRESHOLD]

dirs = []
for x in bvec:
    new_dir = np.take(x, indices)
    dirs.append(new_dir)
new_bvec = np.stack(dirs, axis=0)

new_bvec = get_new_bvecs(new_bvec)      #gets bvecs into a list of lists of strings
bvectxt = get_new_bvec_txt(new_bvec)
#now, bvectxt can be output to a text file
    #must do the same for bvals
bvaltxt= get_bval_str(new_bval)


#new_bvec = bvec[:, bval<THRESHOLD]
#print("Extracting volumes from {} with bvals less than 1500...".format(dwi.name))
#new_img = img[:, :, :, rounded_bvals<=THRESHOLD]
new_img = img[:, :, :, ((rounded_bvals<=HIGH_THRESHOLD) & (rounded_bvals>=LOW_THRESHOLD)) | (rounded_bvals==0)]

#save the extracted volumes
nii2 = nib.Nifti1Image(new_img, nii.affine)
print("Saving extracted volumes to {}...".format(output_file))
nib.save(nii2, output_file)

#write the new bvals/bvecs
print("Saving new bvec and bval files...")
with open(bvec_new_file, 'w') as f:
    f.write(bvectxt)
with open(bval_new_file, 'w') as f:
    f.write(bvaltxt)

print("**********************************")
print("FINISHED EXTRACTING b={} to b={} VOLUMES".format(LOW_THRESHOLD, HIGH_THRESHOLD))
print("*********************************")
