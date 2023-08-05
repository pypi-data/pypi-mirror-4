# -*- coding: utf-8 -*-
import sys
import os
import argparse
import StringIO
import elfcloud
import codecs
import csv
import urllib2
import urlparse

from elfcloud.exceptions import ClientException
from elfcloud.exceptions import HolviException


def tag_parser(s):
    try:
        tags = s.split(',')
        return tags
    except:
        raise argparse.ArgumentTypeError("Tags must be comma separated list.")


def parse_args(args):
    parser = argparse.ArgumentParser(description='elfCLOUD.fi Weasel', usage="ecw [-u USERNAME] [-p PASSWORD] [-k APIKEY] [-s SERVER] ACTION [options]")
    parser.add_argument('--version', action='version', version='elfCLOUD.fi Weasel 1.1')
    auth_group = parser.add_argument_group('authentication')
    auth_group.add_argument('--user', '-u', action="store", default="", help="username to be used for authentication (or set ECW_USER environment variable)")
    auth_group.add_argument('--password', '-p', action="store", default="", help="password to be used for authentication (or set ECW_PASS environment variable)")
    auth_group.add_argument('--apikey', '-k', action="store", default=elfcloud.utils.APIKEY_DEFAULT, help="client's API-key (defaults to elfCLOUD.fi Weasel default key)")
    auth_group.add_argument('--server', '-s', action="store", default=None, help="server to be used (defaults to elfCLOUD.fi (or holvi.org) server automatically)")

    cmd_parsers = parser.add_subparsers(title='available actions')

    add_vault_parser = cmd_parsers.add_parser('add-vault', help="add a new vault")
    add_vault_parser.add_argument('--name', '-n', required=True, help="Name for the new vault.")
    add_vault_parser.add_argument('--type', '-t', default=elfcloud.utils.VAULT_TYPE_DEFAULT, help="Type for the new vault. Vault type defaults to fi.elfcloud.datastore. Default API key allows use of fi.elfcloud.datastore and fi.elfcloud.backup vault types.")
    add_vault_parser.set_defaults(func=add_vault)

    list_vaults_parser = cmd_parsers.add_parser('list-vaults', help="list vaults")
    list_vaults_parser.add_argument('--role', '-r', choices=('account', 'own', 'other'), help='relationship to vault: own / account / other')
    list_vaults_parser.add_argument('--id', '-id', help="id of the searched vault")
    list_vaults_parser.add_argument('--type', '-t', help="application type of the searched vault")
    list_vaults_parser.set_defaults(func=list_vaults)

    rename_vault_parser = cmd_parsers.add_parser('rename-vault', help="rename vault")
    rename_vault_parser.add_argument('--id', '-id', required=True, help="id of the vault")
    rename_vault_parser.add_argument('--new-name', '-nn', required=True, help="new name for the vault")
    rename_vault_parser.set_defaults(func=rename_vault)

    remove_vault_parser = cmd_parsers.add_parser('remove-vault', help="remove vault")
    remove_vault_parser.add_argument('--id', '-id', required=True, help="id of the vault")
    remove_vault_parser.set_defaults(func=remove_vault)

    add_cluster_parser = cmd_parsers.add_parser('add-cluster', help="add a new cluster")
    add_cluster_parser.add_argument('--name', '-n', required=True, help="name for the new cluster")
    add_cluster_parser.add_argument('--id', '-id', required=True, help="parent id for the new cluster")
    add_cluster_parser.set_defaults(func=add_cluster)

    list_clusters_parser = cmd_parsers.add_parser('list-clusters', help="list clusters")
    list_clusters_parser.add_argument('--id', '-id', required=True, help="parent id")  # Help message?
    list_clusters_parser.set_defaults(func=list_clusters)

    rename_cluster_parser = cmd_parsers.add_parser('rename-cluster', help="rename cluster")
    rename_cluster_parser.add_argument('--id', '-id', required=True, help="id of the cluster")
    rename_cluster_parser.add_argument('--new-name', '-nn', required=True, help="new name for the cluster")
    rename_cluster_parser.set_defaults(func=rename_cluster)

    remove_cluster_parser = cmd_parsers.add_parser('remove-cluster', help="remove cluster")
    remove_cluster_parser.add_argument('--id', '-id', required=True, help="id of the cluster")
    remove_cluster_parser.add_argument('--name', '-n', help="name of the cluster")
    remove_cluster_parser.set_defaults(func=remove_cluster)

    list_dataitems_parser = cmd_parsers.add_parser('list-dataitems', help="list data items")
    list_dataitems_parser.add_argument('--id', '-id', required=True, help="identifier of the parent vault or cluster")
    list_dataitems_parser.set_defaults(func=list_dataitems)

    rename_dataitem_parser = cmd_parsers.add_parser('rename-dataitem', help='rename data item')
    rename_dataitem_parser.add_argument('--id', '-id', required=True, help="parent id")
    rename_dataitem_parser.add_argument('--name', '-n', required=True, help="name of the data item")
    rename_dataitem_parser.add_argument('--new-name', '-nn', required=True, help="new name for the data item")
    rename_dataitem_parser.set_defaults(func=rename_dataitem)

    relocate_dataitem_parser = cmd_parsers.add_parser('relocate-dataitem', help='relocate data item')
    relocate_dataitem_parser.add_argument('--id', '-id', required=True, help="parent id")
    relocate_dataitem_parser.add_argument('--name', '-n', required=True, help="name of the data item")
    relocate_dataitem_parser.add_argument('--new-id', '-nid', required=True, help="new parent id")
    relocate_dataitem_parser.add_argument('--new-name', '-nn', required=True, help="new name for the data item")
    relocate_dataitem_parser.set_defaults(func=relocate_dataitem)

    remove_dataitem_parser = cmd_parsers.add_parser('remove-dataitem', help="remove data item")
    remove_dataitem_parser.add_argument('--id', '-id', required=True, help="parent id")
    remove_dataitem_parser.add_argument('--name', '-n', required=True, help="name of the data item")
    remove_dataitem_parser.set_defaults(func=remove_dataitem)

    list_contents_parser = cmd_parsers.add_parser('list-contents', help="list data items and clusters")
    list_contents_parser.add_argument('--id', '-id', required=True, help="parent id")
    list_contents_parser.set_defaults(func=list_contents)

    subscription_info_parser = cmd_parsers.add_parser('subscription-info', help="subscription info")
    subscription_info_parser.set_defaults(func=subscription_info)

    def fetch_and_store_options(parser):
        parser.add_argument('--id', '-id', required=True, help="identifier of the parent vault or cluster")
        parser.add_argument('--name', '-n', required=True, help="data item name")
        parser.add_argument('--description', '-d', default=None, help="description for data item")
        parser.add_argument('--tags', '-t', default=None, type=tag_parser, help="tags for data item")

        encryption_group = parser.add_mutually_exclusive_group(required=True)
        encryption_group.add_argument('--no-encryption', '-nocrypt', action="store_true", default=False, help="disable encryption")

        crypt_enabled = encryption_group.add_mutually_exclusive_group()
        crypt_enabled.add_argument('--keyfile', '-kf', type=argparse.FileType('rb'), default=None, help="path to key file.")
        crypt_enabled.add_argument('--separate-key-files', '-skf', action="store_true", default=None)

        separated_files = crypt_enabled.add_argument_group()
        separated_files.add_argument('--cryptkey', '-ck', type=argparse.FileType('rb'), help="path to cipher key file (filesize of 32 bytes required for AES256)")
        separated_files.add_argument('--initvector', '-iv', type=argparse.FileType('rb'), default=None, help="path to initialization vector file (filesize of 16 bytes required for AES256), IV defaults to a value of 0x31323334353637383930313233343536.")

    store_data_parser = cmd_parsers.add_parser('store', help="store data item")
    store_data_parser.add_argument('--file', '-f', '-i', type=argparse.FileType('rb'), help="file containing the data to be stored")
    store_data_parser.add_argument('--method', '-m', choices=('new', 'replace', 'append', 'patch'), default='new', help="storing method")
    store_data_parser.add_argument('--offset', type=int, help="byte offset")
    fetch_and_store_options(store_data_parser)
    store_data_parser.set_defaults(func=store_data)

    fetch_data_parser = cmd_parsers.add_parser('fetch', help='fetch data item')
    fetch_data_parser.add_argument('--file', '-f', '-o', help="file to write the retrieved data into")
    fetch_data_parser.add_argument('--overwrite', '-ow', action="store_true", default=False, help="overwrite if file already exists")
    fetch_data_parser.add_argument('--info', '-i', action="store_true", default=False, help="retrieve data item information only")
    fetch_and_store_options(fetch_data_parser)
    fetch_data_parser.set_defaults(func=fetch_data)

    update_dataitem_parser = cmd_parsers.add_parser('update-dataitem', help='update data item')
    update_dataitem_parser.add_argument('--id', '-id', required=True, help="parent id")
    update_dataitem_parser.add_argument('--name', '-n', required=True, help="name of the data item")
    update_dataitem_parser.add_argument('--description', help="new description")
    update_dataitem_parser.add_argument('--tags', help="comma separated list of tags")
    update_dataitem_parser.set_defaults(func=update_dataitem)

    param_group = parser.add_argument_group('parameters')
    param_group.add_argument('--verbose', '-v', action="store_true", default=False, help="enable progress printing")

    return parser.parse_args(), parser


