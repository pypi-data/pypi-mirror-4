import unittest
import mock

import elfcloud.client as client
from elfcloud.container import Cluster, Vault


class TestCluster(unittest.TestCase):
    def setUp(self):
        self.client = client.Client('username', 'password')

    def test_cluster_init(self):
        arguments = {
                'name': 'cluster_name',
                'descendants': 1,
                'dataitems': 2,
                'parent_id': 1,
                'type': 'cluster',
                'id': 2
            }
        cluster = Cluster(self.client, **arguments)
        self.assertEquals(cluster._client, self.client)
        self.assertEquals(cluster.name, "cluster_name")
        self.assertEquals(cluster.descendants, 1)
        self.assertEquals(cluster._dataitem_count, 2)
        self.assertEquals(cluster.parent_id, 1)
        self.assertEquals(cluster.id, 2)

    def test_cluster_remove(self):
        valid_result = "REMOVE_CLUSTER_TEST_SUCCESS"

        conn = mock.Mock()
        conn.make_request.return_value = valid_result
        self.client.connection = conn
        arguments = {
                'name': 'cluster_name',
                'descendants': 1,
                'dataitems': 2,
                'parent_id': 1,
                'type': 'cluster',
                'id': 2
            }
        cluster = Cluster(self.client, **arguments)
        response = cluster.remove()
        self.assertEquals(response, valid_result)
        conn.make_request.assert_called_once_with('remove_cluster', {'cluster_id': 2})

    def test_cluster_rename(self):
        valid_result = "RENAME_CLUSTER_TEST"

        conn = mock.Mock()
        conn.make_request.return_value = valid_result
        self.client.connection = conn
        arguments = {
                'name': 'cluster_name',
                'descendants': 1,
                'dataitems': 2,
                'parent_id': 1,
                'type': 'cluster',
                'id': 2
            }
        cluster = Cluster(self.client, **arguments)
        response = cluster.rename('cluster_new_name')
        self.assertEquals(response, valid_result)
        conn.make_request.assert_called_once_with('rename_cluster', {'cluster_id': 2, 'name': 'cluster_new_name'})

    def test_cluster_children_list(self):
        cluster1_args = {
                'name': 'cluster1',
                'descendants': 0,
                'dataitems': 0,
                'parent_id': 2,
                'type': 'cluster',
                'id': 3
                }
        cluster2_args = {
                'name': 'cluster2',
                'descendants': 1,
                'dataitems': 1,
                'parent_id': 2,
                'type': 'cluster',
                'id': 4
                }

        conn = mock.Mock()
        conn.make_request.return_value = [
                    cluster1_args,
                    cluster2_args
                ]
        self.client.connection = conn
        parent_args = {
                'name': 'Parent Cluster',
                'descendants': 2,
                'dataitems': 0,
                'parent_id': 1,
                'type': 'cluster',
                'id': 2
            }

        cluster = Cluster(self.client, **parent_args)
        response = cluster.children
        self.assertEquals(len(response), 2)
        self.assertEquals(response[0].name, cluster1_args['name'])
        self.assertEquals(response[1].name, cluster2_args['name'])
        conn.make_request.assert_called_once_with('list_clusters', {'parent_id': 2})

    def test_cluster_dataitems_list(self):
        conn = mock.Mock()
        conn.make_request.return_value = [
                    {'name': "dataitem1", 'parent_id': 2},
                    {'name': "dataitem2", 'parent_id': 2}
                ]
        self.client.connection = conn
        parent_args = {
                'name': 'Parent Cluster',
                'descendants': 0,
                'dataitems': 2,
                'parent_id': 1,
                'type': 'cluster',
                'id': 2
            }

        cluster = Cluster(self.client, **parent_args)
        response = cluster.dataitems
        self.assertEquals(len(response), 2)
        self.assertEquals(response[0].name, "dataitem1")
        self.assertEquals(response[0].parent_id, cluster.id)
        self.assertEquals(response[1].name, "dataitem2")
        self.assertEquals(response[1].parent_id, cluster.id)
        conn.make_request.assert_called_once_with('list_dataitems', {'parent_id': 2})


class TestVault(unittest.TestCase):
    def setUp(self):
        self.client = client.Client('username', 'password')

    def test_vault_init(self):
        arguments = {
                'name': 'cluster_name',
                'descendants': 1,
                'vault_type': 'test_type',
                'dataitems': 2,
                'type': 'test_type',
                'id': 1
            }
        vault = Vault(self.client, **arguments)
        self.assertEquals(vault._client, self.client)
        self.assertEquals(vault.name, "cluster_name")
        self.assertEquals(vault.descendants, 1)
        self.assertEquals(vault._dataitem_count, 2)
        self.assertEquals(vault.id, 1)

    def test_vault_rename(self):
        conn = mock.Mock()
        conn.make_request.return_value = "VAULT_REMOVE_RESPONSE"
        self.client.connection = conn
        arguments = {
                'name': 'vault_name',
                'descendants': 1,
                'vault_type': 'test_type',
                'dataitems': 2,
                'type': 'test_type',
                'id': 1
            }
        vault = Vault(self.client, **arguments)

        result = vault.rename('new_vault_name')
        self.assertEquals(result, "VAULT_REMOVE_RESPONSE")
        conn.make_request.assert_called_once_with('rename_vault', {'vault_id': 1, 'vault_name': 'new_vault_name'})

    def test_vault_remove(self):
        conn = mock.Mock()
        self.client.connection = conn
        arguments = {
                'name': 'cluster_name',
                'descendants': 1,
                'vault_type': 'test_type',
                'dataitems': 2,
                'type': 'test_type',
                'id': 1
            }
        vault = Vault(self.client, **arguments)

        result = vault.remove()
        self.assertEquals(result, None)
        conn.make_request.assert_called_once_with('remove_vault', {'vault_id': 1})
