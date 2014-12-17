package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"reflect"
	"strconv"
)

type Decoder struct {
	r    *csv.Reader
	init bool // whether Decoder has been initialized
}

func NewDecoder(r io.Reader) Decoder {
	return Decoder{r: csv.NewReader(r)}
}

// ReadHeader reads the first row of the underlying csv file and makes
// sure it has the expected format
func (dec *Decoder) ReadHeader() error {
	var err error
	row, err := dec.r.Read()
	rt := reflect.TypeOf((*Event)(nil)).Elem()
	nmax := rt.NumField()
	if len(row) < nmax {
		nmax = len(row)
	}

	for i := 0; i < nmax; i++ {
		field := rt.Field(i)
		name := field.Tag.Get("higgsml")
		if name == "" {
			name = field.Name
		}
		if name != row[i] {
			return fmt.Errorf("higgsml: field #%d. expected [%s]. got [%s]",
				i,
				name,
				row[i],
			)
		}
	}
	return err
}

func (dec *Decoder) Decode(evt *Event) error {
	if !dec.init {
		if err := dec.ReadHeader(); err != nil {
			return err
		}
		dec.init = true
	}

	row, err := dec.r.Read()
	if err != nil {
		return err
	}

	idx := 0
	evt.EventId, err = strconv.Atoi(row[idx])
	if err != nil {
		return err
	}

	idx++
	evt.DER_mass_MMC, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_mass_transverse_met_lep, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_mass_vis, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_pt_h, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_deltaeta_jet_jet, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_mass_jet_jet, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_prodeta_jet_jet, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_deltar_tau_lep, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_pt_tot, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_sum_pt, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_pt_ratio_lep_tau, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_met_phi_centrality, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.DER_lep_eta_centrality, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_tau_pt, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_tau_eta, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_tau_phi, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_lep_pt, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_lep_eta, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_lep_phi, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_met, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_met_phi, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_met_sumet, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_jet_num, err = strconv.Atoi(row[idx])
	if err != nil {
		return err
	}

	idx++
	evt.PRI_jet_leading_pt, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_jet_leading_eta, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_jet_leading_phi, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_jet_subleading_pt, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_jet_subleading_eta, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_jet_subleading_phi, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	idx++
	evt.PRI_jet_all_pt, err = strconv.ParseFloat(row[idx], 64)
	if err != nil {
		return err
	}

	if len(row) > idx+3 {
		idx++
		evt.Weight, err = strconv.ParseFloat(row[idx], 64)
		if err != nil {
			return err
		}

		idx++
		evt.Label = row[idx]

		idx++
		evt.KaggleSet = row[idx]

		idx++
		evt.KaggleWeight, err = strconv.ParseFloat(row[idx], 64)
		if err != nil {
			return err
		}

	}

	return err
}
