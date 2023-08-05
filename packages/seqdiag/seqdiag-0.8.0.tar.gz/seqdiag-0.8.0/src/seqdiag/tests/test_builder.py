# -*- coding: utf-8 -*-

import unittest2
from utils import __build_diagram as build_diagram


class TestBuilder(unittest2.TestCase):
    def test_separators(self):
        diagram = build_diagram("separators.diag")

        self.assertEqual(5, len(diagram.edges))
        self.assertEqual(4, len(diagram.separators))

        self.assertEqual(2, diagram.separators[0].order)
        self.assertEqual("separator", diagram.separators[0].label)
        self.assertEqual(4, diagram.separators[1].order)
        self.assertEqual("separator", diagram.separators[1].label)
        self.assertEqual(6, diagram.separators[2].order)
        self.assertEqual("quoted separator", diagram.separators[2].label)
        self.assertEqual(8, diagram.separators[3].order)
        self.assertEqual("separator(1)", diagram.separators[3].label)
