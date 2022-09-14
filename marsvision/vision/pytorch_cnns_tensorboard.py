# -*- coding: utf-8 -*-
"""PyTorch_CNNs_Tensorboard.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QxBOt5ploeEEEMz597jCnDi_XT4OjgSY
"""

import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import matplotlib.pyplot as plt
import numpy as np
import datetime
 
from tensorflow import summary

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard

transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.52, 0.52, 0.52), (0.52, 0.52, 0.52))]
)

batch_size = 24

trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                        download=True, transform=transform)
testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                        download=True, transform=transform)

trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size,
                                          shuffle=True, num_workers=2)
testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size,
                                          shuffle=True, num_workers=2)

import matplotlib.pyplot as plt
import numpy as np

def imshow(img):
  img = img / 2 + 0.5
  np_img = img.numpy()
  plt.imshow(np.transpose(np_img, (1, 2, 0)))
  plt.show()

dataiter = iter(trainloader)
images, labels = dataiter.next()

imshow(torchvision.utils.make_grid(images))

class Net(nn.Module):

  def __init__(self):
    super().__init__()
    k_size = 5
    n_input_channels = 3 # rgb
    n_output_channels_1 = 6
    self.conv1 = nn.Conv2d(n_input_channels, n_output_channels_1, k_size)
    self.pool = nn.MaxPool2d(2, 2)
    self.conv2 = nn.Conv2d(n_output_channels_1, 16, k_size)
    self.fc1 = nn.Linear(16 * k_size * k_size, 120)
    self.fc2 = nn.Linear(120, 84)
    self.fc3 = nn.Linear(84, 10)

  def forward(self, x):
    out = self.conv1(x)
    out = F.relu(out)
    out = self.pool(out)

    out = self.conv2(out)
    out = F.relu(out)
    out = self.pool(out)

    out = torch.flatten(out, 1)

    out = self.fc1(out)
    out = F.relu(out)

    out = self.fc2(out)
    out = F.relu(out)

    out = self.fc3(out)
    #out = F.softmax(out, dim=1)
    return out

net = Net()
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
net = net.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters())

current_time = str(datetime.datetime.now().timestamp())
train_log_dir = 'logs/tensorboard/train/' + current_time
val_log_dir = 'logs/tensorboard/val/' + current_time
train_summary_writer = summary.create_file_writer(train_log_dir)
val_summary_writer = summary.create_file_writer(val_log_dir)

def train():
  for epoch in range(35):

    correct = 0
    total = 0
    running_loss = 0.0

    for i, data in enumerate(trainloader, 0):
      inputs, labels = data
      inputs, labels = inputs.to(device), labels.to(device)

      optimizer.zero_grad()
      outputs = net(inputs)
      _, predicted = torch.max(outputs.data, 1)
      total += labels.size(0)
      correct += (predicted == labels).sum().item()

      loss = F.cross_entropy(outputs, labels)
      loss.backward()
      optimizer.step()

      running_loss += loss.item()
             
    with train_summary_writer.as_default():
      summary.scalar('train loss', running_loss / i, step=epoch)
      summary.scalar('train accuracy', correct / total, step=epoch)

    correct = 0
    total = 0
    running_loss = 0.0

    with torch.no_grad():
      for data in testloader:
        images, labels = data
        images, labels = images.to(device), labels.to(device)

        outputs = net(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        loss = F.cross_entropy(outputs, labels)
        running_loss += loss.item()

    with val_summary_writer.as_default():
      summary.scalar('validation loss', running_loss / i, step=epoch)
      summary.scalar('validation accuracy', correct / total, step=epoch)

# Commented out IPython magic to ensure Python compatibility.
# %tensorboard --logdir logs/tensorboard/

train()