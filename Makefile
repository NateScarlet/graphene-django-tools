.PHONY: test dev

dist: graphene_django_tools pyproject.toml
	poetry build

dev:
	poetry run python ./manage.py runserver

test:
	poetry run pytest --cov=graphene_django_tools -vv
