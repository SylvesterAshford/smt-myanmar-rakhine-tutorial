# Learning Log — Converting the SMT Tutorial from Thai to Rakhine

> **Goal:** the original notebook trained Myanmar ↔ Thai SMT, but that Thai corpus is
> **not open source**. We replaced it with the **open Myanmar–Rakhine parallel corpus**
> from Sayar **Ye Kyaw Thu**'s [MTRSS repo](https://github.com/ye-kyaw-thu/MTRSS)
> and made the whole notebook runnable on **Google Colab**.
>
> This log records *how* the conversion was done, step by step, so you can learn the
> method — not just the result.

---

## Part 1 — The investigation (do this before touching anything)

### Step 1: Understand what the notebook actually needs

Before swapping a dataset, list what the old dataset *provided*:

| The Thai corpus provided | Found by |
|---|---|
| 6 files: `train/dev/test` × `.my`/`.th` | `!ls ./data/*` cells |
| Sizes: **5,000 / 500 / 100** sentence pairs | `!wc` cells |
| One sentence per line, already word-segmented | `!head` cells |
| UTF-8 plain text | file format |

**Lesson:** a dataset swap is really an *interface* swap. Write down the interface first.

### Step 2: Find a replacement that matches the interface

The Myanmar–Rakhine corpus lives at:

```
https://github.com/ye-kyaw-thu/MTRSS  →  pbsmt/data/{train,dev,test}.{my,rk}
```

We verified every raw URL returns HTTP 200, downloaded them, and checked:

```
train.my / train.rk : 5000 lines      ← same as the Thai corpus!
dev.my   / dev.rk   :  500 lines
test.my  / test.rk  :  100 lines
```

Sample pair (notice how close Rakhine is to Burmese — same script, different words):

```
my: မင်း အဲ့ဒါ ကို အခြား တစ်ခုနဲ့ မ ချိတ် ဘူးလား ။
rk: မင်း ယင်းချင့် ကို အခြား တစ်ခုနန့်  မ ချိတ် ပါလား ။
```

**Lesson:** perfect match — same splits, same format, same one-sentence-per-line layout.
This is not luck: MTRSS is by the *same instructor*, from the same summer school this
tutorial's scripts come from. When replacing a resource, look in the same author's
public repos first.

### Step 3: Find every place the old language code is hard-coded

Two kinds of places can hard-code `th`:

1. **The pipeline scripts/configs** (`generate_configs.pl`, `config.baseline`, sgm scripts…)
2. **The notebook cells themselves** (`!head ./data/train.th`, `%cd baseline/th-my/`…)

We grepped the scripts and discovered something important:

```perl
# generate_configs.pl — the language codes are AUTO-DETECTED from filenames:
foreach my $trainFile ( <...>/clean-data/train.[a-z][a-z]> ) {
    $trainFile =~ m/train.([a-z][a-z])/;
    push @langs, $1;               # ← "my" and whatever the other extension is
}
```

and the Moses config even contains `myrk-data = ...` — these scripts were **originally
written for Myanmar–Rakhine experiments**! They are language-agnostic: name the files
`train.rk` and the whole pipeline automatically builds `my-rk/` and `rk-my/` experiments.

**Lesson:** read the scripts before editing them. The "hard part" (Moses configs) needed
**zero changes** because the original author parameterized the language codes. Only the
notebook *cells* — the human-facing layer — hard-coded `th`.

---

## Part 2 — The changes (what was edited, and why)

### Design decision: use the real `.rk` extension, don't fake `.th`

An earlier quick fix renamed the Rakhine files to `.th` so old cells would run unmodified.
That works mechanically but is **bad for learning** — you'd be reading "Thai" everywhere
while looking at Rakhine text. We reversed that: files keep their honest `.rk` name and
every cell referencing `th` was updated. **Correct labels beat minimal diffs.**

### Change inventory

| # | Where | Change | Why |
|---|---|---|---|
| 1 | Setup cell "STEP 5" | Download `{train,dev,test}.{my,rk}` from MTRSS directly (no rename) | honest labeling |
| 2 | Setup cell "STEP 5" | Placeholder images renamed `graph.1.my-th*.png → graph.1.my-rk*.png` | the display cells now look for `my-rk` names |
| 3 | Setup cell "STEP 2" (embedded scripts) | sgm setid `Thai-Myanmar_data → Myanmar-Rakhine_data` | metadata inside generated `.sgm` test files |
| 4 | Cells `!head ./data/*.th` | → `*.rk` | data files renamed |
| 5 | Cells writing `src2sgm.pl` / `ref2sgm.pl` | setid → `Myanmar-Rakhine_data` | same as #3, notebook-side copy |
| 6 | `!head test.th.ref.sgm` | → `test.rk.ref.sgm` | generated from `test.rk` |
| 7 | `%cd baseline/th-my/`, `.../my-th/...` (6 cells) | → `rk-my` / `my-rk` | Moses EMS names experiment dirs `<input>-<output>` from file extensions |
| 8 | `!cat ./config.baseline.th-my` | → `.rk-my` | generated config filename follows the pair name |
| 9 | Burmese markdown (8 cells) | ထိုင်း (Thai) → ရခိုင် (Rakhine) | keep the narration truthful |
| 10 | Final BLEU markdown | Note added: instructor's 11.77 was for Thai; expect **higher** BLEU for Rakhine | my↔rk is a much closer language pair |
| 11 | Intro markdown (cell 0) | New "Dataset change: Thai ➜ Rakhine" section | first thing a reader sees |
| 12 | `UNDERSTAND-THIS-NOTEBOOK.md` | Thai → Rakhine in the 2 places it appeared | keep docs in sync |

