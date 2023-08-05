KEY = '05924db8ef5dea9c10b6e92ace19bfd4'
SECRET = '2a8f70e195a306e0'
CALLBACK = 'http://127.0.0.1/callback'

SCOPE_MAP = {
             'basic': ['douban_basic_common', 'community_basic_user'],
             'note': ['community_basic_note'],
             'miniblog': ['shuo_basic_r', 'shuo_basic_w', 'shuo_private'],
             'doumail': ['community_advanced_doumail_r', 'community_advanced_doumail_w'],
             'online': ['community_basic_online', 'community_advanced_online'],
             'photo': ['community_basic_photo', 'community_advanced_photo'],
             'music': ['music_basic_r', 'music_basic_w'],
             'movie': ['movie_basic_r', 'movie_basic_w'],
             'book': ['book_basic_r', 'book_basic_w'],
             'event': ['event_basic_r', 'event_basic_w,event_advanced_r'],
            }

SCOPE = ','.join(reduce(lambda x, y: x + y, SCOPE_MAP.values()))

TOKEN = '' #'0e6e7d9c101228e52b4b78d430367aaf'
