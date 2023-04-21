from ray.rllib.algorithms.mbmpo import MBMPOConfig
from ray import serve

"""
This is in-progress and not yet being used anywhere
Ray:
https://docs.ray.io/en/latest/serve/tutorials/rllib.html
https://github.com/ray-project/ray/blob/master/rllib/algorithms/mbmpo/mbmpo.py
https://docs.ray.io/en/latest/ray-overview/index.html

Other Useful docs:
https://dev.to/mage_ai/how-does-tiktok-use-machine-learning-5b7i
"""

from starlette.requests import Request
import requests


@serve.deployment
class ServePPOModel:
    def __init__(self, checkpoint_path) -> None:
        # Re-create the originally used config.
        config = MBMPOConfig()\
            .framework("torch")\
            .rollouts(num_rollout_workers=0)
        # Build the Algorithm instance using the config.
        self.algorithm = config.build(env="CartPole-v0")
        # Restore the algo's state from the checkpoint.
        self.algorithm.restore(checkpoint_path)

    async def __call__(self, request: Request):
        json_input = await request.json()
        obs = json_input["observation"]

        action = self.algorithm.compute_single_action(obs)
        return {"action": int(action)}


def get_model_action(obs):
    print(f"-> Sending observation {obs}")
    resp = requests.get(
        "http://localhost:8000/", json={"observation": obs.tolist()}
    )
    print(f"<- Received response {resp.json()}")
    return {resp.json()}
