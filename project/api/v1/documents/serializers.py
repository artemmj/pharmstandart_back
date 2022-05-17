from rest_framework import serializers


class DocumentsListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False)


class ListAllDocumentsSerializer(serializers.Serializer):
    """ Сериализатор для GET documents/, список всех документов """

    class DefaultActionsSerializer(serializers.Serializer):
        """ Действия документа по-умолчанию в списке всех документов """
        id = serializers.UUIDField()
        caption = serializers.CharField()

    id = serializers.UUIDField()
    requires_attention = serializers.BooleanField()
    name = serializers.CharField()
    human_name = serializers.CharField()
    date = serializers.DateTimeField(allow_null=True)
    date_deadline = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()
    source = serializers.CharField()
    attachment_count = serializers.IntegerField()
    user_responsible = serializers.CharField()
    type = serializers.CharField()
    default_actions = serializers.ListField(child=DefaultActionsSerializer())


class DetailedDocumentSerializer(serializers.Serializer):
    """ Сериализатор детального вида документа """

    class DetailedDocumentAttachsSerializer(serializers.Serializer):
        """ Вложения в детальном виде документа """
        id = serializers.IntegerField()
        file = serializers.CharField()
        date = serializers.DateTimeField()

    class DetailDocUsersApprovsSerializer(serializers.Serializer):
        """ Подписанты/Лист согласования в детальном виде документа """

        class UserOfDetailDocSignsSerializer(serializers.Serializer):
            """ Пользователь в Листе согласования в детальном виде документа """
            id = serializers.IntegerField()
            name = serializers.CharField()
            position = serializers.CharField()

        id = serializers.IntegerField()
        status = serializers.CharField()
        date_approval = serializers.DateTimeField()
        additional_signature = serializers.CharField()
        created_at = serializers.DateTimeField()
        user = serializers.ListField(child=UserOfDetailDocSignsSerializer())

    class DetailDocActionsSerializer(serializers.Serializer):
        """ Действия по-умолчанию в детальном виде документа """
        id = serializers.IntegerField()
        action_type = serializers.CharField()
        caption = serializers.CharField()
        status = serializers.CharField()

    class DetailDocCommentsSerializer(serializers.Serializer):
        """ Комментарии в детальном виде документов """

        class DetailDocCommentsActionsSerializer(serializers.Serializer):
            caption = serializers.CharField()
            action_type = serializers.CharField()
            is_default = serializers.CharField()
            status = serializers.CharField()

        class DetailDocCommentsAttachsSerializers(serializers.Serializer):
            """ Вложения в комментариях детального вида документов """
            class_name = serializers.CharField()
            id = serializers.UUIDField()
            field_caption = serializers.CharField()
            field_name = serializers.CharField()
            field_attach = serializers.BooleanField()
            filename = serializers.CharField()
            file = serializers.CharField()
            caption = serializers.CharField()
            crc32 = serializers.IntegerField()
            attach_date = serializers.DateTimeField()
            file_size = serializers.IntegerField()
            file_type = serializers.CharField()
            attach_user_caption = serializers.CharField()

        class DetailDocCommentsAcceptorsSerializer(serializers.Serializer):
            """ Акцептанты/подписанты в комментариях детального вида документа """
            class_name = serializers.CharField()
            id = serializers.UUIDField()
            user_id = serializers.UUIDField()
            user_caption = serializers.CharField()
            username = serializers.CharField()
            user_state = serializers.CharField()
            origin = serializers.CharField()
            acceptor_type = serializers.CharField()

        id = serializers.UUIDField()
        comment_text = serializers.CharField()
        motion_type = serializers.CharField()
        event_name = serializers.CharField()
        for_user_caption = serializers.CharField()
        for_user_name = serializers.CharField()
        for_user_id = serializers.CharField()
        author_caption = serializers.CharField()
        author_name = serializers.CharField()
        author_id = serializers.UUIDField()
        datetime = serializers.DateTimeField()
        actions = serializers.ListField(child=DetailDocCommentsActionsSerializer())
        attachs = serializers.ListField(child=DetailDocCommentsAttachsSerializers())
        acceptors = serializers.ListField(child=DetailDocCommentsAcceptorsSerializer())

    id = serializers.IntegerField()
    name = serializers.CharField()
    human_name = serializers.CharField()
    date = serializers.DateField()
    date_deadline = serializers.DateField()
    status = serializers.CharField()
    source = serializers.CharField()
    signatory = serializers.CharField()
    delivery_method = serializers.CharField()
    organisation = serializers.CharField()
    attachment_count = serializers.IntegerField()
    user_responsible = serializers.CharField()
    type = serializers.CharField()
    in_answer_to = serializers.CharField()
    mail = serializers.CharField()

    attachs = serializers.ListField(child=DetailedDocumentAttachsSerializer())
    users_approval = serializers.ListField(child=DetailDocUsersApprovsSerializer())
    green_actions = serializers.ListField(child=DetailDocActionsSerializer())
    red_action = serializers.ListField(child=DetailDocActionsSerializer())
    other_actions = serializers.ListField(child=DetailDocActionsSerializer())
    comments = serializers.ListField(child=DetailDocCommentsSerializer())


