from apps.fs2_api.portal_proxy import PortalApiProxy


def get_mails_count(user):
    fs2_portal = PortalApiProxy(user.email.split('@')[0], user.get_enc_pass)
    return fs2_portal.get_mails_count()
