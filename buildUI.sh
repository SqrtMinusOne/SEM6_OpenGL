#!/usr/bin/env bash
source venv/bin/activate;
rm -rf src/ui/*;
#mkdir src/ui;
for filename in ui/*.ui; do
    echo Converting ${filename:3:-3}.py;
    pyuic5 ${filename} >> src/ui/${filename:3:-3}.py;
done;