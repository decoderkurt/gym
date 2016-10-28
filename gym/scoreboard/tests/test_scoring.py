import numpy as np
from collections import defaultdict
from gym.benchmarks import registration, scoring

import gym
gym.undo_logger_setup()

benchmark = registration.Benchmark(
    id='TestBenchmark-v0',
    scorer=scoring.ClipTo01ThenAverage(),
    tasks=[
        {'env_id': 'CartPole-v0',
         'trials': 1,
         'max_timesteps': 5,
        },
        {'env_id': 'Pendulum-v0',
         'trials': 1,
         'max_timesteps': 5,
        },
    ]
)

def _is_close(x, target):
    return np.all(np.isclose(x, target))

def _assert_benchmark_result(result, score=None, solves=None, summed_training_seconds=None, start_to_finish_seconds=None):
    debug_str = "benchmark_result={}".format(result)
    if score is not None:
        assert _is_close(result['scores'], score), debug_str
    if solves is not None:
        assert np.all(result['solves']) == solves, debug_str

def _assert_benchmark_score(scores, score=None, num_envs_solved=None, summed_training_seconds=None, start_to_finish_seconds=None):
    debug_str = "scores={}".format(scores)
    if score is not None:
        assert _is_close(scores['score'], score), debug_str
    if num_envs_solved is not None:
        assert scores['num_envs_solved'] == num_envs_solved, debug_str
    if summed_training_seconds is not None:
        assert _is_close(scores['summed_training_seconds'], summed_training_seconds), debug_str
    if start_to_finish_seconds is not None:
        assert _is_close(scores['start_to_finish_seconds'], start_to_finish_seconds), debug_str

def _benchmark_result_helper(benchmark, **kwargs):
    for k, defval in dict(
            env_id='CartPole-v0',
            data_sources=[0],
            initial_reset_timestamps=[1],
            episode_lengths=[1],
            episode_rewards=[1],
            episode_types=['t'],
            timestamps=[2]).items():
        kwargs.setdefault(k, defval)

    return benchmark.score_evaluation(**kwargs)

def test_clip_average_scoring():
    benchmark = registration.Benchmark(
        id='TestBenchmark-v0',
        scorer=scoring.ClipTo01ThenAverage(num_episodes=1),
        tasks=[
            {'env_id': 'CartPole-v0',
             'trials': 1,
             'max_timesteps': 5,
            },
        ]
    )
    # simple scoring
    benchmark_result = _benchmark_result_helper(benchmark)
    _assert_benchmark_result(benchmark_result, score=0.01)

    # test a successful run
    benchmark_result = _benchmark_result_helper(benchmark, episode_rewards=[100])
    _assert_benchmark_result(benchmark_result, score=1.0, solves=True)

def test_clip_average_max_timesteps():
    benchmark = registration.Benchmark(
        id='TestBenchmark-v0',
        scorer=scoring.ClipTo01ThenAverage(num_episodes=2),
        tasks=[
            {'env_id': 'CartPole-v0',
             'trials': 1,
             'max_timesteps': 2,
            },
        ]
    )

    benchmark_result = _benchmark_result_helper(benchmark, data_sources=[0,0], episode_lengths=[1,1], episode_rewards=[1,1], episode_types=['t','t'], timestamps=[2,3])
    _assert_benchmark_result(benchmark_result, score=0.01)

    # make sure we only include the first result because of timesteps
    benchmark_result = _benchmark_result_helper(benchmark, data_sources=[0,0], episode_lengths=[1,100], episode_rewards=[1,100], episode_types=['t','t'], timestamps=[2,102])
    _assert_benchmark_result(benchmark_result, score=0.005, solves=False)

def test_clip_average_max_seconds():
    benchmark = registration.Benchmark(
        id='TestBenchmark-v0',
        scorer=scoring.ClipTo01ThenAverage(num_episodes=2),
        tasks=[
            {'env_id': 'CartPole-v0',
             'trials': 1,
             'max_seconds': 1,
            },
        ]
    )

    benchmark_result = _benchmark_result_helper(benchmark, data_sources=[0,0], episode_lengths=[100,100], episode_rewards=[0,100], episode_types=['t','t'], timestamps=[1.5, 2])
    _assert_benchmark_result(benchmark_result, score=0.5)

    # make sure we only include the first result because of wall clock time
    benchmark_result = _benchmark_result_helper(benchmark, data_sources=[0,0], episode_lengths=[100,100], episode_rewards=[0,100], episode_types=['t','t'], timestamps=[2,100])
    _assert_benchmark_result(benchmark_result, score=0.0)

def test_clip_average_benchmark_scoring():
    benchmark_results = defaultdict(list)
    for i, task in enumerate(benchmark.tasks):
        env_id = task.env_id
        benchmark_results[env_id].append(_benchmark_result_helper(benchmark, env_id=env_id, timestamps=[i + 2]))
    scores = scoring.benchmark_aggregate_score(benchmark, benchmark_results)

    _assert_benchmark_score(scores, score=0.0001, num_envs_solved=0, summed_training_seconds=3.0, start_to_finish_seconds=2.0)

