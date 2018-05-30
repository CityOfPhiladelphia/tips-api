# tips-api


A lightweight wrapper around the internal TIPS web service for exposing real
estate tax balances to public, client-side web applications.

## Developing locally

### Requirements

- Python 3
- [pipenv](https://docs.pipenv.org/)
- You must be connected to the City network to access TIPS

### Installing

Download the code and install required packages with the following
commands:

```bash
git clone https://github.com/CityOfPhiladelphia/tips-api
cd tips-api
pipenv install
```

### Configuring

The following environment variables are required:

```bash
FLASK_APP=app.py
TIPS_URL=<insert actual TIPS URL here>
```

For a better developer experience:

```bash
FLASK_ENV=development
```

If you're on an environment that supports Bash, there's a script provided
that does all this for you. Just `cp dev_env.sample.sh dev_env.sh`, edit the
file, and insert the actual TIPS web service URL. Then run `. dev_env.sh`.

### Running

Start the pipenv environment with:

```bash
pipenv shell
```

and then:

```bash
flask run
```

### Testing

To try out the API, open your browser and navigate to
`http://127.0.0.1:5000/account/883309050`. You should see the API response for
1234 Market St.

## Deployment

TODO
