FROM node:14-alpine AS front-end

WORKDIR /app
COPY ./client/package*.json ./

RUN npm install

ENV NODE_ENV production
COPY ./client .
RUN npm run build

FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1
ENV APP_STATIC_DIR /static
RUN mkdir /app
WORKDIR /app
COPY server/requirements.txt /app/.
RUN pip3 install -r requirements.txt
COPY --from=front-end /app/dist $APP_STATIC_DIR
COPY ./server /app/.

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0", "--access-logfile=-", "main:web_server_app" ]