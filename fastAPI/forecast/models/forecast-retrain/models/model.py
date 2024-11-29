import torch
import torch.nn as nn
import math

class EnhancedLSTM(nn.Module):
    def _init_(self, input_size, lstm_layer_sizes, linear_layer_size, output_size):
        super(EnhancedLSTM, self)._init_()
        self.input_size = input_size

        self.lstm_layers = nn.ModuleList()
        for i in range(len(lstm_layer_sizes)):
            if i == 0:
                self.lstm_layers.append(nn.LSTM(input_size, lstm_layer_sizes[i], batch_first=True, bidirectional=True))
            else:
                self.lstm_layers.append(nn.LSTM(lstm_layer_sizes[i-1]*2, lstm_layer_sizes[i], batch_first=True, bidirectional=True))

        self.dropout = nn.Dropout(0.3)
        self.fc_layers = nn.ModuleList()
        for i in range(len(linear_layer_size)):
            if i == 0:
                self.fc_layers.append(nn.Linear(lstm_layer_sizes[-1]*2, linear_layer_size[i]))
            else:
                self.fc_layers.append(nn.Linear(linear_layer_size[i-1], linear_layer_size[i]))

        self.output_layer = nn.Linear(linear_layer_size[-1], output_size)
        self.relu = nn.ReLU()

        self.apply(self.initialize_weights)

    def forward(self, x):
        out = x
        for lstm in self.lstm_layers:
            out, (hn, cn) = lstm(out)
        out = self.dropout(out[:, -1, :])

        for fc in self.fc_layers:
            out = self.relu(fc(out))

        out = self.output_layer(out)
        return out

    def initialize_weights(self, layer):
        if isinstance(layer, nn.Linear):
            nn.init.xavier_uniform_(layer.weight)
            nn.init.zeros_(layer.bias)
        elif isinstance(layer, nn.LSTM):
            for name, param in layer.named_parameters():
                if 'weight' in name:
                    nn.init.xavier_uniform_(param.data)
                elif 'bias' in name:
                    nn.init.zeros_(param.data)