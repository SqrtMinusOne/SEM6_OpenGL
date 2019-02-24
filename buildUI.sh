#!/usr/bin/env bash
source venv/bin/activate;
if ! [[ -d src/ui ]]; then
    mkdir src/ui;
fi
rm -rf src/ui/*;
for filename in ui/*.ui; do
    echo Converting ${filename:3:-3}.py;
    pyuic5 ${filename} >> src/ui/${filename:3:-3}.py;
done;