> [!WARNING]
> This repository has not been updated yet and will be receiving some TLC.
>
> If you would like to help, feel free to discuss in Discord or open a pull request.

<!-- markdownlint-disable -->
<p align="center">
  <img src="https://github.com/litestar-org/branding/blob/main/assets/Branding%20-%20SVG%20-%20Transparent/Logo%20-%20Banner%20-%20Inline%20-%20Light.svg#gh-light-mode-only" alt="Litestar Logo - Light" width="100%" height="auto" />
  <img src="https://github.com/litestar-org/branding/blob/5c46ce93092faa36d0ba572f931b5d579ae75ad3/assets/Branding%20-%20SVG%20-%20Transparent/Logo%20-%20Banner%20-%20Inline%20-%20Dark.svg#gh-dark-mode-only" alt="Litestar Logo - Dark" width="100%" height="auto" />
</p>
<!-- markdownlint-restore -->

<div align="center">

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-pg-redis-docker&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar-pg-redis-docker)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-pg-redis-docker&metric=coverage)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar-pg-redis-docker)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-pg-redis-docker&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar-pg-redis-docker)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-pg-redis-docker&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar-pg-redis-docker)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-pg-redis-docker&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar-pg-redis-docker)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-pg-redis-docker&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar-pg-redis-docker)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=litestar-org_litestar-pg-redis-docker&metric=bugs)](https://sonarcloud.io/summary/new_code?id=litestar-org_litestar-pg-redis-docker)

[![Discord](https://img.shields.io/discord/919193495116337154?color=202235&label=%20Discord&logo=discord)](https://discord.gg/X3FJqy8d2j)
[![Matrix](https://img.shields.io/badge/%5Bm%5D%20Matrix-bridged-blue?color=202235)](https://matrix.to/#/#litestarspace:matrix.org)
[![Reddit](https://img.shields.io/reddit/subreddit-subscribers/litestar?label=r%2FLitestar&logo=reddit)](https://reddit.com/r/litestar)

</div>

# litestar-pg-redis-docker

This is an example [Litestar](https://github.com/litestar-api/litestar) project using SQLAlchemy + Alembic + postgresql,
Redis, SAQ and Docker.

## Litestar

Litestar is a light and flexible ASGI API framework.

[Litestar documentation 📚](https://litestar-api.github.io/litestar/)

## Run the application

### Setup

- `$ cp .env.example .env`
- `$ docker compose build`
- `$ docker compose run --rm app alembic upgrade head`

### Run

`$ docker compose up --build`

### Async Worker Emails

To demonstrate usage of the asynchronous `SAQ` workers, when an `Author` is created we trigger a
worker function that sends an email.

`mailhog` is included in `docker-compose.yaml`, and includes a GUI that can be accessed at
`http://localhost:8025`.

Create an `Author`:

```bash
$ curl -w "\n" -X POST -H "Content-Type: application/json" -d '{"name": "James Patterson", "dob": "1974-3-22"}' http://localhost:8000/v1/authors
{"id":"6f395bdf-3e77-481d-98b2-3471c2342654","created":"2022-10-09T23:18:10","updated":"2022-10-09T23:18:10","name":"James Patterson","dob":"1974-03-22"}
```

Then check the `mailhog` GUI to see the email that has been sent by the worker.

## Development

### Install pre-commit hooks

- `pre-commit install`

### Migrations

#### Revision

`$ docker compose run --rm app alembic revision --autogenerate -m "revision description"`

#### Migration

`$ docker compose run --rm app alembic upgrade head`
