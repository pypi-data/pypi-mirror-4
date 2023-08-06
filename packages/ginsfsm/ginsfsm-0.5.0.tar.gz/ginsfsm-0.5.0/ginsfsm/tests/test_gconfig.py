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
        self.assertTrue(hasattr(conf.config, 'x'))
        value = conf.read_parameter('x')
        self.assertEqual(value, 0)

        conf = GConfig({'y': [int, -2, 0, None, '']})
        self.assertTrue(isinstance(conf, GConfig))
        self.assertTrue(hasattr(conf.config, 'y'))
        value = conf.read_parameter('y')
        self.assertEqual(value, -2)

        conf = GConfig(
            {
                'bt': [bool, "True", 0, None, ''],
                'bf': [bool, "False", 0, None, ''],
                'bn': [bool, None, 0, None, ''],
                'x': [int, 100, 0, None, ''],
                'y': [int, -2, 0, None, ''],
                's': [str, "kk", 0, None, ''],
                'None': [str, None, 0, None, ''],
                'ss': [list, "kk,mm", 0, None, ''],
                'pp': [tuple, "kk,mm", 0, None, ''],
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

        value = conf.read_parameter('ss')
        self.assertEqual(value, ['kk', 'mm'])

        value = conf.read_parameter('pp')
        self.assertEqual(value, ('kk', 'mm'))

        conf = GConfig(
            {
                'lst': [list, ['', 0], 0, None, ''],
                'tup': [tuple, ('', 0), 0, None, ''],
            }
        )
        self.assertTrue(isinstance(conf, GConfig))
        value = conf.read_parameter('lst')
        self.assertEqual(value, ['', 0])
        value = conf.read_parameter('tup')
        self.assertEqual(value, ('', 0))
        #conf.write_parameters(xx=False)

        definition = [tuple, ('', 0), 0, None, '']
        conf = GConfig(
            {
                'tup': definition,
            }
        )
        conf.write_parameters(tup=(0, 0))
        definition[0] = GConfig
        conf.write_parameters(tup=(0, 0))

        conf = GConfig(
            {
                'lst': [list, ['', 0], 0, None, ''],
                'tup': [tuple, ('', 0), 0, None, ''],
            }
        )
        conf.read_parameters()

        conf = GConfig(
            {
                'x': [None, GConfig, 0, None, ''],
            }
        )
        value = conf.read_parameter('x')
        self.assertTrue(value is GConfig)

        def validate1(value):
            if value < -5:
                raise ValueError('Value too low %r' % value)
            if value < 0:
                return 0
            return value

        self.assertRaises(
            GConfigValidateError,
            GConfig,
            {
                'y': [int, -10, 0, validate1, '']
            }
        )
        value = conf.read_parameter('y')
        self.assertEqual(value, None)

        conf = GConfig({'y': [int, 10, 0, validate1, '']})
        value = conf.read_parameter('y')
        self.assertEqual(value, 10)
        conf.write_parameters(y=20)
        value = conf.read_parameter('y')
        self.assertTrue(value is 20)
        conf.reset_all_parameters()
        value = conf.read_parameter('y')
        self.assertTrue(value is 10)
        value = conf.read_parameter('yyy')
        self.assertTrue(value is None)

        def validate2(value):
            """
            sca1, sca+sca, http://localhost:8002+http://localhost:8002;
            sca2, sca+sca, http://localhost:8003+http://localhost:8003;

            must convert in:

            ((
                'sca1',
                ('sca','sca'),
                ('http://localhost:8002', 'http://localhost:8002'),
            ),
            (
                'sca2',
                ('sca','sca'),
                ('http://localhost:8003', 'http://localhost:8003'),
            ))

            """
            routes = []
            if value:
                value = value.split(';')
                for r in value:
                    r = r.strip()
                    if r:
                        routes.append(r)

                for idx, r in enumerate(routes):
                    items = r.split(',')
                    v = []
                    for it in items:
                        it = it.strip()
                        if it:
                            v.append(it)
                    routes[idx] = v

                for r in routes:
                    for idx, field in enumerate(r):
                        v = []
                        if not '+' in field:
                            v.append(field)
                            continue
                        items = field.split('+')
                        for e in items:
                            e = e.strip()
                            if e:
                                v.append(e)
                        r[idx] = tuple(v)

                for idx, r in enumerate(routes):
                    routes[idx] = tuple(r)

            return routes

        conf = GConfig(
            {
                'x': [tuple, None, 0, validate2, ''],
            }
        )
        s = """
            sca1, sca+sca, http://localhost:8002+http://localhost:8002;
            sca2, sca+sca, http://localhost:8003+http://localhost:8003;
            """
        d = (
            (
                'sca1',
                ('sca', 'sca'),
                ('http://localhost:8002', 'http://localhost:8002'),
            ),
            (
                'sca2',
                ('sca', 'sca'),
                ('http://localhost:8003', 'http://localhost:8003'),
            )
        )

        conf.write_parameters(x=s)
        x = conf.read_parameter('x')
        self.assertEqual(x, d)
