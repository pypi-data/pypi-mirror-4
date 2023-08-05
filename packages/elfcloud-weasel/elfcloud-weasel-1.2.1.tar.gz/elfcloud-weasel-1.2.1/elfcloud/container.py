# -*- coding: utf-8 -*-
__license__ = """
Copyright 2010-2012 elfCLOUD / elfcloud.fi – SCIS Secure Cloud Infrastructure Services

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from elfcloud.dataitem import DataItem


class Cluster(object):
    """ Cluster provides methods for handling clusters.

    """
    def __init__(self, client, **kwargs):
        """Initializer for Cluster

        :param client: Client used by Cluster methods.
        :param kwargs: Attributes for the cluster.

        """
        if 'dataitems' in kwargs:
            self._dataitem_count = kwargs.pop('dataitems')
        else:
            self._dataitem_count = 0
        self.__dict__.update(kwargs)
        self._client = client

    def rename(self, new_name):
        """renames cluster using it's own id

        :param new_name: new name for cluster
        """
        method = "rename_cluster"
        params = {
            "cluster_id": self.id,
            'name': new_name
            }
        return self._client.connection.make_request(method, params)

    def remove(self):
        """removes cluster using it's own id"""
        method = "remove_cluster"
        params = {
            "cluster_id": self.id
            }
        make_request = self._client.connection.make_request
        return make_request(method, params)

    @property
    def children(self):
        """Lists child Clusters directly under the cluster.

        Queries the elfcloud.fi server with cluster's own ID and returns a list of child Clusters.

        """
        method = "list_clusters"
        params = {
            "parent_id": self.id
            }
        response = self._client.connection.make_request(method, params)

        clusters = []
        for item in response:
            clusters.append(Cluster(self._client, **item))
        return clusters

    @property
    def dataitems(self):
        """Lists DataItems (dataitems) directly under the cluster.

        Queries the elfcloud.fi server with cluster's own ID and returns a list of DataItems.

        """
        method = "list_dataitems"
        params = {
            "parent_id": self.id
            }
        response = self._client.connection.make_request(method, params)

        data_items = []
        for item in response:
            data_items.append(DataItem(self._client, **item))
        return data_items


class Vault(Cluster):
    """Vault provides methods for handling vaults.

    """
    def __init__(self, client, **kwargs):
        """Vault initializer.

        :param client: Client used by Vault methods.

        """
        Cluster.__init__(self, client, **kwargs)

    def rename(self, new_name):
        """renames cluster using it's own id

        :param new_name: new name for the vault

        """
        method = "rename_vault"
        params = {
            "vault_id": self.id,
            'vault_name': new_name
            }
        return self._client.connection.make_request(method, params)

    def remove(self):
        """Removes vault using it's own ID.

        """
        method = "remove_vault"
        params = {
            "vault_id": self.id
            }
        self._client.connection.make_request(method, params)
        return
