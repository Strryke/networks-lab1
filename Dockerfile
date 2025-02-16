# See the following article to learn more about choosing the right base image
# https://pythonspeed.com/articles/base-image-python-docker-images
FROM python:3.11-slim-bookworm

# Configure Python to not buffer "stdout" or create .pyc files
ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install poetry
# RUN pip install psycopg2-binary
# Set the working directory to a secure non-root location
WORKDIR /app

COPY . .

# Install poetry and dependencies, including dev dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --with dev

# Copy the rest of the application


EXPOSE 8000

CMD [ "poetry", "run", "python", "-m", "lab1.main" ]

