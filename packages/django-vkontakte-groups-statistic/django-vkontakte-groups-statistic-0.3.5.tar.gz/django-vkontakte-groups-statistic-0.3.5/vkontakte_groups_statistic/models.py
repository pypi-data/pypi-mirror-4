# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
from vkontakte_api.utils import api_call
from vkontakte_api.models import VkontakteManager, VkontakteModel, VkontakteIDModel, VkontakteDeniedAccessError, VkontakteContentError
from vkontakte_groups.models import Group
from oauth_tokens.providers.vkontakte import VkontakteAccessToken
from datetime import datetime
from urllib import unquote
import logging
import re
import simplejson as json

log = logging.getLogger('vkontakte_groups_statistic')

def fetch_statistic_for_group(group, api=False):
    '''
    Get html page with statistic charts and parse it
    '''
    if api:
        GroupStatistic.remote.fetch_for_group(group)
    else:
        vk = VkontakteAccessToken()
        for act in ['','reach','activity']:
            response = vk.authorized_request(url='http://vk.com/stats?act=%s&gid=%d' % (act, group.remote_id))
            content = response.content.decode('windows-1251')

            if u'У Вас нет прав на просмотр этой страницы.' in content:
                raise VkontakteDeniedAccessError("User doesn't have rights to see statistic of this group %s" % group.name)

            GroupStat.objects.parse_statistic_page(group, act, content)
            GroupStatPercentage.objects.parse_statistic_page(group, content)

    return True

class GroupStatManager(models.Manager):

    def parse_statistic_page(self, group, section, content):

        if 'var graphdata' in content:
            graphs = re.findall(r'var graphdata = \'([^\']+)\'', content)

        elif 'graphdata=' in content:
            graphs = re.findall(r'graphdata=(.+?)&lang', content)
            graphs = [unquote(graph) for graph in graphs]

        else:
            raise VkontakteContentError("Response doesn't contain graphs:\n\n %s" % content)

        fields_map = {
            '': {
                'visitors': (
                    (u'уникальные посетители', 'visitors'),
                    (u'просмотры', 'views'),
                ),
                'gender': (
                    (u'женщины', 'females'),
                    (u'мужчины', 'males'),
                ),
                'age': (
                    (u'до 18', 'age_18'),
                    (u'от 18 до 21', 'age_18_21'),
                    (u'от 21 до 24', 'age_21_24'),
                    (u'от 24 до 27', 'age_24_27'),
                    (u'от 27 до 30', 'age_27_30'),
                    (u'от 30 до 35', 'age_30_35'),
                    (u'от 35 до 45', 'age_35_45'),
                    (u'от 45', 'age_45'),
                ),
                'ads': (
                    (u'Зашедшие с рекламы', 'ads_visitors'),
                    (u'Вступившие с рекламы', 'ads_members'),
                    (u'Зашедшие с акций', 'act_visitors'),
                    (u'Вступившие с акции', 'act_members'),
                ),
                'members': (
                    (u'Новые участники', 'new_members'),
                    (u'Вышедшие участники', 'ex_members'),
                    (u'Всего участников', 'members'),
                ),
                'widget': (
                    (u'Просмотры пользователей ВКонтакте', 'widget_users_views'),
                    (u'Просмотры участников группы', 'widget_members_views'),
                    (u'Новые участники', 'widget_new_users'),
                    (u'Вышедшие участники', 'widget_ex_users'),
                ),
                'sections': (
                    (u'Обсуждения', 'section_discussions'),
                    (u'Аудиозаписи', 'section_audio'),
                    (u'Видеозаписи', 'section_video'),
                    (u'Фотоальбомы', 'section_photoalbums'),
                    # VK убрал график после разделения графиков на вкладки cocacola 2012-12-18
#                    (u'Приложения', 'section_applications'),
                    (u'Документы', 'section_documents'),
                ),
            },
            'reach': {
                'reach': (
                    (u'Полный охват', 'reach'),
                    (u'Охват подписчиков', 'reach_subsribers'),
                ),
                'gender': (
                    (u'женщины', 'reach_females'),
                    (u'мужчины', 'reach_males'),
                ),
                'age': (
                    (u'до 18', 'reach_age_18'),
                    (u'от 18 до 21', 'reach_age_18_21'),
                    (u'от 21 до 24', 'reach_age_21_24'),
                    (u'от 24 до 27', 'reach_age_24_27'),
                    (u'от 27 до 30', 'reach_age_27_30'),
                    (u'от 30 до 35', 'reach_age_30_35'),
                    (u'от 35 до 45', 'reach_age_35_45'),
                    (u'от 45', 'reach_age_45'),
                ),
            },
            'activity': {
                'likes': (
                    (u'Мне нравится', 'likes'),
                    (u'Комментарии', 'comments'),
                    (u'Рассказать друзьям', 'shares'),
                    (u'Упоминания', 'references'),
                ),
                'activity': (
                    (u'Сообщения на стене', 'activity_wall'),
                    (u'Фотографии', 'activity_photos'),
                    (u'Комментарии к фотографиям', 'activity_photo_comments'),
                    (u'Видеозаписи', 'activity_videos'),
                    (u'Комментарии к видеозаписям', 'activity_video_comments'),
                    (u'Темы обсуждений', 'activity_topics'),
                    (u'Комментарии к обсуждениям', 'activity_topic_comments'),
                ),
            }
        }
        data = {}

        graphs = [json.loads(graph) for graph in graphs]
        graph_data = {}

        # make list graph_data from parsed data using fields_map dict
        for key, names in fields_map[section].items():
            new_key = section + '_' + key
            for i, graph in enumerate(graphs):
                if isinstance(graph[0], dict) and len(graph) == len(names) and graph[0]['name'].lower() == names[0][0].lower():
                    graph_data[new_key] = graphs.pop(i)
                    break
                elif isinstance(graph[0], list) and graph[0][0]['name'].lower() == names[0][0].lower():
                    if key == 'members':
                        graph_data[new_key] = graph[0] + graph[1]
                        graphs.pop(i)
                        break
                    elif key in ['age','visitors','reach']:
                        graph_data[new_key] = graph[0]
                        graphs.pop(i)
                        break

        for key, graph_set in graph_data.iteritems():
            section, key = key.split('_')
            for graph in graph_set:
                if not graph['d']:
                    continue

                try:
                    field = dict(fields_map[section][key])[graph['name']]
                except KeyError:
                    log.error("Can't find field name for GroupStat model for graph %s" % graph['name'])
                    continue

                for values in graph['d']:
                    stat_date = datetime.fromtimestamp(values[0]).date()
                    value = values[1]
                    pair = {field: value}
                    if stat_date in data:
                        data[stat_date].update(pair)
                    else:
                        data[stat_date] = pair

        # delete previous statistic
