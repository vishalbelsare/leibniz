# -*- coding: utf-8 -*-

import unittest
import torch as th
import torch.nn as nn

from torch.nn import Tanh, MSELoss, Sequential
from leibniz.nn.activation import Atanh
from leibniz.nn.normalizor import PWLNormalizor


class TestNormalizor(unittest.TestCase):

    def setUp(self):
        self.tanh = Tanh()
        self.atanh = Atanh()
        self.pwln = PWLNormalizor(2, 128)
        self.mlp = Sequential(
            self.pwln.app,
            nn.Linear(2, 16),
            nn.ReLU(inplace=True),
            nn.Linear(16, 16),
            nn.ReLU(inplace=True),
            nn.Linear(16, 2),
            self.pwln.inv,
        )
        self.apx = Sequential(
            self.pwln.app,
            self.pwln.inv,
        )

    def tearDown(self):
        pass

    def func(self, x):
        return x * 2 + 0.5 * th.cos(x * 8)

    def testAtanh(self):
        self.assertAlmostEqual(6.0, self.atanh(self.tanh(th.as_tensor(6.0))).numpy(), places=3)
        self.assertAlmostEqual(5.0, self.atanh(self.tanh(th.as_tensor(5.0))).numpy(), places=3)
        self.assertAlmostEqual(4.0, self.atanh(self.tanh(th.as_tensor(4.0))).numpy(), places=4)
        self.assertAlmostEqual(3.0, self.atanh(self.tanh(th.as_tensor(3.0))).numpy(), places=5)
        self.assertAlmostEqual(2.0, self.atanh(self.tanh(th.as_tensor(2.0))).numpy())
        self.assertAlmostEqual(1.0, self.atanh(self.tanh(th.as_tensor(1.0))).numpy())

        self.assertAlmostEqual(-1.0, self.atanh(self.tanh(th.as_tensor(-1.0))).numpy(), places=6)
        self.assertAlmostEqual(-2.0, self.atanh(self.tanh(th.as_tensor(-2.0))).numpy(), places=5)
        self.assertAlmostEqual(-3.0, self.atanh(self.tanh(th.as_tensor(-3.0))).numpy(), places=4)
        self.assertAlmostEqual(-4.0, self.atanh(self.tanh(th.as_tensor(-4.0))).numpy(), places=4)
        self.assertAlmostEqual(-5.0, self.atanh(self.tanh(th.as_tensor(-5.0))).numpy(), places=3)
        self.assertAlmostEqual(-6.0, self.atanh(self.tanh(th.as_tensor(-6.0))).numpy(), places=3)

        self.assertAlmostEqual(0.1, self.atanh(self.tanh(th.as_tensor(0.1))).numpy())
        self.assertAlmostEqual(0.2, self.atanh(self.tanh(th.as_tensor(0.2))).numpy())
        self.assertAlmostEqual(0.3, self.atanh(self.tanh(th.as_tensor(0.3))).numpy())
        self.assertAlmostEqual(0.4, self.atanh(self.tanh(th.as_tensor(0.4))).numpy())
        self.assertAlmostEqual(0.5, self.atanh(self.tanh(th.as_tensor(0.5))).numpy())
        self.assertAlmostEqual(0.6, self.atanh(self.tanh(th.as_tensor(0.6))).numpy())
        self.assertAlmostEqual(0.7, self.atanh(self.tanh(th.as_tensor(0.7))).numpy())
        self.assertAlmostEqual(0.8, self.atanh(self.tanh(th.as_tensor(0.8))).numpy())
        self.assertAlmostEqual(0.9, self.atanh(self.tanh(th.as_tensor(0.9))).numpy())

    def testPWLN(self):
        lr = 0.001
        optimizer = th.optim.Adam(self.mlp.parameters(), lr=lr)
        mse = MSELoss()
        for _ in range(10):
            for _ in range(100):
                data = self.func(th.rand(128, 2))
                loss = mse(self.mlp(data), data * data * data)
                print('loss', loss.item())
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            with th.no_grad():
                print(0.1, self.func(th.as_tensor([0.1, 0.1])).detach().numpy(), self.pwln.inverse(self.pwln(self.func(th.as_tensor([0.1, 0.1]).reshape(1, 2)))).detach().numpy())
                print(0.2, self.func(th.as_tensor([0.2, 0.2])).detach().numpy(), self.pwln.inverse(self.pwln(self.func(th.as_tensor([0.2, 0.2]).reshape(1, 2)))).detach().numpy())
                print(0.3, self.func(th.as_tensor([0.3, 0.3])).detach().numpy(), self.pwln.inverse(self.pwln(self.func(th.as_tensor([0.3, 0.3]).reshape(1, 2)))).detach().numpy())
                print(0.4, self.func(th.as_tensor([0.4, 0.4])).detach().numpy(), self.pwln.inverse(self.pwln(self.func(th.as_tensor([0.4, 0.4]).reshape(1, 2)))).detach().numpy())
                print(0.5, self.func(th.as_tensor([0.5, 0.5])).detach().numpy(), self.pwln.inverse(self.pwln(self.func(th.as_tensor([0.5, 0.5]).reshape(1, 2)))).detach().numpy())
                print(0.6, self.func(th.as_tensor([0.6, 0.6])).detach().numpy(), self.pwln.inverse(self.pwln(self.func(th.as_tensor([0.6, 0.6]).reshape(1, 2)))).detach().numpy())
                print(0.7, self.func(th.as_tensor([0.7, 0.7])).detach().numpy(), self.pwln.inverse(self.pwln(self.func(th.as_tensor([0.7, 0.7]).reshape(1, 2)))).detach().numpy())
                print(0.8, self.func(th.as_tensor([0.8, 0.8])).detach().numpy(), self.pwln.inverse(self.pwln(self.func(th.as_tensor([0.8, 0.8]).reshape(1, 2)))).detach().numpy())
                print(0.9, self.func(th.as_tensor([0.9, 0.9])).detach().numpy(), self.pwln.inverse(self.pwln(self.func(th.as_tensor([0.9, 0.9]).reshape(1, 2)))).detach().numpy())

        data = self.func(th.rand(1, 2))
        self.assertAlmostEqual(data.detach().numpy()[0, 0], self.pwln.inverse(self.pwln(data)).detach().numpy()[0, 0], places=3)

