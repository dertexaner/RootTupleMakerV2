#ifndef RootTupleMakerV2EventSelection
#define RootTupleMakerV2EventSelection

#include "FWCore/Framework/interface/EDProducer.h"

class RootTupleMakerV2_EventSelection : public edm::EDProducer {
 public:
  explicit RootTupleMakerV2_EventSelection(const edm::ParameterSet&);

 private:
  void produce( edm::Event &, const edm::EventSetup & );
  const edm::InputTag   l1InputTag,vtxInputTag;
  const unsigned int    vtxMinNDOF;
  const double          vtxMaxAbsZ, vtxMaxd0;
  const edm::InputTag   trkInputTag;
  const unsigned int    noOfHPTracks;
  const double          hpTrackThreshold;
  const edm::InputTag   hcalNoiseInputTag;
};

#endif