#----------------------------------------------------------------------------------------------------
# Load PAT template
#----------------------------------------------------------------------------------------------------

# Starting with a skeleton process which gets imported with the following line
from PhysicsTools.PatAlgos.patTemplate_cfg import *

# Load PF isolation for muons and electrons
from PhysicsTools.PatAlgos.tools.pfTools import *
usePFIso ( process )

# Remove MC matching *and* use the right JECs for data analysis 
from PhysicsTools.PatAlgos.tools.coreTools import *
runOnData( process )

# Options and Output Report
process.options.wantSummary = False

import os

############## IMPORTANT ########################################
# If you run over many samples and you save the log, remember to reduce
# the size of the output by prescaling the report of the event number
process.MessageLogger.cerr.FwkReport.reportEvery = 1
process.MessageLogger.cerr.default.limit = 10
#################################################################

#----------------------------------------------------------------------------------------------------
# Load our RootTupleMakerV2 modules
#----------------------------------------------------------------------------------------------------

process.load('Leptoquarks.RootTupleMakerV2.Ntuple_cff')

# Output ROOT file
process.TFileService = cms.Service("TFileService",
    fileName = cms.string( 'rootTupleMaker_CRAB_DATA_2012_Top_53X_LOCALTEST.root' )
)

#----------------------------------------------------------------------------------------------------
# Set global settings (number of events, global tag, input files, etc)
#----------------------------------------------------------------------------------------------------

# GlobalTag
process.GlobalTag.globaltag = 'FT53_V21A_AN6::All'

# Events to process
process.maxEvents.input = 10

# Input files
process.source.fileNames = [
    'root://eoscms//eos/cms/store/user/hsaka/2012prep/Run2012A_SingleElectron_AOD_22Jan2013-v1_20000_EA28F8B2-AE72-E211-97F0-0025901D4938.root'
]

#----------------------------------------------------------------------------------------------------
# HEEP 4.0 (electron ID) still uses the 2011 definitions of rho for isolation corrections.
# 
# Recipe taken from here:
# https://twiki.cern.ch/twiki/bin/view/CMS/EgammaEARhoCorrection#Rho_for_2011_Effective_Areas
#----------------------------------------------------------------------------------------------------

process.load("RecoJets.JetProducers.kt4PFJets_cfi")
process.kt6PFJetsForHEEPIsolation = process.kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
process.kt6PFJetsForHEEPIsolation.Rho_EtaMax = cms.double(2.5)

#----------------------------------------------------------------------------------------------------
# Turn on trigger matching
# 
# Example taken from PAT SWGuide twiki
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTriggerMatchExercise#TrigProduce
#
# Don't include this line (recommended by instructions): removeCleaningFromTriggerMatching( process )
# It will break the matching.
#----------------------------------------------------------------------------------------------------

# load the PAT trigger Python tools
from PhysicsTools.PatAlgos.tools.trigTools import *

# switch on the trigger matching
switchOnTriggerMatching( process, triggerMatchers = [
       # electrons 
        'cleanElectronTriggerMatchHLTSingleElectron',
        'cleanElectronTriggerMatchHLTSingleElectronWP80',
        'cleanElectronTriggerMatchHLTDoubleElectron',
        # muons
        'cleanMuonTriggerMatchHLTSingleMuon',
        'cleanMuonTriggerMatchHLTSingleIsoMuon'
] )

#----------------------------------------------------------------------------------------------------
# Add PFMET and TCMET
# See https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTools#MET_Tools
#----------------------------------------------------------------------------------------------------

from PhysicsTools.PatAlgos.tools.metTools import *
addPfMET(process, 'PF') # This adds Type1-corrected PFMET
addTcMET(process, 'TC') # This adds raw TC MET

#----------------------------------------------------------------------------------------------------
# Add MET filters
#----------------------------------------------------------------------------------------------------

process.load("Leptoquarks.RootTupleMakerV2.metFilters_cfi")

#----------------------------------------------------------------------------------------------------
# Rerun full HPS sequence to fully profit from the fix of high pT taus
#----------------------------------------------------------------------------------------------------

process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")

