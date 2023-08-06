from gevent.queue import JoinableQueue
from gevent import spawn, sleep
import json
import BaseHTTPServer

import scikits
import scikits.crab
from scikits.crab.models import MatrixPreferenceDataModel
from scikits.crab.metrics import pearson_correlation
from scikits.crab.similarities import UserSimilarity
from scikits.crab.recommenders.knn import UserBasedRecommender
from scikits.crab.models.utils import UserNotFoundError

import gflags
FLAGS = gflags.FLAGS

class Engine:
    def __init__(self):
        self.intake_que = JoinableQueue()

        self.data = {}
        self.process = spawn(self.process_incoming)


    def intake(self, data):
        self.intake_que.put(data)

    def process_incoming(self):
        for shard, data in self.intake_que:
            self.data[shard] = json.loads(data)
            sleep(0)

    def recommend(self, identity):
        print "Recommend for:", identity
        shard = identity % FLAGS.shards
        data = self.data.get(shard, {})
        if isinstance(data, dict) and not data:
            return dict(shard=shard, error='Not ready')
        for key in list(data):
            if len(data[key]) == 1:
                del(data[key])
        
        print "Loading model", len(data)
        model = MatrixPreferenceDataModel(data)
        print "Similarity"
        similarity = UserSimilarity(model, pearson_correlation)
        print "Recommender"
        recommender = UserBasedRecommender(model, similarity, with_preference=True)
        print "Making recommendation"
        try:
            recommend = recommender.recommend(str(identity))
        except UserNotFoundError:
            recomment = []
        print "Done:", recommend
        recommend = [(int(k), v) for k, v in recommend]
            
        return dict(shard=shard, data=recommend)


        

