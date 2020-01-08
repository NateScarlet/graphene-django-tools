# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.19.3](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/compare/v0.19.2...v0.19.3) (2020-01-08)


### Bug Fixes

* can not use without django filter ([ffba136](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/commit/ffba136))


### Features

* add `connection.set_optimization_default` ([36eef88](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/commit/36eef88))
* add `get_models_for_typename` ([3d36963](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/commit/3d36963))
* add `queryset.optimize` ([43278d0](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/commit/43278d0))

### [0.19.2](https://github.com/NateScarlet/graphene-django-tools/compare/v0.19.1...v0.19.2) (2019-12-02)

### Features

- allow use string as data loader key ([19fafb0](https://github.com/NateScarlet/graphene-django-tools/commit/19fafb0f84c9388fc8fc13e0f01f4f4a81e72361))
- lazy resolve for connection ([6177f8a](https://github.com/NateScarlet/graphene-django-tools/commit/6177f8ad5e67dd5893eb5d58487a4d5ce958e4a4))
- support enum ([da86fcb](https://github.com/NateScarlet/graphene-django-tools/commit/da86fcb2b0ee725bf8612a73468149d2cab1df03))
- support union ([475d085](https://github.com/NateScarlet/graphene-django-tools/commit/475d085b05312063b5ff5448010ea2f5b86a1ee3))

### Bug Fixes

- should not convert iterable to list ([7ef7ffc](https://github.com/NateScarlet/graphene-django-tools/commit/7ef7ffc1402186786061804499e591d61e6f2ba3))

### [0.19.1](http://github.com/NateScarlet/graphene-django-tools/compare/v0.19.0...v0.19.1) (2019-11-19)

Correct `graphene-django` instal require from `>=2.5` to `>=2.2`.
