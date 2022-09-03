import torch
import torch.nn as nn
class CNN(nn.Module):
    def __init__(self,):
        super(CNN, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=4,
                kernel_size=(32,2),
                stride=1,
                padding=1,
            ),
            nn.ReLU(),
            nn.MaxPool2d((4,2), stride=2),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(
                in_channels=4,
                out_channels=8,
                kernel_size=(16,2),
                stride=1,
            ),
            nn.ReLU(),
            nn.MaxPool2d(2, stride=2)
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(
                in_channels=8,
                out_channels=16,
                kernel_size=(8,2),
                stride=1,
            ),
            nn.ReLU(),
        )
        self.input_layer = nn.Linear(864, 2048)
        self.layer_output = nn.Linear(2048, 2)
        self.dropout = nn.Dropout(p=0.25)
        self.relu = nn.ReLU()

    def forward(self, x):
        # [b,1,199,13]
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = x.view(x.size(0), -1)
        x = self.input_layer(x)
        x = self.dropout(x)
        fea = self.relu(x)
        x = self.layer_output(x)
        return x,fea