def test_clip_average_benchmark_empty():
    scores = scoring.benchmark_aggregate_score(benchmark, {})

    benchmark_results = defaultdict(list)
    task = benchmark.tasks[0]
    env_id = task.env_id
    benchmark_results[env_id].append(_benchmark_result_helper(benchmark, env_id=env_id))
    scores = scoring.benchmark_aggregate_score(benchmark, benchmark_results)

    _assert_benchmark_score(scores, score=0.00005, num_envs_solved=0, summed_training_seconds=1.0, start_to_finish_seconds=1.0)

def test_clip_average_benchmark_solved():
    benchmark_results = defaultdict(list)
    N = 200
    for i, task in enumerate(benchmark.tasks):
        env_id = task.env_id
        benchmark_results[env_id].append(benchmark.score_evaluation(
            env_id,
            data_sources=[0] * N,
            initial_reset_timestamps=[1],
            episode_lengths=[1000] * N,
            episode_rewards=[1000] * N,
            episode_types=['t'] * N,
            timestamps=list(range(N)),
        ))
    scores = scoring.benchmark_aggregate_score(benchmark, benchmark_results)
    _assert_benchmark_score(scores, score=1.0, num_envs_solved=len(benchmark.tasks))

def test_clip_average_benchmark_incomplete():
    benchmark_results = defaultdict(list)
    env_id = benchmark.tasks[0].env_id
    benchmark_results[env_id].append(_benchmark_result_helper(benchmark, env_id=env_id, timestamps=[2]))
    scores = scoring.benchmark_aggregate_score(benchmark, benchmark_results)
    _assert_benchmark_score(scores, score=0.00005, num_envs_solved=0, summed_training_seconds=1.0, start_to_finish_seconds=1.0)

def test_clip_average_benchmark_extra():
    benchmark_results = defaultdict(list)
    for i, task in enumerate(benchmark.tasks):
        env_id = task.env_id
        benchmark_results[env_id].append(_benchmark_result_helper(benchmark, env_id=env_id, timestamps=[i + 2]))

    # add one more at the end with a high reward
    benchmark_results[env_id].append(_benchmark_result_helper(benchmark, env_id=env_id, episode_rewards=[100], timestamps=[2]))

    scores = scoring.benchmark_aggregate_score(benchmark, benchmark_results)
    _assert_benchmark_score(scores, score=0.0001, num_envs_solved=0, summed_training_seconds=3.0, start_to_finish_seconds=2.0)

# Tests for total reward scoring

reward_benchmark = registration.Benchmark(
    id='TestBenchmark-v0',
    scorer=scoring.TotalReward(),
    tasks=[
        {'env_id': 'CartPole-v0',
         'trials': 1,
         'max_timesteps': 5,
        },
        {'env_id': 'Pendulum-v0',
         'trials': 1,
         'max_timesteps': 5,
        },
    ]
)

def test_total_reward_clip_scoring():
    benchmark = registration.Benchmark(
        id='TestBenchmark-v0',
        scorer=scoring.TotalReward(),
        tasks=[
            {'env_id': 'CartPole-v0',
             'trials': 1,
             'max_timesteps': 5,
            },
        ]
    )
    # simple scoring
    benchmark_result = _benchmark_result_helper(benchmark)
    _assert_benchmark_result(benchmark_result, score=0.01)

    # test a successful run
    benchmark_result = _benchmark_result_helper(benchmark, episode_rewards=[100])
    _assert_benchmark_result(benchmark_result, score=1.0, solves=True)

def test_total_reward_max_timesteps():
    benchmark = registration.Benchmark(
        id='TestBenchmark-v0',
        scorer=scoring.TotalReward(),
        tasks=[
            {'env_id': 'CartPole-v0',
             'trials': 1,
             'max_timesteps': 2,
            },
        ]
    )

    benchmark_result = _benchmark_result_helper(benchmark, data_sources=[0,0], episode_lengths=[1,1], episode_rewards=[1,1], episode_types=['t','t'], timestamps=[2,3])
    _assert_benchmark_result(benchmark_result, score=0.01)

    # make sure we only include the first result because of timesteps
    benchmark_result = _benchmark_result_helper(benchmark, data_sources=[0,0], episode_lengths=[1,100], episode_rewards=[1,100], episode_types=['t','t'], timestamps=[2,102])
    _assert_benchmark_result(benchmark_result, score=0.01, solves=False)

