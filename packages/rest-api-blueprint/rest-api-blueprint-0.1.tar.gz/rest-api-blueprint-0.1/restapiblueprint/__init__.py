from flask import Flask
from restapiblueprint.lib import use_pretty_default_error_handlers

app = Flask(__name__)


# Use nice error handlers for all common HTTP codes.
use_pretty_default_error_handlers(app)


# This is the recommended way of packaging a Flask app.
# This seems to be a hack to avoid circulat imports.
# See http://flask.pocoo.org/docs/patterns/packages/
import restapiblueprint.views

# (Keep pyflakes quiet)
restapiblueprint.views
