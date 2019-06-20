#!/usr/bin/env python

# Overlays the cutflow hists for bkgd and each of the signal files.
# Uses the root files outputted by makeNtupleBkgd.py and makeNtupleSigs.py
# Uses xsec info from sig_SingleStop_files

from ROOT import TFile, TTree, TH1F, TCanvas, TLorentzVector, TImage, TLegend
from ROOT import gSystem, gStyle
import numpy as np
from math import sqrt

assert len(sys.argv) == 5, "need 4 command line args: testMode{0,1}, cutMode{0,1}, findingSameFlavor{0,1}, muPreference{0,1}"

# limits the number of events and files to loop over
testMode = bool(int(sys.argv[1]))
# applying cuts
cutMode = bool(int(sys.argv[2]))
# selecting for either mu-mu or el-el (as opposed to mu-el or el-mu)
findingSameFlavor = bool(int(sys.argv[3]))
# only applies if findingSameFlav; selects for mu-mu as opposed to el-el
muPreference = bool(int(sys.argv[4]))
# copy in the bkgd and sigs filenames from makeNtupleBkgd.py and makeNtupleSigs.py
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

bkgdNtupleAdr = "~/private/CMSSW_9_4_9/s2019_SUSY/myData/stopCut_27Bkgd_TTDiLept_muel_withcuts.root"
sigsNtupleAdr = "~/private/CMSSW_9_4_9/s2019_SUSY/myData/stopCut_02Sig_muel_withcuts.root"

assert bkgdNtupleAdr[50:54] == "Bkgd", "bkgdNtupleAdr not bkgd"
assert sigsNtupleAdr[50:53] == "Sig", "sigsNtupleAdr not sigs"
assert bkgdNtupleAdr[-18:] == sigsNtupleAdr[-18:], "sigs/bkgd settings don't match"
print "Plotting from",bkgdNtupleAdr,"and",sigsNtupleAdr

numSigFiles = int(sigsNtupleAdr[48:50])

lumi = 3000000 # luminosity = 3000 /fb = 3,000,000 /fb
c1 = TCanvas("c1","Plot",10,20,1000,700)
gStyle.SetOptStat(0) # don't show any stats

xsec = 67.75 # production cross section

bkgdFile = TFile.Open(bkgdNtupleAdr, "READ")
hBkgd = bkgdFile.Get("bkgd_cutflow")
hBkgd.Sumw2()
hBkgd.SetTitle("Cutflow ("+bkgdNtupleAdr[-18:-14]+", norm to 3000 /fb)")
hBkgd.GetYaxis().SetTitle("Number of Events")
hBkgd.Scale(xsec*lumi/hBkgd.GetSumOfWeights())
hBkgd.SetLineColor(1) # black
hBkgd.SetMinimum(1)
hBkgd.SetMaximum(10**12)
hBkgd.Draw("hist")
c1.Update()


sigDataListFile = open("sig_SingleStop_files")
coloropts = [2,4,3,6,7,9,28,46] # some good colors for lines
markeropts = [1,20,21,22,23] # some good marker styles for lines
linestyleopts = [1,2,3,7,9] # some good styles for lines

hSigArr = []
print
for fileNum, line in enumerate(sigDataListFile):
    if fileNum + 1 > numSigFiles: break
    line = line.rstrip('\n')
    filename, xsec = line.split(" ")
    xsec = float(xsec)

    sigFile = TFile.Open(sigsNtupleAdr, "READ")
    hSigArr.append(sigFile.Get("sig_"+filename[21:31]+"_cutflow"))
    hSigArr[fileNum].SetDirectory(0)

    hcolor = coloropts[fileNum % len(coloropts)]
    hSigArr[fileNum].SetLineColor(hcolor) 
    hmarkerstyle = markeropts[(fileNum/len(coloropts)) % len(markeropts)]
    hSigArr[fileNum].SetMarkerStyle(hmarkerstyle)
    hSigArr[fileNum].SetMarkerColor(hcolor)
    hlinestyle = linestyleopts[(fileNum/len(coloropts)/len(markeropts)) % \
            len(linestyleopts)]
    hSigArr[fileNum].SetLineStyle(hlinestyle)

    hSigArr[fileNum].Sumw2()
    hSigArr[fileNum].Scale(xsec * lumi /
            hSigArr[fileNum].GetSumOfWeights())
    hSigArr[fileNum].SetMinimum(1)
    hSigArr[fileNum].SetMaximum(10**12)
    hSigArr[fileNum].Draw("hist same") # same pad, draw marker
    c1.Update()

    print "Num surviving events after each cut from sig %s:" % filename 
    for i in range(1,hBkgd.GetNbinsX()):
        # print hBkgd.GetXaxis().GetBinLabel(i+1),"S/sqrt(B):",\
        #         hSigArr[fileNum].GetBinContent(i+1)/sqrt(hBkgd.GetBinContent(i+1))
        print hBkgd.GetXaxis().GetBinLabel(i+1),hSigArr[fileNum].GetBinContent(i+1)
    print

print "Num surviving events after each cut from bkgd:" 
for i in range(1,hBkgd.GetNbinsX()):
    print hBkgd.GetXaxis().GetBinLabel(i+1),hBkgd.GetBinContent(i+1)
print

legend = TLegend(.70,.75,.90,.90)
legend.AddEntry(hBkgd, "bkgd_cutflow")
legend.SetTextSize(0.02)
for fileNum, h in enumerate(hSigArr):
    legend.AddEntry(hSigArr[fileNum], hSigArr[fileNum].GetTitle())
legend.Draw("same")

c1.SetLogy()
c1.Update()

print "Done. Press enter to finish."
raw_input()