#        group.statistics.all().delete()

        groupstats = []
        # save statistic
        for stat_date, values in data.items():
            groupstat = self.model.objects.get_or_create(group=group, date=stat_date)[0]
            groupstat.__dict__.update(values)
            groupstat.save()

            groupstats += [groupstat]

        return groupstats

class GroupStatPercentageManager(models.Manager):

    def update_for_group_users(self, group):

        if 'vkontakte_users' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("Application 'vkontakte_users' not in INSTALLED_APPS")

        from vkontakte_users.models import USER_RELATION_CHOICES
        total_count = group.users.count()
        users = {}
        if total_count:
            users['relations_set'] = (
                (1, 'has_relations', u'Отношения указаны', group.users.filter(relation__gt=0).count()),
                (2, 'no_relations', u'Отношения не указаны', group.users.filter(relation=None).count()),
            )
            users['relations'] = [(rel_pair[0], rel_pair[0], rel_pair[1], group.users.filter(relation=rel_pair[0]).count()) for rel_pair in list(USER_RELATION_CHOICES)]
            users['gender'] = (
                (1, 'males', u'Мужчины', group.users.filter(sex=2).count()),
                (2, 'females', u'Женщины', group.users.filter(sex=1).count()),
                (3, 'undefined', u'Не указано', group.users.filter(sex=None).count()),
            )
            users['mobile'] = (
                (1, 'has_mobile', u'Указали мобильный', group.users.filter(has_mobile=True).count()),
                (2, 'no_mobile', u'Не указали мобильный', group.users.filter(has_mobile=False).count()),
            )
            users['avatar'] = (
                (1, 'has_avatar', u'С аватаром', group.users.has_avatars().count()),
                (2, 'no_avatar', u'Без аватара', group.users.no_avatars().count()),
                (3, 'deactivated', u'Заблокированные', group.users.deactivated().count()),
            )
            users['rate'] = (
                (1, 'no_rate', u'Нет рейтинга', group.users.filter(rate=None).count()),
                (2, 'rate_30', u'Рейтинг < 30', group.users.filter(rate__gte=0, rate__lt=30).count()),
                (3, 'rate_30_60', u'30 < рейтинг < 60', group.users.filter(rate__gte=30, rate__lt=60).count()),
                (4, 'rate_60_90', u'60 < рейтинг < 90', group.users.filter(rate__gte=60, rate__lt=90).count()),
                (5, 'rate_90_100', u'90 < рейтинг < 100', group.users.filter(rate__gte=90, rate__lt=100).count()),
                (6, 'rate_100_110', u'100 < рейтинг < 110', group.users.filter(rate__gte=100, rate__lt=110).count()),
                (7, 'rate_110_120', u'110 < рейтинг < 120', group.users.filter(rate__gte=110, rate__lt=120).count()),
                (8, 'rate_120', u'120 < рейтинг', group.users.filter(rate__gte=120).count()),
            )
            users['friends'] = (
                (1, 'no_friends', u'Нет друзей', group.users.filter(friends=0).count()),
                (2, 'friends_50', u'Друзей < 50', group.users.filter(friends__gte=0, friends__lt=50).count()),
                (3, 'friends_50_100', u'50 < друзей < 100', group.users.filter(friends__gte=50, friends__lt=100).count()),
                (4, 'friends_100_150', u'100 < друзей < 150', group.users.filter(friends__gte=100, friends__lt=150).count()),
                (5, 'friends_150_200', u'150 < друзей < 200', group.users.filter(friends__gte=150, friends__lt=200).count()),
                (6, 'friends_200_300', u'200 < друзей < 300', group.users.filter(friends__gte=200, friends__lt=300).count()),
                (7, 'friends_300_400', u'300 < друзей < 400', group.users.filter(friends__gte=300, friends__lt=400).count()),
                (8, 'friends_400', u'400 < рейтинг', group.users.filter(friends__gte=400).count()),
            )
            users['activity'] = (
                (1, 'active', u'Активны в сети', group.users.filter(counters_updated__isnull=False, sum_counters__gt=0).count()),
                (2, 'passive', u'Не активны в сети', group.users.filter(counters_updated__isnull=False, sum_counters=0).count()),
            )

        # save stats
        stats = []
        for type, parts in users.items():
            for order, value_type, name, value in parts:
                stat = self.get_or_create(group=group, type=type, value_type=value_type)[0]
                stat.order = order
                stat.value_name = name
                stat.value = value
                stat.percents = 100*float(value)/total_count
                stat.save()
                stats += [stat]

        return stats

    def parse_statistic_page(self, group, content):

        # TODO: fix percentage graphs. With current headers, there is no charts in response, only graphs
        graphs = re.findall(r'cur.invokeSvgFunction\(\'(.+)_chart\', \'loadData\', \[\[([^\]]+)\]\]\)', content)

        if len(graphs) and len(graphs) < 4:
            raise VkontakteContentError("Response doesn't contain right number of pie charts: 0 < %d < 4" % len(graphs))

        fields_map = {
            u'мужчины': (1, 'males'),
            u'женщины': (2, 'females'),

            u'до 18':        (1, '_18'),
            u'от 18 до 21':  (2, '18_21'),
            u'от 21 до 24':  (3, '21_24'),
            u'от 24 до 27':  (4, '24_27'),
            u'от 27 до 30':  (5, '27_30'),
            u'от 30 до 35':  (6, '30_35'),
            u'от 35 до 45':  (7, '35_45'),
            u'от 45':        (8, '45_'),

            u'мужчины до 18':        (1, 'males__18'),
            u'мужчины от 18 до 21':  (2, 'males_18_21'),
            u'мужчины от 21 до 24':  (3, 'males_21_24'),
            u'мужчины от 24 до 27':  (4, 'males_24_27'),
            u'мужчины от 27 до 30':  (5, 'males_27_30'),
            u'мужчины от 30 до 35':  (6, 'males_30_35'),
            u'мужчины от 35 до 45':  (7, 'males_35_45'),
            u'мужчины от 45':        (8, 'males_45_'),

            u'женщины до 18':        (1, 'females__18'),
            u'женщины от 18 до 21':  (2, 'females_18_21'),
            u'женщины от 21 до 24':  (3, 'females_21_24'),
            u'женщины от 24 до 27':  (4, 'females_24_27'),
            u'женщины от 27 до 30':  (5, 'females_27_30'),
            u'женщины от 30 до 35':  (6, 'females_30_35'),
            u'женщины от 35 до 45':  (7, 'females_35_45'),
            u'женщины от 45':        (8, 'females_45_'),
        }
        stats = []
        for graph in graphs:

            try:
                graph_data = json.loads('[' + graph[1] + ']')
                assert len(graph_data) > 0
            except:
                log.error('Error while parse content of chart %s' % graph[0])

            for graph_slice in graph_data:
                # {"l":"до 18","q":552,"p":"9.13","id":0,"c":"женщины"}
                name = [graph_slice['l']]
                if graph_slice['c']:
                    name = [graph_slice['c']] + name
                name = ' '.join(name)

                type = graph[0]
                try:
                    order = fields_map[name][0]
                    value_type = fields_map[name][1]
                    if 'females_' in value_type:
                        value_type = value_type.replace('females_','')
                        type += '_females'
                    elif 'males_' in value_type:
                        value_type = value_type.replace('males_','')
                        type += '_males'
                except KeyError:
                    value_type = name
                    order = 1

                stats += [{
                    'type': type,
                    'order': order,
                    'value_type': value_type,
                    'value':  graph_slice['q'],
                    'percents': float(graph_slice['p']),
                    'value_name': name,
                }]

        # delete previous statistic