#----------------------------------------------------------------------------------------------------
# Modify cleanPatTaus (HPS Taus) - loosen up a bit
# http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/CMSSW/PhysicsTools/PatAlgos/python/cleaningLayer1/tauCleaner_cfi.py?revision=1.11&view=markup
#----------------------------------------------------------------------------------------------------

process.cleanPatTaus.preselection = cms.string(' tauID("decayModeFinding") > 0.5 ')
process.cleanPatTaus.finalCut     = cms.string(' pt > 15.0 & abs(eta) < 2.5      ')

#----------------------------------------------------------------------------------------------------
# Add Tau ID sources (HPS Taus)
#----------------------------------------------------------------------------------------------------

process.load("Leptoquarks.RootTupleMakerV2.tauIDsources_cfi")

#----------------------------------------------------------------------------------------------------
# Add MVA electron ID
#
# MVA electron ID details on this twiki:
# https://twiki.cern.ch/twiki/bin/view/CMS/MultivariateElectronIdentification#MVA_based_Id_in_PAT
#
# Taken from the example:
# http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/CMSSW/EgammaAnalysis/ElectronTools/test/patTuple_electronId_cfg.py?revision=1.2&view=markup&pathrev=V00-00-09
#----------------------------------------------------------------------------------------------------

process.load('EgammaAnalysis.ElectronTools.electronIdMVAProducer_cfi')
process.mvaID = cms.Sequence(  process.mvaTrigV0 + process.mvaTrigNoIPV0 + process.mvaNonTrigV0 )
process.patElectrons.electronIDSources.mvaTrigV0     = cms.InputTag("mvaTrigV0")  
process.patElectrons.electronIDSources.mvaNonTrigV0  = cms.InputTag("mvaNonTrigV0") 
process.patElectrons.electronIDSources.mvaTrigNoIPV0 = cms.InputTag("mvaTrigNoIPV0")

process.patConversions = cms.EDProducer("PATConversionProducer",
    electronSource = cms.InputTag("cleanPatElectrons")  
)

#----------------------------------------------------------------------------------------------------
# Add the PFJets
# See https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTools#Jet_Tools
# 
# Recommended JEC for PFJets:
# - L1FastJet : https://twiki.cern.ch/twiki/bin/view/CMS/JECAnalysesRecommendations#Corrections
# - L2Relative: https://twiki.cern.ch/twiki/bin/view/CMS/IntroToJEC#Mandatory_Jet_Energy_Corrections
# - L3Absolute: https://twiki.cern.ch/twiki/bin/view/CMS/IntroToJEC#Mandatory_Jet_Energy_Corrections
#----------------------------------------------------------------------------------------------------

from PhysicsTools.PatAlgos.tools.jetTools import *

process.load("PhysicsTools.PatAlgos.patSequences_cff")

addJetCollection(process,cms.InputTag('ak5PFJets'),
    'AK5', 'PF',
    doJetID      = True , # Perform jet ID algorithm and store ID info in the jet
    doJTA        = True , # Perform jet track association and determine jet charge
    doBTagging   = True , # Perform b-tagging and store b-tagging info in the jet
    doType1MET   = False, # Don't store Type1 PFMET information. This will be done by the runMEtUncertainties tool.
    jetIdLabel   = "ak5",# Which jet ID label should be used?
    jetCorrLabel = ('AK5Calo', ['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual']), # Which jet corrections should be used?
    genJetCollection = cms.InputTag("ak5GenJets") # Which GEN jets should be used?
)

#----------------------------------------------------------------------------------------------------
# Switch to CaloJets
# See https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTools#Jet_Tools
#
# Yes, CaloJets are already the default, so switching to them seems counter-intuitive
# But by default in this version of PAT (V08-09-62), CaloJet corrections are done with L1Offset
# 
# This is a problem for two reasons:
# - The newer GlobalTags (including START53_V27) do not include L1Offset corrections
# - The recommended corrections for L1 corrections in CaloJets are L1FastJet corrections
# 
# So we use switchJetCollection to switch to CaloJets with the L1FastJet corrections
# 
# Recommended JEC for CaloJets:
# - L1FastJet : https://twiki.cern.ch/twiki/bin/view/CMS/JECAnalysesRecommendations#Corrections
# - L2Relative: https://twiki.cern.ch/twiki/bin/view/CMS/IntroToJEC#Mandatory_Jet_Energy_Corrections
# - L3Absolute: https://twiki.cern.ch/twiki/bin/view/CMS/IntroToJEC#Mandatory_Jet_Energy_Corrections
#----------------------------------------------------------------------------------------------------

