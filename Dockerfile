FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN apt-get update && apt-get install -y \
	aria2

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

# System deps:
ENV HOME=/root
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="${HOME}/.poetry/bin:${PATH}"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

COPY plexarr /code/plexarr
RUN poetry build && pip install dist/*.whl


WORKDIR /app
COPY prestart.sh /app
ENV APP_MODULE plexarr.main:app

ENV DOWNLOAD_DIR /downloads
RUN mkdir ${DOWNLOAD_DIR}
ENV PLEX_USERNAME your-plex-username
ENV PLEX_PASSWORD your-plex-password
ENV RADARR_URL http://10.0.13.60:7878/radarr
ENV RADARR_KEY this-is-not-your-real-key

RUN mkdir /conf
#https://github.com/wahyd4/aria2-ariang-docker/blob/4c16558d9ad3602b861a4ae4c6fde841f96ede15/Dockerfile#L37-L45 
RUN mkdir -p /usr/local/www/aria2/Download \
  && cd /usr/local/www/aria2 \
  && version=1.1.4 \
  && wget -N --no-check-certificate https://github.com/mayswind/AriaNg/releases/download/${version}/AriaNg-${version}.zip \
  && unzip AriaNg-${version}.zip \
  && rm -rf AriaNg-${version}.zip \
  && chmod -R 755 /usr/local/www/aria2
