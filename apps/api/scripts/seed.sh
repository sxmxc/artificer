#!/bin/sh
set -eu

python -m scripts.init_db
python -m scripts.seed
