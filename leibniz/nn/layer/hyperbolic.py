# -*- coding: utf-8 -*-

import torch as th
import torch.nn as nn

from leibniz.nn.layer.cbam import CBAM


class BasicBlock(nn.Module):
    def __init__(self, in_channel, out_channel, step, relu, conv, reduction=16):
        super(BasicBlock, self).__init__()
        self.step = step
        self.relu = relu

        self.conv1 = conv(in_channel, in_channel, kernel_size=3, stride=1, padding=1)
        self.conv2 = conv(in_channel, out_channel, kernel_size=3, stride=1, padding=1)
        self.cbam = CBAM(out_channel, reduction=reduction, conv=conv)

    def forward(self, x):
        y = self.conv1(x)
        y = self.relu(y)
        y = self.conv2(y)
        y = self.cbam(y)
        return y


class Bottleneck(nn.Module):
    def __init__(self, in_channel, out_channel, step, relu, conv, reduction=16):
        super(Bottleneck, self).__init__()
        self.step = step
        self.relu = relu

        hd_channel = in_channel // 4 + 1
        self.conv1 = conv(in_channel, hd_channel, kernel_size=1, bias=False)
        self.conv2 = conv(hd_channel, hd_channel, kernel_size=3, bias=False, padding=1)
        self.conv3 = conv(hd_channel, out_channel, kernel_size=1, bias=False)
        self.cbam = CBAM(out_channel, reduction=reduction, conv=conv)

    def forward(self, x):
        y = self.conv1(x)
        y = self.relu(y)
        y = self.conv2(y)
        y = self.relu(y)
        y = self.conv3(y)
        y = self.cbam(y)
        return y


class HyperBasic(nn.Module):
    extension = 1
    least_required_dim = 1

    def __init__(self, dim, step, relu, conv, reduction=16):
        super(HyperBasic, self).__init__()
        self.dim = dim
        self.step = step
        self.input = BasicBlock(dim, 2 * dim, step, relu, conv, reduction=reduction)
        self.output = BasicBlock(7 * self.dim, self.dim, step, relu, conv, reduction=reduction)

    def forward(self, x):
        input = self.input(x)
        cs, ss = input[:, :self.dim] * self.step, input[:, self.dim:] * self.step

        y1 = (1 + ss) * x + cs
        y2 = (1 + cs) * x - ss
        y3 = (1 - cs) * x + ss
        y4 = (1 - ss) * x - cs

        ys = th.cat((y1, y2, y3, y4, cs, ss, x), dim=1)
        return x + self.output(ys)


class HyperBottleneck(nn.Module):
    extension = 1
    least_required_dim = 1

    def __init__(self, dim, step, relu, conv, reduction=16):
        super(HyperBottleneck, self).__init__()
        self.dim = dim
        self.step = step
        self.input = Bottleneck(dim, 2 * dim, step, relu, conv, reduction=reduction)
        self.output = Bottleneck(7 * dim, dim, step, relu, conv, reduction=reduction)

    def forward(self, x):
        input = self.input(x)
        cs, ss = input[:, :self.dim] * self.step, input[:, self.dim:] * self.step

        y1 = (1 + ss) * x + cs
        y2 = (1 + cs) * x - ss
        y3 = (1 - cs) * x + ss
        y4 = (1 - ss) * x - cs

        ys = th.cat((y1, y2, y3, y4, cs, ss, x), dim=1)
        return x + self.output(ys)
