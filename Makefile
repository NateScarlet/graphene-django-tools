ifeq ($(OS), Windows_NT)
activate=.venv/Scripts/activate
else
activate=.venv/bin/activate
endif

.venv/.make_success: requirements.txt dev-requirements.txt .venv
	. $(activate) && pip install -r requirements.txt -r dev-requirements.txt
	echo > .venv/.make_success

.venv:
	virtualenv .venv

.PHONY: test  build

test: .venv/.make_success
	@echo "Not implemented"

build:
	rm -rf build
	. $(activate) && python setup.py sdist bdist_wheel

