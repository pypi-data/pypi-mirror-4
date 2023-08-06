# Django Vkontakte Groups Statistic

[![Build Status](https://travis-ci.org/ramusus/django-vkontakte-groups-statistic.png?branch=master)](https://travis-ci.org/ramusus/django-vkontakte-groups-statistic) [![Coverage Status](https://coveralls.io/repos/ramusus/django-vkontakte-groups-statistic/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-vkontakte-groups-statistic)

Приложение позволяет взаимодействовать со статистикой групп Вконтакте через Вконтакте API и парсер используя стандартные модели Django

## Установка

    pip install django-vkontakte-groups-statistic

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'vkontakte_api',
        'vkontakte_groups',
        'vkontakte_groups_statistic',
    )

    # oauth-tokens settings
    OAUTH_TOKENS_HISTORY = True                                         # to keep in DB expired access tokens
    OAUTH_TOKENS_VKONTAKTE_CLIENT_ID = ''                               # application ID
    OAUTH_TOKENS_VKONTAKTE_CLIENT_SECRET = ''                           # application secret key
    OAUTH_TOKENS_VKONTAKTE_SCOPE = ['ads,wall,photos,friends,stats']    # application scopes
    OAUTH_TOKENS_VKONTAKTE_USERNAME = ''                                # user login
    OAUTH_TOKENS_VKONTAKTE_PASSWORD = ''                                # user password
    OAUTH_TOKENS_VKONTAKTE_PHONE_END = ''                               # last 4 digits of user mobile phone

## Примеры использования

### Получение статистики группы

Получение статистики группы через API

    >>> from vkontakte_groups.models import Group
    >>> group = Group.remote.fetch(ids=[16297716])[0]
    >>> group.update_statistic(api=True)

Статистика, полученная через API доступна через менеджер

    >>> stat = group.statistics_api.all()[0]
    >>> stat.__dict__
    {'_state': <django.db.models.base.ModelState at 0xa2812ac>,
     'age_18': 240,
     'age_18_21': 86,
     'age_21_24': 75,
     'age_24_27': 59,
     'age_27_30': 31,
     'age_30_35': 23,
     'age_35_45': 9,
     'age_45': 13,
     'date': datetime.date(2012, 3, 14),
     'females': 295,
     'fetched': datetime.datetime(2012, 9, 12, 0, 50, 42, 597930),
     'group_id': 14,
     'id': 182,
     'males': 406,
     'views': 1401,
     'visitors': 702}

Получение статистики группы через парсер

    >>> from vkontakte_groups.models import Group
    >>> group = Group.remote.fetch(ids=[16297716])[0]
    >>> group.update_statistic()

Статистика, полученная через парсер доступна через менеджер

    >>> stat = group.statistics.all()[0]
    >>> stat.__dict__
    {'_state': <django.db.models.base.ModelState at 0xa28168c>,
     'act_members': None,
     'act_visitors': None,
     'activity_photo_comments': None,
     'activity_photos': None,
     'activity_topic_comments': None,
     'activity_topics': None,
     'activity_video_comments': None,
     'activity_videos': None,
     'activity_wall': None,
     'ads_members': None,
     'ads_visitors': None,
     'age_18': None,
     'age_18_21': None,
     'age_21_24': None,
     'age_24_27': None,
     'age_27_30': None,
     'age_30_35': None,
     'age_35_45': None,
     'age_45': None,
     'comments': 298,
     'date': datetime.date(2011, 8, 25),
     'ex_members': 595,
     'females': None,
     'group_id': 14,
     'id': 2410,
     'likes': 26,
     'males': None,
     'members': 335748,
     'new_members': 143,
     'reach': None,
     'reach_age_18': None,
     'reach_age_18_21': None,
     'reach_age_21_24': None,
     'reach_age_24_27': None,
     'reach_age_27_30': None,
     'reach_age_30_35': None,
     'reach_age_35_45': None,
     'reach_age_45': None,
     'reach_females': None,
     'reach_males': None,
     'reach_subsribers': None,
     'references': None,
     'section_applications': None,
     'section_audio': None,
     'section_discussions': None,
     'section_documents': None,
     'section_photoalbums': None,
     'section_video': None,
     'shares': 4,
     'views': 1188,
     'visitors': 603,
     'widget_ex_users': None,
     'widget_members_views': None,
     'widget_new_users': None,
     'widget_users_views': None}