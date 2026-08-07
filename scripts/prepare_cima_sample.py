#!/usr/bin/env python3
"""Prepare the public CIMA lung-lesion landmark sample committed upstream."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from skimage import color,exposure,filters,io,transform

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/downloads/dataset-histology-landmarks'
IMAGES=SOURCE/'dataset/lung-lesion_3/scale-5pc'
LANDMARKS=SOURCE/'annotations/lung-lesion_3/user-PS_scale-50pc'
OUT=ROOT/'data/processed/cima_lung_lesion_3'

def representation(rgb):
    gray=color.rgb2gray(rgb);gray=exposure.equalize_adapthist(gray,clip_limit=.015)
    # A stain-agnostic structural channel; identical preprocessing for all methods.
    edges=filters.gaussian(filters.sobel(gray),sigma=1.)
    lo,hi=np.quantile(edges,[.01,.99]);return np.clip((edges-lo)/(hi-lo+1e-12),0,1)

def main():
    OUT.mkdir(parents=True,exist_ok=True);metadata=[]
    for image_path in sorted(IMAGES.glob('*.jpg')):
        rgb=io.imread(image_path);height,width=rgb.shape[:2];name=image_path.stem
        rep=transform.resize(representation(rgb),(256,256),anti_aliasing=True,preserve_range=True)
        np.save(OUT/f'{name}.npy',rep.astype(np.float32))
        points=pd.read_csv(LANDMARKS/f'{name}.csv',skipinitialspace=True)[['X','Y']].to_numpy(float)
        # Annotations are at 50%, images at 5%, then images are resized to 256^2.
        points[:,0]*=.1*256/width;points[:,1]*=.1*256/height
        pd.DataFrame({'X':points[:,0],'Y':points[:,1]}).to_csv(OUT/f'{name}.csv',index=False)
        metadata.append({'name':name,'source_shape':[height,width],'prepared_shape':[256,256],'landmarks':len(points)})
    (OUT/'metadata.json').write_text(json.dumps({'source_repository':'https://github.com/Borda/dataset-histology-landmarks','source_commit':'8413e09e1e53b0e6fc101ae9d7b760c47cc20c77','license':'BSD-3-Clause repository; CIMA image provenance per upstream README','set':'lung-lesion_3','image_scale_percent':5,'annotation_scale_percent':50,'preprocessing':'grayscale, CLAHE, Sobel magnitude, Gaussian sigma=1, percentile normalization','images':metadata},indent=2)+'\n')
    print('prepared',len(metadata),'images in',OUT)

if __name__=='__main__':main()
