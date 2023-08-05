# -*- coding: utf-8 -*-

class Scope(object):

    @classmethod
    def gets_by_item(cls, item):
        items = tuple(item) if isinstance(item, (tuple, list)) else (item,)
        scopes = [SCOPE.get(item, {}).keys() for item in items]
        scopes = reduce(lambda x, y: x + y, scopes)
        return ','.join(scopes)

SCOPE = { 
          'common': 
              { 
                  'douban_basic_common': '豆瓣公共api',
                  'community_basic_user': '豆瓣社区用户信息'
              },
          'note': 
              {
                  'community_basic_note': '豆瓣社区日记功能',
              },
          'photo':
              {  
                  'community_basic_photo': '豆瓣社区相册基本功能',
                  'community_advanced_photo': '豆瓣社区相册高级功能',
              },
          'doumail':
              {
                  'community_advanced_doumail_r': '豆瓣社区读豆邮功能',
                  'community_advanced_doumail_w': '豆瓣社区写豆邮功能',
              },
          'miniblog': 
              {
                  'shuo_basic_r': '获得你的个人信息，好友关系和我说', 
                  'shuo_basic_w': '修改你的个人信息、好友关系; 发布或修改你的广播',
                  'shuo_private': '获取共同关注用户信息',
              },
          'online': 
              {
                  'community_basic_online': '获取线上活动信息，参加者，论坛；获取热门线上活动列表',
                  'community_advanced_online': '线上活动高级功能',
              },
          'book': 
              { 
                  'book_basic_r': '读书基本读功能，包括获取书籍信息，评论等',
                  'book_basic_w': '读书基本写功能，包括发布、修改、删除读书评论',              
              },
          'music': 
              {
                  'music_basic_r': '豆瓣音乐基本读功能，包括获取音乐信息，评论等',
                  'music_basic_w': '豆瓣音乐基本写功能，包括发布，包括发布、修改、删除评论',    
              },
        }
