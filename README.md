# Shortener <!-- omit in TOC -->

- [About](#about)
- [Development](#development)

## About

A URL shortener that provides a clean web interface for managing shortened URLs.

## Development

The project was designed to utilise Docker, so a `docker-compose.yml` file has been provided. The 'Remote Containers' Visual Studio Code plugin can be used to prepare a development environment; that downloads all of the necessary python packages, VSCode plugins and sets the correct linter.

> Before running the web server, ensure that the appropriate variables are set in `./shortener/.env`

The web server and database can be run by using the following command:

```bash
docker-compose up --build
```

You will need to enter the web server's docker container to build the database. You can find the container's name by running `docker ps`, however if everything is default it will likely be 'shortener_app_1'. The following command will create the database:

```bash
docker exec -it shortener_app_1 flask create-db
```

When a change is made to the codebase, the web server will automatically rebuild.
