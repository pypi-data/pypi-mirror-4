import dbm
import gflags
import urllib2

import md5 

FLAGS = gflags.FLAGS

gflags.DEFINE_string('url', 'http://www.wnyc.org/api/v1/recommendations/%(key)s/?mod=%(mod)d&frac=%(frac)d', 'URL to retrieve data')
gflags.DEFINE_string('key', None, 'Recommender API key.')
gflags.DEFINE_integer('shards', 2000, 'Number of shards.  Performance/accuracy tradeoff.')
gflags.DEFINE_string('cache', None, 'Filename of the local cache.')



class Fetcher:
    visited = set()

    @classmethod
    def load(cls, url):
        url_hash = md5.md5(url).hexdigest()[:24]
        if FLAGS.cache and not url_hash in cls.visited:
            cls.visited.add(url_hash)
            db = dbm.open(FLAGS.cache, 'c')
            if url_hash in db:
                return db[url_hash]
        else:
            db = None
        data = urllib2.urlopen(url).read()
        if db is not None:
            db[url_hash] = data
        db.close()
        return data
    
    
    @classmethod
    def loadall(cls, notify=lambda _:None, done=lambda:None):
        for shard in range(FLAGS.shards):
            url = FLAGS.url % dict(key=FLAGS.key,
                                 frac=FLAGS.shards,
                                 mod=shard)
            data = cls.load(url)
            notify((shard, data))
        if done:
            done()