switchJetCollection(process,cms.InputTag('ak5CaloJets'),
    doJetID      = True , # Perform jet ID algorithm and store ID info in the jet
    doJTA        = True , # Perform jet track association and determine jet charge
    doBTagging   = True , # Perform b-tagging and store b-tagging info in the jet
    doType1MET   = True , # Store Type1 PFMET information.  Label of resulting PFMET collection is: patMETsAK5Calo
    jetIdLabel   = "ak5",# Which jet ID label should be used?
    jetCorrLabel = ('AK5Calo', ['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual']), # Which jet corrections should be used?
    genJetCollection = cms.InputTag("ak5GenJets") # Which GEN jets should be used?
)

#----------------------------------------------------------------------------------------------------
# Define the systematic shift correction
# Private email from Christian Veelken.  Original values are here:
# http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/CMSSW/JetMETCorrections/Type1MET/python/pfMETsysShiftCorrections_cfi.py?revision=1.7&view=markup
#----------------------------------------------------------------------------------------------------

process.load("JetMETCorrections.Type1MET.pfMETCorrections_cff")
process.load("JetMETCorrections.Type1MET.pfMETsysShiftCorrections_cfi")

process.pfMEtSysShiftCorrParameters_2012runABCDvsNvtx_data = cms.VPSet(cms.PSet( # CV: ReReco data + Summer'13 JEC
    numJetsMin = cms.int32(-1),
    numJetsMax = cms.int32(-1),
    px = cms.string("+4.83642e-02 + 2.48870e-01*Nvtx"),
    py = cms.string("-1.50135e-01 - 8.27917e-02*Nvtx")
))

process.pfMEtSysShiftCorr.parameter = process.pfMEtSysShiftCorrParameters_2012runABCDvsNvtx_data[0]

#----------------------------------------------------------------------------------------------------
# Use the runMetUncertainties tool here
# See https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTools#MET_Systematics_Tools
#----------------------------------------------------------------------------------------------------

from PhysicsTools.PatUtils.tools.metUncertaintyTools import runMEtUncertainties

runMEtUncertainties(
    process,
    jetCollection           = cms.InputTag('cleanPatJetsAK5PF'), 
    doApplySysShiftCorr     = True,  # Apply correction for systematic x/y shift in MET
    doApplyType0corr        = True,  # Apply correction for pileup
    makeType1corrPFMEt      = True,  # Apply correction for jet energy scale
    makeType1p2corrPFMEt    = False, # DO NOT apply correction for unclustered energy (degrades MET resolution)
    makePFMEtByMVA          = False, # We don't use MVA PFMET 
    doSmearJets             = False, # Very important to NOT smear the pfjets (DATA ONLY)
    addToPatDefaultSequence = True,  # Add this to the PAT sequence
    sysShiftCorrParameter   = process.pfMEtSysShiftCorrParameters_2012runABCDvsNvtx_data[0]
)

#----------------------------------------------------------------------------------------------------
# Available pat::MET collections for analysis
# - process.patMETsTC                               : raw        TCMET   (NO  jet smearing)
# 
# - process.patMETsRawCalo                          : raw        CaloMET (NO  jet smearing)
# - process.patMETs                                 : Type1      CaloMET (NO  jet smearing)
# 
# - process.patMETsRawPF                            : raw        PFMET   (NO  jet smearing)
# - process.patType1CorrectedPFMet_Type1Only        : Type1      PFMET   (NO  jet smearing)
# - process.patType1CorrectedPFMet_Type01Only       : Type0+1    PFMET   (NO  jet smearing)
# - process.patType1CorrectedPFMet                  : Type0+1+XY PFMET   (NO  jet smearing) <-- Recommended for analysis
# 
# Notes:
# - No Type0 corrections are available for CaloMET
# - No Type0 or Type1 corrections are available for TCMET
# - No Type2 corrections recommended for any MET, since they degrade the MET resolution
#
# Thanks to Jared Sturdy, Christian Veelken, and Guler Karapinar
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# Add the raw CaloMET and raw PFMET
# Raw TCMET is already included: patMETsRawTC
#----------------------------------------------------------------------------------------------------

