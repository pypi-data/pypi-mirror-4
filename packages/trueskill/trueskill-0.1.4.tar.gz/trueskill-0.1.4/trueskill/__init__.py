# -*- coding: utf-8 -*-
"""
    trueskill
    ~~~~~~~~~

    This module implements the TrueSkill rating system.

    :copyright: (c) 2012 by Heungsub Lee.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
import itertools
import math

from .mathematics import cdf, pdf, ppf, Gaussian, Matrix


__copyright__ = 'Copyright 2012 by Heungsub Lee'
__license__ = 'BSD License'
__author__ = 'Heungsub Lee'
__email__ = 'h''@''subl.ee'
__version__ = '0.1.4'
__all__ = ['TrueSkill', 'Rating', 'transform_ratings', 'match_quality',
           'calc_draw_probability', 'calc_draw_margin', 'setup',
           'MU', 'SIGMA', 'BETA', 'TAU', 'DRAW_PROBABILITY']


#: default initial mean of ratings
MU = 25.
#: default initial standard deviation of ratings
SIGMA = MU / 3
#: default guarantee about an 80% chance of winning
BETA = SIGMA / 2
#: default dynamic factor
TAU = SIGMA / 100
#: default draw probability of the game
DRAW_PROBABILITY = .10
#: a basis to check reliability of the result
DELTA = 0.0001


def V(diff, draw_margin):
    """The non-draw version of "V" function. "V" calculates a variation of a
    mean.
    """
    x = diff - draw_margin
    return pdf(x) / cdf(x)


def W(diff, draw_margin):
    """The non-draw version of "W" function. "W" calculates a variation of a
    standard deviation.
    """
    x = diff - draw_margin
    v = V(diff, draw_margin)
    return v * (v + x)


def V_draw(diff, draw_margin):
    """The draw version of "V" function."""
    abs_diff = abs(diff)
    a, b = draw_margin - abs_diff, -draw_margin - abs_diff
    denom = cdf(a) - cdf(b)
    numer = pdf(b) - pdf(a)
    return numer / denom * (-1 if diff < 0 else 1)


def W_draw(diff, draw_margin):
    """The draw version of "W" function."""
    abs_diff = abs(diff)
    a, b = draw_margin - abs_diff, -draw_margin - abs_diff
    denom = cdf(a) - cdf(b)
    v = V_draw(abs_diff, draw_margin)
    return (v ** 2) + (a * pdf(a) - b * pdf(b)) / denom


def calc_draw_probability(draw_margin, beta, size):
    """Calculates a draw-probability from the given ``draw_margin``."""
    return 2 * cdf(draw_margin / (math.sqrt(size) * beta)) - 1


def calc_draw_margin(draw_probability, beta, size):
    """Calculates a draw-margin from the given ``draw_probability``."""
    return ppf((draw_probability + 1) / 2.) * math.sqrt(size) * beta


def _team_sizes(rating_groups):
    """Makes a size map of each teams."""
    team_sizes = [0]
    for group in rating_groups:
        team_sizes.append(len(group) + team_sizes[-1])
    del team_sizes[0]
    return team_sizes


class Rating(Gaussian):
    """Represents a player's skill as Gaussian distrubution. The default mu and
    sigma value follows the global TrueSkill environment's settings.

    :param mu: mean
    :param sigma: standard deviation
    """

    def __init__(self, mu=None, sigma=None):
        if isinstance(mu, tuple):
            mu, sigma = mu
        if mu is None:
            mu = g().mu
        if sigma is None:
            sigma = g().sigma
        super(Rating, self).__init__(mu, sigma)

    @property
    def exposure(self):
        """A value that will go up on the whole."""
        return self.mu - 3 * self.sigma

    def __iter__(self):
        return iter((self.mu, self.sigma))

    def __repr__(self):
        args = (type(self).__name__, self.mu, self.sigma)
        return '%s(mu=%.3f, sigma=%.3f)' % args


class TrueSkill(object):
    """Implements a TrueSkill environment. An environment could have customized
    constants. Every games have not same design and may need to customize
    TrueSkill constants. For example, 60% of matches in your game have finished
    as draw then you should set ``draw_probability`` to 0.60.

    >>> my_env = TrueSkill(draw_probability=0.60)

    :param mu: initial mean of ratings
    :param sigma: initial standard deviation of ratings
    :param beta: guarantee about an 80% chance of winning
    :param tau: dynamic factor
    :param draw_probability: draw probability of the game

    For more details of the constants, see `The Math Behind TrueSkill
    <http://bit.ly/trueskill-math>`_.
    """

    def __init__(self, mu=MU, sigma=SIGMA, beta=BETA, tau=TAU,
                 draw_probability=DRAW_PROBABILITY):
        self.mu = mu
        self.sigma = sigma
        self.beta = beta
        self.tau = tau
        self.draw_probability = draw_probability

    def Rating(self, mu=None, sigma=None):
        """Initializes new :class:`Rating` object, but it fixes default mu and
        sigma to the environment's.

        >>> env = TrueSkill(mu=0, sigma=1)
        >>> env.Rating()
        Rating(mu=0.000, sigma=1.000)
        """
        if mu is None:
            mu = self.mu
        if sigma is None:
            sigma = self.sigma
        return Rating(mu, sigma)

    def make_as_global(self):
        """Registers the environment as the global environment.

        >>> env = TrueSkill(mu=50)
        >>> Rating()
        Rating(mu=25.000, sigma=8.333)
        >>> env.make_as_global() #doctest: +ELLIPSIS
        <TrueSkill mu=50...>
        >>> Rating()
        Rating(mu=50.000, sigma=8.333)

        But if you need just one environment, use :func:`setup` instead.
        """
        return setup(env=self)

    def validate_rating_groups(self, rating_groups):
        """Validates a ``rating_groups`` argument. It should contain more than
        2 groups and all groups must not be empty.

        >>> env = TrueSkill()
        >>> env.validate_rating_groups([])
        Traceback (most recent call last):
            ...
        ValueError: need multiple rating groups
        >>> env.validate_rating_groups([(Rating(),)])
        Traceback (most recent call last):
            ...
        ValueError: need multiple rating groups
        >>> env.validate_rating_groups([(Rating(),), ()])
        Traceback (most recent call last):
            ...
        ValueError: each group must contain multiple ratings
        >>> env.validate_rating_groups([(Rating(),), (Rating(),)])
        ... #doctest: +ELLIPSIS
        [(Rating(...),), (Rating(...),)]
        """
        rating_groups = [(x,) if isinstance(x, Rating) else x \
                         for x in rating_groups]
        if len(rating_groups) < 2:
            raise ValueError('need multiple rating groups')
        elif 0 in map(len, rating_groups):
            raise ValueError('each group must contain multiple ratings')
        return list(rating_groups)

    def build_factor_graph(self, rating_groups, ranks):
        """Makes nodes for the factor graph."""
        from .factorgraph import Variable, PriorFactor, LikelihoodFactor, \
                                 SumFactor, TruncateFactor
        ratings = sum(rating_groups, ())
        size = len(ratings)
        group_size = len(rating_groups)
        # create variables
        rating_vars = [Variable() for x in xrange(size)]
        perf_vars = [Variable() for x in xrange(size)]
        teamperf_vars = [Variable() for x in xrange(group_size)]
        teamdiff_vars = [Variable() for x in xrange(group_size - 1)]
        team_sizes = _team_sizes(rating_groups)
        def get_perf_vars_by_team(team):
            if team > 0:
                start = team_sizes[team - 1]
            else:
                start = 0
            end = team_sizes[team]
            return perf_vars[start:end]
        # layer builders
        def build_rating_layer():
            for rating_var, rating in zip(rating_vars, ratings):
                yield PriorFactor(rating_var, rating, self.tau)
        def build_perf_layer():
            for rating_var, perf_var in zip(rating_vars, perf_vars):
                yield LikelihoodFactor(rating_var, perf_var, self.beta ** 2)
        def build_teamperf_layer():
            for team, teamperf_var in enumerate(teamperf_vars):
                child_perf_vars = get_perf_vars_by_team(team)
                yield SumFactor(teamperf_var, child_perf_vars,
                                [1] * len(child_perf_vars))
        def build_teamdiff_layer():
            for team, teamdiff_var in enumerate(teamdiff_vars):
                yield SumFactor(teamdiff_var, teamperf_vars[team:team + 2],
                                [+1, -1])
        def build_trunc_layer():
            for x, teamdiff_var in enumerate(teamdiff_vars):
                size = sum(len(group) for group in rating_groups[x:x + 2])
                draw_margin = calc_draw_margin(self.draw_probability,
                                               self.beta, size)
                if ranks[x] == ranks[x + 1]:
                    v_func, w_func = V_draw, W_draw
                else:
                    v_func, w_func = V, W
                yield TruncateFactor(teamdiff_var, v_func, w_func, draw_margin)
        # build layers
        return list(build_rating_layer()), \
               list(build_perf_layer()), \
               list(build_teamperf_layer()), \
               list(build_teamdiff_layer()), \
               list(build_trunc_layer())

    def run_schedule(self, rating_layer, perf_layer, teamperf_layer,
                     teamdiff_layer, trunc_layer, min_delta=DELTA):
        """Sends messages within every nodes of the factor graph until the
        result is reliable.
        """
        # gray arrows
        for f in itertools.chain(rating_layer, perf_layer, teamperf_layer):
            f.down()
        # arrow #1, #2, #3
        teamdiff_len = len(teamdiff_layer)
        for x in xrange(10):
            if teamdiff_len == 1:
                # only two teams
                teamdiff_layer[0].down()
                delta = trunc_layer[0].up()
            else:
                # multiple teams
                delta = 0
                for x in xrange(teamdiff_len - 1):
                    teamdiff_layer[x].down()
                    delta = max(delta, trunc_layer[x].up())
                    teamdiff_layer[x].up(1) # up to right variable
                for x in xrange(teamdiff_len - 1, 0, -1):
                    teamdiff_layer[x].down()
                    delta = max(delta, trunc_layer[x].up())
                    teamdiff_layer[x].up(0) # up to left variable
            # repeat until to small update
            if delta <= min_delta:
                break
        # up both ends
        teamdiff_layer[0].up(0)
        teamdiff_layer[teamdiff_len - 1].up(1)
        # up the remainder of the black arrows
        for f in teamperf_layer:
            for x in xrange(len(f.vars) - 1):
                f.up(x)
        for f in perf_layer:
            f.up()

    def transform_ratings(self, rating_groups, ranks=None, min_delta=DELTA):
        """Calculates transformed ratings from the given rating groups by the
        ranking table.
        
        ``rating_groups`` is a list of rating tuples that correspond each team
        of the match. ``ranks`` is rakings of the teams that can be omitted if
        the ranking is same as the order of ``rating_groups``.

        >>> env = TrueSkill()
        >>> team1 = (env.Rating(20), env.Rating(21)) # winner
        >>> team2 = (env.Rating(22), env.Rating(23)) # loser
        >>> env.transform_ratings(rating_groups=[team1, team2])
        ... #doctest: +NORMALIZE_WHITESPACE
        [(Rating(mu=23.645, sigma=7.736), Rating(mu=24.645, sigma=7.736)),
         (Rating(mu=18.355, sigma=7.736), Rating(mu=19.355, sigma=7.736))]

        You can replace the old ratings like:

        >>> (team1, team2) = tuple(env.transform_ratings([team1, team2]))
        >>> team1[0]
        Rating(mu=23.645, sigma=7.736)

        :param rating_groups: a list of tuples that contain :class:`Rating`
                              objects
        :param ranks: a ranking table. by default, it is same as the order of
                      the ``rating_groups``
        :param min_delta: each loop checks a delta of changes, and the loop
                          will stop if the delta is less then this argument
        """
        rating_groups = self.validate_rating_groups(rating_groups)
        group_size = len(rating_groups)
        # sort rating groups by rank
        if ranks is None:
            ranks = range(group_size)
        elif len(ranks) != group_size:
            raise ValueError('wrong ranks')
        def compare(x, y):
            return cmp(x[1][0], y[1][0])
        sorting = sorted(enumerate(zip(ranks, rating_groups)), compare)
        sorted_groups = [g for x, (r, g) in sorting]
        sorted_ranks = sorted(ranks)
        unsorting_hint = [x for x, (r, g) in sorting]
        # build factor graph
        layers = self.build_factor_graph(sorted_groups, sorted_ranks)
        self.run_schedule(*layers, min_delta=min_delta)
        # make result
        rating_layer, team_sizes = layers[0], _team_sizes(sorted_groups)
        transformed_groups = []
        for start, end in zip([0] + team_sizes[:-1], team_sizes):
            group = []
            for f in rating_layer[start:end]:
                group.append(Rating(f.var.mu, f.var.sigma))
            transformed_groups.append(tuple(group))
        def compare(x, y):
            return cmp(x[0], y[0])
        unsorting = sorted(zip(unsorting_hint, transformed_groups), compare)
        return [g for x, g in unsorting]

    def match_quality(self, rating_groups):
        """Calculates the match quality of the given rating groups. A result
        is the draw probability in the association.

        >>> env = TrueSkill()
        >>> rating_groups = [(env.Rating(25, 0.001),),
        ...                  (env.Rating(25, 0.001),)]
        >>> print env.match_quality(rating_groups)
        0.9999999712

        :param rating_groups: a list of tuples that contain :class:`Rating`
                              objects
        """
        rating_groups = self.validate_rating_groups(rating_groups)
        ratings = sum(rating_groups, ())
        length = len(ratings)
        # a vector of all of the skill means
        mean_matrix = Matrix([[r.mu] for r in ratings])
        # a matrix whose diagonal values are the variances (sigma^2) of each
        # of the players.
        def variance_matrix(width, height):
            for x, variance in enumerate(r.sigma ** 2 for r in ratings):
                yield (x, x), variance
        variance_matrix = Matrix(variance_matrix, length, length)
        # the player-team assignment and comparison matrix
        def rotated_a_matrix(set_width, set_height):
            t = 0
            for r, (cur, next) in enumerate(zip(rating_groups[:-1],
                                                rating_groups[1:])):
                for x in xrange(t, t + len(cur)):
                    yield (r, x), 1
                    t += 1
                x += 1
                for x in xrange(x, x + len(next)):
                    yield (r, x), -1
            set_width(x + 1)
            set_height(r + 1)
        rotated_a_matrix = Matrix(rotated_a_matrix)
        a_matrix = rotated_a_matrix.transpose()
        # match quality further derivation
        _ata = (self.beta ** 2) * rotated_a_matrix * a_matrix
        _atsa = rotated_a_matrix * variance_matrix * a_matrix
        start = mean_matrix.transpose() * a_matrix
        middle = _ata + _atsa
        end = rotated_a_matrix * mean_matrix
        # make result
        e_arg = (-0.5 * start * middle.inverse() * end).determinant()
        s_arg = _ata.determinant() / middle.determinant()
        return math.exp(e_arg) * math.sqrt(s_arg)

    def __repr__(self):
        args = (type(self).__name__, self.mu, self.sigma, self.beta, \
                self.tau, self.draw_probability * 100)
        return '<%s mu=%.3f sigma=%.3f beta=%.3f tau=%.3f ' \
               'draw_probability=%.1f%%>' % args


def transform_ratings(rating_groups, ranks=None, min_delta=DELTA):
    """A proxy function for :meth:`TrueSkill.transform_ratings` of the global
    TrueSkill environment.
    """
    return g().transform_ratings(rating_groups, ranks, min_delta)


def match_quality(rating_groups):
    """A proxy function for :meth:`TrueSkill.match_quality` of the global
    TrueSkill environment.
    """
    return g().match_quality(rating_groups)


_global = []
def g():
    """Gets the global TrueSkill environment."""
    if not _global:
        setup() # setup the default environment
    return _global[0]


def setup(mu=MU, sigma=SIGMA, beta=BETA, tau=TAU,
          draw_probability=DRAW_PROBABILITY, env=None):
    """Setups the global TrueSkill environment.

    >>> Rating()
    Rating(mu=25.000, sigma=8.333)
    >>> setup(mu=50) #doctest: +ELLIPSIS
    <TrueSkill mu=50...>
    >>> Rating()
    Rating(mu=50.000, sigma=8.333)
    """
    try:
        _global.pop()
    except IndexError:
        pass
    _global.append(env or TrueSkill(mu, sigma, beta, tau, draw_probability))
    return g()
