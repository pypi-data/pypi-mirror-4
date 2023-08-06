import unittest

from ginsfsm.gconfig import (
    GConfig,
    GConfigTemplateError,
    GConfigValidateError,
    )


class TestGConfig(unittest.TestCase):
    def setUp(self):
        self.gconfig = GConfig({})

    def test_set_bad_argument(self):
        self.assertRaises(GConfigTemplateError, GConfig, '')
        self.assertRaises(GConfigTemplateError, GConfig, {0: []})
        self.assertRaises(GConfigTemplateError, GConfig, {'': []})
        self.assertRaises(GConfigTemplateError, GConfig, {'x': []})
        self.assertRaises(GConfigTemplateError, GConfig, {'x': 0})
        self.assertRaises(GConfigTemplateError, GConfig, {'x': [0]})
        self.assertRaises(GConfigTemplateError, GConfig,
                          {'x': [0, 0, 0, 0, '']})
        self.assertRaises(GConfigTemplateError, GConfig,
                          {'x': [GConfig, 0, 0, None, '']})

        def p():
            pass
        self.assertRaises(GConfigTemplateError, GConfig, {'x': [0, 0, 0, p, 0]})

        conf = GConfig({'x': [int, 0, 0, None, '']})
        self.assertTrue(isinstance(conf, GConfig))
        self.assertTrue(hasattr(conf, 'x'))
        value = conf.read_parameter('x')
        self.assertEqual(value, 0)

        conf = GConfig({'y': [int, -2, 0, None, '']})
        self.assertTrue(isinstance(conf, GConfig))
        self.assertTrue(hasattr(conf, 'y'))
        value = conf.read_parameter('y')
        self.assertEqual(value, -2)

        conf = GConfig({
            'bt': [bool, "True", 0, None, ''],
            'bf': [bool, "False", 0, None, ''],
            'bn': [bool, None, 0, None, ''],
            'x': [int, 100, 0, None, ''],
            'y': [int, -2, 0, None, ''],
            's': [str, "kk", 0, None, ''],
            'None': [str, None, 0, None, ''],
            }
        )
        self.assertTrue(isinstance(conf, GConfig))
        value = conf.read_parameter('x')
        self.assertEqual(value, 100)
        value = conf.read_parameter('y')
        self.assertEqual(value, -2)
        value = conf.read_parameter('s')
        self.assertEqual(value, 'kk')
        value = conf.read_parameter('bt')
        self.assertEqual(value, True)
        value = conf.read_parameter('bf')
        self.assertEqual(value, False)
        value = conf.read_parameter('bn')
        self.assertEqual(value, False)
        value = conf.read_parameter('None')
        self.assertEqual(value, None)

        conf.write_parameters(bt=False)
        value = conf.read_parameter('bt')
        self.assertEqual(value, False)

        conf.reset_parameter('bt')
        value = conf.read_parameter('bt')
        self.assertEqual(value, True)

        conf = GConfig({
            'lst': [list, ['', 0], 0, None, ''],
            'tup': [tuple, ('', 0), 0, None, ''],
            }
        )
        self.assertTrue(isinstance(conf, GConfig))
        value = conf.read_parameter('lst')
        self.assertEqual(value, ['', 0])
        value = conf.read_parameter('tup')
        self.assertEqual(value, ('', 0))
        conf.write_parameters(xx=False)

        definition = [tuple, ('', 0), 0, None, '']
        conf = GConfig({
            'tup': definition,
            }
        )
        conf.write_parameters(tup=(0, 0))
        definition[0] = GConfig
        conf.write_parameters(tup=(0, 0))

        conf = GConfig({
            'lst': [list, ['', 0], 0, None, ''],
            'tup': [tuple, ('', 0), 0, None, ''],
            }
        )
        conf.read_parameters()

        conf = GConfig({
            'x': [None, GConfig, 0, None, ''],
            }
        )
        value = conf.read_parameter('x')
        self.assertTrue(value is GConfig)

        def validate(value):
            if value < -5:
                raise Exception
            if value < 0:
                return False
            return True

        self.assertRaises(GConfigValidateError, GConfig,
            {'y': [int, -10, 0, validate, '']})
        value = conf.read_parameter('y')
        self.assertTrue(value is None)

        conf = GConfig({'y': [int, 10, 0, validate, '']})
        value = conf.read_parameter('y')
        self.assertTrue(value is 10)
        conf.write_parameters(y=20)
        value = conf.read_parameter('y')
        self.assertTrue(value is 20)
        conf.reset_all_parameters()
        value = conf.read_parameter('y')
        self.assertTrue(value is 10)
        value = conf.read_parameter('yyy')
        self.assertTrue(value is None)