# CaloMET: raw

process.patMETsRawCalo = process.patMETsTC.clone()
process.patMETsRawCalo.metSource = cms.InputTag("met")

# PFMET: raw

process.patMETsRawPF = process.patMETsTC.clone()
process.patMETsRawPF.metSource = cms.InputTag("pfMet")

# PFMET: Type1, with jet smearing

process.patType1CorrectedPFMetType1Only = process.patType1CorrectedPFMet.clone()
process.patType1CorrectedPFMetType1Only.srcType1Corrections = cms.VInputTag(
    cms.InputTag("patPFJetMETtype1p2Corr","type1"), 
    # cms.InputTag("patPFMETtype0Corr"), 
    # cms.InputTag("pfMEtSysShiftCorr")
)

# PFMET: Type0+1, with jet smearing

process.patType1CorrectedPFMetType01Only = process.patType1CorrectedPFMet.clone()
process.patType1CorrectedPFMetType01Only.srcType1Corrections = cms.VInputTag(
    cms.InputTag("patPFJetMETtype1p2Corr","type1"), 
    cms.InputTag("patPFMETtype0Corr"), 
    # cms.InputTag("pfMEtSysShiftCorr")
)

#----------------------------------------------------------------------------------------------------
# This is data, so the systematic MET collections shouldn't be considered
#----------------------------------------------------------------------------------------------------

process.rootTuplePFMETType01XYCorUnclusteredUp.InputTag   = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorUnclusteredDown.InputTag = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorElectronEnUp.InputTag    = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorElectronEnDown.InputTag  = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorMuonEnUp.InputTag        = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorMuonEnDown.InputTag      = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorTauEnUp.InputTag         = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorTauEnDown.InputTag       = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorJetResUp.InputTag        = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorJetResDown.InputTag      = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorJetEnUp.InputTag         = cms.InputTag("patType1CorrectedPFMet")
process.rootTuplePFMETType01XYCorJetEnDown.InputTag       = cms.InputTag("patType1CorrectedPFMet") 

#----------------------------------------------------------------------------------------------------
# Set Lepton-Gen Matching Parameters
#----------------------------------------------------------------------------------------------------

process.load("Leptoquarks.RootTupleMakerV2.leptonGenMatching_cfi")
process.patDefaultSequence.replace( process.electronMatch, process.elMatch )
process.patElectrons.genParticleMatch = cms.VInputTag( cms.InputTag("elMatch") )
process.patDefaultSequence.replace( process.muonMatch, process.muMatch )
process.patMuons.genParticleMatch = cms.VInputTag( cms.InputTag("muMatch") )
process.patDefaultSequence.replace( process.tauMatch, process.tauLepMatch )
process.patTaus.genParticleMatch = cms.VInputTag( cms.InputTag("tauLepMatch") )
process.patDefaultSequence.replace( process.tauGenJetMatch, process.tauJetMatch )
process.patTaus.genJetMatch = cms.InputTag("tauJetMatch")

#----------------------------------------------------------------------------------------------------
# Lepton + Jets filter
#----------------------------------------------------------------------------------------------------

process.load("Leptoquarks.LeptonJetFilter.leptonjetfilter_cfi")

#### Shared Muon/Electron/Tau Skim
process.LJFilter.tauLabel  = cms.InputTag("cleanPatTaus")                        
process.LJFilter.muLabel   = cms.InputTag("cleanPatMuons")
process.LJFilter.elecLabel = cms.InputTag("cleanPatElectrons")
process.LJFilter.jetLabel  = cms.InputTag("cleanPatJetsAK5PF")
process.LJFilter.muonsMin = 0
process.LJFilter.muPT     = 10.0
process.LJFilter.electronsMin = 0
process.LJFilter.elecPT       = 15.0
process.LJFilter.tausMin = 0
process.LJFilter.tauPT   = 15.0
process.LJFilter.jetsMin = 0
process.LJFilter.jetPT   = 15.0
process.LJFilter.counteitherleptontype = True
process.LJFilter.customfilterEMuTauJet2012 = True
# -- WARNING :
# "customfilterEMuTauJet2012" configuration is hard-coded.
# (see: http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/Leptoquarks/LeptonJetFilter/src/LeptonJetFilter.cc )
# "customfilterEMuTauJet2012" is the desired mode of operation for the Lepton+Jets Filter in 2012.

