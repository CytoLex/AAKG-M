### Limitations

**The operating range is specific and §5.3 measures it**: recall is twice as high on stability as on activity, and
the improvement reaches +0.00003 on the largest quartile. The aggregate is the centre of that range, not a property
of any one assay.

**The structural experts are inherited, not retrained inside each outer fold**; a fully nested protocol would
retrain them per fold. The headline, the scheme breakdown and the category breakdown come from the benchmark's own evaluation script run
on the submitted score file, and that output ships with the submission. The per-mutant predictions released alongside
them are a re-run, not that file: their unit-level Spearman values differ from the submitted ones by 0.008 on average,
which moves the aggregate to 0.692 and the top-of-list figures by about 0.003. The submitted score file is the
artefact the claims rest on; the per-mutant file is offered as a convenience and should not be treated as its source. The one hyperparameter that matters, the distillation weight, was re-selected inside each fold and
chose the same value in all five.

**Scope of the evaluation.** Every result is on ProteinGym substitutions, ProteinGym indels, or FLIP2's published
splits, the panel is skewed toward particular families and assay types, and the top-of-list analysis characterises a
*ranking*; turning one into a measured hit rate is a prospective study against a wet-lab readout. The claims stop at
the ranking.

### Ethical considerations

**Dual use.** Protein fitness predictors can be applied to gain-of-function engineering. Our method ranks
a user-supplied set of single-residue variants; it does not generate sequences, does not perform design,
and offers no capability beyond what public ProteinGym baselines already provide. Ranking is nevertheless
the step deciding which candidates a laboratory synthesises. We release predictions for existing public
assays only.





**Data and released artifacts.** All assays are previously published deep-mutational-scanning datasets distributed
by ProteinGym: no new experimental data, no human subjects, no clinical material. The supplementary material adds per-mutant predictions
for the fusion, the out-of-fold predictions of each expert that the allocation analysis needs, the code behind every
reported number, and the recovered kernel. The code is permissively licensed; the expert prediction tables are research-use only because they derive from
third-party methods.