What was deliberately **kept**: the instructor's 3 planted bugs (wrong paths, missing
`mkcls`, `test-gen` typo) — they are the debugging lesson; and one historical note that
the original course planned a Thai medical corpus for later notebooks.

### How we verified before shipping

1. **Notebook validates** against the Jupyter nbformat schema after editing.
2. **Re-decoded the embedded asset bundle** (STEP 2 stores all scripts as base64) and
   confirmed the sgm scripts carry the new setid.
3. **Simulated STEP 5 locally**: downloaded the real corpus, ran `sylbreak.py` over
   `train.my`, built the syllable dictionary → **1,259 syllables** (top: ။, မ, ကို, အ, တယ်).
4. **Simulated the sgm + config stage** with `.rk` files: `generate_sgms.pl` produced
   `test.rk.{src,ref}.sgm`, and the language auto-detection found `my` + `rk` → so Moses
   will create exactly the `baseline/my-rk/` and `baseline/rk-my/` dirs the cells expect.

**Lesson:** you can't run a 40-minute Moses build to test a rename — so *isolate* the
parts affected by your change (filenames, globs, generated names) and test just those.

---

## Part 3 — How to run it on Google Colab

1. Upload `SMT-Tutorial-for-AI-Class-1.ipynb` to [colab.research.google.com](https://colab.research.google.com).
2. Run **STEP 1 → STEP 5** once, top to bottom.
   - STEP 3 (Moses build from source) is the long one: **~20–40 min**. If it dies,
     re-run the same cell — the build resumes where it stopped.
3. Continue with the original tutorial cells below the setup section.
4. Expected flow: data inspection → Burmese cleaning (`sylbreak` + normalize) →
   sgm generation → `generate_configs.pl` → `run-baseline.pl` (trains **both**
   directions my→rk and rk→my) → BLEU in `baseline/*/evaluation/test.multi-bleu.1`.

⚠️ Colab free tier can disconnect after long idle periods. Do the Moses build (STEP 3)
in one sitting; everything after it is minutes, not hours.

---

## Part 3.5 — Bug found while running on Colab (SGM section) and the fix

**Symptom chain** (from the actual Colab run):

1. `SyntaxError: invalid syntax` pointing at `use strict;` (a *Perl* line!) —
   the first SGM cell had `!mkdir -p ...` **above** `%%writefile`. Cell magics like
   `%%writefile` only work as the **very first line** of a cell; with anything above it,
   IPython runs the whole cell as *Python* and chokes on the Perl code.
2. Because that cell died, the `mkdir` never ran → the next two `%%writefile` cells
   failed with `FileNotFoundError` (`%%writefile` writes a file but does **not** create
   parent directories).

**Lesson:** one broken cell can *cause* the next errors — always fix the **first** error
in a chain before touching the later ones.

**The fix — stop hand-writing files that already exist upstream.** The three Perl
scripts live in the MTRSS repo (`pbsmt/data/test-sgm/`) and — because that repo *is* the
Myanmar–Rakhine experiment — they already contain `Myanmar-Rakhine_data` and the right
relative paths. So the three fragile `%%writefile` cells became one simple cell:

```python
!mkdir -p /home/ye/exp/SMT-NMT_tutorial/clean-data/scripts
%cd /home/ye/exp/SMT-NMT_tutorial/clean-data/scripts

base = "https://raw.githubusercontent.com/ye-kyaw-thu/MTRSS/master/pbsmt/data/test-sgm"
!wget -q -O generate_sgms.pl $base/generate_sgms.pl
!wget -q -O src2sgm.pl $base/src2sgm.pl
!wget -q -O ref2sgm.pl $base/ref2sgm.pl
!chmod +x *.pl
```

Details worth noticing:
- `wget -O <name>` makes the cell **rerun-safe** (overwrites instead of creating `.1` copies).
- `chmod +x` is required because upstream `generate_sgms.pl` invokes `./ref2sgm.pl`
  directly (no `perl` prefix), which needs the execute bit.
- Verified end-to-end locally: the downloaded scripts produced all 4 sgm files
  (`test.{my,rk}.{src,ref}.sgm`) with 100 `<seg>` entries each.

**Meta-lesson:** *prefer downloading a canonical file over re-typing it.* Embedded copies
drift and each `%%writefile` is a chance for a transcription bug; a URL to the author's
repo is one line and always matches the source.

## Part 3.6 — Second Colab bug: `generate_sgms.pl` runs but produces nothing

**Symptom:** `!perl ./generate_sgms.pl` finishes with no error, but `!ls *sgm` says
*No such file or directory*.

**Root cause — a silent failure + hidden server state:**

1. `generate_sgms.pl` finds languages by globbing `../train.[a-z][a-z]`. If nothing
   matches, `@langs` is empty, the loop body never runs, and the script **exits happily
   with zero output**. Perl backticks also swallow any sub-script errors. No error ≠ success.
2. Why did nothing match? The notebook's cleaning flow does `mv *.*  ./normalize` (moving
   **all six** corpus files in) but only copies back `*.clean` — the Burmese side. The
   Rakhine/Thai side **never returns to `clean-data/`** in any notebook cell.