#        group.percentage_statistics.all().delete()

        groupstats = []
        # save statistic
        for stat in stats:
            groupstat = self.model.objects.get_or_create(group=group, type=stat['type'], value_type=stat['value_type'])[0]
            groupstat.__dict__.update(stat)
            groupstat.save()

            groupstats += [groupstat]

        return groupstats

class GroupStatisticRemoteManager(VkontakteManager):

    def fetch_for_group(self, group, date_from=None, date_to=None):

        if not date_from:
            date_from = datetime(2000,1,1).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.today().strftime('%Y-%m-%d')

        return self.fetch(group=group, date_from=date_from, date_to=date_to)

    def fetch(self, **kwargs):

        kwargs['gid'] = kwargs.get('group').remote_id

        instances = []
        for instance in self.get(**kwargs):
            instance.fetched = datetime.now()
            instance.group = kwargs.get('group')
            instances += [self.get_or_create_from_instance(instance)]

class GroupStatistic(VkontakteModel):
    '''
    Group statistic model collecting information via API
    http://vk.com/developers.php?oid=-1&p=stats.get
    TODO: inherit from GroupStatisticAbstract and check
    '''
    class Meta:
        verbose_name = _('Vkontakte group API statistic')
        verbose_name_plural = _('Vkontakte group API statistics')
        unique_together = ('group','date')
        ordering = ('group','date')

    methods_namespace = 'stats'

    group = models.ForeignKey(Group, verbose_name=u'Группа', related_name='statistics_api')
    date = models.DateField(u'Дата')

    visitors = models.PositiveIntegerField(u'Уникальные посетители', null=True)
    views = models.PositiveIntegerField(u'Просмотры', null=True)

