import _charting
import converters


def __check_data__(data):
    if 'lines' not in data:
        raise ValueError('The data dictionary must contain a "lines" key.')
    if data['lines'].__class__ is not list:
        raise ValueError('The values entry must be submited as a list.')
    for line in data['lines']:
        if 'values' not in line:
            raise ValueError('Each line entry must contain a "values" key.')


def plot(data, path):
    __check_data__(data)

    x_vals = [x[0] for x in [i for s in data['lines'] for i in s['values']]]
    y_vals = [x[1] for x in [i for s in data['lines'] for i in s['values']]]

    max_x = max(x_vals)
    max_y = max(y_vals)
    min_x = min(x_vals)
    min_y = min(y_vals)

    max_x = converters.float_to_upper_rounded_int(max_x)
    max_y = converters.float_to_upper_rounded_int(max_y)
    min_x = converters.float_to_upper_rounded_int(min_x)
    min_y = converters.float_to_upper_rounded_int(min_y)

    for line in data['lines']:
        if 'color' in line:
            line['color'] = converters.rgb_to_cairo_rgb(line['color'])
        line['values'] = sorted(line['values'], key=lambda t: t[0])
        map(converters.tuple_items_to_float, line['values'])
        print  line['values']



    _charting.plot_linechart(data, (709, 500), max_x, max_y, min_x, min_y, path)




