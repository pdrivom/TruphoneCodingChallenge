# TruphoneCodingChallenge

## Introduction

- no unit tests for consumer (why not and what to test)
- api with tests and automated tests

## How it works

docker-compose -f docker-compose.yml run --rm consumer sh -c "python consumer.py"

## Database Schema

- view vs query (views make sense if used for multiple services/systems)
- join vs column
- batch(pgcopy) vs row (psycopg2)

A common practice to implement batching is to store new records in memory first, then after the batch reaches a certain size, insert all the records from memory into the database in one transaction. The perfect batch size isn't universal, but you can experiment with different batch sizes (for example, 100, 1000, 10000, and so on) and see which one fits your use case better. Using batching is a fairly common pattern when ingesting data into TimescaleDB from Kafka, Kinesis, or websocket connections.

## Why this stack

- SQL
- Timeseries
- Grafana Datasource

## How to scale and make production ready