#    likes = models.PositiveIntegerField(u'Мне нравится', null=True)
#    comments = models.PositiveIntegerField(u'Комментарии', null=True)
#    shares = models.PositiveIntegerField(u'Рассказать друзьям', null=True)
#    references = models.PositiveIntegerField(u'Упоминания', null=True)
#
#    new_members = models.PositiveIntegerField(u'Новые участники', null=True)
#    ex_members = models.PositiveIntegerField(u'Вышедшие участники', null=True)
#    members = models.PositiveIntegerField(u'Всего участников', null=True)
#
#    reach = models.PositiveIntegerField(u'Полный охват', null=True)
#    reach_subsribers = models.PositiveIntegerField(u'Охват подписчиков', null=True)
#
#    widget_users_views = models.PositiveIntegerField(u'Просмотры пользователей ВКонтакте', null=True)
#    widget_members_views = models.PositiveIntegerField(u'Просмотры участников группы', null=True)
#    widget_new_users = models.PositiveIntegerField(u'Новые участники', null=True)
#    widget_ex_users = models.PositiveIntegerField(u'Вышедшие участники', null=True)
#
#    ads_visitors = models.PositiveIntegerField(u'Зашедшие с рекламы', null=True)
#    ads_members = models.PositiveIntegerField(u'Вступившие с рекламы', null=True)
#    act_visitors = models.PositiveIntegerField(u'Зашедшие с акций', null=True)
#    act_members = models.PositiveIntegerField(u'Вступившие с акций', null=True)

    males = models.PositiveIntegerField(u'Мужчины', null=True)
    females = models.PositiveIntegerField(u'Женщины', null=True)

