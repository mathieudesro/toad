from lib.generictask import GenericTask
from lib import mriutil
import os

__author__ = 'desmat'

class Dtifit(GenericTask):


    #@TODO add appropriate mask to __tensorsFsl the command line
    def __init__(self, subject):
        """Fits a diffusion tensor model at each voxel

        """
        GenericTask.__init__(self, subject, 'denoising', 'preparation', 'eddy')


    def implement(self):
        """Placeholder for the business logic implementation

        """
        dwi = self.getImage(self.dependDir, 'dwi', 'denoise')

        bVal = self.getImage(self.eddyDir, 'grad', None, 'bval')
        bVec = self.getImage(self.eddyDir, 'grad', None, 'bvec')
        if (not bVal) or (not bVec):
            bVal = self.getImage(self.preparationDir,'grad', None, 'bval')
            bVec = self.getImage(self.preparationDir,'grad', None, 'bvec')

        #dtifit required a mask
        b0 = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.config.get("prefix", 'dwi'), self.config.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi, b0, bVal))
        mask = self.__createMask(b0)
        print "DEBUG mask name =", mask
        self.__tensorsFsl(dwi, bVec, bVal, mask)

        l1 = self.getImage(self.workingDir, 'dwi', 'fsl_value1', 'nii.gz')
        l2 = self.getImage(self.workingDir, 'dwi', 'fsl_value2', 'nii.gz')
        l3 = self.getImage(self.workingDir, 'dwi', 'fsl_value3', 'nii.gz')

        ad = self.buildName(dwi, 'fsl_ad', 'nii.gz')
        rd = self.buildName(dwi, 'fsl_rd', 'nii.gz')

        os.rename(l1, ad)
        self.__mean(l2, l3, rd)


    def __tensorsFsl(self, source, bVec, bVal, mask=""):
        """Fits a diffusion tensor model at each voxel

        Args:
            source: A diffusion weighted volumes and volume(s) with no diffusion weighting
            bVec: Text file containing a list of gradient directions applied during diffusion weighted volumes.
            bVal: Text file containing a list of b values applied during each volume acquisition.
            mask: A binarised volume in diffusion space containing ones inside the brain and zeroes outside the brain.

        """
        self.info("Starting dtifit from fsl")

        target = self.buildName(source, 'fsl', '')
        cmd ="dtifit -k {} -o {} -r {} -b {} --save_tensor --sse ".format(source, target, bVec, bVal)
        if mask:
            cmd += "-m {}".format(mask)
        self.launchCommand(cmd)


    def __mean(self, source1, source2, target):
        cmd = "fslmaths {} -add {} -div 2 {}".format(source1, source2, target)
        self.launchCommand(cmd)


    def __createMask(self, source):
        """deletes non-brain tissue from an image of the whole head

        bias field & neck cleanup will always be perform by this method

        Args:
            source: The input file name

        Return:
            The resulting output file name
        """
        self.info("Launch brain extraction from fsl")
        target = self.buildName(source, "brain")
        fractionalIntensity = 0.4
        verticalGradient = 0
        self.info("End brain extraction from fsl")
        cmd = "bet {} {} -f {} -g {} -v -m".format(source, target, fractionalIntensity, verticalGradient)
        self.launchCommand(cmd)
	
        return self.getImage(self.workingDir, 'b0', ['brain','mask'], 'nii.gz')

    def meetRequirement(self, result=True):
        """Validate if all requirements have been met prior to launch the task

        """

        images = {'.bval gradient encoding file': self.getImage(self.eddyDir, 'grad', None, 'bval'),
                '.bvec gradient encoding file': self.getImage(self.eddyDir, 'grad', None, 'bvec')}

        if self.isSomeImagesMissing(images):
            images = {'.bval gradient encoding file': self.getImage(self.preparationDir, 'grad', None, 'bval'),
                    '.bvec gradient encoding file': self.getImage(self.preparationDir, 'grad', None, 'bvec')}
            if self.isSomeImagesMissing(images):
                result=False

        if self.isSomeImagesMissing({'diffusion weighted':  self.getImage(self.dependDir, 'dwi', 'denoise')}):
            result=False

        return result


    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        images = {"1st eigenvector": self.getImage(self.workingDir, 'dwi', 'fsl_vector1', 'nii.gz'),
                  "2rd eigenvector": self.getImage(self.workingDir, 'dwi', 'fsl_vector2', 'nii.gz'),
                  "3rd eigenvector": self.getImage(self.workingDir, 'dwi', 'fsl_vector3', 'nii.gz'),
                  "selected eigenvalue(s) AD": self.getImage(self.workingDir, 'dwi', 'fsl_ad', 'nii.gz'),
                  "selected eigenvalue(s) RD": self.getImage(self.workingDir, 'dwi', 'fsl_rd', 'nii.gz'),
                  "mean diffusivity": self.getImage(self.workingDir, 'dwi', 'fsl_md', 'nii.gz'),
                  "fractional anisotropy": self.getImage(self.workingDir, 'dwi', 'fsl_fa', 'nii.gz'),
                  "raw T2 signal with no weighting": self.getImage(self.workingDir, 'dwi', 'fsl_so', 'nii.gz')}

        return self.isSomeImagesMissing(images)
