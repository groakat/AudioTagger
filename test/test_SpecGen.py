import scipy.io.wavfile
import numpy as np
import AudioTagger.audioTagger as AT
from PySide import QtGui
import sys
import unittest


# setup Qt application
try:
    app = QtGui.QApplication(sys.argv)
except:
    pass


# old Spectrogram code
def SpecGen_org(self, filepath):
    sr,x = scipy.io.wavfile.read(filepath)

    ## Parameters: 10ms step, 30ms window
    nstep = int(sr * self.specNStepMod)
    nwin  = int(sr * self.specNWinMod)
    nfft = nwin

    window = np.hamming(nwin)

    ## will take windows x[n1:n2].  generate
    ## and loop over n2 such that all frames
    ## fit within the waveform
    nn = range(nwin, len(x), nstep)

    X = np.zeros( (len(nn), nfft/2) )

    for i,n in enumerate(nn):
        xseg = x[n-nwin:n]
        z = np.fft.fft(window * xseg, nfft)
        X[i,:] = np.log(np.abs(z[:nfft/2]))

    return X


# test class
class TestSequenceFunctions(unittest.TestCase):

    def test_SpecGen(self):

        print 'Testing Spectrogram creation'

        # create audiotagger instance and set variables
        at = AT.AudioTagger(basefolder=None, labelfolder=None, labelTypes=None, test=True)
        at.contentChanged = False
        at.specNStepMod = 0.1
        at.specNWinMod = 0.3

        file_list = ['day.wav', 'night.wav']

        for fp in file_list:
            sr, x = scipy.io.wavfile.read(fp)
            print 'sampling rate', sr, 'number of samples', len(x)

            spec_old = SpecGen_org(at, fp)
            spec_new = at.SpecGen(fp)

            self.assertTrue((spec_old-spec_new).sum() == 0)


if __name__ == '__main__':
    unittest.main()