#----------------------------------------------------------------------------------------------------
# Define the output tree for RootTupleMakerV2
#----------------------------------------------------------------------------------------------------

# RootTupleMakerV2 tree
process.rootTupleTree = cms.EDAnalyzer("RootTupleMakerV2_Tree",
    outputCommands = cms.untracked.vstring(
        'drop *',
        # Event information
        'keep *_rootTupleEvent_*_*',
        'keep *_rootTupleEventSelection_*_*',
        # Single objects
        'keep *_rootTuplePFCandidates_*_*',
        'keep *_rootTuplePFJets_*_*',
        'keep *_rootTupleCaloJets_*_*',
        'keep *_rootTupleElectrons_*_*',
        'keep *_rootTupleMuons_*_*',
        'keep *_rootTupleHPSTaus_*_*',
        'keep *_rootTuplePhotons_*_*',
        'keep *_rootTupleVertex_*_*',
        # MET objects for analysis
        'keep *_rootTupleTCMET_*_*',
        'keep *_rootTupleCaloMET_*_*',
        'keep *_rootTupleCaloMETType1Cor_*_*',
        'keep *_rootTuplePFMET_*_*',
        'keep *_rootTuplePFMETType1Cor_*_*',
        'keep *_rootTuplePFMETType01Cor_*_*',
        'keep *_rootTuplePFMETType01XYCor_*_*',
        'keep *_rootTuplePFMETType01XYCor_*_*',
        # pdf weights
        'keep *_rootTuplePFMETType01XYCorUnclusteredUp_*_*',
        'keep *_rootTuplePFMETType01XYCorUnclusteredDown_*_*',
        'keep *_rootTuplePFMETType01XYCorElectronEnUp_*_*',
        'keep *_rootTuplePFMETType01XYCorElectronEnDown_*_*',
        'keep *_rootTuplePFMETType01XYCorMuonEnUp_*_*',
        'keep *_rootTuplePFMETType01XYCorMuonEnDown_*_*',
        'keep *_rootTuplePFMETType01XYCorTauEnUp_*_*',
        'keep *_rootTuplePFMETType01XYCorTauEnDown_*_*',
        'keep *_rootTuplePFMETType01XYCorJetResUp_*_*',
        'keep *_rootTuplePFMETType01XYCorJetResDown_*_*',
        'keep *_rootTuplePFMETType01XYCorJetEnUp_*_*',
        'keep *_rootTuplePFMETType01XYCorJetEnDown_*_*',
        # Trigger objects
        'keep *_rootTupleTrigger_*_*',
        'keep *_rootTupleTriggerObjects_*_*',
        # GEN objects
        'keep *_rootTupleGenEventInfo_*_*',
        'keep *_rootTupleGenParticles_*_*',
        'keep *_rootTupleGenJets_*_*',
        'keep *_rootTupleGenElectronsFromWs_*_*',
        'keep *_rootTupleGenElectronsFromZs_*_*',
        'keep *_rootTupleGenMuonsFromWs_*_*',
        'keep *_rootTupleGenMuonsFromZs_*_*',
        'keep *_rootTupleGenTausFromWs_*_*',
        'keep *_rootTupleGenTausFromZs_*_*',
        'keep *_rootTupleGenMETTrue_*_*',
        'keep *_rootTupleGenMETCalo_*_*'       
    )
)

#----------------------------------------------------------------------------------------------------
# Define GEN particle skimmer modules
#----------------------------------------------------------------------------------------------------

process.load ('Leptoquarks.LeptonJetGenTools.genTauMuElFromZs_cfi')
process.load ('Leptoquarks.LeptonJetGenTools.genTauMuElFromWs_cfi') 

#----------------------------------------------------------------------------------------------------
# Define the path 
#----------------------------------------------------------------------------------------------------

