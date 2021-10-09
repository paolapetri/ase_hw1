from werkzeug.exceptions import MethodNotAllowed
from flakon import JsonBlueprint
from flask import abort, jsonify, request

from bedrock_a_party.classes.party import CannotPartyAloneError, FoodList, ItemAlreadyInsertedByUser, NotExistingFoodError, NotInvitedGuestError, Party

parties = JsonBlueprint('parties', __name__)

_LOADED_PARTIES = {}  # dict of available parties
_PARTY_NUMBER = 0  # index of the last created party


# TODO: complete the decoration
@parties.route("/parties", methods = ['POST', 'GET'])
def all_parties():
    result = None
    if request.method == 'POST':
        try:
            response = create_party(request)
            result = response
            # TODO: create a party
        except CannotPartyAloneError:
            abort(400, 'Cannot party alone!') 
            # TODO: return 400

    elif request.method == 'GET':
        response = get_all_parties()
        result = response
        # TODO: get all the parties

    return result


# TODO: complete the decoration
@parties.route("/parties/loaded")
def loaded_parties():
    result = None
    num_parties = len(_LOADED_PARTIES)
    return jsonify({'loaded_parties': num_parties})
    # TODO: returns the number of parties currently loaded in the system


# TODO: complete the decoration
@parties.route("/party/<id>", methods = ['GET', 'DELETE'])
def single_party(id):
    global _LOADED_PARTIES
    result = ""
    exists_party(id)
    
    # TODO: check if the party is an existing one
    if 'GET' == request.method:
        result =  _LOADED_PARTIES[id].serialize()
        #result =  _LOADED_PARTIES.get(id).serialize()
        return result
        # TODO: retrieve a party

    elif 'DELETE' == request.method:
        _LOADED_PARTIES.pop(id)
        # TODO: delete a party

    return result
    

# TODO: complete the decoration
@parties.route("/party/<id>/foodlist")
def get_foodlist(id):
    global _LOADED_PARTIES
    result = ""

    # TODO: check if the party is an existing one
    exists_party(id)
    if 'GET' == request.method:
        # TODO: retrieve food-list of the party
        party =  _LOADED_PARTIES.get(id).serialize()
        result = party.get("foodlist")
        return jsonify({'foodlist' : result})
    return result


# TODO: complete the decoration
@parties.route("/party/<id>/foodlist/<user>/<item>", methods = ['POST', 'DELETE'])
def edit_foodlist(id, user, item):
    global _LOADED_PARTIES
    # TODO: check if the party is an existing one
    # TODO: retrieve the party
    result = ""
    exists_party(id)
    if 'POST' == request.method:
        # TODO: add item to food-list handling NotInvitedGuestError (401) and ItemAlreadyInsertedByUser (400)
        try:
            food = _LOADED_PARTIES[id].add_to_food_list(item, user)
            result = {'food' : food.food, 'user' : food.user}
        except NotInvitedGuestError:
            abort(401, 'The user is not invited') 

        except ItemAlreadyInsertedByUser:
            abort(400, 'This item is already in the foodlist')

    if 'DELETE' == request.method:
        try:
            _LOADED_PARTIES[id].remove_from_food_list(item, user)
            result = {'msg':"Food deleted!"}
        except NotExistingFoodError:
            abort(400, 'This item is not in the foodlist')
        # TODO: delete item to food-list handling NotExistingFoodError (400)

    return result

#
# These are utility functions. Use them, DON'T CHANGE THEM!!
#

def create_party(req):
    global _LOADED_PARTIES, _PARTY_NUMBER

    # get data from request
    json_data = req.get_json()

    # list of guests
    try:
        guests = json_data['guests']
    except:
        raise CannotPartyAloneError("you cannot party alone!")

    # add party to the loaded parties lists
    _LOADED_PARTIES[str(_PARTY_NUMBER)] = Party(_PARTY_NUMBER, guests)
    _PARTY_NUMBER += 1

    return jsonify({'party_number': _PARTY_NUMBER - 1})

def get_all_parties():
    global _LOADED_PARTIES

    return jsonify(loaded_parties=[party.serialize() for party in _LOADED_PARTIES.values()])


def exists_party(_id):
    global _PARTY_NUMBER
    global _LOADED_PARTIES

    if int(_id) > _PARTY_NUMBER:
        abort(404)  # error 404: Not Found, i.e. wrong URL, resource does not exist
    elif not(_id in _LOADED_PARTIES):
        abort(410)  # error 410: Gone, i.e. it existed but it's not there anymore
