# SMT Myanmar-Rakhine tutorial — everything pre-built.
#   docker build -f docker/Dockerfile -t smt-tutorial .
#   docker run -p 8888:8888 smt-tutorial                  → JupyterLab at http://localhost:8888
#   docker run smt-tutorial demo                          → headless full pipeline → BLEU
#
# Stage 1 builds Moses + GIZA++ (the ~30 min part, done once at image build).

FROM ubuntu:22.04 AS builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential git ca-certificates perl automake libtool pkg-config cmake \
      libboost-all-dev libbz2-dev liblzma-dev zlib1g-dev \
      libgoogle-perftools-dev libcmph-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/moses-smt/mosesdecoder.git /opt/mosesdecoder
RUN cd /opt/mosesdecoder && ./bjam --with-boost=/usr --with-cmph=/usr -j"$(nproc)" || true
# fail the build here if the important binaries did not come out
RUN test -x /opt/mosesdecoder/bin/moses && test -x /opt/mosesdecoder/bin/lmplz \
    && test -f /opt/mosesdecoder/scripts/ems/experiment.perl

RUN git clone --depth 1 https://github.com/moses-smt/giza-pp.git /opt/giza-pp \
    && cd /opt/giza-pp && make all -j2 \
    && cp mkcls-v2/mkcls GIZA++-v2/ \
    && test -x /opt/giza-pp/GIZA++-v2/GIZA++

# ---------------------------------------------------------------- runtime image
FROM ubuntu:22.04
# USER=root matters: GIZA++ segfaults if USER is unset (strlen(getenv("USER")))
ENV DEBIAN_FRONTEND=noninteractive USER=root LC_ALL=C.UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends \
      perl python3 python3-pip tree wget curl ca-certificates \
      imagemagick graphviz libipc-system-simple-perl time \
      libboost-all-dev libgoogle-perftools-dev libcmph-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir jupyterlab pillow

# Moses: only bin/ + scripts/ are needed at run time (EMS, decoder, KenLM, mert)
COPY --from=builder /opt/mosesdecoder/bin     /home/ye/tool/mosesbin/ubuntu-17.04/moses/bin
COPY --from=builder /opt/mosesdecoder/scripts /home/ye/tool/mosesbin/ubuntu-17.04/moses/scripts
# GIZA++: the three binaries train-model.perl looks for in external-bin-dir
COPY --from=builder /opt/giza-pp/GIZA++-v2/GIZA++ \
                    /opt/giza-pp/GIZA++-v2/snt2cooc.out \
                    /opt/giza-pp/GIZA++-v2/mkcls \
                    /home/ye/tool/giza-pp/GIZA++-v2/

# The tutorial notebook (with all fixes) + staging of corpus/scripts/dictionary
COPY SMT-Tutorial-for-AI-Class-1.ipynb /home/ye/exp/SMT-NMT_tutorial/
COPY docker/stage_tutorial.py docker/run_pipeline_demo.sh docker/entrypoint.sh /opt/smt/
RUN chmod +x /opt/smt/*.sh \
    && mkdir -p /content \
    && python3 /opt/smt/stage_tutorial.py

WORKDIR /home/ye/exp/SMT-NMT_tutorial
EXPOSE 8888
ENTRYPOINT ["/opt/smt/entrypoint.sh"]
CMD ["lab"]