#    section_discussions = models.PositiveIntegerField(u'Обсуждения', null=True)
#    section_audio = models.PositiveIntegerField(u'Аудиозаписи', null=True)
#    section_video = models.PositiveIntegerField(u'Видеозаписи', null=True)
#    section_photoalbums = models.PositiveIntegerField(u'Фотоальбомы', null=True)
#    section_applications = models.PositiveIntegerField(u'Приложения', null=True)
#    section_documents = models.PositiveIntegerField(u'Документы', null=True)
#
#    activity_wall = models.PositiveIntegerField(u'Сообщения на стене', null=True)
#    activity_photos = models.PositiveIntegerField(u'Фотографии', null=True)
#    activity_photo_comments = models.PositiveIntegerField(u'Комментарии к фотографиям', null=True)
#    activity_videos = models.PositiveIntegerField(u'Видеозаписи', null=True)
#    activity_video_comments = models.PositiveIntegerField(u'Комментарии к видеозаписям', null=True)
#    activity_topics = models.PositiveIntegerField(u'Темы обсуждений', null=True)
#    activity_topic_comments = models.PositiveIntegerField(u'Комментарии к обсуждениям', null=True)

    age_18 = models.PositiveIntegerField(u'До 18', null=True)
    age_18_21 = models.PositiveIntegerField(u'От 18 до 21', null=True)
    age_21_24 = models.PositiveIntegerField(u'От 21 до 24', null=True)
    age_24_27 = models.PositiveIntegerField(u'От 24 до 27', null=True)
    age_27_30 = models.PositiveIntegerField(u'От 27 до 30', null=True)
    age_30_35 = models.PositiveIntegerField(u'От 30 до 35', null=True)
    age_35_45 = models.PositiveIntegerField(u'От 35 до 45', null=True)
    age_45 = models.PositiveIntegerField(u'От 45', null=True)

    objects = models.Manager()
    remote = GroupStatisticRemoteManager(remote_pk=('group','date'), methods={
        'get': 'get',
    })

    def parse(self, response):
        '''
        Transform response for correct parsing it in parent method
        '''
        response['date'] = response.get('day')

        fields_map = {
            'sex': {
                'f': 'females',
                'm': 'males',
            },
            'age': {
                '12-18': 'age_18',
                '18-21': 'age_18_21',
                '21-24': 'age_21_24',
                '24-27': 'age_24_27',
                '27-30': 'age_27_30',
                '30-35': 'age_30_35',
                '35-45': 'age_35_45',
                '45-100': 'age_45',
            }
        }
        for response_field in ['sex','age']:
            if response.get(response_field):
                for item in response.get(response_field):
                    response[fields_map[response_field][item['value']]] = item['visitors']

        super(GroupStatistic, self).parse(response)

