.PHONY: test dev

dist: graphene_django_tools/* graphene_django_tools/*/* graphene_django_tools/*/*/* pyproject.toml
	poetry build

test:
	poetry run pytest --cov=graphene_django_tools -vv
