# Understanding the SMT Tutorial — A Beginner's Guide

> A map of the concepts you need **before** running the notebook.
> This notebook trains a machine that translates **Myanmar (Burmese) ↔ Rakhine (Arakanese)** using
> **Statistical Machine Translation (SMT)** with the **Moses** toolkit.

---

## 1. The Big Picture (in one sentence)

> **You feed the computer thousands of sentence pairs that mean the same thing in two
> languages, and it learns the statistical patterns to translate new sentences on its own.**

No grammar rules are written by hand. The machine *learns from examples*.

---

## 2. Two Eras of Machine Translation

| | **SMT** (this notebook) | **NMT** (modern, e.g. Google Translate) |
|---|---|---|
| Full name | Statistical Machine Translation | Neural Machine Translation |
| Era | ~1990–2016 | 2016–now |
| How it learns | Counting word/phrase **probabilities** | A **neural network** (deep learning) |
| Core tool here | **Moses** | Transformers / LLMs |
| Why learn it | Foundation of the field; transparent & explainable | State of the art today |

👉 SMT is taught **first** because you can *see* every step. NMT is a black box.

---

## 3. The Core Idea: How SMT "Learns" to Translate

SMT combines **two questions** for every translation:

```
   Best translation  =  Does this phrase usually mean that?   ×   Does the output sound fluent?
                        └─── Translation Model ───┘             └──── Language Model ────┘
```

- **Translation Model** → learned from a **parallel corpus** (sentence pairs).
- **Language Model** → learned from lots of text in the *target* language only.

Think of it as: **"faithful to the meaning"** AND **"sounds natural."**

---

## 4. The 5 Key Ingredients

| Ingredient | What it is | In this notebook |
|---|---|---|
| 📚 **Parallel corpus** | Thousands of aligned sentence pairs | `train.my` ↔ `train.rk` (5,000 pairs) |
| 🔗 **Word alignment** | Which word maps to which word | done by **GIZA++** |
| 🧩 **Phrase table** | A learned dictionary of phrase→phrase + probabilities | built by Moses |
| 🗣️ **Language model** | Scores how "natural" output text is | built by **KenLM** (`lmplz`) |
| ⚙️ **Decoder** | Searches for the best translation | the **`moses`** program |

---

## 5. The SMT Pipeline (what happens when you "run" it)

```
 ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
 │ 1. Prepare │ → │ 2. Align   │ → │ 3. Build   │ → │ 4. Train   │ → │ 5. Tune    │ → │ 6. Evaluate│
 │    data    │   │   words    │   │ phrase tbl │   │ language   │   │ (optimize  │   │  (score    │
 │            │   │ (GIZA++)   │   │            │   │ model (LM) │   │  weights)  │   │  quality)  │
 └────────────┘   └────────────┘   └────────────┘   └────────────┘   └────────────┘   └────────────┘
      data/           giza            phrase-table       lm              mert            BLEU score
```

This whole chain is automated by Moses's **EMS** (Experiment Management System) —
that's what the `run-baseline.pl` and `config.baseline` files control.

**Data splits** (a universal ML concept):
- **train** (5,000) → the machine learns from this
- **dev / validation** (500) → used to tune settings
- **test** (100) → the final exam; the machine has never seen it

---

## 6. How We Measure Success: BLEU Score

- **BLEU** = a number from **0 to 100** measuring how close the machine's translation is to a human reference.
- Higher = better. (This tutorial gets ~**11.77** — low, because it's a tiny demo run.)
- It works by checking how many word-sequences (n-grams) overlap with the correct answer.

---

## 7. The Myanmar-Specific Part (why there's extra preprocessing)

Burmese text has a special challenge that English doesn't:

| Concept | Meaning | Tool in notebook |
|---|---|---|
| **Syllable segmentation** | Burmese has no spaces between words; you must break text into syllables first | `sylbreak.py` |
| **Typing-order errors** | The same syllable can be typed in a wrong character order but *look* identical | shown via `print-codepoint.pl` |
| **Normalization** | Fixing those spelling/order errors so the machine sees consistent text | `syl_normalizer.py` |

👉 **Garbage in = garbage out.** Cleaning the Myanmar text first makes translation better.

---

## 8. The Tools You'll See (cheat sheet)

| Tool | Job | Language |
|---|---|---|
| **Moses** | The whole SMT system (decoder + scripts) | C++ / Perl |
| **GIZA++** | Word alignment | C++ |
| **KenLM** (`lmplz`) | Language model training | C++ |
| **Perl scripts** (`.pl`) | Glue that runs the pipeline & makes config files | Perl |
| **`sylbreak.py` / `syl_normalizer.py`** | Myanmar text preprocessing | Python |
| **`.sgm` files** | XML-wrapped test data used for scoring | — |

---

## 9. How This Notebook Is Structured

1. **Look at the data** — peek at the sentence pairs and their sizes.
2. **Clean the Myanmar side** — syllable break + normalize.
3. **Set up Moses & GIZA++** — point config files at the right paths.
4. **Run the SMT pipeline** — train, tune, decode, score.
5. **Read the BLEU score** — for both my→th and th→my directions.

⚠️ **Important:** the instructor *deliberately left 3 errors* in the notebook to teach
**debugging**, the most common ones in real SMT work:
1. **Wrong file paths** in scripts/configs
2. **GIZA++ `mkcls` not found**
3. A **typo in a folder name** (`test-gen` vs `test-sgm`)

So seeing errors is *part of the lesson*, not a failure.

---

## 10. Glossary (quick reference)

| Term | Plain-English meaning |
|---|---|
| **Corpus** | A large collection of text |
| **Parallel corpus** | Same text in two languages, sentence-by-sentence |
| **Tokenization** | Splitting text into pieces (words/syllables) |
| **Alignment** | Matching words across the two languages |
| **Phrase table** | The learned phrase→phrase dictionary with probabilities |
| **Language model (LM)** | A model of what "natural" text looks like |
| **Decoding** | The act of producing a translation |
| **Tuning (MERT)** | Adjusting the model's internal weights for best quality |
| **BLEU** | The translation quality score (0–100) |
| **EMS** | Moses's Experiment Management System (automates the pipeline) |

---

## 11. The One Thing to Remember

> **SMT = learn from examples (parallel data) → align → extract phrases → score fluency →
> search for the best translation → measure with BLEU.**
> Everything in the notebook is one of those steps, plus Myanmar-specific cleaning.
