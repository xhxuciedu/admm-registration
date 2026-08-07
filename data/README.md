# Public 2D validation data

Raw images are excluded from Git.

- **FIRE retinal registration benchmark:** official source `https://projects.ics.forth.gr/cvrl/fire/`, 129 images/134 landmarked pairs. Cite C. Hernandez-Matas et al., *FIRE: Fundus Image Registration Dataset*, Journal for Modeling in Ophthalmology 1(4):16--28, 2017, DOI 10.35119/maio.v1i4.42. The official journal states a Creative Commons Attribution license after the publication embargo; raw data are not redistributed here.
- **scikit-image retina:** public-domain/CC0 human retina image attributed to Mikael Häggström.
- **scikit-image immunohistochemistry:** colonic-gland IHC image from CMMI, documented as having no known copyright restrictions.
- **CIMA histology landmark sample:** obtained from the archived BSD-licensed
  `Borda/dataset-histology-landmarks` repository at commit
  `8413e09e1e53b0e6fc101ae9d7b760c47cc20c77`. The included lung-lesion-3
  sample contains five 5%-scale stained-section images; manual landmarks are
  supplied at 50% scale. Image provenance and the ICIP 2018 citation are given
  in the upstream README.

The latter two are subjected to committed, seeded synthetic diffeomorphisms so displacement ground truth is exactly known. They test real image structure but are not represented as established paired registration benchmarks.

Run `scripts/download_public_2d.sh` for FIRE,
`scripts/prepare_public_samples.py` for the openly packaged samples, and
`scripts/prepare_cima_sample.py` after cloning the CIMA landmark repository.
The FIRE archive must pass `7z t` before it is treated as available.
