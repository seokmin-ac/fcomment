# fcomment

![Heroku](https://pyheroku-badge.herokuapp.com/?app=fcomment&path=/comments)

Attachable self-hosting comment service for static web site.

## Overview

This is a capstone project for Udacity FSND.

There are some comment hosting service like as [Disqus](https://disqus.com/). It offers strong functionality but there are some restriction for design. So I want to make a very simple API for hosting comments.

Full stack demo: https://fcomment-sample.netlify.app

## **Deployment**

1. Fork or clone this repository.
2. Setup your [Auth0](https://auth0.com/) application.
3. Connect the repository with [Heroku](https://www.heroku.com/).
4. Setup environment variables.

## Installation for development

### PostgreSQL

1. Install [PostgreSQL](https://www.postgresql.org/download/).
2. Create a table for local developments.

   ```shell
   createdb fcomment
   ```

### Auth0

1. Sign in to [Auth0](https://auth0.com/).
2. Create an API.
3. Go to `{YOUR_API}` > `Permissions` window and add following three permissions.
   - **post:articles**: It allows the user can add articles. It will be granted to client credential token.
   - **delete:articles**: It allows the user can remove articles. It will be granted to client credential token.
   - **post:comments**: It allows the user can add or edit comments. It will be granted to qualified users.
   - **delete:comments**: It allows the user can remove comments. It will be granted to an admin user.
4. Go to `{YOUR_API}` > `Machine to Machine Applications` window. You may see the auto generated application named `{YOUR_API} (Test Application)` and it would be authorized. Click uncollapse button looks like symbol ">" and check `post:articles` and `delete:articles`.
5. Click update button to submit.

### Python

1. Clone the project

   ```shell
   git clone https://github.com/seokmin-ac/fcomment
   cd fcomment
   ```

2. Install dependencies for development.

   ```shell
   pip install -r requirements-dev.txt
   ```

3. Add a file named `.env` to root directory of the project. Local environment variables would be provided by `.env` file with `dotenv` package.

   ```
   DATABASE_URL="postgres://postgres@localhost:XXXX/XXXXX"
   AUTH_DOMAIN="XXXX.us.auth0.com"
   AUTH_AUDIENCE="XXXX"
   ```

   - **DATABASE_URL**: Database URL for your PostgreSQL table.
   - **AUTH_DOMAIN**: A domain of your Auth0 account.
   - **AUTH_AUDIENCE**: An identifier of API what you created.

4. Now you can run the project with following command.

   ```shell
   python main.py
   ```

## Roles

There are two roles for fcomment.

### Admin

Admin users can post or remove articles and comments.

### Qualified

Qualified users can post or edit comments.

## Testing

```shell
./test
```

If provided tokens are expired, you need to get new tokens by yourself. Following emails and passwords are accounts for testing.

| email            | Password    | Role      |
| ---------------- | ----------- | --------- |
| manager@test.com | manager123! | admin     |
| barista@test.com | barista123! | qualified |
| test@test.com    | test123!    | none      |

| Key            | Value                                                            |
| -------------- | ---------------------------------------------------------------- |
| Domain         | dev-vztcxiti.us.auth0.com                                        |
| Audience       | fcomment                                                         |
| Client ID      | gv5Krf3lP54qHnK59seHecv4qZhLY6G7                                 |
| API Identifier | rnHpgDR6jjEztHRVpLYZKEg8FHPdZRp8                                 |
| Client Secret  | un6B0T-B65BxI9zgYh-zxegNqOKcpZz2vin2ePlx9mVtkmaWMBuynrxLDhiTBzBZ |

## Endpoints

### `POST /auth`

Check is the JWT is valid. If is not, it aborts 400, 401 or 403 error.

- **Permission**
  - login only
- **Returns**
  - None

### `GET /users`

Get all users.

- **Permission**
  - public
- **Returns**
  - `users: [User]`: List of users.
- **Sample Returns**
  ```jsonc
  {
    "success": true,
    "users": [
      {
        "id": "auth0|5f3e92f9fe4527006d9383bc",
        "nickname": "manager",
        "picture": "https://s.gravatar.com/avatar/ad5c2c75bd08bbf326ace2a8addf1e05?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fma.png"
      },
      {
        "id": "google-oauth2|106050262959037228016",
        "nickname": "fprtlwidmd240",
        "picture": "https://lh3.googleusercontent.com/a-/AOh14GgptlNbuvx27oTDIr3aLyCTjcQvAva6UTIDp4k15Q"
      }
    ]
  }
  ```

### `POST /users`

Update or add a given user.

- **Permission**
  - login only
- **Request Body**
  - `id`: ID of a user. It is a `sub` parameter of JWT.
  - `nickname`: Nickname of the user.
  - `picture`: URL for user's profile image.
- **Returns**
  - `id: string`: ID for updated user.
- **Sample Returns**
  ```jsonc
  {
    "success": true,
    "id": "google-oauth2|106050262959037228016"
  }
  ```

### `GET /articles`

Get all articles from the database.

- **Permission**
  - public
- **Returns**
  - `articles: [Article]`: List of articles.
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
  - `post:articles`
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

### `DELETE /articles/<id:string>`

Remove an article from the database. Comments related with the articles will be removed too.

- **Permission**
  - `delete:articles`
- **Returns**
  - `id: string`: ID for a removed article.
- **Sample Returns**
  ```jsonc
  {
    "success": true,
    "id": "new-beginnings"
  }
  ```

### `GET /articles/<id:string>/comments`

Get all comments for a given article.

- **Permission**
  - public
- **Returns**
  - `count: int`: Number of the comments for the article.
  - `comments: [RecursiveComment]`: Comments for the article. It has recursive structure for replies. Note that it includes removed comments if its replies are exist.
- **Sample Returns**
  ```jsonc
  {
    "comments": [
      {
        "article": "new-beginnings",
        "content": "Hello, world!",
        "datetime": "Wed, 09 Sep 2020 16:20:28 GMT",
        "id": 1,
        "parent": null,
        "removed": false,
        "user": "auth0|5f3e92f9fe4527006d9383bc"
      },
      {
        "article": "new-beginnings",
        "content": "Comment from mobile!",
        "datetime": "Wed, 09 Sep 2020 21:17:25 GMT",
        "id": 2,
        "parent": null,
        "removed": false,
        "replies": [
          {
            "article": "new-beginnings",
            "datetime": "Wed, 09 Sep 2020 21:19:21 GMT",
            "id": 3,
            "parent": 2,
            "removed": true,
            "replies": [
              {
                "article": "new-beginnings",
                "content": "Reply for removed comment.",
                "datetime": "Wed, 09 Sep 2020 21:19:47 GMT",
                "id": 4,
                "parent": 3,
                "removed": false,
                "user": "google-oauth2|106050262959037228016"
              }
            ]
          }
        ],
        "user": "google-oauth2|106050262959037228016"
      }
    ],
    "count": 3,
    "success": true
  }
  ```

### `POST /articles/<id:string>/comments`

Add a comment to a given article.

- **Permission**
  - `post:comments`
- **Request Body**
  - `content`: A content of comment.
- **Returns**
  - `id: int`: ID for an added comment.
- **Sample Returns**
  ```jsonc
  {
    "success": true,
    "id": 2
  }
  ```

### `GET /comments`

Get all comments ordered by time.

- **Permission**
  - public
- **Arguments**
  - `page`: Page of comment. Contents for page is 20.
- **Returns**
  - `comments: [Comment]`: List of comments. It is not a recursive form and it ignores removed ones.
- **Sample Returns**
  ```jsonc
  {
    "comments": [
      {
        "article": "new-beginnings",
        "content": "Hello, world!",
        "datetime": "Wed, 09 Sep 2020 16:20:28 GMT",
        "id": 1,
        "parent": null,
        "removed": false,
        "user": "auth0|5f3e92f9fe4527006d9383bc"
      },
      {
        "article": "new-beginnings",
        "content": "Comment from mobile!",
        "datetime": "Wed, 09 Sep 2020 21:17:25 GMT",
        "id": 2,
        "parent": null,
        "removed": false,
        "user": "google-oauth2|106050262959037228016"
      },
      {
        "article": "new-beginnings",
        "content": "Reply for removed comment.",
        "datetime": "Wed, 09 Sep 2020 21:19:47 GMT",
        "id": 4,
        "parent": 3,
        "removed": false,
        "user": "google-oauth2|106050262959037228016"
      }
    ],
    "success": true
  }
  ```

### `GET /comments/<id:int>`

Get a comment by given id.

- **Permission**
  - public
- **Returns**
  - `comment: Comment`: A comment having given ID.
- **Sample Returns**
  ```jsonc
  {
    "comment": {
      "article": "new-beginnings",
      "content": "Hello, world!",
      "datetime": "Wed, 09 Sep 2020 16:20:28 GMT",
      "id": 1,
      "parent": null,
      "removed": false,
      "user": "auth0|5f3e92f9fe4527006d9383bc"
    },
    "success": true
  }
  ```

### `POST /comments/<id:int>`

Add a reply for a given comment.

- **Permission**
  - `post:comments`
- **Request Body**
  - `content`: A content of comment.
- **Returns**
  - `id: int`: ID for an added reply.
- **Sample Returns**
  ```jsonc
  {
    "success": true,
    "id": 4
  }
  ```

### `PATCH /comments/<id:int>`

Edit a given comment.

- **Permission**
  - author of the comment
- **Request Body**
  - `content`: A content of comment.
- **Returns**
  - `id: int`: ID for an edited comment.
- **Sample Returns**
  ```jsonc
  {
    "success": true,
    "id": 2
  }
  ```

### `DELETE /comments/<id:int>`

Remove a given comment.

- **Permission**
  - author of the comment
  - `delete:comments`
- **Returns**
  - `id: int`: ID for an removed comment.
- **Sample Returns**
  ```jsonc
  {
    "success": true,
    "id": 3
  }
  ```
