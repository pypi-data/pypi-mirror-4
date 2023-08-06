from datetime import datetime
import operator
import random
import re

from config import CONFIG as cfg
from db import _key, msetbit, sequential_id

# This is pretty restrictive, but we can always relax it later.
VALID_EXPERIMENT_ALTERNATIVE_RE = re.compile(r"^[a-z0-9][a-z0-9\-_ ]*$", re.I)
RANDOM_SAMPLE = .2


class Client(object):

    def __init__(self, client_id, redis_conn):
        self.redis = redis_conn
        self.client_id = client_id
        self._sequential_id = None

    @property
    def sequential_id(self):
        if self._sequential_id is None:
            self._sequential_id = sequential_id(
                'internal_user_ids',
                self.client_id)
        return self._sequential_id


class ExperimentCollection(object):

    def __init__(self, redis_conn):
        self.redis = redis_conn
        self.experiments = []

    def __iter__(self):
        self.experiments = []
        for exp_key in self.redis.smembers(_key('experiments')):
            self.experiments.append(exp_key)

        return self

    def __next__(self):
        for i in self.experiments:
            yield Experiment.find(i, self.redis)


class Experiment(object):

    def __init__(self, name, alternatives, redis_conn):
        if len(alternatives) < 2:
            raise ValueError('experiments require at least two alternatives')

        self.name = name
        self.alternatives = Experiment.initialize_alternatives(
            name,
            alternatives,
            redis_conn)
        self.redis = redis_conn
        self.random_sample = RANDOM_SAMPLE

    def __repr__(self):
        return '<Experiment: {0} (version: {1})>'.format(self.name, self.version())

    def save(self):
        pipe = self.redis.pipeline()
        if self.is_new_record():
            pipe.sadd(_key('experiments'), self.name)

            # Set version to zero
            pipe.set(_key("experiments:{0}".format(self.name)), 0)

            # Empty desc by default
            pipe.hset(self.key(), 'description', '')

        pipe.hset(self.key(), 'created_at', datetime.now())
        # reverse here and use lpush to keep consistent with using lrange
        for alternative in reversed(self.alternatives):
            pipe.lpush("{0}:alternatives".format(self.key()), alternative.name)

        pipe.execute()

    def control(self):
        return self.alternatives[0]

    def created_at(self):
        return self.redis.hget(self.key(), 'created_at')

    def get_alternative_names(self):
        return [alt.name for alt in self.alternatives]

    def is_new_record(self):
        return not self.redis.sismember(_key("experiments"), self.name)

    def total_participants(self):
        key = _key("participations:{0}:_all:all".format(self.rawkey()))
        return self.redis.bitcount(key)


    def participants_by_day(self):
        return self._get_stats('participations', 'days')

    def participants_by_month(self):
        return self._get_stats('participations', 'months')

    def participants_by_year(self):
        return self._get_stats('participations', 'years')

    def total_conversions(self):
        key = _key("conversions:{0}:_all:users:all".format(self.rawkey()))
        return self.redis.bitcount(key)

    def conversions_by_day(self):
        return self._get_stats('conversions', 'days')

    def conversions_by_month(self):
        return self._get_stats('conversions', 'months')

    def conversions_by_year(self):
        return self._get_stats('conversions', 'years')

    def _get_stats(self, stat_type, stat_range):
        if stat_type not in ['participations', 'conversions']:
            raise ValueError

        if stat_range not in ['days', 'months', 'years']:
            raise ValueError

        stats = {}

        search_key = _key("{0}:{1}:{2}".format(stat_type, self.rawkey(), stat_range))
        keys = self.redis.smembers(search_key)
        for k in keys:
            mod = '' if stat_type == 'participations' else "users:"
            range_key = _key("{0}:{1}:_all:{2}{3}".format(stat_type, self.rawkey(), mod, k))
            print range_key
            stats[k] = self.redis.bitcount(range_key)

        return stats

    def update_description(self, description=None):
        self.redis.hset(self.key(), 'description', description or '')

    def get_description(self):
        return self.redis.hget(self.key(), 'description')

    def reset(self):
        self.increment_version()

        experiment = Experiment(self.name, self.get_alternative_names(), self.redis)
        experiment.save()

    def delete(self):
        pipe = self.redis.pipeline()
        pipe.srem(_key('experiments'), self.name)
        pipe.delete(self.key())
        pipe.delete(_key(self.rawkey()))
        pipe.delete(_key('experiments:{0}'.format(self.name)))

        # Consider a 'non-keys' implementation of this
        keys = self.redis.keys('*{0}*'.format(self.rawkey()))
        for key in keys:
            pipe.delete(key)

        pipe.execute()

    def archive(self):
        self.redis.hset(self.key(), 'archived', 1)

    def unarchive(self):
        self.redis.hdel(self.key(), 'archived')

    def is_archived(self):
        return self.redis.hexists(self.key(), 'archived')

    def version(self):
        version = self.redis.get(_key("experiments:{0}".format(self.name)))
        return int(version) if version else 0

    def increment_version(self):
        self.redis.incr(_key('experiments:{0}'.format(self.name)))

    def convert(self, client):
        alternative = self.get_alternative_by_client_id(client)

        if not alternative:  # TODO or has already converted?
            raise ValueError('this client was not participaing')

        alternative.record_conversion(client)

        return alternative.name

    def set_winner(self, alternative_name):
        if alternative_name not in self.get_alternative_names():
            raise ValueError('this alternative is not in this experiment')

        self.redis.set(self._winner_key, alternative_name)

    def has_winner(self):
        return self.redis.exists(self._winner_key)

    def get_winner(self):
        if self.has_winner():
            return self.redis.get(self._winner_key)

        return None

    def reset_winner(self):
        self.redis.delete(self._winner_key)

    @property
    def _winner_key(self):
        return "{0}:winner".format(self.key())

    def get_alternative(self, client):
        if self.is_archived():
            return self.control()

        chosen_alternative = self.get_alternative_by_client_id(client)
        if not chosen_alternative:
            chosen_alternative = self.choose_alternative(client=client)
            chosen_alternative.record_participation(client)

        return chosen_alternative

    def get_alternative_by_client_id(self, client):
        # TODO, THIS IS SCRATCH/PROTO
        # MOVE INTO A LUA SCRIPT
        for alternative in self.get_alternative_names():
            key = _key("participations:{0}:{1}:all".format(self.rawkey(), alternative))
            if self.redis.getbit(key, client.sequential_id):
                return Alternative(alternative, self.name, self.redis)

        return None

    def has_converted_by_client_id(self, client_id):
        # TODO, THIS IS SCRATCH/PROTO
        # MOVE INTO A LUA SCRIPT
        for alternative in self.get_alternative_names():
            key = _key("conversions:{0}:{1}:all".format(self.rawkey(), alternative))
            if self.redis.getbit(key, client_id):
                return True

        return False

    def choose_alternative(self, client=None):
        if cfg.get('disable_whiplash'):
            return self._random_choice()

        if random.random() < self.random_sample:
            return self._random_choice()
        else:
           return Alternative(self._whiplash(), self.name, self.redis)

    def _random_choice(self):
        return random.choice(self.alternatives)

    # my best attempt at implementing whiplash/multi-armed-bandit
    # math guy steve, help!
    def _whiplash(self):
        stats = {}
        for alternative in self.alternatives:
            participant_count = alternative.participant_count()
            completed_count = alternative.completed_count()
            stats[alternative.name] = self._arm_guess(participant_count, completed_count)

        return max(stats.iteritems(), key=operator.itemgetter(1))[0]

    def _arm_guess(self, participant_count, completed_count):
        fairness_score = 7

        a = max([participant_count, 0])
        b = max([participant_count - completed_count, 0])

        return random.betavariate(a + fairness_score, b + fairness_score)

    def rawkey(self):
        return "{0}/{1}".format(self.name, self.version())

    def key(self):
        key = "experiments:{0}".format(self.rawkey())
        return _key(key)

    @classmethod
    def find(cls, experiment_name, redis_conn):
        if redis_conn.sismember(_key("experiments"), experiment_name):
            return cls(experiment_name, Experiment.load_alternatives(experiment_name, redis_conn), redis_conn)
        else:
            raise ValueError('experiment does not exist')

    @classmethod
    def find_or_create(cls, experiment_name, alternatives, redis_conn):
        if len(alternatives) < 2:
            raise ValueError('experiments require at least two alternatives')

        # We don't use the class method key here
        if redis_conn.sismember(_key("experiments"), experiment_name):
            # Note during refactor:
            # We're not instanciating a new Experiment, rather than this load_alternatives hackery
            exp = Experiment.find(experiment_name, redis_conn)

            # get the existing alternatives
            current_alternatives = exp.get_alternative_names()

            # Make sure the alternative options are correct.
            # If they are not, then we have to make a new version
            # above `experiment` is then returned eventually
            if sorted(current_alternatives) != sorted(alternatives):
                exp.increment_version()

                # initialize a new one
                experiment = cls(experiment_name, alternatives, redis_conn)
                experiment.save()
            else:
                experiment = exp
        # completely new experiment
        else:
            experiment = cls(experiment_name, alternatives, redis_conn)
            experiment.save()

        return experiment

    @staticmethod
    def all(redis_conn, exclude_archived=True):
        experiments = []
        keys = redis_conn.smembers(_key('experiments'))

        for key in keys:
            experiment = Experiment.find(key, redis_conn)
            if experiment.is_archived() and exclude_archived:
                continue
            experiments.append(Experiment.find(key, redis_conn))

        return experiments

    @staticmethod
    def load_alternatives(experiment_name, redis_conn):
        # get latest version of experiment
        version = redis_conn.get(_key("experiments:{0}".format(experiment_name)))
        key = _key("experiments:{0}/{1}:alternatives".format(experiment_name, version))
        return redis_conn.lrange(key, 0, -1)

    @staticmethod
    def initialize_alternatives(experiment_name, alternatives, redis_conn):
        for alternative_name in alternatives:
            if not Alternative.is_valid(alternative_name):
                raise ValueError('invalid alternative name')

        return [Alternative(n, experiment_name, redis_conn) for n in alternatives]

    @staticmethod
    def is_valid(experiment_name):
        return (isinstance(experiment_name, basestring) and
                VALID_EXPERIMENT_ALTERNATIVE_RE.match(experiment_name) is not None)


