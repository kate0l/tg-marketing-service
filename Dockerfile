FROM python:3.13.2-slim

RUN apt-get update && apt-get install -yq make \
                && pip install uv

WORKDIR /app

COPY . .

RUN uv sync

RUN make migrate

CMD ["make", "prod-run"]