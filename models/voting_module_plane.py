# Copyright (c) Facebook, Inc. and its affiliates.
# 
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

''' Voting module: generate votes from XYZ and features of seed points.

Date: July, 2019
Author: Charles R. Qi and Or Litany
'''

import torch
import torch.nn as nn
import torch.nn.functional as F

class VotingPlaneModule(nn.Module):
    def __init__(self, vote_factor, seed_feature_dim):
        """ Votes generation from seed point features.

        Args:
            vote_facotr: int
                number of votes generated from each seed point
            seed_feature_dim: int
                number of channels of seed point features
            vote_feature_dim: int
                number of channels of vote features
        """
        super().__init__()
        self.vote_factor = 1#vote_factor
        self.in_dim = seed_feature_dim
        self.out_dim = 3+2#+self.in_dim#xyz rotation + d1 + d2

        self.conv_upper1 = torch.nn.Conv1d(self.in_dim + 3 + 4, self.in_dim, 1)
        self.conv_upper2 = torch.nn.Conv1d(self.in_dim, self.in_dim, 1)
        #self.conv_upper3 = torch.nn.Conv1d(self.in_dim, (self.out_dim) * self.vote_factor, 1)
        self.conv_upper3_angle = torch.nn.Conv1d(self.in_dim, 12, 1) ### 12 Class
        self.conv_upper3_res = torch.nn.Conv1d(self.in_dim, 1, 1)
        self.conv_upper3_sign = torch.nn.Conv1d(self.in_dim, 1, 1) ### Binary class
        self.conv_upper3_off = torch.nn.Conv1d(self.in_dim, 2, 1) ### Vote for 2 offset
        
        #self.conv_lower1 = torch.nn.Conv1d(self.in_dim, self.in_dim, 1)
        #self.conv_lower2 = torch.nn.Conv1d(self.in_dim, self.in_dim, 1)
        #self.conv_lower3 = torch.nn.Conv1d(self.in_dim, (self.out_dim) * self.vote_factor, 1)

        self.conv_front1 = torch.nn.Conv1d(self.in_dim+3+4, self.in_dim, 1)
        self.conv_front2 = torch.nn.Conv1d(self.in_dim, self.in_dim, 1)
        self.conv_front3_angle = torch.nn.Conv1d(self.in_dim, 12, 1) ### 12 Class
        self.conv_front3_res = torch.nn.Conv1d(self.in_dim, 1, 1)
        self.conv_front3_sign = torch.nn.Conv1d(self.in_dim, 1, 1) ### Binary class
        self.conv_front3_off = torch.nn.Conv1d(self.in_dim, 2, 1)

        #self.conv_back1 = torch.nn.Conv1d(self.in_dim, self.in_dim, 1)
        #self.conv_back2 = torch.nn.Conv1d(self.in_dim, self.in_dim, 1)
        #self.conv_back3 = torch.nn.Conv1d(self.in_dim, (self.out_dim) * self.vote_factor, 1)

        self.conv_left1 = torch.nn.Conv1d(self.in_dim+3+4, self.in_dim, 1)
        self.conv_left2 = torch.nn.Conv1d(self.in_dim, self.in_dim, 1)
        self.conv_left3_angle = torch.nn.Conv1d(self.in_dim, 12, 1) ### 12 Class
        self.conv_left3_res = torch.nn.Conv1d(self.in_dim, 1, 1)
        self.conv_left3_sign = torch.nn.Conv1d(self.in_dim, 1, 1) ### Binary class
        self.conv_left3_off = torch.nn.Conv1d(self.in_dim, 2, 1)
        
        #self.conv_right1 = torch.nn.Conv1d(self.in_dim, self.in_dim, 1)
        #self.conv_right2 = torch.nn.Conv1d(self.in_dim, self.in_dim, 1)
        #self.conv_right3 = torch.nn.Conv1d(self.in_dim, (self.out_dim) * self.vote_factor, 1)
        
        self.bn_upper1 = torch.nn.BatchNorm1d(self.in_dim)
        self.bn_upper2 = torch.nn.BatchNorm1d(self.in_dim)

        #self.bn_lower1 = torch.nn.BatchNorm1d(self.in_dim)
        #self.bn_lower2 = torch.nn.BatchNorm1d(self.in_dim)

        self.bn_front1 = torch.nn.BatchNorm1d(self.in_dim)
        self.bn_front2 = torch.nn.BatchNorm1d(self.in_dim)

        #self.bn_back1 = torch.nn.BatchNorm1d(self.in_dim)
        #self.bn_back2 = torch.nn.BatchNorm1d(self.in_dim)

        self.bn_left1 = torch.nn.BatchNorm1d(self.in_dim)
        self.bn_left2 = torch.nn.BatchNorm1d(self.in_dim)

        #self.bn_right1 = torch.nn.BatchNorm1d(self.in_dim)
        #self.bn_right2 = torch.nn.BatchNorm1d(self.in_dim)
                
    def forward(self, seed_xyz, seed_features, end_points):
        """ Forward pass.

        Arguments:
            seed_xyz: (batch_size, num_seed, 3) Pytorch tensor
            seed_features: (batch_size, feature_dim, num_seed) Pytorch tensor
        Returns:
            vote_xyz: (batch_size, num_seed*vote_factor, 3)
            vote_features: (batch_size, vote_feature_dim, num_seed*vote_factor)
        """
        batch_size = seed_xyz.shape[0]
        num_seed = seed_xyz.shape[1]
        num_vote = num_seed*self.vote_factor
        newseed_features = torch.cat((seed_xyz.transpose(2,1).contiguous(), seed_features), 1)
        
        net_upper = F.relu(self.bn_upper1(self.conv_upper1(newseed_features)))
        #net_upper = torch.cat((seed_xyz.transpose(2,1).contiguous(), net_upper), 1)
        net_upper = F.relu(self.bn_upper2(self.conv_upper2(net_upper)))
        #net_upper = self.conv_upper3(net_upper) # (batch_size, (3+out_dim)*vote_factor, num_seed)
        #net_upper = torch.cat((seed_xyz.transpose(2,1).contiguous(), net_upper), 1)
        end_points['z_angle'] = self.conv_upper3_angle(net_upper) # (batch_size, (3+out_dim)*vote_factor, num_seed)
        end_points['z_res'] = self.conv_upper3_res(net_upper)
        end_points['z_sign'] = self.conv_upper3_sign(net_upper)
        upper_off = self.conv_upper3_off(net_upper)
        end_points['z_off0'] = upper_off.contiguous().transpose(2,1)[:,:,0]
        end_points['z_off1'] = upper_off.contiguous().transpose(2,1)[:,:,1]
        end_points['z_d0'] = seed_xyz[:,:,-1] + upper_off.contiguous().transpose(2,1)[:,:,0]
        end_points['z_d1'] = seed_xyz[:,:,-1] + upper_off.contiguous().transpose(2,1)[:,:,1]
        
        net_front = F.relu(self.bn_front1(self.conv_front1(newseed_features)))
        #net_front = torch.cat((seed_xyz.transpose(2,1).contiguous(), net_front), 1)
        net_front = F.relu(self.bn_front2(self.conv_front2(net_front)))
        #net_front = torch.cat((seed_xyz.transpose(2,1).contiguous(), net_front), 1)
        #net_front = self.conv_front3(net_front) # (batch_size, (3+out_dim)*vote_factor, num_seed)
        end_points['y_angle'] = self.conv_front3_angle(net_front) # (batch_size, (3+out_dim)*vote_factor, num_seed)
        end_points['y_res'] = self.conv_front3_res(net_front)
        end_points['y_sign'] = self.conv_front3_sign(net_front)
        front_off = self.conv_front3_off(net_front)
        end_points['y_off0'] = front_off.contiguous().transpose(2,1)[:,:,0]
        end_points['y_off1'] = front_off.contiguous().transpose(2,1)[:,:,1]
        end_points['y_d0'] = seed_xyz[:,:,-1] + front_off.contiguous().transpose(2,1)[:,:,0]
        end_points['y_d1'] = seed_xyz[:,:,-1] + front_off.contiguous().transpose(2,1)[:,:,1]

        net_left = F.relu(self.bn_left1(self.conv_left1(newseed_features)))
        #net_left = torch.cat((seed_xyz.transpose(2,1).contiguous(), net_left), 1)
        net_left = F.relu(self.bn_left2(self.conv_left2(net_left)))
        #net_left = torch.cat((seed_xyz.transpose(2,1).contiguous(), net_left), 1)
        #net_left = self.conv_left3(net_left) # (batch_size, (3+out_dim)*vote_factor, num_seed)
        end_points['x_angle'] = self.conv_left3_angle(net_left) # (batch_size, (3+out_dim)*vote_factor, num_seed)
        end_points['x_res'] = self.conv_left3_res(net_left)
        end_points['x_sign'] = self.conv_left3_sign(net_left)
        left_off = self.conv_left3_off(net_left)
        end_points['x_off0'] = left_off.contiguous().transpose(2,1)[:,:,0]
        end_points['x_off1'] = left_off.contiguous().transpose(2,1)[:,:,1]
        end_points['x_d0'] = seed_xyz[:,:,-1] + left_off.contiguous().transpose(2,1)[:,:,0]
        end_points['x_d1'] = seed_xyz[:,:,-1] + left_off.contiguous().transpose(2,1)[:,:,1]

        #residual_features1 = net_upper_lower[:,5:,:] # (batch_size, num_seed, vote_factor, out_dim)
        #residual_features2 = net_front_back[:,5:,:]
        #residual_features3 = net_left_right[:,5:,:]
        #vote_features = seed_features + residual_features1 + residual_features2 + residual_features3
        #vote_features = residual_features1 + residual_features2 + residual_features3
        
        return end_points#net_upper, net_lower, net_left, net_right, net_front, net_back#, vote_features
 
if __name__=='__main__':
    net = VotingModule(2, 256).cuda()
    xyz, features = net(torch.rand(8,1024,3).cuda(), torch.rand(8,256,1024).cuda())
    print('xyz', xyz.shape)
    print('features', features.shape)