def test_total_reward_max_seconds():
    benchmark = registration.Benchmark(
        id='TestBenchmark-v0',
        scorer=scoring.TotalReward(),
        tasks=[
            {'env_id': 'CartPole-v0',
             'trials': 1,
             'max_seconds': 1,
            },
        ]
    )

    benchmark_result = _benchmark_result_helper(benchmark, data_sources=[0,0], episode_lengths=[100,100], episode_rewards=[0,100], episode_types=['t','t'], timestamps=[1.5, 2])
    _assert_benchmark_result(benchmark_result, score=0.5)

    # make sure we only include the first result because of wall clock time
    benchmark_result = _benchmark_result_helper(benchmark, data_sources=[0,0], episode_lengths=[100,100], episode_rewards=[0,100], episode_types=['t','t'], timestamps=[2,100])
    _assert_benchmark_result(benchmark_result, score=0.0)

def test_total_reward_benchmark_scoring():
    benchmark_results = defaultdict(list)
    for i, task in enumerate(reward_benchmark.tasks):
        env_id = task.env_id
        benchmark_results[env_id].append(_benchmark_result_helper(reward_benchmark, env_id=env_id, timestamps=[i + 2]))
    scores = scoring.benchmark_aggregate_score(reward_benchmark, benchmark_results)

    _assert_benchmark_score(scores, score=0.01, num_envs_solved=0, summed_training_seconds=3.0, start_to_finish_seconds=2.0)

def test_total_reward_benchmark_empty():
    scores = scoring.benchmark_aggregate_score(reward_benchmark, {})

    benchmark_results = defaultdict(list)
    task = reward_benchmark.tasks[0]
    env_id = task.env_id
    benchmark_results[env_id].append(_benchmark_result_helper(reward_benchmark, env_id=env_id))
    scores = scoring.benchmark_aggregate_score(reward_benchmark, benchmark_results)

    _assert_benchmark_score(scores, score=0.005, num_envs_solved=0, summed_training_seconds=1.0, start_to_finish_seconds=1.0)

def test_total_reward_benchmark_solved():
    benchmark_results = defaultdict(list)
    N = 200
    for i, task in enumerate(reward_benchmark.tasks):
        env_id = task.env_id
        benchmark_results[env_id].append(reward_benchmark.score_evaluation(
            env_id,
            data_sources=[0] * N,
            initial_reset_timestamps=[1],
            episode_lengths=[1000] * N,
            episode_rewards=[1000] * N,
            episode_types=['t'] * N,
            timestamps=list(range(N)),
        ))
    scores = scoring.benchmark_aggregate_score(reward_benchmark, benchmark_results)
    _assert_benchmark_score(scores, score=1.0, num_envs_solved=len(reward_benchmark.tasks))

def test_total_reward_benchmark_incomplete():
    benchmark_results = defaultdict(list)
    env_id = reward_benchmark.tasks[0].env_id
    benchmark_results[env_id].append(_benchmark_result_helper(reward_benchmark, env_id=env_id, timestamps=[2]))
    scores = scoring.benchmark_aggregate_score(reward_benchmark, benchmark_results)
    _assert_benchmark_score(scores, score=0.005, num_envs_solved=0, summed_training_seconds=1.0, start_to_finish_seconds=1.0)

def test_total_reward_benchmark_extra():
    benchmark_results = defaultdict(list)
    for i, task in enumerate(reward_benchmark.tasks):
        env_id = task.env_id
        benchmark_results[env_id].append(_benchmark_result_helper(reward_benchmark, env_id=env_id, timestamps=[i + 2]))

    # add one more at the end with a high reward
    benchmark_results[env_id].append(_benchmark_result_helper(reward_benchmark, env_id=env_id, episode_rewards=[100], timestamps=[2]))

    scores = scoring.benchmark_aggregate_score(reward_benchmark, benchmark_results)
    _assert_benchmark_score(scores, score=0.01, num_envs_solved=0, summed_training_seconds=3.0, start_to_finish_seconds=2.0)

def test_total_reward_benchmark_simple():
    benchmark_results = defaultdict(list)
    for i, task in enumerate(reward_benchmark.tasks):
        env_id = task.env_id
        benchmark_results[env_id].append(_benchmark_result_helper(reward_benchmark, env_id=env_id, timestamps=[i + 2]))
    scores = scoring.benchmark_aggregate_score(reward_benchmark, benchmark_results)
    _assert_benchmark_score(scores, score=0.01, num_envs_solved=0, summed_training_seconds=3.0, start_to_finish_seconds=2.0)

def test_total_reward_benchmark_eval_handling():
    # make sure we count all episodes
    benchmark_results = defaultdict(list)
    for i, task in enumerate(reward_benchmark.tasks):
        env_id = task.env_id
        benchmark_results[env_id].append(reward_benchmark.score_evaluation(
            env_id,
            data_sources=[0, 1, 1],
            initial_reset_timestamps=[1, 1],
            episode_lengths=[1, 1, 1],
            episode_rewards=[1, 2, 3],
            episode_types=['e', 't', 'e'],
            timestamps=[i + 2, i + 3, i + 4],
        ))
    scores = scoring.benchmark_aggregate_score(reward_benchmark, benchmark_results)
    _assert_benchmark_score(scores, score=0.02, num_envs_solved=0, summed_training_seconds=10.0, start_to_finish_seconds=4.0)