def call_client_func(user, password, apikey, server_url, func, args):
    client = elfcloud.Client(username=user, auth_data=password, apikey=apikey, server_url=server_url)
    func(args, client)


def main(argv=sys.argv):
    args, parser = parse_args(argv)
    user = os.environ.get("ECW_USER")
    password = os.environ.get("ECW_PASS")

    if args.user:
        user = args.user
    if args.password:
        password = args.password
    if not user or not password:
        parser.print_help()
        sys.exit(-1)

    if args.func == update_dataitem:
        if args.tags is None and args.description is None:
            parser.error("at least one of --tags and --description required")

    if args.server is None:
        if args.verbose:
            print >> sys.stderr, "Selecting server automatically..."

        req = urllib2.Request("http://elfcloud.fi/api.url")
        resp = urllib2.urlopen(req, timeout=10)

        parsed_url = urlparse.urlparse(resp.readline().strip())

        if parsed_url.hostname not in ['my.holvi.org', 'api.elfcloud.fi', 'my.elfcloud.fi']:
            raise Exception("Invalid hostname.")

        if parsed_url.scheme != 'https':
            raise Exception("Invalid scheme.")

        args.server = parsed_url.geturl()

        if args.verbose:
            print >> sys.stderr, "Selected server:", repr(args.server)

    if args.server is None:
        raise Exception("No server provided, use --server/-s to provide valid API URL.")

    try:
        call_client_func(user, password, args.apikey, args.server, args.func, args)
    except HolviException as e:
        print >> sys.stderr, e
        sys.exit(-1)
    except UnicodeError as e:
        print >> sys.stderr, e
        sys.exit(-1)
    except ClientException as e:
        print >> sys.stderr, e
        sys.exit(-1)
    except urllib2.URLError as e:
        if hasattr(e, 'reason'):
            print >> sys.stderr, e.reason
        elif hasattr(e, 'code'):
            print >> sys.stderr, e.code, e.msg
        sys.exit(-1)
    except IOError as e:
        print >> sys.stderr, e.strerror
        sys.exit(-1)


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    def write_cluster(self, cluster):
        self.writerow([
            cluster.__class__.__name__,
            str(cluster.id),
            cluster.name,
            str(cluster.last_accessed_date),
            str(cluster.modified_date),
            ','.join(cluster.permissions),
            str(cluster.parent_id),
            str(cluster.descendants),
            str(cluster._dataitem_count),
        ])

    def write_clusters(self, clusters):
        for cluster in clusters:
            self.write_cluster(cluster)

    def write_vault(self, vault):
        self.writerow([
            vault.__class__.__name__,
            str(vault.id),
            vault.name,
            str(vault.last_accessed_date),
            str(vault.modified_date),
            ','.join(vault.permissions),
            str(vault.vault_type),
            str(vault.descendants),
            str(vault._dataitem_count),
        ])

    def write_vaults(self, vaults):
        for vault in vaults:
            self.write_vault(vault)

    def write_dataitem(self, dataitem):
        tags = dataitem.tags
        if tags is None:
            tags = []

        self.writerow([
            dataitem.__class__.__name__,
            str(dataitem.parent_id),
            dataitem.name,
            str(dataitem.size),
            str(dataitem.last_accessed_date),
            str(dataitem.modified_date),
            str(dataitem.md5sum),
            str(dataitem.description),
            str(','.join(tags)),
            dataitem.meta.get("ENC", ''),
            str(dataitem.key_hash),
            str(dataitem.content_hash),
        ])

    def write_dataitems(self, dataitems):
        for dataitem in dataitems:
            self.write_dataitem(dataitem)


