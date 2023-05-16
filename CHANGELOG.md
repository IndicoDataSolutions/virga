# Changelog

This changelog follows the guides and principles set forth by Common Changelog <https://common-changelog.org/>.

## 2.0.0 - 2023-05-15

### Changed

- Bump FastAPI from `^0.63.0` to `^0.65.2` [(#24)](https://github.com/IndicoDataSolutions/virga/pull/24).
- Improve the generated API Dockerfile.
- Improve the UI Dockerfile for production use.
- Deprecate the old generation pattern to a `--standalone` flag.

### Added

- Add a Kubernetes deployment flag to generate Helm templates based on the other provided generation options. This is the new default [(#23)](https://github.com/IndicoDataSolutions/virga/pull/23).

## 1.3.2 - 2023-04-18

_Changes were all merged as part of [(#22)](https://github.com/IndicoDataSolutions/virga/pull/22)._

### Changed

- Fix static typing in Noct and GraphQL plugins.

### Added

- Add a `testing` plugin for mocking Noct users and tokens.

## 1.2.2 - 2023-03-23

_Changes were all merged as part of [(#21)](https://github.com/IndicoDataSolutions/virga/pull/21)._

### Changed

- Improved the base GraphQLRoute for extendable context management.

### Added

- Overloadable GraphQL context setup and shutdown hooks.

## 1.2.1 - 2023-02-22

### Changed

- Resolve the unresolved entrypoint in generated projects [(#20)](https://github.com/IndicoDataSolutions/virga/pull/20).

## 1.2.0 - 2022-04-04

_Changes were all merged as part of [(#19)](https://github.com/IndicoDataSolutions/virga/pull/19)._

### Changed

- Separate user parsing from the FastAPI dependency in the Noct plugin.
- Move dependencies into conditional extras to reduce unnecessary overhead on projects.
- Ridiculously speedup unit tests by mocking dependency installations.
- GraphQL will now always return HTTP 200 instead of HTTP 400 if errors are encountered.
- Generated projects no longer use a pre-set pin for virga, instead using `virga@main`.

### Added

- Add a `SessionedGraphQLRoute` to support authentication and database access from GraphQL queries/mutations.
- Unit tests for plugins.
