#!/bin/bash

if [[ -f .env ]]; then 
. ./.env
fi

if [[ ${OS} == Windows_NT ]]; then
. .venv/Scripts/activate
else
. .venv/bin/activate;
fi


