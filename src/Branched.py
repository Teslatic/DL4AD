#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
end to end driving

exercise 3: Branched architecture 

by: Michael Floßmann, Kshitij Sirohi, Hendrik Vloet

"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

torch.manual_seed(1)
device = torch.device("cuda")

class Net(nn.Module):
    branches = []
    def __init__(self):
        super(Net, self).__init__()
        #8 layers if con layers for image module
        self.conv1 = nn.Conv2d(3, 32, kernel_size=5, padding=2) #(output = 200x88)
        self.conv2 = nn.Conv2d(32, 32, kernel_size=3, padding=1)#(output = 200x88)   
        self.conv3= nn.Conv2d(32, 64, kernel_size=3, padding=2) #(output = 202x90)
        self.conv4 = nn.Conv2d(64, 64, kernel_size=3, padding=1)#(output = 202x90)
        self.conv5 = nn.Conv2d(64, 128, kernel_size=3, padding=2)#(output = 204x92)
        self.conv6 = nn.Conv2d(128, 128, kernel_size=3, padding=1)#(output = 204x92)    
        self.conv7 = nn.Conv2d(128, 256, kernel_size=3, padding=1)#(output = 204x92)
        self.conv8 = nn.Conv2d(256, 256, kernel_size=3, padding=1)#(output = 204x92)
        
        
        #defining 2 different dropouts required after the conv and fc layers
        self.conv_drop = nn.Dropout2d(p=0.2)
        self.fc_drop = nn.Dropout2d(p=0.5)
        
        
        #batch normalisers for every convolution layer
        self.conv1_bn = nn.BatchNorm2d(32)
        self.conv2_bn = nn.BatchNorm2d(32)
        self.conv3_bn = nn.BatchNorm2d(64)
        self.conv4_bn = nn.BatchNorm2d(64)
        self.conv5_bn = nn.BatchNorm1d(128)
        self.conv6_bn = nn.BatchNorm1d(128)
        self.conv7_bn = nn.BatchNorm1d(256)
        self.conv8_bn = nn.BatchNorm1d(256)
                                        
        
        #2 fc layers for image module
        self.fc1 = nn.Linear(204*92*256, 512) #(please reconfirm with team)
        self.fc2 = nn.Linear(512, 512)
        
        #3 fc layers for control and measurement modules
        self.fc3= nn.Linear(1,128)
        self.fc4= nn.Linear(128,128)
        
        #4 fc layers for concatenated module
        self.fc5= nn.Linear(640,512)
        self.fc6= nn.Linear(512,256)
        self.fc7= nn.Linear(256,256)
        
        #5 for action output
        self.fc8= nn.Linear(256,3)
        self.fc8= nn.Linear(256,1)
        
        
    def forward(self, x,speed):
        #######conv layers##############
        x= self.conv1(x)
        x= self.conv1_bn(x)
        x= self.conv_drop(x)
        x = relu(x)
        
        
        x= self.conv2(x)
        x= self.conv2_bn(x)
        x= self.conv_drop(x)
        x = relu(x)
        
        x= self.conv3(x)
        x= self.conv3_bn(x)
        x= self.conv_drop(x)
        x = relu(x)
        
        x= self.conv4(x)
        x= self.conv4_bn(x)
        x= self.conv_drop(x)
        x = relu(x)
        
        x= self.conv5(x)
        x= self.conv5_bn(x)
        x= self.conv_drop(x)
        x = relu(x)
        
        x= self.conv6(x)
        x= self.conv6_bn(x)
        x= self.conv_drop(x)
        x = relu(x)
        
        x= self.conv7(x)
        x= self.conv7_bn(x)
        x= self.conv_drop(x)
        x = relu(x)
        
        x= self.conv8(x)
        x= self.conv8_bn(x)
        x= self.conv_drop(x)
        x = relu(x)
        
        ###################################
        
        x = x.view(-1, 204*92*256)      ### do change this
        
        
        #########fully connected layers####
        x = self.fc1(x)
        x= self.fc_drop(x)
        x = relu(x)
        
        x = self.fc2(x)
        x= self.fc_drop(x)
        x = relu(x)
        
        
        #####do something for control########
        
        ####for  measurement(speed)#########
        ###not to use in real raiscar#######
        speed = self.fc3(speed)
        speed= self.fc_drop(speed)
        speed = relu(speed)
        speed = self.fc4(speed)
        speed= self.fc_drop(speed)
        speed = relu(speed)
        ####################################
        
        ####################################
        
        j = torch.cat((x,speed), 1)
        j = self.fc5(j)
        j= self.fc_drop(j)
        j = relu(j)
        
        
        ####initiating branches############
        branch_config = [["Steer", "Gas", "Brake"],["Steer", "Gas", "Brake"], ["Steer", "Gas", "Brake"], ["Speed"]]
        ###there were 5 in the code they made, dontn have idea why####
        
        for i in range(0, len(branch_config)):
        #have to look for this regarding the dataset , on how to use it?
        with tf.name_scope("Branch_" + str(i)):
            if branch_config[i][0] == "Speed":
                # we only use the image as input to speed prediction
                branch_output = self.fc6(x)
                branch_output= self.fc_drop(branch_output)
                branch_output = relu(branch_output)
                
                branch_output = self.fc7(x)
                branch_output= self.fc_drop(branch_output)
                branch_output = relu(branch_output)
                
            else:
                branch_output = self.fc6(x)
                branch_output= self.fc_drop(branch_output)
                branch_output = relu(branch_output)
                
                branch_output = self.fc7(x)
                branch_output= self.fc_drop(branch_output)
                branch_output = relu(branch_output)
            
            if i == 3:
                branches.append(self.fc8(branch_output))
            else:
                branches.append(self.fc9(branch_output))
                
        #### output action##########
        
        
        return branches


model = Net().to(device)

relu = F.relu

optimizer = optim.Adam(model.parameters(), lr=0.0002)

criterion = nn.CrossEntropyLoss()

lossx = []