process.p = cms.Path(
    # gen particle skimmer modules
    process.genTausFromWs*
    process.genMuonsFromWs*
    process.genElectronsFromWs*
    process.genTausFromZs*
    process.genMuonsFromZs*
    process.genElectronsFromZs*
    # MVA electron ID
    process.mvaID*
    # HEEP rho for isolation correction
    process.kt6PFJetsForHEEPIsolation*
    # Good vertices
    process.goodVertices*
    # PFMET corrections
    process.type0PFMEtCorrection*
    process.patPFMETtype0Corr*
    process.producePFMETCorrections*
    process.pfMEtSysShiftCorrSequence*
    # MET filters (required):
    process.EcalDeadCellTriggerPrimitiveFilter*
    process.EcalDeadCellBoundaryEnergyFilter*
    process.HBHENoiseFilterResultProducer*
    process.trackingFailureFilter*
    process.eeBadScFilter*
    process.ecalLaserCorrFilter*
    # Now the regular PAT default sequence
    process.patDefaultSequence*
    # MET producers
    process.patMETsRawCalo*
    process.patMETsRawPF*
    process.patType1CorrectedPFMetType1Only*
    process.patType1CorrectedPFMetType01Only*
    # L+J Filter
    process.LJFilter*  
    # Run PAT conversions for electrons
    process.patConversions*
    # Now produce the raw CaloMET and raw PFMET 
    # Re-run full HPS sequence to fully profit from the fix of high pT taus
    process.recoTauClassicHPSSequence*
    # RootTupleMakerV2
    (
    # Event information
    process.rootTupleEvent+
    process.rootTupleEventSelection+
    # Single objects
    process.rootTuplePFCandidates+
    process.rootTuplePFJets+
    process.rootTupleCaloJets+
    process.rootTupleElectrons+
    process.rootTupleMuons+
    process.rootTupleHPSTaus+
    process.rootTuplePhotons+
    process.rootTupleVertex+
    # MET objects for analysis
    process.rootTupleTCMET+
    process.rootTupleCaloMET+
    process.rootTupleCaloMETType1Cor+
    process.rootTuplePFMET+
    process.rootTuplePFMETType1Cor+
    process.rootTuplePFMETType01Cor+
    process.rootTuplePFMETType01XYCor+
    # MET objects for systematics
    process.rootTuplePFMETType01XYCorUnclusteredUp+
    process.rootTuplePFMETType01XYCorUnclusteredDown+
    process.rootTuplePFMETType01XYCorElectronEnUp+
    process.rootTuplePFMETType01XYCorElectronEnDown+
    process.rootTuplePFMETType01XYCorMuonEnUp+
    process.rootTuplePFMETType01XYCorMuonEnDown+
    process.rootTuplePFMETType01XYCorTauEnUp+
    process.rootTuplePFMETType01XYCorTauEnDown+
    process.rootTuplePFMETType01XYCorJetResUp+
    process.rootTuplePFMETType01XYCorJetResDown+
    process.rootTuplePFMETType01XYCorJetEnUp+
    process.rootTuplePFMETType01XYCorJetEnDown+
    # Trigger objects
    process.rootTupleTrigger+
    process.rootTupleTriggerObjects+
    # GEN objects
    process.rootTupleGenEventInfo+
    process.rootTupleGenParticles+
    process.rootTupleGenJets+
    process.rootTupleGenElectronsFromWs+
    process.rootTupleGenElectronsFromZs+
    process.rootTupleGenMuonsFromWs+
    process.rootTupleGenMuonsFromZs+
    process.rootTupleGenTausFromWs+
    process.rootTupleGenTausFromZs+
    process.rootTupleGenMETTrue+
    process.rootTupleGenMETCalo
    )*
    # Put everything into the tree
    process.rootTupleTree
)

#----------------------------------------------------------------------------------------------------
# Dump the root file
#----------------------------------------------------------------------------------------------------

process.dump_module = cms.OutputModule("PoolOutputModule",
    outputCommands = cms.untracked.vstring('keep *'),
    fileName       = cms.untracked.string ('dump.root')
)
process.dump = cms.EndPath (process.dump_module )


#----------------------------------------------------------------------------------------------------
# Run the path
#----------------------------------------------------------------------------------------------------

process.schedule = cms.Schedule(process.p,process.dump)
