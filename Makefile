.PHONY: test dev

dist: graphene_django_tools/* graphene_django_tools/*/* poetry.lock
	poetry build

test:
	poetry run pytest --cov=graphene_django_tools -vv
