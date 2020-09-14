# To load .env file for local development.
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path='.test.env')
except Exception:
    pass

import os
import unittest
import json

from app import app


class FCommentTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client

    def tearDown(self):
        # Executed after reach test
        pass

    # POST /auth
    def test_check_auth_without_token(self):
        res = self.client().post('/auth')
        self.assertEqual(res.status_code, 401)

    def test_check_auth_with_expired_token(self):
        res = self.client().post('/auth', headers={
            'Authorization':
                f'Bearer {os.environ["JWT_CLIENT_CREDENTIAL_EXPIRED"]}'
        })
        self.assertEqual(res.status_code, 401)

    def test_check_auth_with_valid_token(self):
        res = self.client().post('/auth', headers={
            'Authorization':
                f'Bearer {os.environ["JWT_CLIENT_CREDENTIAL_VALID"]}'
        })
        self.assertEqual(res.status_code, 200)

    # GET /users
    def test_get_users(self):
        res = self.client().get('/users')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['users']), 3)

    # POST /users
    def test_update_users(self):
        # Get users
        res = self.client().get('/users')
        users = json.loads(res.data)['users']
        testUser = next(u for u in users if u['nickname'] == 'test')
        # Edit a picture as null string for an user named "test".
        testUser['picture'] = ''

        # Commit edit.
        res = self.client().post('/users', headers={
                'Authorization': f'Bearer {os.environ["JWT_TEST"]}'
            },
            json=testUser
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['id'], testUser['id'])

        # Check the latest picture is null string for "test".
        res = self.client().get('/users')
        users = json.loads(res.data)['users']
        testUser = next(u for u in users if u['nickname'] == 'test')
        self.assertEqual(testUser['picture'], '')

    # GET /articles
    def test_get_articles(self):
        res = self.client().get('/articles')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['articles']), 3)

    # POST /articles & DELETE /articles/:id
    def test_post_and_delete_articles(self):
        # Post article
        res = self.client().post('/articles', headers={
                'Authorization': f'Bearer {os.environ["JWT_MANAGER"]}'
            },
            json={
                'id': 'new-post'
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['id'], 'new-post')

        res = self.client().get('/articles')
        data = json.loads(res.data)

        # Remove article
        res = self.client().delete('/articles/new-post', headers={
                'Authorization': f'Bearer {os.environ["JWT_MANAGER"]}'
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['id'], 'new-post')

    # RBAC test for POST /articles
    def test_post_article_with_inappropriate_role(self):
        res = self.client().post('/articles', headers={
                'Authorization': f'Bearer {os.environ["JWT_BARISTA"]}'
            },
            json={
                'id': 'new-post'
            })
        self.assertEqual(res.status_code, 403)

    # RBAC test for DELETE /articles/:id
    def test_delete_article_with_inappropriate_role(self):
        res = self.client().delete('/articles/new-beginnings', headers={
                'Authorization': f'Bearer {os.environ["JWT_BARISTA"]}'
            })
        self.assertEqual(res.status_code, 403)

    # GET /articles/:id/comments
    def test_get_comments_from_article(self):
        res = self.client().get('/articles/new-beginnings/comments')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['count'], 3)
        self.assertEqual(len(data['comments']), 2)

    # POST /articles/:id/comments
    def test_post_comment_to_article(self):
        # Post a comment
        res = self.client().post('/articles/my-second-post/comments', headers={
                'Authorization': f'Bearer {os.environ["JWT_BARISTA"]}'
            },
            json={
                'content': 'This is a comment for test!'
            }
        )
        self.assertEqual(res.status_code, 200)

        # Check is the comment is committed.
        res = self.client().get('/articles/my-second-post/comments')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['count'], 1)

    def test_post_comment_to_article_with_unqualified(self):
        res = self.client().post('/articles/my-second-post/comments', headers={
                'Authorization': f'Bearer {os.environ["JWT_TEST"]}'
            },
            json={
                'content': 'This is a comment for test!'
            }
        )
        self.assertEqual(res.status_code, 403)

    # GET /comments
    def test_get_comments(self):
        res = self.client().get('/comments')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data['comments']), 0)

    # GET /comments/:id
    def test_get_comment(self):
        res = self.client().get('/comments/16')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['comment']['content'], 'Reply to reply!')

    def test_get_comment_with_invalid_id(self):
        res = self.client().get('/comments/0')
        self.assertEqual(res.status_code, 404)

    def test_get_already_removed_comment(self):
        res = self.client().get('/comments/3')
        self.assertEqual(res.status_code, 404)

    # POST /comments/:id
    def test_post_reply(self):
        # Post a comment.
        res = self.client().post('articles/hello-world/comments', headers={
                'Authorization': f'Bearer {os.environ["JWT_BARISTA"]}'
            },
            json={
                'content': 'This is a comment for test!'
            }
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

        # Post a reply.
        id = data['id']
        res = self.client().post(f'comments/{id}', headers={
                'Authorization': f'Bearer {os.environ["JWT_MANAGER"]}'
            },
            json={
                'content': 'This is a reply for test!'
            }
        )
        self.assertEqual(res.status_code, 200)

        # Post a reply from unqualified user.
        id = data['id']
        res = self.client().post(f'comments/{id}', headers={
                'Authorization': f'Bearer {os.environ["JWT_TEST"]}'
            },
            json={
                'content': 'This is a reply to be not accepted'
            }
        )
        self.assertEqual(res.status_code, 403)

    # PATCH /comments/:id
    def test_edit_comment(self):
        # Edit a comment.
        res = self.client().patch('comments/21', headers={
                'Authorization': f'Bearer {os.environ["JWT_BARISTA"]}'
            },
            json={
                'content': 'Edited comment!'
            }
        )
        self.assertEqual(res.status_code, 200)

        res = self.client().get('/comments/21')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['comment']['content'], 'Edited comment!')

    def test_edit_comment_with_other_account(self):
        # Edit a comment.
        res = self.client().patch('comments/21', headers={
                'Authorization': f'Bearer {os.environ["JWT_MANAGER"]}'
            },
            json={
                'content': 'Edited comment!'
            }
        )
        self.assertEqual(res.status_code, 403)

    # DELETE /comments
    def test_delete_reply(self):
        # Post a comment.
        res = self.client().post('articles/hello-world/comments', headers={
                'Authorization': f'Bearer {os.environ["JWT_BARISTA"]}'
            },
            json={
                'content': 'Test comment for DELETE /comments'
            }
        )
        data = json.loads(res.data)
        comment_id = data['id']
        self.assertEqual(res.status_code, 200)

        # Post a reply.
        res = self.client().post(f'comments/{comment_id}', headers={
                'Authorization': f'Bearer {os.environ["JWT_MANAGER"]}'
            },
            json={
                'content': 'This is a reply for test!'
            }
        )
        data = json.loads(res.data)
        reply_id = data['id']
        self.assertEqual(res.status_code, 200)

        res = self.client().get('articles/hello-world/comments')
        data = json.loads(res.data)
        cnt_1 = data['count']
        self.assertEqual(res.status_code, 200)

        # Delete a comment.
        res = self.client().delete(f'comments/{comment_id}', headers={
                'Authorization': f'Bearer {os.environ["JWT_MANAGER"]}'
            }
        )
        self.assertEqual(res.status_code, 200)

        # Check is the parent comment remains with a removed state.
        res = self.client().get('/articles/hello-world/comments')
        data = json.loads(res.data)
        cnt_2 = data['count']
        removed_comment = next(
            c for c in data['comments'] if c['id'] == comment_id
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(cnt_1 - 1, cnt_2)
        self.assertTrue(removed_comment['removed'])

        # Delete a reply.
        res = self.client().delete(f'comments/{reply_id}', headers={
                'Authorization': f'Bearer {os.environ["JWT_MANAGER"]}'
            }
        )
        self.assertEqual(res.status_code, 200)

        # Check is the reply is removed.
        res = self.client().get('/articles/hello-world/comments')
        data = json.loads(res.data)
        cnt_3 = data['count']
        self.assertEqual(res.status_code, 200)
        self.assertEqual(cnt_2 - 1, cnt_3)
        # Check is the parent comment is also removed.
        removed_comment = None
        try:
            removed_comment = next(
                c for c in data['comments'] if c['id'] == comment_id
            )
        except Exception:
            pass
        self.assertIsNone(removed_comment)


if __name__ == '__main__':
    unittest.main()
