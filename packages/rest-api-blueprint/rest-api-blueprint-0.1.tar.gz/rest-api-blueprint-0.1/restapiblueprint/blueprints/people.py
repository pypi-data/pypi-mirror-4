from flask import Blueprint, request
from schema import (Schema, Optional)
from validate_email import validate_email

from restapiblueprint.database import people_database
from restapiblueprint.lib import (
    http_method_dispatcher, make_ok, make_error, check,
    document_using, validate_json, if_content_exists_then_is_json)


blueprint = Blueprint(__name__, __name__)


# Define input schemas.
# See https://github.com/halst/schema
person_full = Schema(
    {
        'email': validate_email,
        'comment': basestring
    }, error='Invalid specification for a person'
)


person_partial = Schema(
    {
        Optional('email'): validate_email,
        Optional('comment'): basestring
    }, error='Invalid partial specification for a person'
)


@blueprint.route('', methods=['GET', 'DELETE'])
@document_using('static/apidocs/people.html')
@check(if_content_exists_then_is_json)
@http_method_dispatcher
class People(object):

    def delete(self):
        people_database.reset()
        return make_ok()


@blueprint.route('/<name>', methods=['GET', 'PATCH', 'POST', 'PUT', 'DELETE'])
@document_using('static/apidocs/people.html')
@check(if_content_exists_then_is_json)
@http_method_dispatcher
class PeopleWithName(object):

    def person_exists(self, name):
        if not people_database.has_person(name):
            return make_error('Person does not exist', 404)

    @check(person_exists)
    def get(self, name):
        email = people_database.get_email_address(name)
        comment = people_database.get_comment(name)
        return make_ok(name=name, email=email, comment=comment)

    @check(person_exists)
    @validate_json(person_full.validate)
    def post(self, name):
        json = request.json
        people_database.set_email_address(name, json['email'])
        people_database.set_comment(name, json['comment'])
        return make_ok()

    @validate_json(person_partial.validate, default=dict)
    def put(self, name):
        json = request.json
        people_database.add_person(name, json.get('email'), json.get('comment'))
        return make_ok()

    @check(person_exists)
    @validate_json(person_partial.validate, default=dict)
    def patch(self, name):
        json = request.json
        if 'email' in json:
            people_database.set_email_address(name, json['email'])
        if 'comment' in json:
            people_database.set_comment(name, json['comment'])
        return make_ok()

    @check(person_exists)
    def delete(self, name):
        people_database.delete_person(name)
        return make_ok()
