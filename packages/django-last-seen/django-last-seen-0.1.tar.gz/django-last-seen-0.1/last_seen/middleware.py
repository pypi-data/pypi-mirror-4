

from models import user_seen


class LastSeenMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            user_seen(request.user)

        return None
