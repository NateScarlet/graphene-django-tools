# Graphene django tools

[![build status](https://github.com/NateScarlet/graphene-django-tools/workflows/Python%20package/badge.svg)](https://github.com/NateScarlet/graphene-django-tools/actions)
[![version](https://img.shields.io/pypi/v/graphene-django-tools)](https://pypi.org/project/graphene-django-tools/)
![python version](https://img.shields.io/pypi/pyversions/graphene-django-tools)
![django version](https://img.shields.io/pypi/djversions/graphene-django-tools)
![wheel](https://img.shields.io/pypi/wheel/graphene-django-tools)
![maintenance](https://img.shields.io/maintenance/yes/2020)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

Tools for use [`graphene`](https://github.com/graphql-python/graphene) with django.
Use a explicit schema definition approach that different from `graphene-django`.

Documentation is placed in [docs folder](./docs).

## Install

`pip install graphene-django-tools`

## Features

- django integration for [graphene-resolver](https://github.com/NateScarlet/graphene-resolver).
- optimize queryset with django `only`,`selected_related`,`prefetch_related` to only select fields that used in query.
- data loader graphene middleware.

## Development

run dev server: `make dev`

test: `make test`
