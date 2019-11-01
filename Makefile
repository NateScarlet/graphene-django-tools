.venv/.make_success: requirements.txt dev-requirements.txt .venv
	. ./scripts/activate-venv.sh && pip install -r requirements.txt -r dev-requirements.txt
	echo > .venv/.make_success

.venv:
	virtualenv .venv

.PHONY: test build dev

dev: .venv/.make_success
	. ./scripts/activate-venv.sh && ./manage.py runserver

test: .venv/.make_success
	pytest --cov=graphene_django_tools -vv

build: .venv/.make_success
	rm -rf build
	. ./scripts/activate-venv.sh && python setup.py sdist bdist_wheel