def add_vault(args, client):
    vault = client.add_vault(name=args.name, vault_type=args.type)
    writer = UnicodeWriter(sys.stdout)
    writer.write_vault(vault)


def list_vaults(args, client):
    vaults = client.list_vaults(vault_type=args.type, id_=args.id, role=args.role)
    writer = UnicodeWriter(sys.stdout)
    writer.write_vaults(vaults)


def rename_vault(args, client):
    client.rename_vault(vault_id=args.id, new_name=args.new_name)


def remove_vault(args, client):
    client.remove_vault(vault_id=args.id)


def add_cluster(args, client):
    cluster = client.add_cluster(name=args.name, parent_id=args.id)
    writer = UnicodeWriter(sys.stdout)
    writer.write_cluster(cluster)


def list_clusters(args, client):
    clusters = client.list_clusters(parent_id=args.id)
    writer = UnicodeWriter(sys.stdout)
    writer.write_clusters(clusters)


def rename_cluster(args, client):
    client.rename_cluster(cluster_id=args.id, new_name=args.new_name)


def remove_cluster(args, client):
    if not args.name:
        client.remove_cluster(cluster_id=args.id)
    else:
        clusters = client.list_clusters(parent_id=args.id)
        for cluster in clusters:
            if cluster.name == args.name:
                cluster.remove()
                break


