FROM node:20 as build-stage

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM python:3.10-buster as production-stage

RUN printf "%s\n" \
    "deb http://archive.debian.org/debian buster main contrib non-free" \
    "deb http://archive.debian.org/debian buster-updates main contrib non-free" \
    > /etc/apt/sources.list

RUN echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid

RUN apt-get update && apt-get install -y \
    gcc pkg-config libssl-dev xmlsec1 libxmlsec1-dev libxmlsec1-openssl \
    libxml2-dev libxslt-dev libz-dev \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i 's/SECLEVEL=2/SECLEVEL=1/g' /etc/ssl/openssl.cnf

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=build-stage /app/static /app/static

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]