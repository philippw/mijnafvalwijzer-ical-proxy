Mijnafvalwijzer iCal Proxy
==========================

This is a simple Python project acting as a proxy for Mijnafvalwijzer.
The problem with Mijnafvalwijzer is that they don't provide an easy API which can be used for home automation, or showing the pickup moments in your agenda.
This application parses the Mijnafvalwijzer portal using Beautifulsoup.
The content is then returned as a nice json object containing the next pickup moment,
or as a full iCal file which can be dynamically imported to your agenda.

### Installing
First, install all the dependencies using pip:

    $ pip install -r requirements.txt

Afterwards you can simply start the application using uvicorn:

    $ uvicorn mijnafvalwijzer_ical_proxy:app

By default uvicorn will listen on port 8000, but that can be customized. For more information see `uvicorn --help`.

There are no external dependencies and there is no configuration needed.

### API endpoints
Currently this application exposes 2 API endpoints.

To fetch information about the next pickup moment per waste type call the following endpoint:

    $ curl 'http://localhost:8000/next-pickup/?postal_code=<postal code>&number=<number>&suffix=<optional suffix>&waste_type=<waste type>'

This will return the following json object:

```json
{
    "waste_type": "gft",
    "pickup_date": "2022-09-29",
    "description": "Groente, Fruit en Tuinafval en Etensresten"
}
```
The output of this endpoint could be used as a Json sensor in Home Assistant.

It's also possible to retrieve an iCal file containing the next pickup moments of this year:

    $ curl 'http://localhost:8000/ical/?postal_code=<postal code>&number=<number>&suffix=<optional suffix>'

### Running with Docker

You can also run the service with Docker Compose:

```bash
docker compose up -d
```

### Running Tests

You can run the test suite using Python's built-in `unittest` runner or `pytest`:

```bash
# Using standard library unittest
python -m unittest discover -s tests

# Or using pytest
pytest
```

### Roadmap & Ideas

For future enhancements (including neighbourhood calendar generator UI, caching, filters, and custom alarms), see [business_plan.md](business_plan.md).

### Attribution

This project is based on and extends the original work by Jeffrey Kog: [jeffreykog/mijnafvalwijzer-ical-proxy](https://github.com/jeffreykog/mijnafvalwijzer-ical-proxy).
