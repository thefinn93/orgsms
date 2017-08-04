# Org SMS

A tool to allow multiple users read and send texts from a single number.


## Setup

Requires Python 3. Tested on 3.6, 3.4 and 3.5 will probably work. Recommend using a virtualenv, not covered here.

1. Install python dependencies: `pip install -r requirements.txt`
2. Install frontend dependencies: `yarn install` or `npm install`
3. Setup your config, currently at `orgsms/orgsms_config.py`. An example config might look like:

```python
TELI_OUTBOUND_TOKEN = "d9e11eb5-4174-4a2e-83cb-2bff8c69321d"
```

4. `./run.py`