class PrepareSpecActionSerializer(serializers.Serializer):
    """ Сериализатор запроса на подготову выполнения действия документа """
    action_id = serializers.UUIDField(required=True)


class PrepareSpecActionResultSerializer(serializers.Serializer):
    """ Сериализатор результата запроса на подготовку действия документа """

    class CompleteAcceptorsSerializer(serializers.Serializer):
        """ Акцептанты действия разбитые по группам/названиям """

        class AcceptorsSerializer(serializers.Serializer):
            """ Список акцептантов действия, есть несколько видов """
            id = serializers.IntegerField()
            name = serializers.CharField()

        title = serializers.CharField()
        values = serializers.ListField(child=AcceptorsSerializer())

    id = serializers.IntegerField()
    display_name = serializers.CharField()
    comment_label = serializers.CharField()
    default_comment = serializers.CharField()
    can_modify_attachs = serializers.BooleanField()
    default_dead_line = serializers.DateTimeField()
    dead_line_visible = serializers.BooleanField()
    need_dead_line = serializers.BooleanField()
    dead_line_label = serializers.CharField()
    hint = serializers.CharField()
    warn_hint = serializers.CharField()
    caption = serializers.CharField()
    need_attach = serializers.BooleanField()
    need_comment = serializers.BooleanField()
    need_dialog = serializers.BooleanField()
    max_attach_size = serializers.IntegerField()
    max_attach_count = serializers.IntegerField()
    sign_confirm_type = serializers.CharField()
    acceptors = serializers.ListField(child=CompleteAcceptorsSerializer())


class CommitActionSerializer(serializers.Serializer):
    """ Сериализатор запроса на коммит действия """

    class CommitActionAcceptorsSerializer(serializers.Serializer):
        """ Сериализатор акцептантов в коммите действия """
        acceptortype = serializers.CharField(required=True)
        userid = serializers.UUIDField(required=True)

    action_id = serializers.UUIDField(required=True)
    deadline = serializers.DateField(required=False)
    comment = serializers.CharField(required=False)
    sign_confirm_code = serializers.IntegerField(required=False)
    acceptors = serializers.ListField(required=False, child=CommitActionAcceptorsSerializer())


class CommitActionResultSerializer(serializers.Serializer):
    """ Сериализатор результата на запрос коммита действия """
    status_code = serializers.IntegerField()
    result = serializers.CharField()


class RollbackActionSerializer(serializers.Serializer):
    """ Сериализатор запроса на роллбэк действия """
    action_id = serializers.UUIDField(required=True)


class RollbackActionResultSerializer(serializers.Serializer):
    """ Сериализатор результата на запрос роллбэка действия """
    status_code = serializers.IntegerField()
    result = serializers.CharField()


class SendAttachActionSerializer(serializers.Serializer):
    """ Сериализатор запроса на отправку вложения в действии """
    action_id = serializers.UUIDField(required=True)
    file = serializers.FileField(required=True, use_url=True)


class SendAttachActionResultSerializer(serializers.Serializer):
    """ Сериализатор результата запроса на отправку вложения в действии """
    status_code = serializers.IntegerField()
    filegeturi = serializers.URLField()


class CheckDssStatusSerializer(serializers.Serializer):
    """ Сериализатор запроса на проверку статуса подписи DSS """
    action_id = serializers.UUIDField(required=True)


class DssStatusSerializer(serializers.Serializer):
    """ Сериализатор результата проверки статуса DSS """
    classname = serializers.CharField()
    id = serializers.CharField()
    signstatus = serializers.CharField()
    messagetext = serializers.CharField()


class DocumentsStatusesRequestSerializer(serializers.Serializer):
    status = serializers.CharField(required=True)
    search = serializers.CharField(required=False)


class DocsStatusesSerializer(serializers.Serializer):
    result = serializers.ListField(child=serializers.CharField())
