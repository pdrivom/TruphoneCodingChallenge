# SIM Card Usage Coding Challenge

## Environment of Development

## Introduction

- no unit tests for consumer (why not and what to test)
- api with tests and automated tests

## How it works

- consumer: docker-compose -f docker-compose.yml run --rm consumer sh -c "python consumer.py"
- api: docker-compose -f docker-compose.yml run --rm --service-ports api sh -c "uvicorn api:app --host 0.0.0.0 --port 8000 --reload"
- api test: docker-compose -f docker-compose.yml run --rm api sh -c "pytest"
- url: http://domain:port/api/v1/entity/subentity/id_parameter?query_parameters
    - http://domain:port/api/v1/usage/organizations
    - http://domain:port/api/v1/usage/simcards
    - http://domain:port/api/v1/organization/x00g8/usage?start=2020-01-01&end=2020-01-31&every=1hour&page=1&size=5
    - http://domain:port/api/v1/simcard/89440010/usage?start=2020-01-01&end=2020-01-31&every=1day&page=1&size=5


## Database Schema

- view vs query (views make sense if used for multiple services/systems)
- join vs column
- batch(pgcopy) vs row (psycopg2)

## Development steps

## Why this stack

- SQL
- Timeseries
- Grafana Datasource
- REST (not GraphQL or gRPC)
    - (gRPC) no bi-directional or streaming needed
    - (GraphQL) upfront dev effort and more field related queries

## How to make production ready

- certificate to expose API on https
- test security token on the requests
- add unit tests for other non-required features
- add unit testing to consumer
- add database tests

## How to scale

- [Distributed Hypertables](https://docs.timescale.com/api/latest/distributed-hypertables/#distributed-hypertables)
- [Partitioning in hypertables with chunks](https://docs.timescale.com/timescaledb/latest/overview/core-concepts/hypertables-and-chunks/#partitioning-in-hypertables-with-chunks)

## Future of the repo
- add flake8 for linting
- add consumer and database tests
- add a NodeJS(Koa/Loopback/Nest) to implement the API in order to make clear compare between the two technologies
- develop proper sql statement builder since sqlalchemy does not help very much