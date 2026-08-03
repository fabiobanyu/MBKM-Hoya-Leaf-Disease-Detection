import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models

class CBAM(nn.Module):
    def __init__(self, channels, reduction=16):
        super(CBAM, self).__init__()
        self.fc1 = nn.Conv2d(channels, channels // reduction, 1, bias=False)
        self.relu = nn.ReLU(inplace=True)
        self.fc2 = nn.Conv2d(channels // reduction, channels, 1, bias=False)
        self.sigmoid_channel = nn.Sigmoid()
        
        self.conv_spatial = nn.Conv2d(2, 1, kernel_size=7, padding=3, bias=False)
        self.sigmoid_spatial = nn.Sigmoid()

    def forward(self, x):
        avg_out = self.fc2(self.relu(self.fc1(F.adaptive_avg_pool2d(x, 1))))
        max_out = self.fc2(self.relu(self.fc1(F.adaptive_max_pool2d(x, 1))))
        out = avg_out + max_out
        x = x * self.sigmoid_channel(out)
        
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        spatial_out = self.sigmoid_spatial(self.conv_spatial(torch.cat([avg_out, max_out], dim=1)))
        return x * spatial_out

class MultiTaskHoyaModel(nn.Module):
    def __init__(self, feature_extractor, in_features, num_disease, num_species, dropout):
        super().__init__()
        self.feature_extractor = feature_extractor
        self.attention = CBAM(in_features)
        self.disease_head = nn.Sequential(
            nn.Dropout(dropout), nn.Linear(in_features, 512), nn.GELU(),
            nn.BatchNorm1d(512), nn.Dropout(dropout), nn.Linear(512, num_disease),
        )
        self.species_head = nn.Sequential(
            nn.Dropout(dropout), nn.Linear(in_features, 256), nn.GELU(),
            nn.BatchNorm1d(256), nn.Dropout(dropout), nn.Linear(256, num_species),
        )
        self.gate_head = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        feat_map = self.feature_extractor(x)
        
        # Gate path (uses raw backbone features before attention)
        raw_feat = F.relu(feat_map, inplace=False)
        raw_feat_pooled = F.adaptive_avg_pool2d(raw_feat, (1, 1)).view(raw_feat.size(0), -1)
        gate_out = self.gate_head(raw_feat_pooled)
        
        # Disease / Species path
        feat_map_att = self.attention(feat_map) 
        feat_att = F.relu(feat_map_att, inplace=False)
        feat_att_pooled = F.adaptive_avg_pool2d(feat_att, (1, 1)).view(feat_att.size(0), -1)
        
        return gate_out, self.disease_head(feat_att_pooled), self.species_head(feat_att_pooled)

def build_model(arch='resnet50', num_disease=5, num_species=10, dropout=0.40):
    if arch.lower() == 'densenet121':
        base = models.densenet121(weights=None)
        in_features = base.classifier.in_features
        feature_extractor = base.features
    else:
        base = models.resnet50(weights=None)
        in_features = base.fc.in_features
        feature_extractor = nn.Sequential(*list(base.children())[:-2])
        
    model = MultiTaskHoyaModel(feature_extractor, in_features, num_disease, num_species, dropout)
    return model

class DiseaseOnlyWrapper(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model
    def forward(self, x):
        _, disease_out, _ = self.model(x)
        return disease_out
