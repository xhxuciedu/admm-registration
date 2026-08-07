#!/usr/bin/env python3
from pathlib import Path
import json
import numpy as np
from skimage import color,data,transform,io

ROOT=Path(__file__).resolve().parents[1];out=ROOT/'data'/'processed'/'public_samples';out.mkdir(parents=True,exist_ok=True)
items={'retina_cc0':data.retina(),'histology_ihc':data.immunohistochemistry()};meta={}
for name,image in items.items():
    gray=color.rgb2gray(image);gray=transform.resize(gray,(256,256),anti_aliasing=True,preserve_range=True);gray=(gray-gray.min())/(gray.max()-gray.min()+1e-12)
    np.save(out/f'{name}.npy',gray.astype(np.float64));io.imsave(out/f'{name}.png',(255*gray).astype(np.uint8));meta[name]={'shape':[256,256],'min':float(gray.min()),'max':float(gray.max())}
(out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
