#!/bin/bash
case "$1" in
  demo)
    exec bash /opt/smt/run_pipeline_demo.sh
    ;;
  lab|"")
    echo "JupyterLab starting — open http://localhost:8888"
    echo "(setup STEPs 1-5 in the notebook will detect everything is pre-built and skip fast)"
    exec jupyter lab --allow-root --ip=0.0.0.0 --port=8888 --no-browser \
         --ServerApp.token= --ServerApp.password= \
         --notebook-dir=/home/ye/exp/SMT-NMT_tutorial
    ;;
  *)
    exec "$@"
    ;;
esac
