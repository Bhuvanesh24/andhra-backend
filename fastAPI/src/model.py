import torch
import torch.nn as nn
import math
#from transformers import AutoModelForCausalLM, AutoTokenizer

class EnhancedLSTM(nn.Module):
    def __init__(self, input_size, lstm_layer_sizes, linear_layer_size, output_size):
        super(EnhancedLSTM, self).__init__()
        self.input_size = input_size

        self.lstm_layers = nn.ModuleList()
        if lstm_layer_sizes:
            for i in range(len(lstm_layer_sizes)):
                if i == 0:
                    self.lstm_layers.append(nn.LSTM(input_size, lstm_layer_sizes[i], batch_first=True, bidirectional=True))
                else:
                    self.lstm_layers.append(nn.LSTM(lstm_layer_sizes[i-1]*2, lstm_layer_sizes[i], batch_first=True, bidirectional=True))

        self.dropout = nn.Dropout(0.3)
        self.fc_layers = nn.ModuleList()
        if linear_layer_size:
            for i in range(len(linear_layer_size)):
                if i == 0:
                    self.fc_layers.append(nn.Linear(lstm_layer_sizes[-1]*2, linear_layer_size[i]))
                else:
                    self.fc_layers.append(nn.Linear(linear_layer_size[i-1], linear_layer_size[i]))

        self.output_layer = nn.Linear(linear_layer_size[-1], output_size)
        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()

        self.apply(self.initialize_weights)
        self.gross_capacity_weight = nn.Parameter(torch.ones(1))

    def forward(self, x):
        gross_capacity = x[:, 0, 1].unsqueeze(1)
        out = x
        for lstm in self.lstm_layers:
            out, (hn, cn) = lstm(out)
        out = self.dropout(out[:, -1, :])

        for fc in self.fc_layers:
            out = self.relu(fc(out))

        out = self.output_layer(out)
        out = out * gross_capacity
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

class EnhancedUsageLSTM(nn.Module):
    def __init__(self, input_size, lstm_layer_sizes, linear_layer_size, output_size):
        super(EnhancedUsageLSTM, self).__init__()
        self.input_size = input_size

        self.lstm_layers = nn.ModuleList()
        if lstm_layer_sizes:
            for i in range(len(lstm_layer_sizes)):
                if i == 0:
                    self.lstm_layers.append(nn.LSTM(input_size, lstm_layer_sizes[i], batch_first=True, bidirectional=True))
                else:
                    self.lstm_layers.append(nn.LSTM(lstm_layer_sizes[i-1]*2, lstm_layer_sizes[i], batch_first=True, bidirectional=True))

        self.dropout = nn.Dropout(0.3)
        self.fc_layers = nn.ModuleList()
        if linear_layer_size:
            for i in range(len(linear_layer_size)):
                if i == 0:
                    self.fc_layers.append(nn.Linear(lstm_layer_sizes[-1]*2, linear_layer_size[i]))
                else:
                    self.fc_layers.append(nn.Linear(linear_layer_size[i-1], linear_layer_size[i]))

        self.output_layer = nn.Linear(linear_layer_size[-1], output_size)
        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()

        self.apply(self.initialize_weights)
        self.gross_capacity_weight = nn.Parameter(torch.ones(3))

    def forward(self, x):
        values = x[:, -1, 1:4]
        out = x
        for lstm in self.lstm_layers:
            out, (hn, cn) = lstm(out)
        out = self.dropout(out[:, -1, :])

        for fc in self.fc_layers:
            out = self.relu(fc(out))

        out = self.output_layer(out)
        out = torch.relu(out) * self.gross_capacity_weight * values
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

class LSTM(nn.Module):
    def __init__(self, input_size, lstm_layer_sizes,linear_layer_size, output_size):
        super(LSTM, self).__init__()

        self.input_size = input_size
        self.linear_layer_size = linear_layer_size

        self.lstm_layer_1 = nn.LSTM(input_size, lstm_layer_sizes[0], batch_first=True)
        self.lstm_layer_2 = nn.LSTM(lstm_layer_sizes[0], lstm_layer_sizes[1], batch_first=True)
        self.lstm_layer_3 = nn.LSTM(lstm_layer_sizes[1], lstm_layer_sizes[2], batch_first=True)

        self.fc = Linear(lstm_layer_sizes[2], self.linear_layer_size,output_size)

        self.apply(self.initialize_weights)

    def forward(self, x):

        out, (hn_1, cn_1) = self.lstm_layer_1(x)
        out, (hn_2, cn_2) = self.lstm_layer_2(out)
        out, (hn_3, cn_3) = self.lstm_layer_3(out)

        out = hn_3[-1]
        out = self.fc(out)
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

class Linear(nn.Module):
    def __init__(self,input_size,linear_layer_size,output_size):
        super(Linear,self).__init__()
        
        self.relu =nn.ReLU()
        self.sigmoid =nn.Sigmoid()
        self.tanh = nn.Tanh()
        for i in range(len(linear_layer_size)):
                if i == 0:
                    self.fc_layers.append(nn.Linear(input_size, linear_layer_size[i]))
                else:
                    self.fc_layers.append(nn.Linear(linear_layer_size[i-1], linear_layer_size[i]))
        self.output = nn.Linear(linear_layer_size[-1],output_size)

        self.apply(self.initialize_weights)

    def forward(self,x):
        out = self.relu(self.input(x))
        out = self.relu(self.fc(out))
        out = self.output(out)
        return out
    
    def initialize_weights(self, layer):
        if isinstance(layer, nn.Linear):
            nn.init.xavier_uniform_(layer.weight)
            nn.init.zeros_(layer.bias)
            
class LUCLSTM(nn.Module):
    def __init__(self, input_size, lstm_layer_sizes, output_size):
        super(LUCLSTM, self).__init__()

        self.input_size = input_size

        self.lstm_layer_1 = nn.LSTM(input_size, lstm_layer_sizes[0], batch_first=True)
        self.lstm_layer_2 = nn.LSTM(lstm_layer_sizes[0], lstm_layer_sizes[1], batch_first=True)
        self.lstm_layer_3 = nn.LSTM(lstm_layer_sizes[1], lstm_layer_sizes[2], batch_first=True)

        self.fc = nn.Linear(lstm_layer_sizes[2],64)
        self.fc2 = nn.Linear(64,output_size)
        self.tanh = nn.Tanh()
        self.relu =nn.ReLU()

        self.apply(self.initialize_weights)

    def forward(self, x):

        out, (hn_1, cn_1) = self.lstm_layer_1(x)
        out, (hn_2, cn_2) = self.lstm_layer_2(out)
        out, (hn_3, cn_3) = self.lstm_layer_3(out)

        out = hn_3[-1]
        out = self.tanh(self.fc(out))
        out = self.fc2(out)
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

class RainfallLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, num_layers):
        super(RainfallLSTM, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.relu = nn.ReLU()

    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        h_n = h_n[-1] 
        return self.relu(self.fc(h_n))
    
class PositionalEncoding(nn.Module):
    def __init__(self, dim, max_len=300):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, dim, 2).float() * (-math.log(10000.0) / dim))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:x.size(0), :]
    
class Transformer(nn.Module):
    def __init__(self):
        super(Transformer,self).__init__()