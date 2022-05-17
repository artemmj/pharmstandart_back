from rest_framework.exceptions import ValidationError

from apps.fs2_api.api_proxy import Fs2ApiProxy
from apps.user.models import PharmSession


def create_new_session(user) -> Fs2ApiProxy:
    api = Fs2ApiProxy(login=user.email, password=user.get_enc_pass)
    session = PharmSession.objects.create(id=api.app_id, db_id=api.db_id)
    user.pharm_session = session
    user.save()
    return api


def get_actual_fs2_api(user, need_new_session=False) -> Fs2ApiProxy:
    """
    В некоторые моменты работы необходимо решить, создать ли для пользователя
    новый экземпляр сессии, или передать в объект уже существующие данные
    сессии (ap_id, db_id). Сессия привязывается к пользователю.
    - need_new_session - создать новую сессию, иначе проверить существующую
    """
    if need_new_session or not user.pharm_session:
        return create_new_session(user)

    last_session = user.pharm_session
    api = Fs2ApiProxy(user.email.split('@')[0], user.get_enc_pass)  # , need_init=False)
    api.init_with_db_datas(
        login=user.email.split('@')[0],
        password=user.get_enc_pass,
        app_id='{' + str(last_session.id).upper() + '}',
        db_id='{' + str(last_session.db_id).upper() + '}',
    )
    if not api.is_alive():
        raise ValidationError({
            'detail': 'Время жизни сессии истекло',
            'source': 'session_expired',
            'status': 400,
        })
    return api
