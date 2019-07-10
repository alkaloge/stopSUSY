#!/usr/bin/env python

# NOTE: NEEDS 4 CMD LINE ARGS with values {0 (false) or 1 (true)}: 
# displayMode, experimental, findingSameFlavor, muPreference
# True displayMode displays rather than saves w/o displaying the hists. True 
# experimental mode makes extra cuts for cut optimization.
# Draws the cutflow for some channel and a piechart from both no cuts and
# after all cuts showing the breakdown of the bkgd.
# Uses the output generated by generateCutflows.py.

import sys
from ROOT import TFile, TH1F, TCanvas, TImage, TLegend, TText, THStack, TPie
from ROOT import gSystem, gStyle, gROOT, kTRUE
from collections import OrderedDict
import numpy as np
import time
from array import array

assert len(sys.argv) == 5, "needs 4 command line args: displayMode{0,1}, experimental{0,1}, findingSameFlavor{0,1}, muPreference{0,1}"

# Determining adr of bkgd and sig ntuples.
# limits the number of events and files to loop over
displayMode = bool(int(sys.argv[1]))
print "Display mode:", displayMode
experimental = bool(int(sys.argv[2]))
print "Experimental mode:", experimental
# selecting for either mu-mu or el-el (as opposed to mu-el or el-mu)
findingSameFlavor = bool(int(sys.argv[3]))
print "Finding same flavor:", findingSameFlavor
# only applies if findingSameFlav; selects for mu-mu as opposed to el-el
muPreference = bool(int(sys.argv[4]))
print "Mu preference:", muPreference
channelName = ""
if findingSameFlavor:
    if muPreference: 
        l1Flav = "muon"
        l2Flav = "muon"
    else: 
        l1Flav = "electron"
        l2Flav = "electron"
else: 
    l1Flav = "muon"
    l2Flav = "electron"
channelName = l1Flav[:2] + l2Flav[:2]

# bkgd process name : color for plotting
processes = OrderedDict([("W-Jets",38), ("Drell-Yan",46), ("Diboson",41), \
        ("Single-Top",30), ("TT+X",7)])

if not displayMode:
    gROOT.SetBatch(kTRUE) # prevent displaying canvases

#--------------------------------------------------------------------------------#

statsFileAdr = "/afs/cern.ch/user/c/cmiao/private/CMSSW_9_4_9/s2019_SUSY/"+\
        "plots/v3CutSequence/cutflow_stats_"+channelName
if experimental: statsFileAdr += "_experimental"
statsFileAdr += ".txt"
print "Reading from", statsFileAdr
statsFile = open(statsFileAdr)
header = statsFile.readline()
header = header.rstrip('\n').split()
header.remove("#")
numStatsCols = len(header)
statsFile.close()

cuts = np.genfromtxt(statsFileAdr, dtype='str', delimiter='   ', usecols=0)
nCuts = len(cuts)
hBkgdCutsCountDict = {} # maps process to arr of cutflow counts for that process
hBkgdDict = {} # maps process to an hBkgd for that process
hSigCutsCountDict = {} # maps sig name to arr of cutflow counts for that sig 
hSigDict = {} # maps sig name to an hSig for that sig 
for col in range(1, numStatsCols):
    cutflowArr = np.genfromtxt(statsFileAdr, dtype='int', usecols=col)
    dataName = header[col]
    if dataName[:2] == "C1": 
        hSigCutsCountDict.update({dataName:cutflowArr})
        hSig = TH1F("sig_" + dataName, "sig_" + dataName, nCuts, 0, nCuts)
        hSig.SetDirectory(0) # necessary to keep hist from closing
        hSig.SetDefaultSumw2() # automatically sum w^2 while filling
        hSigDict.update({dataName:hSig})
    else: 
        hBkgdCutsCountDict.update({dataName:cutflowArr})
        hBkgd = TH1F("bkgd_"+dataName, "bkgd_"+dataName, nCuts, 0, nCuts)
        hBkgd.SetDirectory(0)
        hBkgd.SetDefaultSumw2() # automatically sum w^2 while filling
        hBkgdDict.update({dataName:hBkgd})
