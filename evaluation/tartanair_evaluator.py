# Copyright (c) 2020 Carnegie Mellon University, Wenshan Wang <wenshanw@andrew.cmu.edu>
# For License information please see the LICENSE file in the root directory.

import numpy as np
from evaluator_base import ATEEvaluator, RPEEvaluator, KittiEvaluator, transform_trajs, quats2SEs
from os.path import isdir, isfile

# from trajectory_transform import timestamp_associate

class TartanAirEvaluator:
    def __init__(self, scale = False, round=1):
        self.ate_eval = ATEEvaluator()
        self.rpe_eval = RPEEvaluator()
        self.kitti_eval = KittiEvaluator()
        
    def evaluate_one_trajectory(self, gt_traj_name, est_traj_name, scale=False):
        """
        scale = True: calculate a global scale
        """
        # load trajectories
        gt_traj = np.loadtxt(gt_traj_name)
        est_traj = np.loadtxt(est_traj_name)

        if gt_traj.shape[0] != est_traj.shape[0]:
            raise Exception("POSEFILE_LENGTH_ILLEGAL")
        if gt_traj.shape[1] != 7 or est_traj.shape[1] != 7:
            raise Exception("POSEFILE_FORMAT_ILLEGAL")

        # transform and scale
        gt_traj_trans, est_traj_trans, s = transform_trajs(gt_traj, est_traj, scale)
        gt_SEs, est_SEs = quats2SEs(gt_traj_trans, est_traj_trans)

        ate_score, gt_ate_aligned, est_ate_aligned = self.ate_eval.evaluate(gt_traj, est_traj, scale)
        rpe_score = self.rpe_eval.evaluate(gt_SEs, est_SEs)
        kitti_score = self.kitti_eval.evaluate(gt_SEs, est_SEs)

        return {'ate_score': ate_score, 
                'rpe_score': rpe_score, 
                'kitti_score': kitti_score}

if __name__ == "__main__":
    
    # scale = True for monocular track, scale = False for stereo track
    aicrowd_evaluator = TartanAirEvaluator()
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("poses_gt", help="input ground truth pose path file in xyzq format")
    parser.add_argument(
        "poses_input", help="input file path to evaluate")
    args = parser.parse_args()
    result = aicrowd_evaluator.evaluate_one_trajectory(args.poses_gt, args.poses_input, scale=True)
    print(result)
