from restapiblueprint import app
from restapiblueprint.blueprints import people, counter, private

# Attach blueprints.
app.register_blueprint(people.blueprint, url_prefix='/v1/people')
app.register_blueprint(counter.blueprint, url_prefix='/v1/counter')
app.register_blueprint(private.blueprint, url_prefix='/v1/private')
