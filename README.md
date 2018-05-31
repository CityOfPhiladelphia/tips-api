# tips-api


A RESTful wrapper around the internal TIPS web service for exposing real
estate tax balances to public, client-side web applications.

## Developing locally

### Requirements

- An operating system that supports [Bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell)) (such as macOS or Linux; should work on Windows 10 using the [Linux subsystem](https://docs.microsoft.com/en-us/windows/wsl/install-win10))
- Python 3
- [pipenv](https://docs.pipenv.org/)
- You must be connected to the City network to access TIPS

### Installing

Clone this repo and create a pipenv environment by doing the following:

```bash
git clone https://github.com/CityOfPhiladelphia/tips-api
cd tips-api
pipenv install
```

### Configuring

The application is configured via [environment variables](https://12factor.net/config) defined in `.env` files, located in the `.env` directory at the root of the project. Note that these files are excluded from source control because they may contain sensitive information, such as the internal TIPS endpoint. There are samples provided that you can copy and edit as needed.

To create the necessary `.env` files:

```bash
cd .env
cp dev.env.sample dev.env
# this is optional, if you want to test the production deployment locally
cp prod.env.sample prod.env
```

Now you can edit them in a text editor to fill in the missing values, in particular `TIPS_URL`.


### Running the server

There's a handy `start` script you can use to start the development server:

```bash
./bin/start --dev
```

If you get an error about not having enough permissions, you may need to run:

```bash
chmod u+x ./bin/start.sh
```

If you want to test the production deployment, just remove the `--dev` flag:

```bash
.bin/start
```


### Testing

To try out the API, open your browser and navigate to
`http://127.0.0.1:8000/account/883309050`. You should see the API response for
1234 Market St.

## Deployment

These instructions are for deploying the application to a new EC2 instance running Ubuntu Linux 16.04 (may or may not work for other versions).

### Installing

First, update the `apt` package index and upgrade installed packages:

```bash
sudo apt update
sudo apt upgrade
```

Install Python 3.6, pip, and pipenv:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.6 python3-pip
pip3 install pipenv
```

Clone this repo and set up the pipenv environment:

```bash
git clone https://github.com/CityOfPhiladelphia/tips-api
cd tips-api
pipenv install
```

### Configuring

Create the `prod.env` configuration file and insert necessary values, such as the TIPS URL.

```bash
cd .env
cp prod.env.sample prod.env
nano prod.env
<make necessary changes and save>
cd ..
```

### Running the server


Start Gunicorn with:

```bash
./bin/start
```


## Roadmap

This project began as an AWS Lambda function, which is still mostly intact in `api.py`. It was later wrapped as a Flask/WSGI application and deployed to load-balanced EC2 instances for networking/connectivity reasons. When Lambda becomes a viable deployment option, it should be fairly straightforward to copy `api.py` into a new project and use a framework such as [Serverless](https://serverless.com/) to deploy it along with necessary resources, such as an API gateway.
