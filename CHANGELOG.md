# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.20.1](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/compare/v0.20.0...v0.20.1) (2020-03-11)


### Bug Fixes

* default lookup for generic foreign key ([1195e38](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/commit/1195e38))
* import error on django contenttype ([fb8f29e](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/commit/fb8f29e))


### Features

* add `model_type.get_content_type` ([2b0889c](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/commit/2b0889c))
* add model_type.get_typename ([b4476b1](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/commit/b4476b1))
* foramt invalid id message ([e63383d](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/commit/e63383d))
* support python3.6 ([1e83b8d](http://git.zhouxuan.site:10022/Nate/graphene-django-tools/commit/1e83b8d))

## [0.20.0](https://github.com/NateScarlet/graphene-django-tools/compare/v0.19.4...v0.20.0) (2020-01-13)

### ⚠ BREAKING CHANGES

- removed `graphene-django` related code
- removed alias related to connection,
  use `gdtools.connection.{function name}` instead.

### Features

- drop `graphene-django` dependency ([41eda52](https://github.com/NateScarlet/graphene-django-tools/commit/41eda52))

### [0.19.4](https://github.com/NateScarlet/graphene-django-tools/compare/v0.19.3...v0.19.4) (2020-01-09)

### Bug Fixes

- optimization default only lookup ([b736b46](https://github.com/NateScarlet/graphene-django-tools/commit/b736b46))
- optimize query with fragment ([2a81652](https://github.com/NateScarlet/graphene-django-tools/commit/2a81652))

### Features

- add `select` to optimization `qs.only` lookup ([f95d518](https://github.com/NateScarlet/graphene-django-tools/commit/f95d518))
- queryset optimization auto detect `only` option ([6364355](https://github.com/NateScarlet/graphene-django-tools/commit/6364355))

### [0.19.3](https://github.com/NateScarlet/graphene-django-tools/compare/v0.19.2...v0.19.3) (2020-01-08)

### Bug Fixes

- can not use without django filter ([ffba136](https://github.com/NateScarlet/graphene-django-tools/commit/ffba136))

### Features

- add `connection.set_optimization_default` ([36eef88](https://github.com/NateScarlet/graphene-django-tools/commit/36eef88))
- add `get_models_for_typename` ([3d36963](https://github.com/NateScarlet/graphene-django-tools/commit/3d36963))
- add `queryset.optimize` ([43278d0](https://github.com/NateScarlet/graphene-django-tools/commit/43278d0))

### [0.19.2](https://github.com/NateScarlet/graphene-django-tools/compare/v0.19.1...v0.19.2) (2019-12-02)

### Features

- allow use string as data loader key ([19fafb0](https://github.com/NateScarlet/graphene-django-tools/commit/19fafb0f84c9388fc8fc13e0f01f4f4a81e72361))
- lazy resolve for connection ([6177f8a](https://github.com/NateScarlet/graphene-django-tools/commit/6177f8ad5e67dd5893eb5d58487a4d5ce958e4a4))
- support enum ([da86fcb](https://github.com/NateScarlet/graphene-django-tools/commit/da86fcb2b0ee725bf8612a73468149d2cab1df03))
- support union ([475d085](https://github.com/NateScarlet/graphene-django-tools/commit/475d085b05312063b5ff5448010ea2f5b86a1ee3))

### Bug Fixes

- should not convert iterable to list ([7ef7ffc](https://github.com/NateScarlet/graphene-django-tools/commit/7ef7ffc1402186786061804499e591d61e6f2ba3))

### [0.19.1](https://github.com/NateScarlet/graphene-django-tools/compare/v0.19.0...v0.19.1) (2019-11-19)

Correct `graphene-django` instal require from `>=2.5` to `>=2.2`.
