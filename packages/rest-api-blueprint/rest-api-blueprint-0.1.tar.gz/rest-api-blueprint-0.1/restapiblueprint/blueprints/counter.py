from flask import Blueprint, jsonify
from restapiblueprint.lib import make_ok


blueprint = Blueprint(__name__, __name__)


class Counter:

    value = 0


@blueprint.route('', methods=['GET'])
def counter():
    Counter.value += 1
    return jsonify(value=Counter.value)


@blueprint.route('', methods=['DELETE'])
def reset_counter():
    Counter.value = 0
    return make_ok()
