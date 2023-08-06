# django-funkymetrics

django-funkymetrics is a super simple Django application for easily tracking events and submit them asynchronously to KISSmetrics using celery tasks.

## Features

* Track app events easily
* Submits analytics events asynchronously to KISSmetrics

## Installation

Add the KISSmetrics JS snippet to your project template(s).

Install `django-funkymetrics`:

    pip install django-funkymetrics

Alternatively, download the source code and manually add it to your `PYTHONPATH`.

Set your KISSmetrics API key:

    KISS_API_KEY = '<your_api_key>'

Track events and profit.

## Prerequisites

The library assumes that Celery is installed and configured for the Django project. Tasks are automatically created for each `record_event`.

## Usage

Simply import `record_event` in your code where you want to track events, and call it as needed:

    from funkymetrics.events import record_event
    
    # Without properties
    record_event('downgraded')
    
    # With properties
    record_event('upgraded plan', {'to_plan': 'Standard'})

## Identifying users

Anonymous users are identified by their KISSmetrics anonymous ID (ie. the value of the `km_ai` cookie).

Authenticated users are identified by their username.

## Future stuff

* Overriding user identifiers
* Queue events locally and submit in batches
