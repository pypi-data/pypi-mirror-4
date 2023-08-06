#!/bin/bash -e

#dot2tex --autosize --crop --figonly --graphstyle="scale=.5" --prog=neato -d net-001.dot > net-001.tex

for fig in net-realisations-001
do
  epstool --copy --bbox $fig.eps $fig-bbox.eps
  ps2pdf -dEPSCrop $fig-bbox.eps
done

pdflatex figures

