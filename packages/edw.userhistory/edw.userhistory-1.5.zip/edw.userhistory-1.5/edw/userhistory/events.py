from datetime import datetime

from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList


def get_ip(request):
    if "HTTP_X_FORWARDED_FOR" in request.environ:
        # Virtual host
        ip = request.environ["HTTP_X_FORWARDED_FOR"]
    elif "HTTP_HOST" in request.environ:
        # Non-virtualhost
        ip = request.environ["REMOTE_ADDR"]
    else:
        ip = None

    return ip

def userLoggedIn(user, event):
    userip = get_ip(user.REQUEST)
    logintime = datetime.now()

    member = user.portal_membership.getMemberById(user.getId())
    if member is None:
        return
    anno = IAnnotations(member)
    data = anno.setdefault('login_history', PersistentList())
    data.append({'date': logintime, 'ip': userip})
