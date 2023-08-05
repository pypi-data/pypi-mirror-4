Backplane Client Library for Python
===================================

This library integrates server side Backplane clients with the Backplane server protocol (https://github.com/janrain/janrain-backplane-2).

Installation
============
```shell
pip install backplane2-pyclient
```

Usage
=====

You should have client credentials for a Backplane server, with a bus provisioned for your use. If you have admin access to a backplane server, the following steps will get you set up:

1. Provision a client (/v2/provision/client/update)
2. Provision a bus (/v2/provision/bus/update)
3. Grant client access to bus (/v2/provision/grant/add)

For more information see the [Backplane server readme](https://github.com/janrain/janrain-backplane-2/blob/master/README20.md).

Example:

```python
import backplane
from backplane import ClientCredentials, Client, Message, channel_from_scope

backplane.debug() # Enable debugging output

client_credentials = ClientCredentials('https://backplane1.janrainbackplane.com', 'client id', 'secret')
client = Client(client_credentials, True, 'bus:mybusname')
access_token = client.get_regular_token('mybusname')
channel = channel_from_scope(access_token.scope)
message = Message('mybusname', channel, 'test', 'payload', True)
client.post_message(message)

# Poll server for messages
message_wrapper = None
while True:
    # connect to Backplane server for 20 seconds at a time
    message_wrapper = client.get_messages(message_wrapper, 20)
    ...
```
