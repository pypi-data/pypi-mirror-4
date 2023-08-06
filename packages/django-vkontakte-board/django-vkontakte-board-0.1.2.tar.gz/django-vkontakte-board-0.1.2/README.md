# Django Vkontakte Board

Приложение позволяет взаимодействовать с дисскуссиями групп через Вконтакте API используя стандартные модели Django

## Установка

    pip install django-vkontakte-board

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'vkontakte_api',
        'vkontakte_groups',
        'vkontakte_board',
    )

## Примеры использования

### Получение дискуссий группы через метод группы

    >>> from vkontakte_groups.models import Group
    >>> group = Group.remote.fetch(ids=[16297716])
    >>> group.fetch_topics()
    [<Topic: ЭСТАФЕТА ОЛИМПИЙСКОГО ОГНЯ ► задаем вопросы в этой теме>,
     <Topic: ПРОМО-АКЦИЯ "ВСТРЕЧАЙ НОВЫЙ ГОД С ПРИЗАМИ! СОБЕРИ ТЁПЛУЮ КОМПАНИЮ МИШЕК!" ► вопросы и обсуждение>,
     '...(remaining elements truncated)...']

### Получение дискуссий группы через менеджер

    >>> from vkontakte_board.models import Topic
    >>> Topic.remote.fetch(group=group, all=True)
    [<Topic: ЭСТАФЕТА ОЛИМПИЙСКОГО ОГНЯ ► задаем вопросы в этой теме>,
     <Topic: ПРОМО-АКЦИЯ "ВСТРЕЧАЙ НОВЫЙ ГОД С ПРИЗАМИ! СОБЕРИ ТЁПЛУЮ КОМПАНИЮ МИШЕК!" ► вопросы и обсуждение>,
     '...(remaining elements truncated)...']

### Получение комментариев дискуссии через метод дискуссии

    >>> from vkontakte_groups.models import Group
    >>> from vkontakte_board.models import Topic
    >>> group = Group.remote.fetch(ids=[16297716])
    >>> topics = Topic.remote.fetch(group=group, ids=[26523718])
    >>> topics[0].fetch_comments()
    [<Comment: Comment object>,
     <Comment: Comment object>,
     '...(remaining elements truncated)...']
    >>> topic[0].comments.count()
    39

### Получение комментариев дискуссии через менеджер

    >>> from vkontakte_groups.models import Group
    >>> from vkontakte_board.models import Topic, Comment
    >>> group = Group.remote.fetch(ids=[16297716])
    >>> topics = Topic.remote.fetch(group=group, ids=[26523718])
    >>> Comment.remote.fetch(topic=topics[0])
    [<Comment: Comment object>,
     <Comment: Comment object>,
     '...(remaining elements truncated)...']