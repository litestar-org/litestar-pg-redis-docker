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
Redis, SAQ and Docker.

## Starlite

Starlite is a light and flexible ASGI API framework.

[Starlite documentation 📚](https://starlite-api.github.io/starlite/)

## Run the application

### Setup

- `$ cp .env.example .env`
- `$ docker-compose build`
- `$ docker-compose run --rm app alembic upgrade head`

### Run

`$ docker-compose up --build`

### Async Worker Emails

To demonstrate usage of the asynchronous `SAQ` workers, when an `Author` is created we trigger a
worker function that sends an email.

`mailhog` is included in `docker-compose.yaml`, and includes a GUI that can be accessed at
`http://localhost:8025`.

Create an `Author`:

```bash
$ curl -w "\n" -X POST -H "Content-Type: application/json" -d '{"name": "James Patterson", "dob": "1974-3-22"}' http://localhost:8000/authors
{"id":"6f395bdf-3e77-481d-98b2-3471c2342654","created":"2022-10-09T23:18:10","updated":"2022-10-09T23:18:10","name":"James Patterson","dob":"1974-03-22"}
```

Then check the `mailhog` GUI to see the email that has been sent by the worker.

## Development

### Install pre-commit hooks

- `pre-commit install`

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
# run a specific hook
tox -e lint mypy
```

#### Unit tests

```bash
tox -e test
```

#### Integration tests

```bash
tox -e integration
```
