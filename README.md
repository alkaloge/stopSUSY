# stopSUSY
SUSY project with Alexis S2019-F2019

## Run2
v1: Working with Run 2 NanoAOD data.  
Workflow instructions to make control plots from scratch after cloning this repo. _NOTE: All scripts have commenting at top with more detailed instructions on use. Also, in general, for the commands listed below, changing "all" to "test" will typically run a smaller number of jobs locally rather than submitting them to condor._  
#### Ntupling
1. (Very fast) Given datasets listed in bkgd_datasets, sig_datasets, and data_fileRedirector, creates lists of all the file names for those datasets. This step isn't technically necessary as these ntuple list files have already been included in the repo, but to recreate these files, execute:
```
bash getDASNtuples.sh
```
2. (Very slow) Produce ntuples. This will submit a condor job for each ntuple for each subprocess listed in bkgd_fileRedirector, for each channel, applying very loose cuts. 
- If necessary, change these variables for directories before running:
  - `myReferenceDataDir`, `myDataDir` in `makeNtuple.py`
  - `baseDir`, `condorLogDir`, `x509Adr` in `createCondorsubNtuplingSubprocess.sh`
  - Note that the directory `myReferenceDataDir` must contain the following files:
    - Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt
    - MC_Moriond17_PU25ns_V1.root
    - Data_Pileup_2016_271036-284044_80bins.root
  - Note that `x509Adr` can be found in the printed information when executing voms-proxy-init for the GRID certificate.
- Adjust which channels and processes to submit in `makeAllNtuples.py`:
```
bash makeAllNtuples.py all
```
3. (Fast) hadd the ntuples from step 2 so that there is only 1 ntuple for each subprocess. This will submit a condor job for each subprocess listed in bkgd_fileRedirector, for each channel.
- If necessary, change these variables for directories before running:
  - `myDataDir` in `haddSubprocess.sh`
  - `baseDir` and `condorLogDir` in `createCondorsubHadd.sh`
- Adjust which channels and processes to submit in `haddAllNtuples.sh`. Then execute:
```
bash haddAllNtuples.sh all
```
#### Plotting
_The next few steps can all be executed using the same command, but different sections of `plotAllVars.sh` should be commented out:_
```
bash plotAllVars.sh all save
```
4. (Slow to very slow) Plot with QCD from MC (aka round 1 of plotting): `plot1D_qcdMC.py`. For each of the ABCD regions, it will produce a root file containing the canvases for all the control variables which uses MC for QCD as well as each of the individual histograms. It will also save 2 files with the cutflow information: the txt file is human readable and the hdf (pandas dataframe) file is used as input when drawing the cutflow (step 7).
- If necessary, change these variables for directories before running:
  - `myDataDir`, `statsDir`, `imgDir` in `plot1D_qcdMC.py`
  - `baseDir` and `condorLogDir` in `createCondorsubPlotting.sh`
- To submit all of these jobs to condor, uncomment section 1A "Normal 1d plots (QCD MC)" and adjust cuts, regions, and channels in `plotAllVars.sh` (note that all 4 regions for a particular cut + channel need to have been completed before step 5 can be executed for that cut + channel). Then execute: `bash plotAllVars.sh all save`
- You can also run this on 1 specific channel, last cut, and region by executing
```
python plot1D_qcdMC.py all save [mumu/muel/elel] [lastcut] [A/B/C/D/any]
```
5. (Very fast) Plot with QCD estimated from data using the ABCD method (aka round 2 of plotting): `plot1D_qcdData.py`. This will produce the same structure of root file that step 4 produces, but will only plot in the signal (B) region.
- If necessary, change these variables for directories before running:
  - `imgDir` in `plot1D_qcdData.py`
- This step is run locally. Uncomment section 1B and adjust cuts and channels in `plotAllVars.sh` as needed. Then execute: `bash plotAllVars.sh all save`
- You can also run this on 1 specific channel and last cut by executing
```
python plot1D_qcdData.py all save [mumu/muel/elel] [lastcut]
```
#### Drawing/saving plots
_The plots outputted by steps 4 and 5 can be viewed directly from the outputted plots root file, or:_  
6. (Very fast) Save the plots as actual pngs from the root files outputted in steps 4 and 5.
- If necessary, change these variables for directories before running:
  - `imgDir` in `getPlots.py`
- This step is run locally. Uncomment sections 3A and/or 3B in `plotAllVars.sh`, then execute `bash plotAllVars.sh all save`
- You can also run this on 1 specific channel and last cut by executing
```
python getPlots.py all save [mumu/muel/elel] [lastcut] [qcdMC/qcdData] [A/B/C/D (only needed for qcdMC)]
```
7. (Very fast) Save the cutflow plots and piecharts (for baseline and nJet<4 cuts) from the cutflow stats outputted in step 4.
- If necessary, change these variables for directories before running:
  - `statsDir`, `cutflowPlotsDir` in `plotCutflows.py`
- This step is run locally. Uncomment section 4 in `plotAllVars.sh`, then execute `bash plotAllVars.sh all save` 
- You can also run this on 1 specific channel and last cut by executing
```
python plotCutflows.py all save [mumu/muel/elel] [A/B/C/D]
```

## HLLHC
v3CutSequence:
Handling stacking bkgd from multiple different sources, condor submit files are now automatically created, cutflows first created as a text file before an additional script plots the cutflows and pie charts for bkgd, actually FINALLY fixing correctly scaling everything using genweights.
Played around with machine learning.

v2CutSequence:
Make ttbar bkgd ntuple separately from sig bkgd, started adding parameters into plotting/ntupling scripts to streamline condor submission process.

v1CutSequence:
Separate plotting into an ntuple maker with extra cuts (makes 1 ntuple with all the trees from sig and ttbar bkgd), started using stopSelection to select leptons. Able to plot cutflows.

v0prep:
Basic plotting some var directly from signal and ttbar bkgd raw files (no cuts or selection)
Preprocess root: rewriting Alexis's code into python, similar to what I did later on but with more steps and from a different format of ntuple trees (e.g. needs b-tag upgrade/downgrade stuff)
