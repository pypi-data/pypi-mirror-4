import unittest

from cdecimal import Decimal
import numpy as np

from bmfstock import Paper, PaperItem


class TestItemPaper(unittest.TestCase):
    def test_str(self):
        item = PaperItem('petr4')
        self.assertEqual(item.paper.code, 'PETR4')

    def test_paper(self):
        paper = Paper('petr4')
        item = PaperItem(paper)
        self.assertIs(item.paper, paper)

        self.assertIs(item.value, None)
        item.value = '2.23'
        self.assertNotEqual(item.value, None)

        item.paper = 'petrf22'
        self.assertEqual(item.paper.code, 'PETRF22')
        self.assertNotEqual(item.paper, paper)
        self.assertIs(item.value, None)

    def test_calculate(self):
        petr4 = PaperItem('petr4')
        petr4.value = '25.27'
        petrf25 = PaperItem('petrf25')
        petrf25.paper.strike = '25.00'
        petrf25.value = '0.66'
        petrf25.buy = False

        arange = np.arange(0, 100, Decimal('0.01'))
        c1 = petr4.calculate(arange)
        c2 = petrf25.calculate(arange)

        cs = np.array([c1, c2]).sum(axis=0)
        lucro_max = cs.argmax() / 100.
        self.assertEqual(25.00, lucro_max)
