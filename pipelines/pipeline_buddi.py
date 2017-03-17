import sys
from pipelines.pnllib import StrctXc, DwiXc, FsInDwiDirect, FreeSurferUsingMask, T1wMaskMabs, DwiMaskHcpBet, DwiEd, UkfDefault, Wmql, TractMeasures, T2wMaskRigid, DwiEpi, DoesNotExistException
from pipelib import Src
import pipelib

DEFAULT_TARGET = 'tractmeasures'

def makePipeline(caseid,
                 t1PathKey,
                 dwiPathKey,
                 dwimaskPathKey='',
                 hash_UKFTractography='421a7ad',
                 hash_tract_querier='e045eab',
                 hash_BRAINSTools='41353e8',
                 hash_trainingDataT1AHCC='d6e5990'):
    """Makes the PNL's standard pipeline, given an eddy corrected DWI
    (For example, a DRBUDDI processed DWI.). Same as 'std' except eddy
    current correction is not performed."""
    pipeline = {'_name': "standard PNL pipeline with no eddy correction"}
    pipeline['t1'] = Src(caseid, t1PathKey)
    pipeline['dwi'] = Src(caseid, dwiPathKey)
    pipeline['t1xc'] = StrctXc(caseid, pipeline['t1'], hash_BRAINSTools)
    pipeline['dwimask'] = Src(caseid,
                              dwimaskPathKey) if dwimaskPathKey else DwiMaskHcpBet(
                                  caseid, pipeline['dwi'], hash_BRAINSTools)
    pipeline['t1mask'] = T1wMaskMabs(caseid, pipeline['t1xc'],
                                     hash_trainingDataT1AHCC, hash_BRAINSTools)
    pipeline['fs'] = FreeSurferUsingMask(caseid, pipeline['t1xc'],
                                         pipeline['t1mask'])
    pipeline['fsindwi'] = FsInDwiDirect(caseid, pipeline['fs'],
                                        pipeline['dwi'], pipeline['dwimask'],
                                        hash_BRAINSTools)
    pipeline['ukf'] = UkfDefault(caseid, pipeline['dwi'], pipeline['dwimask'],
                                 hash_UKFTractography, hash_BRAINSTools)
    pipeline['wmql'] = Wmql(caseid, pipeline['fsindwi'], pipeline['ukf'],
                            hash_tract_querier)
    pipeline['tractmeasures'] = TractMeasures(caseid, pipeline['wmql'])
    return pipeline


def status(paramPoints):
    import pipelines.pnllib
    pipelines.pnllib.tractMeasureStatus(paramPoints, makePipeline)