for process in processes:
    if process not in hBkgdDict: processes.pop(process)
    # doing it this way so can still stack in the desired order (by using the 
    # ordered dict)

c = TCanvas("c","c",10,20,1000,700)
legend = TLegend(.70,.70,.90,.90)
title = "cutflow ("+channelName+")"
hBkgdStack = THStack("cutflow_bkgdStack", title)
nEvtsLabels = []
gStyle.SetOptStat(0) # don't show any stats

lumi = 3000000 # luminosity = 3 /ab = 3000 /fb = 3,000,000 /fb

# ********** Looping over each bkgd process. ***********
for process in processes:
    hBkgd = hBkgdDict[process] 
    hBkgdCutsCount = hBkgdCutsCountDict[process]
    for i, cut in enumerate(cuts):
        if i>nCuts: break
        hBkgd.Fill(i, hBkgdCutsCount[i])
        hBkgd.GetXaxis().SetBinLabel(i+1, cut)

    c.cd()
    # hBkgd.Sumw2() # already summed while filling
    hBkgd.SetFillColor(processes[process])
    hBkgd.SetLineColor(processes[process])
    hBkgdStack.Add(hBkgd)
    legend.AddEntry(hBkgd, process+"_bkgd")

hBkgdStack.Draw("hist")
hBkgdStack.GetXaxis().SetTitle("cutflow")
hBkgdStack.GetYaxis().SetTitle("Number of Events, norm to 3000 /fb")
hBkgdStack.SetMinimum(1)
hBkgdStack.SetMaximum(10**12)

# # show the number of events left over after each cut
# processNum = 0
# for process, color in processes.items():
#     print
#     print "Num surviving events after each cut from bkgd %s:" % process 
#     for i, cut in enumerate(cuts):
#         nEvtsLabel = TText()
#         nEvtsLabel.SetNDC()
#         nEvtsLabel.SetTextSize(0.02)
#         nEvtsLabel.SetTextAlign(22)
#         nEvtsLabel.SetTextAngle(0)
#         nEvtsLabel.SetTextColor(color)
#         nEvtsLabel.DrawText(0.1+0.4/nCuts+0.8*float(i)/nCuts, \
#                 0.7-(processNum)*0.02, \
#                 str(int(hBkgdCutsCountDict[process][i])))
#         print cut, hBkgdCutsCountDict[process][i]
#         nEvtsLabels.append(nEvtsLabel)
#     processNum += 1
# print

#--------------------------------------------------------------------------------#
# *************** Filling each signal in a separate hist  ************
print "Plotting from signal."

coloropts = [2,4,3,6,7,9,28,46] # some good colors for lines
markeropts = [1,20,21,22,23] # some good marker styles for lines
linestyleopts = [1,2,3,7,9] # some good styles for lines

for fileNum, sig in enumerate(hSigCutsCountDict.keys()):
    hSig = hSigDict[sig] 
    hSigCutsCount = hSigCutsCountDict[sig]
    for i, cut in enumerate(cuts):
        if i>nCuts: break
        hSig.Fill(i, hSigCutsCount[i])
        hSig.GetXaxis().SetBinLabel(i+1, cut)

    hcolor = coloropts[fileNum % len(coloropts)]
    hmarkerstyle = markeropts[(fileNum/len(coloropts)) % len(markeropts)]

    hSig.SetLineColor(hcolor) 
    hSig.SetMarkerStyle(hmarkerstyle)
    hSig.SetMarkerColor(hcolor)
    hlinestyle = linestyleopts[(fileNum/len(coloropts)/len(markeropts)) % \
            len(linestyleopts)]
    hSig.SetLineStyle(hlinestyle)

    legend.AddEntry(hSig, hSig.GetTitle())
    hSig.Draw("hist same") # same pad

    # # show the number of events left over after each cut
    # print "Num surviving events after each cut from sig %s:" % filename 
    # for i, cut in enumerate(cuts):
    #     print cut, hSig.GetBinContent(i+1)
    #     nEvtsLabel = TText()
    #     nEvtsLabel.SetNDC()
    #     nEvtsLabel.SetTextSize(0.02)
    #     nEvtsLabel.SetTextAlign(22)
    #     nEvtsLabel.SetTextAngle(0)
    #     nEvtsLabel.SetTextColor(hcolor)
    #     nEvtsLabel.DrawText(0.1+0.4/nCuts+0.8*float(i)/nCuts, \
    #             0.7-(processNum)*0.02-(1+fileNum)*0.02, \
    #             str(int(hSig.GetBinContent(i+1))))
    #     nEvtsLabels.append(nEvtsLabel)
    # print


