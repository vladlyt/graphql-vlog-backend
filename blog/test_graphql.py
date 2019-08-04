import json

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from .models import Post


class GraphQlTestHelper(TestCase):
    def setUp(self):
        self._client = Client()

    def query(self, query: str, op_name: str = None, variables: dict = None):
        """
        Args:
            query (string) - GraphQL query to run
            op_name (string) - If the query is a mutation or named query, you must supply the op_name.
                               For anonymous queries ("{ ... }"), should be None (default).
            variables (dict) - If provided, the all $variable in GraphQL will be set to this value

        Returns:
            dict, response from graphql endpoint.  The response has the "data" key.
                  It will have the "error" key if any error happened.
        """
        body = {'query': query}
        if op_name:
            body['operation_name'] = op_name
        if variables:
            body['variables'] = variables

        response = self._client.post('/graphql', json.dumps(body), content_type='application/json')
        json_response = json.loads(response.content.decode())
        return json_response

    def assertResponseNoErrors(self, resp: dict, expected: dict):
        """
        Assert that the resp (as returned from query) has the data from expected
        """
        self.assertNotIn('errors', resp, 'Response had errors')
        self.assertEqual(resp['data'], expected, 'Response has correct data')


class PostTestCase(GraphQlTestHelper):

    def setUp(self):
        super().setUp()
        credentials = dict(username='test', password='test')
        self.user = get_user_model().objects.create_user(**credentials, email='test@test.com')
        self._client.login(**credentials)

        Post.objects.bulk_create([
            Post(
                title="First",
                body="first",
                author_id=self.user,
                status=Post.ARCHIVED,
            ), Post(
                title="Second",
                body="second",
                author_id=self.user,
                status=Post.DRAFT,
            ), Post(
                title="Third",
                body="third",
                author_id=self.user,
                status=Post.PUBLISHED,
            )
        ])

    def test_get_all_posts(self):
        query = """
            {
                allPosts {
                    title
                    body
                    status
                }
            }
            """
        json_resp = self.query(query)
        self.assertResponseNoErrors(json_resp,
                                    {'allPosts': [{'title': 'First', 'body': 'first', 'status': 'A_3'},
                                                  {'title': 'Second', 'body': 'second', 'status': 'A_1'},
                                                  {'title': 'Third', 'body': 'third', 'status': 'A_2'}]
                                     })

    def test_create_and_get_post(self):
        query = """
            mutation createPost($title: String!, $body: String!) {
                createPost(title: $title, body: $body) {
                    post {
                        id
                        title
                        body
                        status
                    }
                }
            }
        """
        res = {'title': 'Fourth',
               'body': 'fourth',
               'status': 'A_1'}
        json_resp_create = self.query(query, op_name='createPost', variables={'title': 'Fourth',
                                                                              'body': 'fourth'})
        if 'errors' not in json_resp_create:
            query = """
                query getPost($id: ID) {
                    post(id: $id) {
                        title
                        body
                        status
                    }
                }
            """
            id = json_resp_create['data']['createPost']['post']['id']
            json_resp_get = self.query(query, op_name='getPost', variables={'id': id})
            self.assertResponseNoErrors(json_resp_get, {'post': {**res}})
            del json_resp_create['data']['createPost']['post']['id']
        self.assertResponseNoErrors(json_resp_create, {'createPost': {'post': {**res}}})

    def test_graphql_POST(self):
        response = self._client.post('/graphql', json.dumps({'query': "{}"}), content_type='application/json')
        print(response.content)
        self.assertEqual(response.status_code, 200)
