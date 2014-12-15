// go-higgsml is a command to exercize a simple window on one variable DER_mass_MMC, to compute the score and build a submission file in Kaggle format.
//
// It is heavily based on higgsml_opendata_simplest.py
package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"math"
	"os"
	"sort"
	"time"
)

const (
	MassCut = 125.0
)

var (
	// somewhat arbitrary value, should be optimised
	g_cutoff = flag.Float64("cut", -22.0, "cut-off value")
)

// Score is the final Kaggle score.
type Score struct {
	Id    int     // event id
	Score float64 // score for that event (eg: AMS)
}

type Scores []Score

func (p Scores) Len() int           { return len(p) }
func (p Scores) Less(i, j int) bool { return p[i].Score < p[j].Score }
func (p Scores) Swap(i, j int)      { p[i], p[j] = p[j], p[i] }

// AMS returns the Approximate Median Significance for sig and bkg,
// where sig and bkg are the sum of signal and background weights in the
// selection region.
func AMS(sig, bkg float64) float64 {
	if bkg == 0 {
		return 0
	}
	return math.Sqrt(2 * ((sig+bkg+10)*math.Log(1+sig/(bkg+10)) - sig))
}

func init() {
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		fmt.Fprintf(os.Stderr, " $ %s [options] [input-data-file [output.csv]]\n\nOptions:\n", os.Args[0])
		flag.PrintDefaults()
	}
}

func main() {
	flag.Parse()

	start := time.Now()
	err := run()
	fmt.Printf("::: timing: %v\n", time.Since(start))
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("::: bye.\n")
}

func run() error {

	fname := "atlas-higgs-challenge-2014-v2.csv"
	ofname := "submission_go_simplest.csv"

	if flag.NArg() > 0 {
		fname = flag.Arg(0)
	}
	if flag.NArg() > 1 {
		ofname = flag.Arg(1)
	}

	fmt.Printf("::: read data file [%s]\n", fname)
	f, err := os.Open(fname)
	if err != nil {
		return err
	}
	defer f.Close()

	fmt.Printf("::: loop on dataset and compute the score\n")
	evts := make([]Event, 0, 1024)
	dec := NewDecoder(f)
	for {
		i := len(evts)
		evts = append(evts, Event{})
		var evt *Event = &evts[i]
		err = dec.Decode(evt)
		if err != nil {
			evts = evts[:i]
			break
		}
		//fmt.Printf("evt=%d weight=%12.10f label=%s\n", evt.EventId, evt.Weight, evt.Label)
		// this is a simple discriminating variable.
		// Signal should be closer to zero.
		// minus sign so that signal has the highest values
		// so we will be making a simple window cut on the Higgs mass estimator
		// 125 GeV is the middle of the window
		evt.Score = -math.Abs(evt.DER_mass_MMC - MassCut)
	}

	if err != nil && err != io.EOF {
		return err
	}
	err = nil

	cutoff := *g_cutoff

	fmt.Printf("::: loop again to determine the AMS, using threshold=%v\n", cutoff)
	sum := struct {
		SelSig float64
		SelBkg float64
		AllSig float64
		AllBkg float64
		SubSig float64
		SubBkg float64

		SelKaggleSig float64
		SelKaggleBkg float64
	}{}

	fmt.Printf("::: only looking at Kaggle public data set ('b') ('t': training, 'v': private, 'u': unused)\n")
	fmt.Printf("::: one could make their own dataset (then the weight should be renormalized)\n")

	for i := range evts {
		evt := &evts[i]
		// compute sum of signal and background weight needed to renormalize
		switch evt.Label {
		case "s":
			sum.AllSig += evt.Weight
		default:
			sum.AllBkg += evt.Weight
		}

		if evt.KaggleSet != "b" {
			continue
		}

		// from now on, only work on subset
		switch evt.Label {
		case "s":
			sum.SubSig += evt.Weight
		default:
			sum.SubBkg += evt.Weight
		}

		// sum event weight passing the selection.
		// of course, in real life the threshold should be optimised
		if evt.Score <= cutoff {
			//fmt.Printf(">>> discard evt=%d (score=%v)\n", evt.EventId, evt.Score)
			continue
		}
		switch evt.Label {
		case "s":
			sum.SelSig += evt.Weight
			sum.SelKaggleSig += evt.KaggleWeight
		case "b":
			sum.SelBkg += evt.Weight
			sum.SelKaggleBkg += evt.KaggleWeight
		}
	}

	// ok, now we have our signal (sum.SelKaggleSig) and background (sum.SelKaggleBkg) estimation.
	// just as an illustration, also compute the renormalization ourself from weight.
	sumsig := sum.SelSig * sum.AllSig / sum.SubSig
	sumbkg := sum.SelBkg * sum.AllBkg / sum.SubBkg
	ams := AMS(sumsig, sumbkg)
	fmt.Printf("::: AMS with recomputed weight: %v (sig=%v, bkg=%v)\n",
		ams, sumsig, sumbkg,
	)
	fmt.Printf("::: AMS with kaggle weight: %v (sig=%v, bkg=%v)\n",
		AMS(sum.SelKaggleSig, sum.SelKaggleBkg), sum.SelKaggleSig, sum.SelKaggleBkg,
	)

	fmt.Printf("::: recomputed weight and Kaggle-weight should be identical if using a predefined Kaggle-subset\n")

	fmt.Printf("::: now building submission file a-la-Kaggle: [%s]...\n", ofname)

	// build subset with only the needed variables
	scores := make([]Score, len(evts))
	for i := range evts {
		evt := &evts[i]
		switch evt.KaggleSet {
		case "b", "v":
			// ok
		default:
			continue
		}
		scores[i] = Score{evt.EventId, evt.Score}
	}

	fmt.Printf("::: sort on the score\n")
	sort.Sort(Scores(scores))

	fmt.Printf("::: build a map key=id, value=rank\n")
	dict := make(map[int]int, len(scores))
	for rank, bdt := range scores {
		dict[bdt.Id] = rank + 1 // kaggle asks to start at 1
	}

	out, err := os.Create(ofname)
	if err != nil {
		return err
	}
	defer out.Close()

	// write header
	fmt.Fprintf(out, "EventId,RankOrder,Class\n")

	for i := range scores {
		evt := &scores[i]
		rank, ok := dict[evt.Id]
		if !ok {
			fmt.Fprintf(os.Stderr, "*** evt-id=%d not in map\n", evt.Id)
			os.Exit(1)
		}
		if rank > len(evts) {
			fmt.Fprintf(os.Stderr, "*** large rank=%d for event #%d (id=%d)\n",
				rank, i, evt.Id,
			)
			break
		}

		// compute label
		label := "b"
		if evt.Score > cutoff {
			label = "s"
		}

		fmt.Fprintf(out, "%d,%d,%s\n", evt.Id, rank, label)
	}

	err = out.Sync()
	if err != nil {
		return err
	}

	err = out.Close()
	if err != nil {
		return err
	}

	fmt.Printf("::: now building submission file a-la-Kaggle: [%s]... [done]\n", ofname)

	return err
}
