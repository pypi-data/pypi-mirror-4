import os
import unittest
import charting
import converters

class ConvertersTests(unittest.TestCase):
    def test_convert_rgb_to_cairo_rgb(self):
        rgb = (3, 42, 31)
        result = converters.rgb_to_cairo_rgb(rgb)
        self.assertEquals(result[0], 0.011764705882352941)
        self.assertEquals(result[1], 0.16470588235294117)
        self.assertEquals(result[2], 0.12156862745098039)



class BeautifulChartsTests(unittest.TestCase):
    def setUp(self):
        if not os.path.exists('examples'):
            os.makedirs('examples')

    def test_should_fail_without_lines_key(self):
        self.assertRaises(ValueError, charting.plot, {}, 'examples/chart1.png')

    def test_should_fail_without_values_key(self):
        self.assertRaises(ValueError, charting.plot, { 'lines' : [] }, 'examples/chart1.png')

    def test_non_list_values_must_fail(self):
        self.assertRaises(ValueError, charting.plot, { 'lines' : [{ 'values' : [] }] }, 'examples/chart1.png')

    def test_generate_linechart(self):
        charting.plot({
            'lines' : [
                { 'values' : [
                (6.0, 4.0),
                (3.0, 2.0),
                (8.0, 10.0),
                (1.0, 5.0),
                (0.0, 10.0)
                ],
                'legend' : 'legend 1',
                'color' : (231, 101, 100)
                },
                { 'values' : [
                (6.0, 2.0),
                (3.0, 6.0),
                (8.0, 15.0),
                (10.0, 9.0),
                (0.0, 10.0)
                ],
                'legend' : 'legend 2',
                'color' : (177, 203, 127)
                }
            ]
        }, 'examples/chart.png')

    def test_generate_large_linechart(self):
        charting.plot({
            'lines' : [
                { 'values' : [
                (6.0, 4.0),
                (3.0, 6.0),
                (8.0, 7.0),
                (1.0, 45.0),
                (0.0, 10.0)
                ],
                'legend' : 'legend 1',
                'color' : (231, 101, 100)
                },
                { 'values' : [
                (6.0, 4.0),
                (3.0, 6.0),
                (44.0, 14.0),
                (10.0, 9.0),
                (0.0, 15.0)
                ],
                'legend' : 'legend 2',
                'color' : (177, 203, 127)
                }
            ]
        }, 'examples/largechart.png')



if __name__ == '__main__':
    unittest.main()
