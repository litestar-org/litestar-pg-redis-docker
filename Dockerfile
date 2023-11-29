#syntax=docker/dockerfile:1.4

ARG INSTALL_DEPENDENCIES=prod

FROM python:3.11-slim AS base

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends curl git build-essential python3-setuptools \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/apt/lists/* \
    && rm -rf /var/cache/apt/*


ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH" \
    POETRY_VERSION=1.6.1
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false \
    && mkdir -p /cache/poetry \
    && poetry config cache-dir /cache/poetry

FROM base AS base-prod

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# install only production dependencies
RUN --mount=type=cache,target=/cache/poetry \
    poetry install --no-root --only main


FROM base-prod AS base-dev

# install the rest of the dependencies
RUN --mount=type=cache,target=/cache/poetry \
    poetry install --no-root

# hadolint ignore=DL3006
FROM base-${INSTALL_DEPENDENCIES} AS final

# copy all the application code and install our project

COPY . ./

RUN poetry install --only-root

# create a non-root user and switch to it, for security.
RUN addgroup --system --gid 1001 "app-user"
RUN adduser --system --uid 1001 "app-user"
USER "app-user"

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["./scripts/entry"]