3. The proof is in the instructor's own saved outputs: their `tree` shows `clean-data/`
   holding only `train.my, dev.my, test.my`… yet their SGM step produced both languages.
   The `.th` files existed on their **server from outside the notebook** — hidden state
   that a fresh Colab runtime doesn't have.

**Fixes applied to the notebook:**

- The copy-back cell now restores both sides:
  ```bash
  !cp ./normalize/*.clean .   # cleaned Burmese
  !cp ./normalize/*.rk .      # Rakhine side (was left stranded in normalize/)
  ```
- A **self-healing guard cell** was added right before `!perl ./generate_sgms.pl`: it
  checks all 6 files exist in `clean-data/` and restores any missing one (preferring the
  cleaned version from `normalize/`, falling back to raw `data/`). This also makes the
  section survive a Colab runtime restart where earlier cells' work was lost.

**Lessons:**
- **"No error" is not "it worked."** Shell-outs in backticks and empty globs fail
  silently — always verify the *artifact* (here: `ls *sgm`), not the exit banner.
- **Notebooks can depend on invisible state.** If a cell works for the author but not on
  a fresh machine, diff what's *on disk* at that point, not what's *in the notebook*.
- **Make preconditions explicit.** A 10-line guard cell that checks-and-restores inputs
  converts a silent downstream failure into either success or a loud, early message.

## Part 3.7 — Third Colab bug: `%cd baseline/rk-my/` → "No such file or directory"

**Symptom:** after `%cd ..` put us at the tutorial root, the next cell's relative
`%cd baseline/rk-my/` failed — `baseline/` actually lives inside `pbsmt/`.

**Root cause — relative paths written against an undocumented working directory.**
A notebook's cwd is **global mutable state**: every `%cd` changes it for all later cells.
The instructor's saved outputs prove they weren't running linearly — their `%cd ..`
printed `.../pbsmt` (so their cwd had been `pbsmt/baseline`, set by hand or by re-running
cells out of order). Relative `%cd`s recorded from such a session silently encode that
session's history.

**Diagnosis technique worth stealing:** simulate the cwd flow *offline*. Walk every
`%cd` line top to bottom with `posixpath.join`/`normpath` and print the resulting
directory — no Colab needed. This exposed **four** broken relative `%cd`s in one pass
(including the one that had been quietly creating a stray `clean-data/scripts/pbsmt/`
folder later in the notebook):

| Cell command | Where it actually landed (linear run) | Intended |
|---|---|---|
| `%cd ../clean-data/` | `clean-data/clean-data` ✗ | `clean-data` |
| `%cd baseline/rk-my/` | `<root>/baseline/rk-my` ✗ | `pbsmt/baseline/rk-my` |
| `%cd ../../` | `pbsmt/baseline/rk-my` ✗ | tutorial root |
| `%cd ./pbsmt/` | `clean-data/scripts/pbsmt` ✗ | `<root>/pbsmt` |

**Fix:** all four became absolute paths. Note the failure asymmetry: a failed `%cd`
*keeps the old cwd* and the notebook keeps running — so the error often surfaces cells
later, as a missing file or a mysteriously created directory, far from the real cause.

**Lessons:**
- In notebooks, prefer **absolute paths in every `%cd`** — relative ones embed the
  author's session history, which a fresh linear run doesn't share.
- When a path error makes no sense, don't debug the failing cell — **reconstruct the
  cwd history** that led to it.
- You can verify this class of bug *statically* (the offline cwd walk) — faster and more
  complete than re-running the notebook to find them one at a time.

## Part 3.8 — Fourth Colab bug: `generate_configs.pl` can't run twice

