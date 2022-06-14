# SIM Card Usage Coding Challenge

## Introduction

- no unit tests for consumer (why not and what to test)
- api with tests and automated tests

## How it works

- consumer: docker-compose -f docker-compose.yml run --rm consumer sh -c "python consumer.py"
- api: docker-compose -f docker-compose.yml run --rm api sh -c "uvicorn api:app --host 0.0.0.0 --port 8000 --reload"
- api test: docker-compose -f docker-compose.yml run --rm api sh -c "pytest"
- url: http://domain:port/api/v1/entity/subentity/id_parameter?query_parameters
    - http://domain:port/api/v1/usage/organizations
    - http://domain:port/api/v1/usage/simcards
    - http://domain:port/api/v1/usage/organization/x00g8?start=2012-01-01&end=2012-01-31&page_num=1&page_size=5
    - http://domain:port/api/v1/usage/simcard/89440010?start=2012-01-01&end=2012-01-31&page_num=1&page_size=5


## Database Schema

- view vs query (views make sense if used for multiple services/systems)
- join vs column
- batch(pgcopy) vs row (psycopg2)


## Why this stack

- SQL
- Timeseries
- Grafana Datasource
- REST (not GraphQL or gRPC)
    - (gRPC) no bi-directional or streaming needed
    - (GraphQL) upfront dev effort and more field related queries

## How to scale and make production ready

- certificate to expose API on https
- test security token on the requests
- add unit testing to consumer

## Future of the repo

- add a NodeJS(Koa/Loopback/Nest) to implement the API in order to make clear compare between the two technologies