# Bomberman

This is a Python client for the Bomberman HTTP API. It has been built
and tested against Python 2.6.1.

[Bomberman](http://addons.heroku.com/bomberman): shelter from profanity bombing, is an [add-on](http://addons.heroku.com) for Heroku
applications. If you would like to be part of the alpha or early beta
testing process please email <bomberman-support@ikayzo.com>.

For detailed instructions on installing the addon to your Heroku
application please see our [add-on documentation page](http://bomberman.ikayzo.com/)

## Installation

Install the Python client using pip.

```term
$ pip install bomberman-python
```

Before making client requests, make sure your environment contains your API key. If you're using Heroku or Foreman, this should already be set for you.

```term
$ export BOMBERMAN_API_KEY=<your api key>
```

Once that is done, create the client in your Python code.
```python
from bomberman.client import Client

bomberman = Client()
```

### Checking if Text Contains Profanity

To check if a piece of text or *corpus* contains profanity use the
`.is_profane(corpus)` method.  This will return a boolean value as the
result

```python
non_profane_text = "The quick brown fox jumped over the lazy dog."
bomberman.is_profane(non_profane_text)
  #=> False
profane_text = "The quick brown fox jumped over the F-BOMBing lazy dog."
bomberman.is_profane(profane_text)
  #=> True
```

### Censoring Profane Words & Phrases

If you would like to save or display text where the profane words (if
any) are censored, use the `.censor(corpus, replacement_text)` method.

```python
non_profane_text = "The quick brown fox jumped over the lazy dog."
bomberman.censor(non_profane_text, "####")
  #=> "The quick brown fox jumped over the lazy dog."
profane_text = "The quick brown fox jumped over the F-BOMBing lazy dog."
bomberman.censor(profane_text, "####")
  #=> "The quick brown fox jumped over the ### lazy dog."
```

The `replacement_text` parameter is a string and optional. `"***"` is
suppled by default.

### Highlighting Profane Words & Phrases

Sometimes it is useful to leave the original profane word/phrase intact
but wrap it in some sort of tag to make it stand out. This can be
accomplished with the `.highlight(corpus, start_tag, end_tag)` method.

```python
non_profane_text = "The quick brown fox jumped over the lazy dog."
bomberman.highlight(non_profane_text, "<blink>", "</blink>")
  #=> "The quick brown fox jumped over the lazy dog."
profane_text = "The quick brown fox jumped over the F-BOMBing lazy dog."
bomberman.highlight(profane_text, "<blink>", "</blink>")
  #=> "The quick brown fox jumped over the <blink>F-BOMBing</blink> lazy dog."
```

The `start_tag` & `end_tag` parameters are strings and optional. A pair
of opening and closing `<strong>` tags are used if none are provided.

For more info on customizing Bomberman please refer to the [add-on documentation](http://bomberman.ikayzo.com/).

## Troubleshooting

We are just starting out.  If you experience trouble please contact us
at <bomberman-support@ikayzo.com>.

## Contributing

Given the early stage of this project we are open to comments &
suggestions for this library please send them to <bomberman-support@ikayzo.com>.