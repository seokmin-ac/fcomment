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
4. Setup environment variables.

## How To Use

## Endpoints

### `GET /articles`

Get all articles from the database.

- **Permission**
  - public
- **Returns**
  - `articles: [Articles]`: List of articles.
- **Sample Returns**
  ```jsonc
  {
    "success": true,
    "articles": [
      {
        "id": "hello-world"
      },
      {
        "id": "my-second-post"
      },
      {
        "id": "new-beginnings"
      }
    ]
  }
  ```

### `POST /articles`

Add an article to the database. It's recommended to be fetched automatically when the static site's pages are generated.

_NOTICE_: It assumes you are fetching this endpoint for automatic page generation. Thus it allows to fetch to existing id and it ignores internally.

- **Permission**
  - Client credentials
- **Request Body**
  - `id`: Identifier for articles. It should be unique so it is recommened to be URL or slug for itself.
- **Returns**
  - `id: string`: ID for an added article.
- **Sample Returns**
  ```jsonc
  {
    "success": true,
    "id": "new-beginnings"
  }
  ```

### `DELETE /articles/<id: string>`

Remove an article from the database. Comments related with the articles will be removed too.

- **Permission**
  - Client credentials
- **Returns**
  - `id: string`: ID for a removed article.
- **Sample Returns**
  ```jsonc
  {
    "success": true,
    "id": "new-beginnings"
  }
  ```

`GET /articles/<id>`: Get all comments for a given article.

`POST /articles/<id>`: Add a comment to a given article.

`GET /comments`: Get all comments ordered by time.

`GET /comments/<id>`: Get a comment by given id.

`POST /comments/<id>`: Add a reply for a given comment.

`PATCH /comments/<id>`: Edit a given comment.

`DELETE /comments/<id>`: Remove a given comment.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/seokmin-ac/fcomment)