#--------------------------------------------------------------------------------#
print "Drawing cutflow."

legend.SetTextSize(0.02)
legend.Draw("same")
c.SetLogy()
c.Update()

if displayMode:
    print "Done with cutflow. Press enter to continue."
    raw_input()
else:
    gSystem.ProcessEvents()
    imgName = "/afs/cern.ch/user/c/cmiao/private/CMSSW_9_4_9/s2019_SUSY/"+\
            "plots/v3CutSequence/cutflow_"+channelName+".png"
    print "Saving image", imgName
    img = TImage.Create()
    img.FromPad(c)
    img.WriteImage(imgName)

#--------------------------------------------------------------------------------#
# *************** Draw pie charts ************
c.SetLogy(0) # unset logy
c = TCanvas("c","c",10,10,700,700)

nocutPieVals = []
allcutsPieVals = []
pieColors = []
for process in processes:
    nocutPieVals.append(hBkgdCutsCountDict[process][0])
    allcutsPieVals.append(hBkgdCutsCountDict[process][nCuts-1])
    pieColors.append(processes[process])

nocutPie = TPie("nocutPie", "Bkgd breakdown, no cuts ("+channelName+")", \
        len(nocutPieVals), array('f',nocutPieVals))
nocutPie.SetLabelFormat("%txt %val (%perc)")
nocutPie.SetFillColors(array('i',pieColors))
nocutPie.SetValueFormat("%.0f")
nocutPie.SetTextSize(0.02)
nocutPie.SetRadius(0.3)

lastcut = cuts[nCuts-1]
allcutsPie = TPie("allcutsPie", "Bkgd breakdown, "+lastcut+"("+channelName+")", \
        len(allcutsPieVals), array('f',allcutsPieVals))
allcutsPie.SetLabelFormat("#splitline{%txt}{%val (%perc)}")
allcutsPie.SetFillColors(array('i',pieColors))
allcutsPie.SetValueFormat("%.0f")
allcutsPie.SetTextSize(0.02)
allcutsPie.SetRadius(0.3)

for i, process in enumerate(hBkgdCutsCountDict.keys()):
    nocutPie.SetEntryLabel(i, process)
    allcutsPie.SetEntryLabel(i, process)

c.cd()
nocutPie.Draw("nol sc")
c.Update()
if displayMode:
    print "Done with nocut pie. Press enter to continue."
    raw_input()
else:
    gSystem.ProcessEvents()
    imgName = "/afs/cern.ch/user/c/cmiao/private/CMSSW_9_4_9/s2019_SUSY/"+\
            "plots/v3CutSequence/pie_nocut_"+channelName+".png"
    print "Saving image", imgName
    img = TImage.Create()
    img.FromPad(c)
    img.WriteImage(imgName)

c.cd()
allcutsPie.Draw("nol sc")
c.Update()
if displayMode:
    print "Done with all cuts pie. Press enter to finish."
    raw_input()
else:
    gSystem.ProcessEvents()
    imgName = "/afs/cern.ch/user/c/cmiao/private/CMSSW_9_4_9/s2019_SUSY/"+\
            "plots/v3CutSequence/pie_"+lastcut+"_"+channelName+".png"
    print "Saving image", imgName
    img = TImage.Create()
    img.FromPad(c)
    img.WriteImage(imgName)
    print "Done."
