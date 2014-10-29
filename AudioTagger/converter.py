import json
import os
import scipy.io.wavfile
import numpy as np
import datetime as dt
import csv
import math

SpecRows = 360

def createLabelFilename(jsonFilename, fileAppendix="", ending='.csv'):
    currentWavFilename = jsonFilename
    if currentWavFilename.endswith('.json'):
        filename = currentWavFilename[:-5]#Everything other than last 4 characters, i.e. .wav
    else:
        1/0

    filename += fileAppendix + ending

    return filename


def loadJSON(filepath):
    filename = filepath

    if os.path.exists(filename):
        with open(filename, "r") as f:
            rects = json.load(f)

        return rects


def SpecGen(filepath):
    sr,x = scipy.io.wavfile.read(filepath)

    ## Parameters: 10ms step, 30ms window
    nstep = int(sr * 0.01)
    nwin  = int(sr * 0.03)
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

def getBoxCoordinates(r, SpecRows):
    """
    Function which parses coordinates of bounding boxes in .json files to x1, x2, y1, and y2 objects.

    Takes account of different methods of drawing bounding boxes, so that coordinates are correct regardless of how bounding boxes are drawn.

    Also takes account of boxes that are accidently drawn outside of the spectrogram.

    """
    if r[2]>0 and r[3]>0:
        x1 = r[0]
        x2 = r[0] + r[2]
        y1 = r[1]
        y2 = r[1] + r[3]
    elif r[2]<0 and r[3]<0:
        x1 = r[0] + r[2]
        x2 = r[0]
        y1 = r[1] + r[3]
        y2 = r[1]
    elif r[2]>0 and r[3]<0:
        x1 = r[0]
        x2 = r[0] + r[2]
        y1 = r[1] + r[3]
        y2 = r[1]
    else:
        x1 = r[0] + r[2]
        x2 = r[0]
        y1 = r[1]
        y2 = r[1] + r[3]
    if x1 < 0:
        x1 = 0
    if y1 < 0:
        y1 = 0
    if y2 > SpecRows:
        y2 = SpecRows
    #Transform y coordinates
    #y1 = (y1 - SpecRows)#*-1
    #y2 = (y2 - SpecRows)#*-1


    return x1, x2, y1, y2

def convertLabelRectsToRects(rects, wavpath):
    labels = []
    for r, c in rects:
        if not (r[2] == 0 or r[3] == 0):
        #     label = [
        #         os.path.basename(wavpath),                      # filename
        #         c,                                              # Label
        #         dt.datetime.now().isoformat(),                  # LabelTimeStamp
        #         0.01,                                           # Spec_NStep
        #         0.03,                                           # Spec_NWin
        #         ["Not a box"]
        #         ]
        # else:

            x1, x2, y1, y2 = getBoxCoordinates(r, SpecRows)

            rect = [x1, y1, x2, y2]

            sr,x = scipy.io.wavfile.read(wavpath)
            spec = SpecGen(wavpath)
            freqStep = float(sr) / spec.shape[1] / 2
            boundingBox = spec[x1:x2, y1:y2]
            # label head:
            # (wav)Filename    Label    LabelTimeStamp     Spec_NStep
            # Spec_NWin     Spec_x1     Spec_y1     Spec_x2     Spec_y2
            # LabelStartTime_Seconds    LabelEndTime_Seconds    MinimumFreq_Hz
            # MaximumFreq_Hz    MaxAmp    MinAmp    MeanAmp
            # AmpSD LabelArea_DataPoints
            label = [
                os.path.basename(wavpath),                      # filename
                c,                                              # Label
                dt.datetime.now().isoformat(),                  # LabelTimeStamp
                0.01,                                           # Spec_NStep
                0.03,                                           # Spec_NWin
                rect[0],rect[1],rect[2],rect[3],                # Spec_x1, y1, x2, y2
                rect[0] * 0.01,                                 # LabelStartTime_Seconds
                rect[2] * 0.01,                                 # LabelEndTime_Seconds
                rect[1] * freqStep,                             # MinimumFreq_Hz
                rect[3] * freqStep,                             # MaximumFreq_Hz
                np.max(boundingBox),                            # MaxAmp
                np.min(boundingBox),                            # MinAmp
                np.mean(boundingBox),                           # MeanAmp
                np.std(boundingBox),                            # AmpSD
                math.fabs(r[2]) * math.fabs(r[3])               # LabelArea_DataPoints
                ]

            labels += [label]

    return labels


def saveLabels(labels, jsonPath, fileAppendix="-sceneRect"):
    filename = createLabelFilename(jsonPath, fileAppendix, ending='.csv')

    if not os.path.exists(os.path.dirname(jsonPath)):
        os.makedirs(os.path.dirname(jsonPath))

    with open(filename, "w") as f:
        wr = csv.writer(f, dialect='excel')
        wr.writerow(["Filename", "Label", "LabelTimeStamp", "Spec_NStep", "Spec_NWin", "Spec_x1", "Spec_y1", "Spec_x2", "Spec_y2",
                    "LabelStartTime_Seconds", "LabelEndTime_Seconds", "MinimumFreq_Hz", "MaximumFreq_Hz",
                    "MaxAmp", "MinAmp", "MeanAmp", "AmpSD", "LabelArea_DataPoints"])
        for label in labels:
            wr.writerow(label)


def convertJSON2CSV(jsonpath, wavpath, csvAppendix=''):
    rects = loadJSON(jsonpath)
    labels = convertLabelRectsToRects(rects, wavpath)
    saveLabels(labels, jsonpath, fileAppendix=csvAppendix)


if __name__ == "__main__":
    convertJSON2CSV('/home/peter/phd/projects/spectogram/Python/Amalgamated_Code/Snd_files_label/HA53AA-13548_20130727_050000 Part 01 of 30-sceneRect.json',
                    '/home/peter/phd/projects/spectogram/Python/Amalgamated_Code/Snd_files/HA53AA-13548_20130727_050000 Part 01 of 30.wav',
                    csvAppendix='-test')