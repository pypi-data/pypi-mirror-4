'Shove objects to ElasticSearch'

from collections import deque
import requests
import simplejson as json

from contexture import monitor


url = 'localhost:9200/_bulk'
batch_size = 1
index = dict(_ttl='7d',
             _index='contexture',
             _type='object',
             _id=None)

buffer_ = deque()


def main():
    objects = monitor.objects(verbose=True,
                              capture_messages=True,
                              queue='analytics.es')
    # channel = objects.channel

    print 'Pushing objects to ElasticSearch'
    session = requests.session()
    #buffer_.clear()
    for obj in objects:
        buffer_.append({'index': dict(_ttl='7d',
                                      _index='lc',
                                      _type=obj.pop('rkey'),
                                      _id=obj.pop('id'),
                                      _timestamp={
                                          "enabled": True,
                                          "path": "end",
                                          "format": "YYYY-MM-dd HH:mm:ss"
                                      })})
        buffer_.append(obj)
        data = b'\n'.join(map(json.dumps, buffer_)) + b'\n'
        session.post(url, data=data)
        # channel.basic_publish('elasticsearch',
        #                       'elasticsearch',
        #                       '\n'.join(map(json.dumps, buffer_)) + '\n')

if __name__ == '__main__':
    main()