**Symptom (two errors stacked, again):** in the "Notes" section, `!ls *` and
`!perl ./generate_configs.pl` both failed with *No such file or directory* — the session
was sitting inside the stray `clean-data/scripts/pbsmt/` folder (fallout of the relative
`%cd ./pbsmt/` from Part 3.7, before the fix was applied to that session).

**The hidden second trap:** even from the correct `pbsmt/` directory, the script dies,
because of this guard:

```perl
die("$smtpath/$expt") if (-d "$smtpath/$expt");   # refuse if baseline/ exists
```

That's a deliberate **safety guard** — an EMS `baseline/` can hold hours of training
output, and the author didn't want a re-run to clobber a finished experiment. But it
makes the cell **non-idempotent**: it only works the *first* time. The instructor's own
outputs confirm they never hit it here (their earlier attempts had failed before
creating `baseline/`), and that they manually did `%rm -r baseline/` when *they*
needed to regenerate later. A linear runner who succeeded earlier arrives with
`baseline/` present and dies.

**Fix:** the Notes-section cell now clears the stale config-only `baseline/` before
regenerating (`rm -rf ./baseline` + `generate_configs.pl`) — matching what the
instructor does by hand two sections later.

**Lessons:**
- **Idempotence matters in notebooks.** Cells get re-run. A cell that only works once
  (create-if-not-exists, die-if-exists, `wget` without `-O`) will eventually bite someone.
- **Die-if-exists guards protect data but punish retries.** When you wrap such a tool in
  a re-runnable cell, decide explicitly which state is disposable (here: a `baseline/`
  containing only generated configs) and clear exactly that.
- **Whether a "shared" notebook works can depend on the author's failures.** The
  instructor could run this cell *because* their earlier steps had failed. A fixed-up
  linear run changes which states each later cell sees.

## Part 3.9 — "Missing" graph.1.png after training: not a bug at all

**Symptom:** training completed, but `!ls *.png` in `steps/1` found nothing, while the
instructor's saved output shows a `graph.1.png` there.

**Root cause:** `run-baseline.pl` invokes `experiment.perl -config ... -exec -no-graph`
— and checking the **upstream MTRSS script confirms the same flag**. With `-no-graph`,
Moses EMS skips rendering the pipeline diagram. The instructor's png came from their own
server environment (an invocation without the flag, plus graphviz installed) — one more
artifact of their session, not of the notebook's code.

**Triage lesson — classify before fixing.** Three kinds of "the file isn't there":
1. *Your pipeline broke* (Parts 3.5–3.8) → fix the pipeline.
2. *The author's environment differed* → decide whether the artifact matters.
3. *The artifact is decorative* → it must never block the run.
This one is (2)+(3): the graph is only a picture of the EMS step DAG; the model,
tuning, and BLEU are completely unaffected.

**Fix:** the `!ls *.png` cell became a render-or-skip cell — if EMS left a `graph.*`
dot description it installs graphviz and renders the png; otherwise it prints that
skipping is fine and points to the evaluation cells. Either way the cell succeeds.

**Lesson:** when a shared notebook errors, first ask *"is the missing thing an input,
an output, or an illustration?"* Only inputs and outputs deserve pipeline surgery;
illustrations deserve a graceful fallback.

---

## Part 4 — What to learn from this exercise (the transferable skills)

1. **Interface thinking.** A dataset, like an API, has a contract: file names, sizes,
   format, encoding. Match the contract and the pipeline doesn't care what's inside.
2. **Read before you write.** The scary Moses configs needed no edits because the
   original author had parameterized them. 10 minutes of grep saved hours of editing.
3. **Auto-detection is a double-edged sword.** `train.[a-z][a-z]` globbing meant renaming
   files silently *renames experiment directories* too (`th-my → rk-my`) — every
   downstream `%cd` had to follow. Trace where a name *propagates*.
4. **Honest data labeling.** Renaming `.rk` to `.th` "to make it run" creates a notebook
   that lies to its reader. Prefer the bigger-but-truthful diff.
5. **Verify in slices.** Full pipeline = 40 min. The parts affected by the change =
   seconds. Test the slices.
6. **Linguistic expectation setting.** BLEU 11.77 (my↔th, unrelated languages, tiny data)
   vs. expected much-higher BLEU (my↔rk, sister languages sharing script and grammar).
   Same code, different difficulty — scores only mean something *relative to the pair*.

### Dataset credit

Myanmar–Rakhine parallel corpus: **Ye Kyaw Thu**, MTRSS — Machine Translation Research
Summer School, Yangon Technological University. Repo: <https://github.com/ye-kyaw-thu/MTRSS>.
Related paper: Thazin Myint Oo, Ye Kyaw Thu, Khin Mar Soe, *"Statistical Machine
Translation between Myanmar (Burmese) and Rakhine (Arakanese)"*.
