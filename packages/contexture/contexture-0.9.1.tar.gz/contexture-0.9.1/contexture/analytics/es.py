'Shove objects to ElasticSearch'

# Memory leak here somewhere...

from collections import deque
import requests
import simplejson as json

from contexture import monitor


url = 'http://localhost:9200/_bulk'
batch_size = 30

buffer_ = deque()


# RTPAL hack:
# We need this hack to "normalize" post_params and get_params found
# in WebPage calls. Sometimes they are lists of tuples and sometimes
# they are dicts, ElasticSearch is not happy about that.
def transformed_params(d):
    # Turn *_params into lists of tuples
    if not isinstance(d, dict):
        return d

    ret = dict()
    for k, v in d.iteritems():
        if isinstance(v, dict):
            if k.endswith('_params'):
                v = v.items()
            else:
                v = transform_params(v)
        ret[k] = v
    return ret


def transform_params(d):
    # Same, but trasnform the object destructively
    for k, v in d.iteritems():
        if isinstance(v, dict):
            if k.endswith('_params'):
                d[k] = v.items()
            else:
                transform_params(v)


def main():
    objects = monitor.objects(verbose=True,
                              # capture_messages=True,
                              # binding_keys=['#.web_rtpal_server.#'],
                              # queue='analytics.es'
                              )
    # channel = objects.channel

    print 'Pushing objects to ElasticSearch'
    session = requests.session()
    #buffer_.clear()
    for obj in objects:
        rkey = obj.pop('rkey')
        buffer_.append({'index': dict(_ttl='7d',
                                      _index='contexture',
                                      _type=rkey.replace('.', '_'),
                                      _id=obj.pop('id'),
                                      # _timestamp={
                                      #     "enabled": True,
                                      #     "path": "end",
                                      #     "format": "YYYY-MM-dd HH:mm:ss"
                                      # }
                                      )})

        if 'WebPage' in rkey:
            #obj = transformed_params(obj)
            transform_params(obj)
        buffer_.append(obj)

        if len(buffer_) > batch_size * 2:
            data = b'\n'.join(map(json.dumps, buffer_)) + b'\n'
            r = session.post(url, data=data)
            if int(r.status_code) != 200:
                #print data
                print r.reason
                print r.text
            buffer_.clear()
        # channel.basic_publish('elasticsearch',
        #                       'elasticsearch',
        #                       '\n'.join(map(json.dumps, buffer_)) + '\n')

if __name__ == '__main__':
    main()
