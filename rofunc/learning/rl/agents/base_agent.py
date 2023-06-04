from typing import Union, Tuple, Dict, Optional

import os
import rofunc as rf
import gym
import gymnasium
import numpy as np
import torch
import collections
from omegaconf import DictConfig

from rofunc.learning.rl.utils.memory import Memory


class BaseAgent:
    def __init__(self,
                 cfg: DictConfig,
                 observation_space: Optional[Union[int, Tuple[int], gym.Space, gymnasium.Space]],
                 action_space: Optional[Union[int, Tuple[int], gym.Space, gymnasium.Space]],
                 memory: Optional[Union[Memory, Tuple[Memory]]] = None,
                 device: Optional[Union[str, torch.device]] = None,
                 experiment_dir: Optional[str] = None,
                 rofunc_logger: Optional[rf.utils.BeautyLogger] = None
                 ):
        """
        Base class of Rofunc RL Agents.
        :param cfg: Custom configuration
        :param observation_space: Observation/state space or shape
        :param action_space: Action space or shape
        :param memory: Memory for storing transitions
        :param device: Device on which the torch tensor is allocated
        """
        self.cfg = cfg
        self.observation_space = observation_space
        self.action_space = action_space
        self.memory = memory
        self.device = device
        self.experiment_dir = experiment_dir
        self.rofunc_logger = rofunc_logger

        '''Checkpoint'''
        self.checkpoint_modules = {}
        self.checkpoint_interval = self.cfg.get("Trainer", {}).get("checkpoint_interval", 1000)
        if self.checkpoint_interval > 0:
            self.checkpoint_dir = os.path.join(self.experiment_dir, "checkpoints")
            rf.file.create_dir(self.checkpoint_dir)
        # self.checkpoint_store_separately = self.cfg.get("Trainer", {}).get("store_separately", False)
        self.checkpoint_best_modules = {"timestep": 0, "reward": -2 ** 31, "saved": False, "modules": {}}

        '''Logging'''
        self.track_rewards = collections.deque(maxlen=100)
        self.track_timesteps = collections.deque(maxlen=100)
        self.cumulative_rewards = None
        self.cumulative_timesteps = None
        self.tracking_data = collections.defaultdict(list)

    def act(self, states: torch.Tensor, timestep: int = None):
        """
        Make a decision based on the current state.
        :param states: current environment states
        :param timestep: current timestep
        :return: action
        """
        raise NotImplementedError

    def track_data(self, tag: str, value: float) -> None:
        self.tracking_data[tag].append(value)

    def store_transition(self, states: torch.Tensor, actions: torch.Tensor, rewards: torch.Tensor,
                         next_states: torch.Tensor, terminated: torch.Tensor, truncated: torch.Tensor,
                         infos: torch.Tensor):
        """
        Record the transition.
        """
        if self.cumulative_rewards is None:
            self.cumulative_rewards = torch.zeros_like(rewards, dtype=torch.float32)
            self.cumulative_timesteps = torch.zeros_like(rewards, dtype=torch.int32)

        self.cumulative_rewards.add_(rewards)
        self.cumulative_timesteps.add_(1)

        # check ended episodes
        finished_episodes = (terminated + truncated).nonzero(as_tuple=False)
        if finished_episodes.numel():
            # storage cumulative rewards and timesteps
            self.track_rewards.extend(self.cumulative_rewards[finished_episodes][:, 0].reshape(-1).tolist())
            self.track_timesteps.extend(self.cumulative_timesteps[finished_episodes][:, 0].reshape(-1).tolist())

            # reset the cumulative rewards and timesteps
            self.cumulative_rewards[finished_episodes] = 0
            self.cumulative_timesteps[finished_episodes] = 0

        # record data
        self.tracking_data["Reward / Instantaneous reward (max)"].append(torch.max(rewards).item())
        self.tracking_data["Reward / Instantaneous reward (min)"].append(torch.min(rewards).item())
        self.tracking_data["Reward / Instantaneous reward (mean)"].append(torch.mean(rewards).item())

        if len(self.track_rewards):
            track_rewards = np.array(self.track_rewards)
            track_timesteps = np.array(self.track_timesteps)

            self.tracking_data["Reward / Total reward (max)"].append(np.max(track_rewards))
            self.tracking_data["Reward / Total reward (min)"].append(np.min(track_rewards))
            self.tracking_data["Reward / Total reward (mean)"].append(np.mean(track_rewards))

            self.tracking_data["Episode / Total timesteps (max)"].append(np.max(track_timesteps))
            self.tracking_data["Episode / Total timesteps (min)"].append(np.min(track_timesteps))
            self.tracking_data["Episode / Total timesteps (mean)"].append(np.mean(track_timesteps))

    def update_net(self):
        """
        Update the agent model parameters.
        """
        raise NotImplementedError

    def _get_internal_value(self, module):
        return module.state_dict() if hasattr(module, "state_dict") else module

    def save_ckpt(self, path: str):
        """
        Save the agent model parameters to a checkpoint.
        :param path:
        :return:
        """
        modules = {}
        for name, module in self.checkpoint_modules.items():
            modules[name] = self._get_internal_value(module)
        torch.save(modules, path)

    def load_ckpt(self, path: str):
        """
        Load the agent model parameters from a checkpoint.
        :param path:
        :return:
        """
        modules = torch.load(path, map_location=self.device)
        if type(modules) is dict:
            for name, data in modules.items():
                module = self.checkpoint_modules.get(name, None)
                if module is not None:
                    if hasattr(module, "load_state_dict"):
                        module.load_state_dict(data)
                        if hasattr(module, "eval"):
                            module.eval()
                    else:
                        raise NotImplementedError
                else:
                    self.rofunc_logger.warning(
                        "Cannot load the {} module. The agent doesn't have such an instance".format(name))
