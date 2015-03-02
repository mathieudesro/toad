from lib.generictask import GenericTask
from lib import util, mriutil

__author__ = 'desmat'


class Preparation(GenericTask):


    def __init__(self, subject):
       GenericTask.__init__(self, subject, 'backup')


    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi')
        bEnc = self.getImage(self.dependDir, 'grad', None, 'b')
        bVal = self.getImage(self.dependDir, 'grad', None, 'bval')
        bVec = self.getImage(self.dependDir, 'grad', None, 'bvec')

        expectedLayout = self.get('stride_orientation')
        if not mriutil.isDataStridesOrientationExpected(dwi, expectedLayout) \
                and self.getBoolean("force_realign_strides"):

            self.warning("Reorienting stride for image {}".format(dwi))
            originalLayout = mriutil.getDataStridesOrientation(dwi)
            dwi = mriutil.strideImage(dwi, expectedLayout, self.buildName(dwi, "stride"))
            if bEnc:
                bEnc = mriutil.strideEncodingFile(bEnc, originalLayout, expectedLayout, self.buildName(dwi, None, 'b'))
            if bVec:
                bVec = mriutil.strideEncodingFile(bVec, originalLayout, expectedLayout, self.buildName(dwi, None, 'bvec'))
        else:
            util.symlink(dwi, self.workingDir)

        #produce missing gradient files
        (bEnc, bVal, bVec) = self.__produceEncodingFiles(bEnc, bVal, bVec, dwi)

        images = {'high resolution': self.getImage(self.dependDir, 'anat'),
                    'B0 posterior to anterior': self.getImage(self.dependDir, 'b0PA'),
                    'B0 anterior to posterior': self.getImage(self.dependDir, 'b0AP'),
                    'MR magnitude ': self.getImage(self.dependDir, 'mag'),
                    'MR phase ': self.getImage(self.dependDir, 'phase'),
                    'parcellation': self.getImage(self.dependDir,'aparc_aseg'),
                    'freesurfer anatomical': self.getImage(self.dependDir, 'anat', 'freesurfer'),
                    'left hemisphere ribbon': self.getImage(self.dependDir, 'lh_ribbon'),
                    'right hemisphere ribbon': self.getImage(self.dependDir, 'rh_ribbon'),
                    'brodmann': self.getImage(self.dependDir, 'brodmann')}

        for key, value in images.iteritems():
            if value:
                if not mriutil.isDataStridesOrientationExpected(value, expectedLayout) \
                        and self.getBoolean("force_realign_strides"):
                    mriutil.strideImage(value, expectedLayout, self.buildName(value, "stride"))

                else:
                    self.info("Found {} image, linking file {} to {}".format(key, value, self.workingDir))
                    util.symlink(value, self.workingDir)

    def __produceEncodingFiles(self, bEnc, bVal, bVec, dwi):

        self.info("Produce .b .bval and .bvec gradient file if not existing")
        if not bEnc:
            mriutil.bValBVec2BEnc(bVal, bVec, self.buildName(dwi, None, "b"))
        else:
            util.symlink(bEnc, self.workingDir)

        if not bVal:
            mriutil.bEnc2BVal(bEnc, self.buildName(dwi, None, "bval"))
        else:
            util.symlink(bVal, self.workingDir)

        if not bVec:
            mriutil.bEnc2BVec(bEnc, self.buildName(dwi, None, "bvec"))
        else:
            util.symlink(bVec, self.workingDir)

        return (self.getImage(self.workingDir, 'grad', None, 'b'),
                self.getImage(self.workingDir, 'grad', None, 'bval'),
                self.getImage(self.workingDir, 'grad', None, 'bvec'))


    def meetRequirement(self, result=True):

        images = {'high resolution':self.getImage(self.dependDir, 'anat'),
                  'diffusion weighted':self.getImage(self.dependDir, 'dwi')}
        if self.isSomeImagesMissing(images):
            result = False

        if not (self.getImage(self.dependDir, 'grad', None, 'b') or
                (self.getImage(self.dependDir, 'grad', None, 'bval')
                 and self.getImage(self.dependDir, 'grad', None, 'bvec'))):
            self.error("No gradient encoding file found in {}".format(self.dependDir))
            result = False

        return result


    def isDirty(self):

        images = {'gradient .bval encoding file': self.getImage(self.workingDir, 'grad', None, 'bval'),
                  'gradient .bvec encoding file': self.getImage(self.workingDir, 'grad', None, 'bvec'),
                  'gradient .b encoding file': self.getImage(self.workingDir, 'grad', None, 'b'),
                  'high resolution': self.getImage(self.workingDir, 'anat'),
                  'diffusion weighted': self.getImage(self.workingDir, 'dwi')}

        return self.isSomeImagesMissing(images)


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        anat = self.getImage(self.workingDir, 'anat')
        dwi = self.getImage(self.workingDir, 'dwi')
        anatPng = self.pngSlicerImage(anat)
        dwiGif = self.nifti4dtoGif(dwi)
        
        imagesArray = [(anatPng, 'High resolution anatomical image'),
                       (dwiGif, 'Diffusion image')]
        return imagesArray



