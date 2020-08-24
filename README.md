# fcomment

![Heroku](https://pyheroku-badge.herokuapp.com/?app=fcomment)

Attachable self-hosting comment service.

## Overview

This is a capstone project for Udacity FSND.

There are some comment hosting service like as [Disqus](https://disqus.com/). It offers strong functionality but there are some restriction for design. So I want to make a very simple API for hosting comments.

## Installation

1. Fork or clone this repository.
2. Connect your [Auth0](https://auth0.com/) account.
3. Connect the repository with [Heroku](https://www.heroku.com/).

## How To Use

1. Grant your account as a `manager`.
2. Call `POST /articles` API to register your article to fcomment. I recommend to use `id` as slug for your article.
3. Now fcomment has your article. Try `POST /articles/<id>/comments` with comment text. It needs JWT token.
4. Try `GET /articles/<id>/comments`. It will returns all comments for the article.

## Endpoints

- `GET /articles`: Get all articles.
- `POST /articles`: Add an article to the database.
- `DELETE /articles`: Remove an article from the database.
- `GET /articles/<id>/comments`: Get all comments for a given article.
- `POST /articles/<id>/comments`: Add a comment to a given article.
- `GET /comments`: Get all comments ordered by time.
- `POST /comments/<id>`: Add a reply for a given comment.
- `PATCH /comments/<id>`: Edit a given comment.
- `DELETE /comments/<id>`: Remove a given comment.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/seokmin-ac/fcomment)
