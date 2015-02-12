from lib.generictask import GenericTask
from lib.logger import Logger
from lib import util
import os

__author__ = 'desmat'

class HardiMrtrix(GenericTask, Logger):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'masking')


    def implement(self):

        dwi = self.getImage(self.dependDir,'dwi', 'upsample')
        bFile = self.getImage(self.dependDir, 'grad', None, 'b')

        maskDwi2Response = self.getImage(self.maskingDir, 'aparc_aseg', ['resample', 'act', 'wm', 'mask'])
        outputDwi2Response = self.__dwi2response(dwi, maskDwi2Response, bFile)

        maskDwi2fod =  self.getImage(self.maskingDir, 'anat',['extended', 'mask'])
        fodImage = self.__dwi2fod(dwi, outputDwi2Response, maskDwi2fod, bFile)

        mask = self.getImage(self.maskingDir, 'anat', ['extended','mask'])
        self.__fod2metric(fodImage, mask)


    def __dwi2response(self, source, mask, bFile):

        target = self.buildName(source, None,'txt')
        tmp = self.buildName(source, "tmp",'txt')

        self.info("Starting dwi2response creation from mrtrix on {}".format(source))
        cmd = "dwi2response {} {} -mask {} -grad {} -nthreads {} -quiet"\
            .format(source, tmp, mask, bFile, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __dwi2fod(self, source, dwi2response, mask, bFile):

        tmp = self.buildName(source, "tmp")
        target = self.buildName(source, "fod")

        self.info("Starting dwi2fod creation from mrtrix on {}".format(source))

        cmd = "dwi2fod {} {} {} -mask {} -grad {} -nthreads {} -quiet"\
            .format(source, dwi2response, tmp, mask, bFile, self.getNTreadsMrtrix())
        self.launchCommand(cmd)

        self.info("renaming {} to {}".format(tmp, target))
        os.rename(tmp, target)

        return target


    def __fod2metric(self, source, mask=None):
        self.info("Starting fod2metric creation from mrtrix on {}".format(source))

        images = {'gfaImage': self.buildName(source, 'gfa'),
        'gfaTmp':self.buildName(source, "tmp"),
        'nufoImage':self.buildName(source, 'nufo'),
        'nufoTmp':self.buildName(source,"tmp1"),
        'fixel_peakImage':self.buildName(source,"fixel_peak", 'msf'),
        'fixel_peakTmp':self.buildName(source, "tmp2" ,'msf')}

        cmd = "fod2metric {} -gfa {} -count {} -fixel_peak {} -nthreads {} -force -quiet"\
            .format(source, images['gfaTmp'], images['nufoTmp'], images['fixel_peakTmp'], self.getNTreadsMrtrix())
        if mask is not None:
            cmd += " -mask {} ".format(mask)

        self.launchCommand(cmd)
        for prefix in ["gfa", "nufo", "fixel_peak"]:
            self.info("renaming {} to {}".format(images["{}Tmp".format(prefix)], images["{}Image".format(prefix)]))
            self.rename(images["{}Tmp".format(prefix)], images["{}Image".format(prefix)])


    def meetRequirement(self):

        images = {'diffusion weighted': self.getImage(self.dependDir,'dwi','upsample'),
                  "gradient encoding b file":  self.getImage(self.dependDir, 'grad', None, 'b'),
                  'white matter segmented mask': self.getImage(self.maskingDir, 'aparc_aseg', ['resample', 'act', 'wm', 'mask']),
                  'ultimate extended mask': self.getImage(self.maskingDir, 'anat', ['extended', 'mask'])}
        return self.isAllImagesExists(images)


    def isDirty(self, result = False):

        images = {"response function estimation text file": self.getImage(self.workingDir, 'dwi', None, 'txt'),
                  "fibre orientation distribution estimation": self.getImage(self.workingDir, 'dwi', 'fod'),
                  "Generalised Fractional Anisotropy": self.getImage(self.workingDir,'dwi','gfa'),
                  'nufo': self.getImage(self.workingDir,'dwi','nufo'),
                  'fixel peak image': self.getImage(self.workingDir,'dwi', 'fixel_peak', 'msf')}

        return self.isSomeImagesMissing(images)