# Teeskins discord bot

#### How to install dependencies ?

```bash
bash install.sh
```

#### Environment

Copy `config_example.ini` to `config.ini` and replace values 

#### Docker

```bash
docker build -t teeskins .
docker run -it -v $PWD/public:/app/public teeskins
```