class AlternativeCollection(object):

    def __init__(self, redis_conn):
        self.redis = redis_conn
        self.alternatives = []

    # def __iter__(self):
    #     self.alternatives = []
    #     for exp_key in self.redis.smembers(_key('experiments')):
    #         self.experiments.append(exp_key)

    #     return self

    # def __next__(self):
    #     for i in self.alternatives:
    #         yield Experiment.find(i)


class Alternative(object):

    def __init__(self, name, experiment_name, redis_conn):
        self.name = name
        self.experiment_name = experiment_name
        self.redis = redis_conn

    def __repr__(self):
        return "<Alternative {0} (Experiment {1})".format(self.name, self.experiment_name)

    def is_control(self):
        return self.experiment().control().name == self.name

    def is_winner(self):
        return self.experiment().has_winner() and self.experiment().get_winner() == self.name

    def experiment(self):
        return Experiment.find(self.experiment_name, self.redis)

    def participant_count(self):
        key = _key("participations:{0}:{1}:all".format(self.experiment().rawkey(), self.name))
        return self.redis.bitcount(key)

    def participants_by_day(self):
        return self._get_stats('participations', 'days')

    def participants_by_month(self):
        return self._get_stats('participations', 'months')

    def participants_by_year(self):
        return self._get_stats('participations', 'years')

    def completed_count(self):
        key = _key("conversions:{0}:{1}:users:all".format(self.experiment().rawkey(), self.name))
        return self.redis.bitcount(key)

    def conversions_by_day(self):
        return self._get_stats('conversions', 'days')

    def conversions_by_month(self):
        return self._get_stats('conversions', 'months')

    def conversions_by_year(self):
        return self._get_stats('conversions', 'years')

    def _get_stats(self, stat_type, stat_range):
        if stat_type not in ['participations', 'conversions']:
            raise ValueError

        if stat_range not in ['days', 'months', 'years']:
            raise ValueError

        stats = {}

        exp_key = self.experiment().rawkey()
        search_key = _key("{0}:{1}:{2}".format(stat_type, exp_key, stat_range))
        keys = self.redis.smembers(search_key)
        for k in keys:
            name = self.name if stat_type == 'participations' else "{0}:users".format(self.name)
            range_key = _key("{0}:{1}:{2}:{3}".format(stat_type, exp_key, name, k))
            stats[k] = self.redis.bitcount(range_key)

        return stats

    def record_participation(self, client):
        """Record a user's participation in a test along with a given variation"""
        date = datetime.now()

        experiment_key = self.experiment().rawkey()

        pipe = self.redis.pipeline()

        pipe.sadd(_key("participations:{0}:years".format(experiment_key)), date.strftime('%Y'))
        pipe.sadd(_key("participations:{0}:months".format(experiment_key)), date.strftime('%Y-%m'))
        pipe.sadd(_key("participations:{0}:days".format(experiment_key)), date.strftime('%Y-%m-%d'))

        pipe.execute()

        keys = [
            _key("participations:{0}:_all:all".format(experiment_key)),
            _key("participations:{0}:_all:{1}".format(experiment_key, date.strftime('%Y'))),
            _key("participations:{0}:_all:{1}".format(experiment_key, date.strftime('%Y-%m'))),
            _key("participations:{0}:_all:{1}".format(experiment_key, date.strftime('%Y-%m-%d'))),
            _key("participations:{0}:{1}:all".format(experiment_key, self.name)),
            _key("participations:{0}:{1}:{2}".format(experiment_key, self.name, date.strftime('%Y'))),
            _key("participations:{0}:{1}:{2}".format(experiment_key, self.name, date.strftime('%Y-%m'))),
            _key("participations:{0}:{1}:{2}".format(experiment_key, self.name, date.strftime('%Y-%m-%d'))),
        ]
        msetbit(keys=keys, args=([client.sequential_id, 1] * len(keys)))

    def record_conversion(self, client):
        """Record a user's conversion in a test along with a given variation"""
        date = datetime.now()
        experiment_key = self.experiment().rawkey()

        pipe = self.redis.pipeline()

        pipe.sadd(_key("conversions:{0}:years".format(experiment_key)), date.strftime('%Y'))
        pipe.sadd(_key("conversions:{0}:months".format(experiment_key)), date.strftime('%Y-%m'))
        pipe.sadd(_key("conversions:{0}:days".format(experiment_key)), date.strftime('%Y-%m-%d'))

        pipe.execute()

        keys = [
            _key("conversions:{0}:_all:users:all".format(experiment_key)),
            _key("conversions:{0}:_all:users:{1}".format(experiment_key, date.strftime('%Y'))),
            _key("conversions:{0}:_all:users:{1}".format(experiment_key, date.strftime('%Y-%m'))),
            _key("conversions:{0}:_all:users:{1}".format(experiment_key, date.strftime('%Y-%m-%d'))),
            _key("conversions:{0}:{1}:users:all".format(experiment_key, self.name)),
            _key("conversions:{0}:{1}:users:{2}".format(experiment_key, self.name, date.strftime('%Y'))),
            _key("conversions:{0}:{1}:users:{2}".format(experiment_key, self.name, date.strftime('%Y-%m'))),
            _key("conversions:{0}:{1}:users:{2}".format(experiment_key, self.name, date.strftime('%Y-%m-%d'))),
        ]
        msetbit(keys=keys, args=([client.sequential_id, 1] * len(keys)))

    def conversion_rate(self):
        try:
            return self.completed_count() / float(self.participant_count())
        except ZeroDivisionError:
            return 0

    def z_score(self):

        if self.is_control():
            return 'N/A'

        control = self.experiment().control()
        ctr_e = self.conversion_rate()
        ctr_c = control.conversion_rate()

        e = self.participant_count()
        c = control.participant_count()

        try:
            std_dev = pow(((ctr_e / pow(ctr_c, 3)) * ((e*ctr_e)+(c*ctr_c)-(ctr_c*ctr_e)*(c+e))/(c*e)), 0.5)
            z_score = ((ctr_e / ctr_c) -1 ) / std_dev
            return z_score
        except ZeroDivisionError:
            return 0

    def confidence_level(self):
        z_score = self.z_score()
        if z_score == 'N/A':
            return z_score

        z_score = abs(round(z_score, 3))

        ret = ''
        if z_score == 0.0:
            ret = 'No Change'
        elif z_score < 1.96:
            ret = 'No Confidence'
        elif z_score < 2.57:
            ret = '95% Confidence'
        elif z_score < 3.27:
            ret = '99% Confidence'
        else:
            ret = '99.9% Confidence'

        return ret

    def key(self):
        return _key("{0}:{1}".format(self.experiment_name, self.name))

    @staticmethod
    def is_valid(alternative_name):
        return (isinstance(alternative_name, basestring) and
                VALID_EXPERIMENT_ALTERNATIVE_RE.match(alternative_name) is not None)
