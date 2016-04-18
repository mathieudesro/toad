# -*- coding: utf-8 -*-
import os
from core.toad.generictask import GenericTask
from lib import mriutil, util
from lib.images import Images


class TractFiltering(GenericTask):
    def __init__(self, subject):
        GenericTask.__init__(
            self, subject, 'tensorfsl', 'tensormrtrix', 'tensordipy',
            'tractfiltering', 'qa')
        self.setCleanupBeforeImplement(False)
        self.dirty = True


    def implement(self):

        mriutil.setWorkingDirTractometry(self.workingDir,
                                         self.getTractFiltering(None, None, 'trk'),
                                         self.__buildListMetrics())

        #mriutil.runTractometry(configTractometry, filteredTractographies, self.workingDir)


    def __buildListMetrics(self):
        return [self.getImage('dwi', 'corpus_callosum', 'trk'),
                self.getImage('dwi', 'cortico_spinal.left', 'trk'),
                self.getImage('dwi', 'cortico_spinal.right', 'trk'),
                self.getImage('dwi', 'inferior_fronto_occipital.left', 'trk'),
                self.getImage('dwi', 'inferior_fronto_occipital.right', 'trk'),
                self.getImage('dwi', 'inferior_longitudinal_fasciculus.left', 'trk'),
                self.getImage('dwi', 'inferior_longitudinal_fasciculus.right', 'trk'),
                self.getImage('dwi', 'uncinate_fasciculus.left', 'trk'),
                self.getImage('dwi', 'uncinate_fasciculus.right', 'trk')]


    def isIgnore(self):
        return self.get("ignore")


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task
        Returns:
            True if all requirement are meet, False otherwise
        """

        images = Images()

        dwi = self.getUpsamplingImage('dwi', 'upsample')
        nbDirections = mriutil.getNbDirectionsFromDWI(dwi)

        # Load tractography
        if nbDirections <= 45:
            postfixTractography = 'tensor_prob'
        else:
            postfixTractography = 'hardi_prob'

        Images((self.getTractographymrtrixImage('dwi', postfixTractography, 'trk'),'Tractography file'),
                (self.__getAtlas(),'Atlas'))

        return images


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution
        Returns:
            True if any expected file or resource is missing, False otherwise
        """

        return True


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()

        return qaImages
