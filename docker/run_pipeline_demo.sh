#!/bin/bash
# Headless demo: run the entire SMT pipeline (both directions) to BLEU.
# The models train in ~10-20 min depending on CPU. Safe to re-run.
set -o pipefail
export USER=${USER:-root}
TUT=/home/ye/exp/SMT-NMT_tutorial

echo "== staging clean-data (raw corpus copies; run the notebook for the full cleaning lesson) =="
mkdir -p $TUT/clean-data
cp -f $TUT/data/*.my $TUT/data/*.rk $TUT/clean-data/
mkdir -p $TUT/clean-data/scripts
cp -f $TUT/scripts/generate_sgms.pl $TUT/scripts/src2sgm.pl $TUT/scripts/ref2sgm.pl $TUT/clean-data/scripts/
chmod +x $TUT/clean-data/scripts/*.pl

echo "== generating SGM test files =="
cd $TUT/clean-data/scripts
perl ./generate_sgms.pl
mkdir -p $TUT/clean-data/test-sgm
cp -f ./*.sgm $TUT/clean-data/test-sgm/

echo "== generating configs =="
cd $TUT/pbsmt
rm -rf baseline
perl ./generate_configs.pl

echo "== training + tuning + evaluation (both directions) =="
time perl ./run-baseline.pl

echo "== BLEU results =="
for d in $TUT/pbsmt/baseline/*/; do
  echo "--- $(basename "$d") ---"
  cat "$d"/evaluation/*multi-bleu* 2>/dev/null || echo "no BLEU file — check $TUT/pbsmt/run1.log"
done
