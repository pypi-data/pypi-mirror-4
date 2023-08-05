.. highlight:: rst

******************************************************
Installation and usage
******************************************************

This document will briefly demonstrate you how to use elfCLOUD.fi Weasel. The Python client distribution includes both a Python Client Library which you can integrate into your own applications, and a standalone command line utility for performing stdin/stdout and file based vault operations. The CLI utility is ideal for power users and script automation tasks.

Before you install
==================

To install and use elfCLOUD.fi Weasel you will need `Python <http://www.python.org/>`_ version 2.7.
Client library is developed and tested using version 2.7.2.

Installation
============

To use elfCLOUD.fi Weasel you first need to download and install it. The installation will also include the ecw command line utility for managing vaults and data items.

Installing package::

    easy_install elfcloud-weasel

To check your installation has completed succcesfully::

    python
    Python 2.7.2 (default, Jun 12 2011, 15:08:59) [MSC v.1500 32 bit (Intel)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >> import elfcloud

If you can import elfcloud without errors your installation has completed succesfully.

Using Command-line interface client (CLI Client)
================================================

This section will briefly demonstrate basic usage of CLI Client.

Once you have installed elfCLOUD.fi Weasel you can use the client by typing::

    ecw

To get help using CLI Client, you can always use -h / --help argument:

.. command-output:: ecw --help

You can also get help for any available action, example for list-vaults:

.. command-output:: ecw list-vaults --help

Authentication
--------------

Using elfCLOUD.fi Weasel requires you to provide at least authentication credentials and action as command line parameters.
Information needed to use the Client are following:

* ``--username / -u`` *\* (Required)*
    *Your username to elfCLOUD.fi service. Alternatively you can set ECW_USER environment variable to be used as a default value.*
* ``--password / -p`` *\* (Required)*
    *Your account password to elfCLOUD.fi service. Alternatively you can set ECW_PASS environment variable to be used as a default value.*

Optional arguments, mostly for client developers or library users:

* ``--apikey / -k``
    *API-key to elfCLOUD.fi service. You can check your API-keys from My elfCLOUD.fi user profile page. The CLI client defaults to a standard CLI Client API key value.*

Username and password can be also supplied with enviroment variables:

 .. code-block:: bash

    export ECW_USER=elfcloud_user
    export ECW_PASS=elfcloud_password

Example usage
--------------

.. code-block:: bash

    # In these examples, the username and password are set as environment variables
    export ECW_USER=elfcloud_user
    export ECW_PASS=elfcloud_password

    # Add vault with custom type and apikey
    ecw --apikey abc add-vault --name My new vault --type my_application_type

    # Remove vault by id
    ecw remove-vault -id 35

    # Renaming vault, --new-name or -nn for new vault name
    ecw rename-vault -id 35 --new-name def

    # List all vaults, filter it by id, type or role (own, account or other)
    ecw list-vaults
    ecw list-vaults --id 35
    ecw list-vaults --type my_application_type
    ecw list-vaults --role own

    # Add new cluster, --id for parent id (cluster id or parent id)
    ecw add-cluster -id 35 -n "New cluster"

    # Remove cluster by id
    ecw remove-cluster -id 36

    # Rename cluster by id
    ecw rename-cluster -n New cluster -id 35

    # List all clusters
    ecw list-clusters --id 35

    # List all dataitems
    ecw list-dataitems --id 35

    # Remove dataitem, parent id and name of dataitem
    ecw remove-dataitem -id 35 -n my_text_file.txt


Storing data
^^^^^^^^^^^^^^^^^^^^^^^^^^

Required parameters:

* ``--id / -id`` *\* (Required)*
    *Parent ID of data item.*
* ``--name / -n`` *\* (Required)*
    *Name of the data item.*
* ``--method / -m``
    *Method used for storing ('new', 'replace', 'append', 'patch') Default: 'new'.*
* ``--file / -f / -i``
    *Input file to be used for storing.*
* ``--offset``
    *If using method 'patch', starting byte for storing.*
* ``--description / -d``
    *Overwrites dataitem description.*
* ``--tags / -t``
    *Overwrites dataitem tags. Must be comma separated list of tags.*

Encryption mode must be set with one of following argument:

* ``--no-encryption / -nocrypt``
    *For plaintext storing of data items, use the --no-encryption parameter.*
* ``--keyfile / -kf FILE``
    *Filepath, containing IV+KEY, 16 bytes of initialization vector and 16, 24, or 32 bytes long encryption key.*
* ``--separate-key-files / -skf``
    *When IV and KEY are in differend files. You must also speficy key with --cryptkey parameter and optionally initialization vector with --initvector parameter.*

If using separated key files with --separete-key-files argument, then the cryptkey file must be specified with --cryptkey argument:

* ``--cryptkey / -ck FILE``
    *File containing 32 bytes long encryption key.*
* ``--initvector / -iv FILE``
    *Optional initialization vector for the AES cipher (file of exactly 16 bytes). Defaults to '1234567890123456'.*

Example usage:

.. code-block:: bash

    # Plaintext store
    ecw store -id 35 -n my_text_file.txt --file C:\my_text_file.txt --no-encryption

    # Plaintext store, replaces if data item already exists
    ecw store -id 35 -n my_text_file.txt --file C:\my_text_file.txt --no-encryption --method replace

    # Encrypted store
    ecw store -id 35 -n my_text_file.txt --file C:\my_text_file.txt --keyfile C:\my_cryptkey_file

    # If you have key and initialization vector in differend files,
    # then use --separate-key-files and provide path to keyfile with --cryptkey and optionally initialization --iv
    ecw store -id 35 -n my_text_file.txt --file C:\my_text_file.txt --separate-key-files --cryptfile C:\my_cryptkey_file --method replace

    # elfCLOUD.fi Weasel supports input from STDIN
    echo "Hello elfCLOUD\!" | ecw store -id 35 -n stdin_test --no-encryption

    # Same in Windows command prompt
    ECHO sample input| ecw store -id 35 -n echo_input.txt --no-encryption

Fetching data
^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``--id / -id`` *\* (Required)*
    *Parent ID of data item.*
* ``--name / -n`` *\* (Required)*
    *Name of the data item.*
* ``--file / -f / -o``
    *Output file to be used for writing retrieved data.*
* ``--info / -i``
    *Retrieve only data item information (content length, checksum, etc.)*
* ``--overwrite / -ow``
    *Allow overwriting existing target file during the fetch operation*

Encryption mode must be set with one of following argument:

* ``--no-encryption / -nocrypt``
    *For plaintext storing of data items, use the --no-encryption parameter. Either --cryptkey or -no-encryption is required to be present.*
* ``--keyfile / -kf FILE``
    *Filepath, containing IV+KEY, 16 bytes of initialization vector and 16, 24, or 32 bytes long encryption key.*
* ``--separate-key-files / -skf``
    *When IV and KEY are in differend files. You must also speficy key with --cryptkey parameter and optionally initialization vector with --initvector parameter.*

If using separated key files with --separete-key-files argument, then the cryptkey file must be specified with --cryptkey argument:

* ``--cryptkey / -ck FILE``
    *File containing 32 bytes long encryption key.*
* ``--initvector / -iv FILE``
    *Optional initialization vector for the AES cipher (file of exactly 16 bytes). Defaults to '1234567890123456'.*

Example usage:

.. code-block:: bash

    # Output to STDOUT
    ecw fetch -id 35 -n my_text_file.txt --no-encryption

    # Output to file specified with --file parameter
    ecw fetch -id 35 -n my_text_file.txt --no-encryption --file "C:\my_text_file_output.txt"

    # Output to file by redirecting the STDOUT to file
    ecw fetch -id 35 -n my_text_file.txt --no-encryption > my_txt_file_output.txt

    # Fetching file when encryption is enabled
    ecw fetch -id 35 -n my_encrypted_text.txt -keyfile "C:\my_cryptkey_file" > my_decrypted_text.txt

Including elfCLOUD.fi Weasel in your project
================================================
You can use elfCLOUD.fi Weasel directly from the command line or create your own client application by including elfCLOUD.fi Weasel Library to your project.

elfCLOUD.fi Weasel Library can be used in your own projects by simply importing it:

.. code-block:: python

    >>> import elfcloud
    >>> client = elfcloud.Client(username="username", auth_data="password", apikey="apikey")

Add vault
----------
Vaults can be added by providing type and name for vault:

.. code-block:: python

    >>> vault = client.add_vault(vault_type="org.holvi.datastore", name="New vault")
    >>> vault.id
    1

Add cluster
------------
Clusters can be added by providing name and parent ID:

.. code-block:: python

    >>> cluster = client.add_cluster(name="New cluster", parent_id=2)
    >>> cluster.id
    2

Store / Fetch data
------------------------------
Data can be stored / fetched by providing the ID of the Vault or Cluster where dataitem is located and the name of the dataitem.
Data itself needs to be `File-like objects <http://docs.python.org/library/stdtypes.html#file-objects>`_

Storing and fetching data:

.. code-block:: python

    >>> import StringIO

    >>> client.store_data(parent_id = 1, key = "dataitem_name", p_data = StringIO.StringIO('Example data'))
    >>> dataitem = client.get_dataitem(parent_id=1, key="dataitem_name")
    >>> dataitem.raw_meta
    'v1:ENC:NONE::'
    >>> dataitem.data
    {'checksum': 'c13b2bc2027489c3398a3113f47c800a', 'data': <elfcloud.filecrypt.FileIterator object at ...>}

    >>> response = client.fetch_data(parent_id = 1, key = "dataitem_name")
    >>> print response
    {'checksum': 'c13b2bc2027489c3398a3113f47c800a', 'data': <elfcloud.filecrypt.FileIterator object at ...>}
    >>> for data in response['data']:
    ...     print data
    Example data
    >>> response['data']._md5.hexdigest()
    'c13b2bc2027489c3398a3113f47c800a'

Encryption enabled storing and fetching data:

.. code-block:: python

    >>> from elfcloud.utils import ENC_AES256

    >>> client.set_encryption_key('12345678901234567890123456789012')
    >>> client.encryption_mode = ENC_AES256
    >>> client.store_data(parent_id = 1, key = "dataitem_name", p_data = StringIO.StringIO('Example data'), method='replace')

    >>> dataitem = client.get_dataitem(parent_id=1, key="dataitem_name")
    >>> dataitem.raw_meta
    'v1:ENC:AES256'
    >>> dataitem.data
    {'checksum': '84b38ae24dd7386227f636b5111434e2', 'data': <elfcloud.filecrypt.CryptIterator object at ...>}
    >>> response = client.fetch_data(parent_id = 1, key = "dataitem_name")
    >>> print response
    {'checksum': '84b38ae24dd7386227f636b5111434e2', 'data': <elfcloud.filecrypt.CryptIterator object at ...>}
    >>> for data in response['data']:
    ...     print data
    Example data
    >>> response['data']._md5.hexdigest()
    '84b38ae24dd7386227f636b5111434e2'

Removing cluster
------------------------------
Cluster can be removed by providing ID of the cluster:

.. code-block:: python

    >>> client.remove_cluster(cluster_id=2)

    # or

    >>> cluster = Cluster(client, id=2)
    >>> cluster.remove()

Removing vault
--------------------
Vault can be removed by providing ID of the vault (but be careful):

.. code-block:: python

    >>> client.remove_vault(vault_id=1)

    # or

    >>> vault = Vault(client, id=10)
    >>> vault.remove()

Removing dataitem
------------------------------
Dataitem can be removed by providing ID:

.. code-block:: python

    >>> client.remove_dataitem(parent_id=1, key="dataitem_name")

    # or

    >>> dataitem = DataItem(client, parent_id=1, name="dataitem_name")
    >>> dataitem.remove()

Listing dataitems, clusters and vaults
--------------------------------------------------
Vault can be listed without any parameters. Possible parameters are *vault_type*, *id_*, and *role*. These are used for filtering vaults:

.. code-block:: python

    >>> vaults = client.list_vaults()
    [<elfcloud.container.Vault object at ...>]

Listing clusters needs parent ID as parameter:

.. code-block:: python

    >>> clusters = client.list_clusters(parent_id=1)
    [<elfcloud.container.Cluster object at ...>]

Listing dataitems needs parent ID as parameter:

.. code-block:: python

    >>> dataitems = client.list_dataitems(parent_id=1)
    [<elfcloud.dataitem.DataItem object at ...>]

Listing dataitems and clusters needs also parent ID as parameter:

.. code-block:: python

    >>> clusters, dataitems = client.list_contents(parent_id=1)
    ([<elfcloud.container.Cluster object at ...>, ...],
     [<elfcloud.dataitem.DataItem object at ...>, ...])

More information
----------------------------------------
For more details about Client API please refer to :doc:`library`
