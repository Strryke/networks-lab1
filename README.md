## Networks Lab 1

By: Gavin Ong (1005896)

A basic book REST API built using FastAPI and Postgres.

To run:

- From root, run `docker compose up --build`
- This should spin up the hot-reload app and the db
- View the Swagger docs at: http://localhost/docs

To run tests:

- Make sure the container is running above ^
- Enter the Docker container: `docker compose exec app sh`
- Run `poetry run pytest --verbose` to run the tests

Checkoff:

- All basic requirements captured in the tests
- Extras: `delete/batch` and a simple `admin` route that looks at headers

Idempotent routes:

- `GET /books`: gets are by nature idempotent. Repeated similar queries will produce the same result, barring any extraneous updates.
- `PUT /books`: same as above.