def remove_dataitem(args, client):
    client.remove_dataitem(parent_id=args.id, key=args.name)


def rename_dataitem(args, client):
    client.rename_dataitem(parent_id=args.id, name=args.name, new_name=args.new_name)


def relocate_dataitem(args, client):
    client.relocate_dataitem(parent_id=args.id, name=args.name,
                             new_id=args.new_id, new_name=args.new_name)


def list_dataitems(args, client):
    dataitems = client.list_dataitems(parent_id=args.id)
    writer = UnicodeWriter(sys.stdout)
    writer.write_dataitems(dataitems)


def _set_encryption(args, client):
    if not args.no_encryption:
        if args.keyfile:
            iv, cryptkey = elfcloud.utils.KeyFile.parse_from_file(args.keyfile)
            if len(cryptkey) == 16:
                enc_mode = elfcloud.utils.ENC_AES128
            elif len(cryptkey) == 24:
                enc_mode = elfcloud.utils.ENC_AES192
            elif len(cryptkey) == 32:
                enc_mode = elfcloud.utils.ENC_AES256
        else:
            cryptkey = bytearray(args.cryptkey.read())
            if args.initvector:
                iv = args.initvector.read()
            else:
                iv = elfcloud.utils.IV_DEFAULT
            enc_mode = elfcloud.utils.ENC_AES256
    else:
        cryptkey = None
        iv = elfcloud.utils.IV_DEFAULT
        enc_mode = elfcloud.utils.ENC_NONE

    client.set_encryption_key(cryptkey)
    client.set_iv(iv)
    client.encryption_mode = enc_mode


def store_data(args, client):
    _set_encryption(args, client)

    data = None
    if args.file:
        data = args.file
    else:
        data = sys.stdin
    if args.verbose:
        print >> sys.stdout, "Sending data"

    client.store_data(parent_id=args.id,
                      key=args.name,
                      method=args.method,
                      p_data=data,
                      offset=args.offset,
                      description=args.description,
                      tags=args.tags)
    if args.verbose:
        print >> sys.stdout, 'OK'
    data.close()


def fetch_data(args, client):
    _set_encryption(args, client)

    data = None
    response = None
    if args.verbose:
        print >> sys.stderr, "Fetching data"
    if not args.info:
        response = client.fetch_data(parent_id=args.id, key=args.name)
    else:
        dataitem = client.get_dataitem(parent_id=args.id, key=args.name)

        writer = UnicodeWriter(sys.stdout)
        writer.write_dataitem(dataitem)

    if response:
        if args.file:
            if os.path.isfile(args.file) and not args.overwrite:
                raise ClientException("File already exists")
            output_file = open(args.file, 'wb')
            for data in response['data']:
                output_file.write(data)
            output_file.close()
        else:
            for data in response['data']:
                sys.stdout.write(data)
        if args.verbose:
            if response['checksum'] == response['data']._md5.hexdigest():
                print >> sys.stderr, "OK"
            else:
                print >> sys.stderr, "Checksums mismatched"


def subscription_formater(writer, d, indent=0):
    for key, value in d.iteritems():
        content = ['' for x in range(indent)]
        content.append(str(key))

        if isinstance(value, dict):
            writer.writerow(content)
            subscription_formater(writer, value, indent + 1)
        else:
            content.append(str(value))
            writer.writerow(content)


def subscription_info(args, client):
    info = client.get_subscription_info()
    writer = UnicodeWriter(sys.stdout)
    subscription_formater(writer, info)


def list_contents(args, client):
    clusters, dataitems = client.list_contents(parent_id=args.id)
    writer = UnicodeWriter(sys.stdout)
    writer.write_clusters(clusters)
    writer.write_dataitems(dataitems)


def update_dataitem(args, client):
    client.update_dataitem(parent_id=args.id, name=args.name,
                           tags=tuple(args.tags.split(",")), description=args.description)


if __name__ == '__main__':
    main()
