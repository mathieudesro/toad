# Correction
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Correction                                            |
|**Goal**        | Motion and distortion correction of dwi images        |
|**Parameters**  | Diffusion and gradient encoding direction <br> Two b0 with opposite PE (phase encoding direction) <br> Fieldmap (phase and magnitude)|
|**Time**        | N/A                                                   |
|**Output**      | dwi corrected <br> gradient encoding direction corrected|

#

## Goal

Correction step creates dwi corrected for motion. If a fielmap or two b0 with opposite PE are provided correction step wil use this information to corerct for geometrical distortion.


## Minimal Requirements

- dwi images
- Gradient encoding direction

## Optimal Requirements

- dwi images <br>
- gradient encoding direction <br><br>
- Two b0 with opposite PE (highly recommended) <br>
or <br>
- Fieldmap (phase and magnitude images)  <br>

## Implementation

### 1- With two b0s PE (highly recommended)

```{.python}
function: self.__createAcquisitionParameterFile('topup')
function: self.__createAcquisitionParameterFile('eddy')
function: self.__correctionEddy2(dwi, mask, topupBaseName, indexFile, acqpEddy, bVecs, bVals)
```

### 2- With fieldmap images (phase and magnitude)

```{.python}
function: self.__createAcquisitionParameterFile('eddy')
function: self.__correctionEddy2(dwi, mask, None, indexFile, acqpEddy, bVecs, bVals)
function: self.__computeFieldmap(eddyCorrectionImage, bVals, mag, phase, norm, parcellationMask, freesurferAnat)
```

### 3- Without fieldmaps or b0s (with opposite PE)

```{.python}
function: self.__createAcquisitionParameterFile('eddy')
function: self.__correctionEddy2(dwi, mask, topupBaseName, indexFile, acqpEddy, bVecs, bVals)
```

## Expected result(s) - Quality Assessment (QA)

- Motion and geometric distortion dwi corrected
- Gradient encoding direction corrected
- Creation of a gif of dwi before and after correction step
- Creation of a gif of gradient encoding direction before and after correction
 




