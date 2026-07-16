# SMT Tutorial — Myanmar ↔ Rakhine (Google Colab edition)

A Statistical Machine Translation (Moses/GIZA++) class tutorial, adapted to run on
**Google Colab** using the **open Myanmar–Rakhine parallel corpus** released by
Sayar **Ye Kyaw Thu** ([MTRSS repo](https://github.com/ye-kyaw-thu/MTRSS)).

The original class notebook used a Myanmar–Thai medical corpus that is **not public**;
this version swaps in the Rakhine corpus (same splits: 5,000 train / 500 dev / 100 test)
with every cell updated honestly — files keep their real `.rk` extension.

## Contents

| File | What it is |
|---|---|
| [`SMT-Tutorial-for-AI-Class-1.ipynb`](SMT-Tutorial-for-AI-Class-1.ipynb) | The tutorial notebook, Colab-ready (setup cells STEP 1–5 at the top) |
| [`LEARNING-LOG.md`](LEARNING-LOG.md) | Step-by-step log of *how* the Thai→Rakhine conversion was done, and the transferable lessons |
| [`UNDERSTAND-THIS-NOTEBOOK.md`](UNDERSTAND-THIS-NOTEBOOK.md) | Beginner's map of the SMT concepts before running the notebook |
| `clean-data/scripts/` | SGM-generation Perl scripts used by the pipeline |

## Quick start

1. Open the notebook in [Google Colab](https://colab.research.google.com).
2. Run **STEP 1 → STEP 5** once, top to bottom (STEP 3 builds Moses from source, ~20–40 min).
3. Continue with the tutorial cells: data inspection → Burmese syllable cleaning →
   SGM generation → Moses EMS training (both directions `my→rk` and `rk→my`) → BLEU.

Note: the notebook keeps the instructor's **deliberate errors** (wrong paths, missing
`mkcls`, a folder-name typo) — debugging them is part of the lesson.

## Credits

- **Ye Kyaw Thu** — original tutorial, Moses/EMS scripts, `sylbreak`, `syl_normalizer`,
  and the Myanmar–Rakhine corpus (MTRSS, Machine Translation Research Summer School, YTU).
- Related paper: Thazin Myint Oo, Ye Kyaw Thu, Khin Mar Soe,
  *"Statistical Machine Translation between Myanmar (Burmese) and Rakhine (Arakanese)"*.
