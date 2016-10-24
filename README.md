# Snagsby(py)

Python module implementing snagsby - https://github.com/roverdotcom/snagsby

Snagsby reads configuration from a json object in s3, formats it in a way
that can easily be injected into `os.environ`, and injects the keys and values
into the destination of your choice, `os.environ` being the default.

## Usage

```javascript
// An example configuration file uploaded to S3
// s3://test-bucket/config.json
{
    "will_upcase": "Keys will be upper cased",
    "wil ignore with spaces": "Keys with spaces will be ignored",
    "NUM": 7.777,
    "YES": true,
    "NO": false,
    "NESTED": {
        "OBJECT": "nested"
    }
}
```

Load s3://test-bucket/config.json with snagsby

```python
import os
import pprint

import snagsby

out = {}

os.environ['SNAGSBY_SOURCE'] = "s3://test-bucket/config.json"
# The default dest is os.environ
snagsby.load(dest=out)

pprint.pprint(out)
```

The following is what would be injected into `out`:

```python
{'NO': '0',
 'NUM': '7.777',
 'WILL_UPCASE': 'Keys will be upper cased',
 'YES': '1'}
```

Source is a whitespace separated list of s3 locations

```python
import snagsby
snagsby.load(
  source="s3://bucket/one.json, s3://bucket/two.json",
)
```

By default snagsby loads the source specified in the `SNAGSBY_SOURCE` environment variable into `os.environ`

```python
import os

import snagsby

snagsby.load()

print(os.environ['NUM']) => u'7.777'
```

It's easy to have snagsby inject into locals()

**settings.py**

```python
import snagsby
snagsby.load(dest=locals())

# Values from the snagsby sources were injected into
# local module variables
print(WILL_UPCASE)
```
