"""Validate actual model action outputs against a held-out LIBERO observation."""
import json
from pathlib import Path
import sys
import time

import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from examples.libero.main_incontext import (LIBERO_DUMMY_ACTION, _get_libero_env, _quat2axisangle, benchmark, get_task_to_index_mapping, LIBERO_TASKS_JSONL, LIBERO_UNSEEN_TASKS)
from openpi_client import image_tools
from openpi_client.websocket_client_policy import WebsocketClientPolicy

suite = benchmark.get_benchmark_dict()['libero_spatial']()
task_id = next(i for i in range(suite.n_tasks) if suite.get_task(i).language in LIBERO_UNSEEN_TASKS)
task = suite.get_task(task_id)
env, description = _get_libero_env(task, 256, 7)
try:
    env.reset()
    obs = env.set_init_state(suite.get_task_init_states(task_id)[0])
    for _ in range(10):
        obs, _, _, _ = env.step(LIBERO_DUMMY_ACTION)
    element = {
        'observation/image': image_tools.convert_to_uint8(image_tools.resize_with_pad(np.ascontiguousarray(obs['agentview_image'][::-1, ::-1]), 224, 224)),
        'observation/wrist_image': image_tools.convert_to_uint8(image_tools.resize_with_pad(np.ascontiguousarray(obs['robot0_eye_in_hand_image'][::-1, ::-1]), 224, 224)),
        'observation/state': np.concatenate((obs['robot0_eef_pos'], _quat2axisangle(obs['robot0_eef_quat']), obs['robot0_gripper_qpos'])),
        'prompt': description,
        'task_index': get_task_to_index_mapping(LIBERO_TASKS_JSONL)[description],
        'split': 'test',
    }
    client = WebsocketClientPolicy('127.0.0.1', 8000)
    results = []
    for i in range(3):
        start = time.monotonic()
        actions = np.asarray(client.infer(element)['actions'])
        elapsed = time.monotonic() - start
        if actions.shape != (50, 7) or not np.isfinite(actions).all():
            raise RuntimeError('Invalid policy actions: ' + str(actions.shape))
        np.savez_compressed(f'logs/reproduction/smoke-actions-{i}.npz', actions=actions)
        results.append({'request': i, 'seconds': elapsed, 'shape': list(actions.shape), 'dtype': str(actions.dtype), 'finite': True, 'min': float(actions.min()), 'max': float(actions.max())})
        print(json.dumps(results[-1]), flush=True)
    record = {'task': description, 'task_index': element['task_index'], 'initial_state_index': 0, 'requests': results, 'first_call_includes_jit_compilation': True}
    Path('logs/reproduction/smoke-inference.json').write_text(json.dumps(record, indent=2) + '\n')
finally:
    env.close()
