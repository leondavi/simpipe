import random
import pandas as pd
import torch
import torch.nn as nn
from torch import optim
import numpy
from numpy import genfromtxt

FEATURES = 8
EPOCHS = 100
EPOCHS_SIZE = 500

ENCODER_IN_SIZE = 8
ENCODER_OUT_SIZE = 5
DECODER_IN_SIZE = 3
DECODER_OUT_SIZE = ENCODER_OUT_SIZE

class AE(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        self.encoder_hidden_layer = nn.Linear(
            in_features=ENCODER_IN_SIZE, out_features=ENCODER_OUT_SIZE
        )
        self.encoder_output_layer = nn.Linear(
            in_features=ENCODER_OUT_SIZE, out_features=DECODER_IN_SIZE
        )
        self.decoder_hidden_layer = nn.Linear(
            in_features=DECODER_IN_SIZE, out_features=DECODER_OUT_SIZE
        )
        self.decoder_output_layer = nn.Linear(
            in_features=DECODER_OUT_SIZE, out_features=ENCODER_IN_SIZE
        )

    def forward(self, features):
        activation = self.encoder_hidden_layer(features)
        activation = torch.relu(activation)
        code = self.encoder_output_layer(activation)
        code = torch.relu(code)
        activation = self.decoder_hidden_layer(code)
        activation = torch.relu(activation)
        activation = self.decoder_output_layer(activation)
        reconstructed = torch.relu(activation)
        return reconstructed

    def createData(self,features,epochs_number,epochs_size):
        outputData = [[[0 for k in range(features)] for j in range(epochs_size)] for i in range(epochs_number)]
        for epoch_ind in range(epochs_number):
            for ind_in_epoch in range(epochs_size):
                for feature_ind in range(features):
                    outputData[epoch_ind][ind_in_epoch][feature_ind] = random.random()
        return outputData

    def MSE(self,y_bar,y):
        summation = 0  # variable to store the summation of differences
        n = len(y)  # finding total number of items in list
        for i in range(0, n):  # looping through each element of the list
            difference = y[i] - y_bar[i]  # finding the difference between observed and predicted value
            squared_difference = difference ** 2  # taking square of the differene
            summation = summation + squared_difference  # taking a sum of all the differences
        return summation / n

def getDataFromCSV(self,Path):
    my_data = genfromtxt(Path, delimiter=',')
    return my_data

# TODO - added disable functions - done
def disableFeature(grad_tensor,FeatIdx,totalFeat,nextLayerSize):
        x = torch.FloatTensor(grad_tensor)                           #using a float tensor
        idx = torch.LongTensor([FeatIdx] * nextLayerSize)       #in each row selecting the feature that we want to zero
        j = torch.arange(x.size(0)).long()                      #selecting the rows that we want to zero the features on
        update_values = torch.FloatTensor([0]*nextLayerSize)
        grad_tensor.data[j, idx] = update_values                     # updating the gradient tensor to disable feature

def disableMultipleFeatures(first_idx,last_idx,grad_tensor,totalFeat,nextLayerSize):
        for i in range(first_idx,last_idx+1):
            disableFeature(grad_tensor,i,totalFeat,nextLayerSize)




#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")

# create a model from `AE` autoencoder class
# load it to the specified device, either gpu or cpu
model = AE(input_shape=FEATURES).to(device)
# create an optimizer object
# Adam optimizer with learning rate 1e-3
optimizer = optim.Adam(model.parameters(), lr=1e-7)
# mean-squared error loss
criterion = nn.MSELoss()

#Data Generation
train_loader = model.createData(FEATURES,EPOCHS,EPOCHS_SIZE)
train_loader = torch.FloatTensor(train_loader)
#data = getDataFromCSV(r"C:\Users\omrir\Desktop\University\Project\Dumps\FFT\‏‏FFT_COMP_100k - Analyzed.csv")
#data = data[:,0:FEATURES]

for epoch in range(EPOCHS):
    loss = 0
    for batch_features in train_loader:
        # reset the gradients back to zero
        # PyTorch accumulates gradients on subsequent backward passes
        optimizer.zero_grad()
        # compute reconstructions
        outputs = model(batch_features)
        # compute training reconstruction loss
        train_loss = criterion(outputs, batch_features)
        # compute accumulated gradients
        train_loss.backward()

        #TODO disable specific grad
        print("before")
        print(model.encoder_hidden_layer.weight.grad)
        disableMultipleFeatures(first_idx=5,last_idx=7,grad_tensor=model.encoder_hidden_layer.weight.grad,totalFeat=FEATURES,nextLayerSize=ENCODER_OUT_SIZE)
        print("after")
        print(model.encoder_hidden_layer.weight.grad)
        # TODO

        # perform parameter update based on current gradients
        optimizer.step()
        # add the mini-batch training loss to epoch loss
        loss += train_loss.item()
    # compute the epoch training loss
    loss = loss / len(train_loader)

    # display the epoch training loss
    print("epoch : {}/{}, loss = {:.6f}".format(epoch + 1, batch_features, loss))


pred1 = model.forward(torch.FloatTensor([1,2,3,4,5,6,7,8]))
pred2 = model.forward(torch.FloatTensor([0.5,0.5,0.2,0.3,0.4,0.6,0.7,0.8]))
print(float(model.MSE([1,2,3,4,5,6,7,8],pred1)))
print(float(model.MSE([0.5,0.5,0.2,0.3,0.4,0.6,0.7,0.8],pred2)))