class GroupStatisticAbstract(models.Model):
    class Meta:
        abstract = True

    visitors = models.PositiveIntegerField(u'Уникальные посетители', null=True)
    views = models.PositiveIntegerField(u'Просмотры', null=True)

    likes = models.PositiveIntegerField(u'Мне нравится', null=True)
    comments = models.PositiveIntegerField(u'Комментарии', null=True)
    shares = models.PositiveIntegerField(u'Рассказать друзьям', null=True)
    references = models.PositiveIntegerField(u'Упоминания', null=True)

    new_members = models.PositiveIntegerField(u'Новые участники', null=True)
    ex_members = models.PositiveIntegerField(u'Вышедшие участники', null=True)
    members = models.IntegerField(u'Всего участников', null=True) # strange, but there is possible negative values

    reach = models.PositiveIntegerField(u'Полный охват', null=True)
    reach_subsribers = models.PositiveIntegerField(u'Охват подписчиков', null=True)

    widget_users_views = models.PositiveIntegerField(u'Просмотры пользователей ВКонтакте', null=True)
    widget_members_views = models.PositiveIntegerField(u'Просмотры участников группы', null=True)
    widget_new_users = models.PositiveIntegerField(u'Новые участники', null=True)
    widget_ex_users = models.PositiveIntegerField(u'Вышедшие участники', null=True)

    ads_visitors = models.PositiveIntegerField(u'Зашедшие с рекламы', null=True)
    ads_members = models.PositiveIntegerField(u'Вступившие с рекламы', null=True)
    act_visitors = models.PositiveIntegerField(u'Зашедшие с акций', null=True)
    act_members = models.PositiveIntegerField(u'Вступившие с акций', null=True)

    section_discussions = models.PositiveIntegerField(u'Обсуждения', null=True)
    section_audio = models.PositiveIntegerField(u'Аудиозаписи', null=True)
    section_video = models.PositiveIntegerField(u'Видеозаписи', null=True)
    section_photoalbums = models.PositiveIntegerField(u'Фотоальбомы', null=True)
    section_applications = models.PositiveIntegerField(u'Приложения', null=True)
    section_documents = models.PositiveIntegerField(u'Документы', null=True)

    activity_wall = models.PositiveIntegerField(u'Сообщения на стене', null=True)
    activity_photos = models.PositiveIntegerField(u'Фотографии', null=True)
    activity_photo_comments = models.PositiveIntegerField(u'Комментарии к фотографиям', null=True)
    activity_videos = models.PositiveIntegerField(u'Видеозаписи', null=True)
    activity_video_comments = models.PositiveIntegerField(u'Комментарии к видеозаписям', null=True)
    activity_topics = models.PositiveIntegerField(u'Темы обсуждений', null=True)
    activity_topic_comments = models.PositiveIntegerField(u'Комментарии к обсуждениям', null=True)

    males = models.PositiveIntegerField(u'Мужчины', null=True)
    females = models.PositiveIntegerField(u'Женщины', null=True)

    age_18 = models.PositiveIntegerField(u'До 18', null=True)
    age_18_21 = models.PositiveIntegerField(u'От 18 до 21', null=True)
    age_21_24 = models.PositiveIntegerField(u'От 21 до 24', null=True)
    age_24_27 = models.PositiveIntegerField(u'От 24 до 27', null=True)
    age_27_30 = models.PositiveIntegerField(u'От 27 до 30', null=True)
    age_30_35 = models.PositiveIntegerField(u'От 30 до 35', null=True)
    age_35_45 = models.PositiveIntegerField(u'От 35 до 45', null=True)
    age_45 = models.PositiveIntegerField(u'От 45', null=True)

    reach_males = models.PositiveIntegerField(u'Мужчины', null=True)
    reach_females = models.PositiveIntegerField(u'Женщины', null=True)

    reach_age_18 = models.PositiveIntegerField(u'До 18', null=True)
    reach_age_18_21 = models.PositiveIntegerField(u'От 18 до 21', null=True)
    reach_age_21_24 = models.PositiveIntegerField(u'От 21 до 24', null=True)
    reach_age_24_27 = models.PositiveIntegerField(u'От 24 до 27', null=True)
    reach_age_27_30 = models.PositiveIntegerField(u'От 27 до 30', null=True)
    reach_age_30_35 = models.PositiveIntegerField(u'От 30 до 35', null=True)
    reach_age_35_45 = models.PositiveIntegerField(u'От 35 до 45', null=True)
    reach_age_45 = models.PositiveIntegerField(u'От 45', null=True)

class GroupStat(GroupStatisticAbstract):
    '''
    Group statistic model collecting information via parser
    '''
    class Meta:
        verbose_name = _('Vkontakte group statistic')
        verbose_name_plural = _('Vkontakte group statistics')
        unique_together = ('group','date')
        ordering = ('group','date')

    group = models.ForeignKey(Group, verbose_name=u'Группа', related_name='statistics')
    date = models.DateField(u'Дата')

    objects = GroupStatManager()

class GroupStatPercentage(models.Model):
    class Meta:
        verbose_name = _('Vkontakte group percetage statistic')
        verbose_name_plural = _('Vkontakte group percetage statistics')
        unique_together = ('group','type','value_type')
        ordering = ('group','-type','order')

    group = models.ForeignKey(Group, verbose_name=u'Группа', related_name='percentage_statistics')
    type = models.CharField(max_length=15)
    value_type = models.CharField(max_length=100)
    value_name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(u'Порядок', default=0)

    value = models.PositiveIntegerField(u'Значение', null=True)
    percents = models.FloatField(u'Проценты', null=True)

    objects = GroupStatPercentageManager()