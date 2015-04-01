# Google App Engine Discourse API Client

This is a client for interacting with the [Discourse](https://www.discourse.org) API from within a Google
App Engine application. It provides methods for interacting with users, categories, and groups.

## Setup

To setup the API client, you must first have a running instance of Discourse. To see how to do
this, please visit
[this page](https://github.com/discourse/discourse/blob/master/docs/INSTALL-cloud.md). Once this
is set up, you must have an API key. To create one, visit http://discourse.example.com/admin/api,
replacing 'discourse.example.com' with the URL of your Discourse site.

Once this is done, place the following lines of code in your GAE application:

```py
from gae_discourse_client import discourse_client
discourse_client.initClient(discourse_url, api_key, api_username)
```

where `discourse_url` is the URL of your Discourse site, `api_key` is the key from above, and
`api_username` is a username associated with the key.

## Usage

Once the client has been setup, it's ready to use. To call the `getUserByEmail` method from the
users module, for example, use:

```py
user = yield discourse_client.users.getUserByEmail('foo@example.com')
```

## Testing

This package has two sets of tests: local unit tests, and functional tests which test the client
against a test instance of Discourse. Before running tests, `requirements.txt` must be installed
(`pip install -r requirements.txt`). To run the unit tests, run:

```
python setup.py test
```

To run the functional tests, you must first have a running instance of Discourse. The easiest way
to do this is to set it up locally using
[this guide](https://github.com/discourse/discourse/blob/master/docs/VAGRANT.md). Once that's
done, you'll need an API key (which you can create or retrieve the same way as above). Then run:

```
python setup.py test_functional --url 'http://localhost:4000/' --apikey 'abc123'
```

replacing the URL and API key with the appropriate values for your test instance. Note: these
tests will have side effects, so make sure not to run them against a production instance of
Discourse.

## Contributing

Contributions to this project are more than welcome. Please follow the
[Google style guide](https://google-styleguide.googlecode.com/svn/trunk/pyguide.html). We look
forward to seeing your pull requests!

## Author

Thomas Davids (thomas@udacity.com)

## License

Available under the MIT License.
