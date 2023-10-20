Datadog integration for sqlalchemy's pool
=========================================

Note: this is just un PoC :)

![Datadog screenshot](/images/screenshot.png)

How to run the testapp ?
------------------------
```sh
# set the DD_API_KEY environment variable
docker compose up -d
DD_SERVICE=testapp DD_ENV=local ddtrace-run uvicorn testapp.main:app
```
