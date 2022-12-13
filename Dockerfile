FROM python:3.11-slim AS base
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends curl git build-essential python3-setuptools \
    && apt-get autoremove -y
ENV POETRY_HOME="/opt/poetry"
RUN curl -sSL https://install.python-poetry.org | python3 -

FROM base AS install
WORKDIR /app/

# allow controlling the poetry installation of dependencies via external args
ARG INSTALL_ARGS="--no-root --no-dev"
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
COPY pyproject.toml poetry.lock ./

# install without virtualenv, since we are inside a container
RUN poetry config virtualenvs.create false \
    && poetry install $INSTALL_ARGS

# cleanup
RUN curl -sSL https://install.python-poetry.org | python3 - --uninstall
RUN apt-get purge -y curl git build-essential \
    && apt-get clean -y \
    && rm -rf /root/.cache \
    && rm -rf /var/apt/lists/* \
    && rm -rf /var/cache/apt/*

FROM install as app-image
COPY alembic.ini ./
COPY alembic alembic
COPY app app

# create a non-root user and switch to it, for security.
RUN addgroup --system --gid 1001 "app-user"
RUN adduser --system --uid 1001 "app-user"
USER "app-user"
