from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

import uuid, random, time, json


def error_405(message) -> JsonResponse:
    return JsonResponse({
            "status": False,
            "message": message
        },
        status=405
    )

def _check_move(move) -> bool:
    if not isinstance(move, list) or len(move) != 2:
        return False
    if (not (1 <= move[0] <= settings.GAME_FIELD_SIZE[0]) or 
        not (1 <= move[1] <= settings.GAME_FIELD_SIZE[1])):
        return False
    return True

def _get_opponent_id(state, user_id) -> str:
    if state["players"][0] == user_id:
        return state["players"][1]
    return state["players"][0]


@csrf_exempt
def make_connection(request) -> JsonResponse:
    """
    Creates connection between with another user if there \
    is one, otherwise adds to the waiting queue.
    """

    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        if user_id is None:
            return JsonResponse({
                    "status": False,
                    "message": "Some attributes are not set"
            },
            status=400)
        opponent_id = cache.get(settings.CACHE_USER_IN_QUEUE_NAME)
        if opponent_id is not None and opponent_id != user_id:
            # get the first competitor
            cache.set(
                settings.CACHE_USER_IN_QUEUE_NAME,
                None,
                settings.CACHE_USER_IN_QUEUE_TIMEOUT
            )
            # creates game session
            game_id = str(uuid.uuid4())
            cache.set(
                f'{settings.CACHE_USER_TO_GAME_PREFIX}-{user_id}',
                game_id,
                settings.GAME_DURATION_TIMEOUT
            )
            cache.set(
                f'{settings.CACHE_USER_TO_GAME_PREFIX}-{opponent_id}',
                game_id,
                settings.GAME_DURATION_TIMEOUT
            )
            # creating game state
            cache.set(f'{settings.CACHE_GAME_STATE_PREFIX}-{game_id}', {
                "players": [user_id, opponent_id],
                "time_start": time.time(),
                user_id: {
                    "last_move": None,
                    "time_last_move": time.time(),
                    "time_remaining": settings.GAME_DURATION_TIMEOUT_PER_USER
                },
                opponent_id: {
                    "last_move": None,
                    "time_last_move": time.time(),
                    "time_remaining": settings.GAME_DURATION_TIMEOUT_PER_USER
                },
                "timeout": settings.GAME_DURATION_TIMEOUT_PER_USER,
                "is_over": False,
                "winner": None,
                "turn": random.choice([user_id, opponent_id])
            }, settings.GAME_DURATION_TIMEOUT)
            return JsonResponse({
                "status": True,
                "data": {
                    "game_id": game_id
                }
            })
        else:
            cache.set(
                settings.CACHE_USER_IN_QUEUE_NAME,
                user_id,
                settings.CACHE_USER_IN_QUEUE_TIMEOUT
            )
            return JsonResponse({
                "status": True,
                "data": {
                    "game_id": None
                }
            })
    else:
        error_405("Method is not allowed")

@csrf_exempt
def get_connection(request) -> JsonResponse:
    """
    Gets the connection by user_id (returns game_id)
    """

    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        if user_id is None:
            return JsonResponse({
                    "status": False,
                    "message": "Some attributes are not set"
            },
            status=400)
        game_id = cache.get(f'{settings.CACHE_USER_TO_GAME_PREFIX}-{user_id}')
        if game_id is not None:
            return JsonResponse({
                "status": True,
                "data": {
                    "game_id": game_id
                },
                "reconnection_required": False
            })
        else:
            if cache.get(settings.CACHE_USER_IN_QUEUE_NAME) == user_id:
                cache.set(
                    settings.CACHE_USER_IN_QUEUE_NAME,
                    user_id,
                    settings.CACHE_USER_IN_QUEUE_TIMEOUT
                )
            else:
                return JsonResponse({
                "status": True,
                "data": {
                    "game_id": None
                },
                "reconnection_required": True
            })
            return JsonResponse({
                "status": True,
                "data": {
                    "game_id": None
                },
                "reconnection_required": False
            })
    else:
        error_405("Method is not allowed")

@csrf_exempt
def make_move(request) -> JsonResponse:
    """
    Makes move by game_id
    """
    
    if request.method == 'POST':
        user_id = request.GET.get('user_id')
        game_id = request.GET.get('game_id')
        move = json.loads(request.body.decode("utf-8")).get('move', None)
        if user_id is None or game_id is None or move is None:
            return JsonResponse({
                    "status": False,
                    "message": "Some attributes are not set"
            },
            status=400)
        state = cache.get(f'{settings.CACHE_GAME_STATE_PREFIX}-{game_id}')
        if state is None:
            return JsonResponse({
                    "status": False,
                    "message": "There is no game with this id"
            },
            status=400)
        if user_id not in state["players"]:
            return JsonResponse({
                    "status": False,
                    "message": "It's very interesting. How could \
                     you do that? You are not a member of this game"
            },
            status=400)
        if state["turn"] != user_id:
            return JsonResponse({
                "status": False,
                "message": "It's not your turn"
            })
        if not _check_move(move):
            return JsonResponse({
                    "status": False,
                    "message": "Move is not valid"
            },
            status=400)
        opponent_id = _get_opponent_id(state, user_id)
        state[user_id] = {
            "last_move": move,
            "time_last_move": time.time(),
            "time_remaining": state[user_id]["time_remaining"] - 
            (time.time() - state[opponent_id]["time_last_move"])
        }
        state["turn"] = opponent_id
        cache.set(
            f'{settings.CACHE_GAME_STATE_PREFIX}-{game_id}',
            state,
            settings.GAME_DURATION_TIMEOUT - \
            (time.time() - int(state["time_start"]))
        )
        return JsonResponse({
            "status": True,
            "data": state
        })
    else:
        error_405("Method is not allowed")

@csrf_exempt
def get_state(request) -> JsonResponse:
    """
    Gets state of the game by game_id
    """
    
    if request.method == 'GET':
        game_id = request.GET.get('game_id')
        if game_id is None:
            return JsonResponse({
                    "status": False,
                    "message": "Some attributes are not set"
            },
            status=400)
        state = cache.get(f'{settings.CACHE_GAME_STATE_PREFIX}-{game_id}')
        if state is None:
            return JsonResponse({
                    "status": False,
                    "message": "There is no game with this id"
            },
            status=400)
        return JsonResponse({
            "status": True,
            "data": state
        })
    else:
        return JsonResponse({
            "status": False,
            "message": "Method is not allowed"
        },
        status=405)

@csrf_exempt
def resign(request) -> JsonResponse:
    """
    Provides implementation for resignation calls
    """

    if request.method == 'POST':
        user_id = request.GET.get("user_id")
        game_id = request.GET.get("game_id")
        if user_id is None or game_id is None:
            return JsonResponse({
                    "status": False,
                    "message": "Some attributes are not set"
            },
            status=400)
        state = cache.get(f'{settings.CACHE_GAME_STATE_PREFIX}-{game_id}')
        if state is None:
            return JsonResponse({
                    "status": False,
                    "message": "There is no game with this id"
            },
            status=400)
        if user_id not in state["players"]:
            return JsonResponse({
                    "status": False,
                    "message": "It's very interesting. How could \
                     you do that? You are not a member of this game"
            },
            status=400)
        state["is_over"] = True
        state["winner"] = _get_opponent_id(state, user_id)
        cache.set(
            f'{settings.CACHE_GAME_STATE_PREFIX}-{game_id}',
            state,
            settings.GAME_DURATION_TIMEOUT - \
            (time.time() - int(state["time_start"]))
        )
        return JsonResponse({
            "status": True
        })
    else:
        error_405("Method is not allowed")