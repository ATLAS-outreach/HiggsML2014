package main

type Event struct {
	EventId                     int
	DER_mass_MMC                float64
	DER_mass_transverse_met_lep float64
	DER_mass_vis                float64
	DER_pt_h                    float64
	DER_deltaeta_jet_jet        float64
	DER_mass_jet_jet            float64
	DER_prodeta_jet_jet         float64
	DER_deltar_tau_lep          float64
	DER_pt_tot                  float64
	DER_sum_pt                  float64
	DER_pt_ratio_lep_tau        float64
	DER_met_phi_centrality      float64
	DER_lep_eta_centrality      float64
	PRI_tau_pt                  float64
	PRI_tau_eta                 float64
	PRI_tau_phi                 float64
	PRI_lep_pt                  float64
	PRI_lep_eta                 float64
	PRI_lep_phi                 float64
	PRI_met                     float64
	PRI_met_phi                 float64
	PRI_met_sumet               float64
	PRI_jet_num                 int
	PRI_jet_leading_pt          float64
	PRI_jet_leading_eta         float64
	PRI_jet_leading_phi         float64
	PRI_jet_subleading_pt       float64
	PRI_jet_subleading_eta      float64
	PRI_jet_subleading_phi      float64
	PRI_jet_all_pt              float64

	Weight       float64
	Label        string
	KaggleSet    string
	KaggleWeight float64

	Score float64
}
