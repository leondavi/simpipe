# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 15:49:43 2020

@author: David Leon
"""
import torch
import torch.nn as nn
from Definitions import *


class Autoencoder(nn.Module):
    def __init__(self, halfNetLayers=[32, 16, 8], act_type=nn.elu):
        super(Autoencoder, self).__init__()
        self.halfNetLayers = halfNetLayers
        self.layers_sizes = halfNetLayers + list(reversed(halfNetLayers)) #32 16 8 8 16 32
        self.Layers = []
        self.layers_model = []
        self.act_type = act_type

        for i in range(0, len(self.layers_sizes) - 1):
            i_next = i + 1
            if self.layers_sizes[i] != self.layers_sizes[i_next]:
                self.Layers.append(nn.Linear(self.layers_sizes[i], self.layers_sizes[i_next]))
                self.layers_model.append((self.layers_sizes[i], self.layers_sizes[i_next]))

        self.Layers = nn.ModuleList(self.Layers)

    @staticmethod
    def layersListStr(LayersList):
        return "-".join([str(it) for it in LayersList])

    @staticmethod
    def layerList_to_intList(LayerListstr: str) -> list:
        return [int(x) for x in LayerListstr.split("-")]

    def forward(self, x):
        for layer in self.Layers:
            x = self.act_type(layer(x))
        return x


def ae_train(model, input_df, win_size, lr=0.0001):
    # device = torch.device("cuda:0")
    # model.to(device)
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    avg_loss_val = 0
    acc_loss_val = 0
    iterations = 0

    start = True
    for win_end_idx in range(win_size, input_df.shape[0]):
        win_start_idx = win_end_idx - win_size
        inout_data = torch.tensor(input_df.iloc[win_start_idx:win_end_idx, :].values.flatten())  # .cuda()
        outputs = model(inout_data.float())
        loss = criterion(outputs, inout_data.float())
        loss.backward()
        optimizer.step()
        # calculating the average loss value
        iterations += 1
        if start:
            # print("loss: "+str(loss.data))
            start = False
        acc_loss_val += float(loss.data)
        avg_loss_val = acc_loss_val / iterations
    # print("loss: " + str(loss.data))
    # model.to('cpu')
    return model, avg_loss_val


def predict(model, input_df, win_size):
    criterion = torch.nn.MSELoss()
    # device = torch.device("cuda:0")
    # model.to(device)

    inout_data = torch.tensor(input_df.values.flatten())  # .cuda()
    outputs = model.forward(inout_data.float())
    loss = criterion(outputs, inout_data.float())
    return loss.data.numpy().item()  # .cpu().numpy()


'''
nn_complexity - larger mean more hidden nodes - more complexity
'''
LIST_OF_LAYERS_SIZES_HASH = dict()


def ListOfLayersSizes(win_size, NumOffeatures, depthsList=MODEL_DEPTH_LIST, nn_complexity_options=MODEL_COMPLEXITY):
    res = []
    key = (win_size, NumOffeatures, tuple(depthsList), nn_complexity_options)
    if key in LIST_OF_LAYERS_SIZES_HASH.keys():
        return LIST_OF_LAYERS_SIZES_HASH[key]
    else:
        input_size = win_size * NumOffeatures
        numerator = 1
        denominator = 2
        for i in range(0, nn_complexity_options):
            for depth in depthsList:
                tmp_val = input_size
                curr_comb_of_sizes = []
                for d in range(0, depth):
                    curr_comb_of_sizes.append(int(tmp_val))
                    tmp_val *= (numerator / denominator)
                res.append(curr_comb_of_sizes)
            numerator += 1
            denominator += 1
        LIST_OF_LAYERS_SIZES_HASH[key] = res
    return res


'''
Key is based on E - event type, W - Window size, L - list of layers 
'''


def get_key_by_EWLL(eventStr, WinSize, LayersList, LearningRate):
    return eventStr + "_" + "w-" + str(WinSize) + "_" + Autoencoder.layersListStr(LayersList) + "_lr-" + str(
        LearningRate)


def key_to_args(key: str):
    params = key.replace("w-", "").replace("lr-", "").split("_")
    eventStr = params[0]
    WinSize = int(params[1])
    LayersList = Autoencoder.layerList_to_intList(params[2])
    lr = int(params[3].split("e")[0]) * pow(10, int(params[3].split("e")[1]))

    return eventStr, WinSize, LayersList, lr


class AEAttribute:
    def __init__(self, event_type, win_size, ae_key):
        self.event_type = event_type
        self.win_size = win_size
        self.loss_val = list()
        self.cv_avg_err = list()
        self.cv_svar_err = list()
        self.tr_avg_err = list()
        self.tr_svar_err = list()
        self.TP = list()  # true positive - anomaly predicted as anomaly
        self.TN = list()  # true negative - no anomaly predicted as no anomaly
        self.FP = list()  # false positive - false alarm - no anomaly predicted as anomaly
        self.FN = list()  # false negative - anomaly was predicted as no anomaly
        self.total_an = list()
        self.ae = None
        self.act_func = None
        self.layers = None
        self.lr = None
        self.ae_key = ae_key

        # ema measures
        self.ema_dict = {
            "ema_tp": list(),
            "ema_tn": list(),
            "ema_fp": list(),
            "ema_fn": list(),
            "ema_val": list(),
            "ema_anomaly_val": list(),
            "ema_not_anomaly": list(),
            "ema_th_val": list(),
            "emaVar_val": list()
        }

        self.train_dict = {
            "ema_tp": list(),
            "ema_tn": list(),
            "ema_fp": list(),
            "ema_fn": list(),
            "ema_val": list(),
            "ema_anomaly_val": list(),
            "ema_not_anomaly": list(),
            "ema_th_val": list(),
            "emaVar_val": list()
        }

    def add_loss_val(self, loss):
        self.loss_val.append(loss)

    def generate_ae(self, layers, lr, actFunc=nn.elu):
        self.layers = layers
        self.lr = lr
        self.act_func = actFunc
        self.ae = Autoencoder(layers, actFunc)

    def set_ae(self, ae: Autoencoder, layers, lr, actFunc=nn.elu):
        self.layers = layers
        self.lr = lr
        self.act_func = actFunc
        self.ae = ae

    def get_ae(self):
        return self.ae

    def get_win_size(self):
        return self.win_size

    def get_lr(self):
        return self.lr

    def to_json(self):
        return {"event": self.event_type,
                "win_size": self.win_size,
                "layers": self.layers,
                "lr": self.lr,
                "loss_vals": list(self.loss_val),
                "cv_avg_err": list(self.cv_avg_err),
                "cv_svar_err": list(self.cv_svar_err),
                "tr_avg_err": list(self.tr_avg_err),
                "tr_svar_err": list(self.tr_svar_err),
                "true positive": list(self.TP),
                "true negative": list(self.TN),
                "false positive": list(self.FP),
                "false negative": list(self.FN),
                "total anomalies": list(self.total_an),
                "ema dict": self.ema_dict,
                "train dict": self.train_dict
                }


def load_torch_model(modelfile_path: Path):
    ''':arg
    returns a tuple of ae_attr and key
    '''
    if modelfile_path.name.startswith("model"):
        activation_str = modelfile_path.name.split("_")[STR_ACTIVATION_IDX]
        act_f = get_activation(activation_str)
        key = "_".join(modelfile_path.name.split("_")[(STR_ACTIVATION_IDX + 1):])
        eventStr, WinSize, LayersList, lr = key_to_args(key)
        ae_attr = AEAttribute(eventStr, WinSize, key)
        ae_attr.generate_ae(LayersList, lr, act_f)
        ae_attr.get_ae().load_state_dict(torch.load(modelfile_path))
        ae_attr.get_ae().eval()
        return ae_attr, key


STR_ACTIVATION_IDX = 1


def load_torch_models(models_path) -> dict:
    autoencoders_dict = dict()
    list_of_experiments = {}
    for (dirpath, dirnames, filenames) in os.walk(models_path):
        for filename in filenames:
            if filename.startswith("model"):
                ae_attr, key = load_torch_model(Path(os.path.join(dirpath, filename)))
                autoencoders_dict[key] = ae_attr

    return autoencoders_dict


omri_ae = Autoencoder()
