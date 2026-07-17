# Running the SMT Tutorial in Docker

This image ships the tutorial **fully pre-built** — Moses and GIZA++ are already
compiled, the Myanmar–Rakhine corpus is downloaded, the syllable dictionary is
generated, and every fix from the debugging log is baked in (most importantly
`USER=root`, without which GIZA++ segfaults). No 20–40 minute Moses compile at run time.

Verified end-to-end inside the image: **my→rk BLEU ≈ 55.8**, **rk→my BLEU ≈ 55.3**.

---

## 1. Build the image (one time, ~30 min)

From the **repository root** (not the `docker/` folder — the build needs the notebook):

```bash
docker build -f docker/Dockerfile -t smt-tutorial .
```

The one slow step is compiling Moses from source; it happens once and is cached, so
later rebuilds are seconds. Final image size is ~1.9 GB.

> **Apple Silicon / ARM Macs:** builds and runs natively (arm64) — no emulation needed.
> On an x86 machine it simply builds for x86; nothing to change.

---

## 2. Run it — two modes

### A) JupyterLab (interactive — recommended for learning)

```bash
docker run --rm -p 8888:8888 smt-tutorial
```

Then open **http://localhost:8888** in your browser (no token/password). The notebook
`SMT-Tutorial-for-AI-Class-1.ipynb` is right there. Start from the tutorial cells — when
you run setup STEPs 1–5 they detect everything is already built and finish in seconds.

Stop it with `Ctrl-C` in the terminal.

### B) Headless demo (just show me the BLEU score)

```bash
docker run --rm smt-tutorial demo
```

This runs the whole pipeline non-interactively — SGM generation → config generation →
training + tuning + evaluation in **both** directions — and prints the BLEU scores at the
end. Takes ~10–20 min depending on your CPU. Nothing is saved after it exits (uses
`--rm`); see §3 to keep the trained models.

---

## 3. Keep your work (optional volume mounts)

Containers are ephemeral by default. Mount a host folder to persist things.

**Edit the notebook and keep your changes** — mount your local notebook over the one in
the image:

```bash
docker run --rm -p 8888:8888 \
  -v "$PWD/SMT-Tutorial-for-AI-Class-1.ipynb:/home/ye/exp/SMT-NMT_tutorial/SMT-Tutorial-for-AI-Class-1.ipynb" \
  smt-tutorial
```

**Keep the trained models / BLEU output** from the demo — mount a host folder for the
experiment directory:

```bash
mkdir -p out
docker run --rm -v "$PWD/out:/home/ye/exp/SMT-NMT_tutorial/pbsmt" smt-tutorial demo
# results land in ./out/baseline/<pair>/evaluation/test.multi-bleu.1
```

**Poke around inside the container** (for debugging or exploration):

```bash
docker run --rm -it smt-tutorial bash
# e.g. inspect a trained phrase table, rerun one direction, cat run1.log, ...
```

---

## 4. Where things live inside the image

| Path | What |
|---|---|
| `/home/ye/exp/SMT-NMT_tutorial/` | tutorial root (working dir); the notebook is here |
| `/home/ye/exp/SMT-NMT_tutorial/data/` | Myanmar–Rakhine corpus (`train/dev/test` × `.my/.rk`) |
| `/home/ye/exp/SMT-NMT_tutorial/pbsmt/` | where experiments run; `baseline/<pair>/evaluation/` holds BLEU |
| `/home/ye/tool/mosesbin/ubuntu-17.04/moses/` | Moses `bin/` + `scripts/` (decoder, KenLM, EMS, mert) |
| `/home/ye/tool/giza-pp/GIZA++-v2/` | GIZA++, snt2cooc.out, mkcls |

These are the exact paths the notebook hard-codes, so notebook cells run unchanged.

---

## 5. Troubleshooting

- **`docker build` fails at `stage_tutorial.py` with a network error** — the corpus
  download hit a transient GitHub hiccup. The script retries automatically; just re-run
  the build (cached layers make it quick).
- **Port 8888 already in use** — map a different host port: `-p 8899:8888`, then open
  http://localhost:8899.
- **`demo` prints "no BLEU file"** — check `run1.log` inside the container:
  `docker run --rm -it smt-tutorial bash -c 'cat /home/ye/exp/SMT-NMT_tutorial/pbsmt/run1.log'`.
- **GIZA++ segfault / training dies at `run-giza`** — means `USER` is unset. The image
  sets `USER=root`; only relevant if you override the environment. Re-add `-e USER=root`.

---

## 6. What the image build does (for reference)

`docker/Dockerfile` is a two-stage build:

1. **builder stage** — clones and compiles `mosesdecoder` (`./bjam`) and `giza-pp`
   (`make all`), asserting the key binaries exist so a broken build fails loudly.
2. **runtime stage** — installs only run-time deps (perl, python, jupyterlab,
   imagemagick, graphviz, boost/tcmalloc libs), copies the built Moses `bin/`+`scripts/`
   and the three GIZA++ binaries, copies the notebook, and runs
   `docker/stage_tutorial.py` to download the corpus + generate the dictionary + write
   placeholder images. `USER=root` is set image-wide.

`docker/run_pipeline_demo.sh` is the `demo` command; `docker/entrypoint.sh` dispatches
between `lab` (default), `demo`, and an arbitrary command.
