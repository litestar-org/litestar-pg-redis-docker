<!-- markdownlint-disable -->
<img alt="Starlite logo" src="./static/starlite-banner.svg" width="100%" height="auto">
<!-- markdownlint-restore -->

<div align="center">

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_starlite-pg-redis-docker&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=starlite-api_starlite-pg-redis-docker)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_starlite-pg-redis-docker&metric=coverage)](https://sonarcloud.io/summary/new_code?id=starlite-api_starlite-pg-redis-docker)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_starlite-pg-redis-docker&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=starlite-api_starlite-pg-redis-docker)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_starlite-pg-redis-docker&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=starlite-api_starlite-pg-redis-docker)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_starlite-pg-redis-docker&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=starlite-api_starlite-pg-redis-docker)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_starlite-pg-redis-docker&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=starlite-api_starlite-pg-redis-docker)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_starlite-pg-redis-docker&metric=bugs)](https://sonarcloud.io/summary/new_code?id=starlite-api_starlite-pg-redis-docker)

</div>

# starlite-pg-redis-docker

This is an example [Starlite](https://github.com/starlite-api/starlite) project using SQLAlchemy + Alembic + postgresql,
Redis and Docker.

## Starlite

Starlite is a light and flexible ASGI API framework.

[Starlite documentation 📚](https://starlite-api.github.io/starlite/)

### Setup

- `pre-commit install`
- `$ cp .env.example .env`
- `$ docker-compose build`
- `$ docker-compose run --rm app alembic upgrade head`

### Run

`$ docker-compose up --build`

### Migrations

#### Revision

`$ docker-compose run --rm app alembic revision --autogenerate -m "revision description"`

#### Migration

`$ docker-compose run --rm app alembic upgrade head`

### Test

To run the tests, have `tox` installed and on your path. I recommend `pipx` which is a tool for
installing python applications in isolated environments.

#### Install `pipx`

```shell
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

#### Install `tox`

```shell
pipx install tox
```

You'll now be able to run `$ pipx run tox`, but that's still a little verbose. I choose to add an
alias for this, e.g.,:

```bash
# ~/.bashrc
# ...
alias tox="pipx run tox"
```

Close and reopen your shell, or `$ source ~/.bashrc` to get the alias working in your current shell.

#### Linting

```bash
tox -e lint
```

#### Unit tests

```bash
tox -e test
```

#### Integration

```bash
tox -e integration
```
