
import colorsys

def unpack_css_color(csscolor):
    # TODO: implement #ABC → #AABBCC
    csscolor = csscolor.lstrip("#")
    rgbtuple = csscolor[:2], csscolor[2:4], csscolor[4:]
    return tuple(int(component, 16) for component in rgbtuple)

def pack_css_color(rgbtuple):
    return "#%02x%02x%02x" % tuple([int(x) for x in rgbtuple])

def decay(module, current_color, rate=0.8):
    if hasattr(module, "_orig_color"):
        h, s, v = colorsys.rgb_to_hsv(*unpack_css_color(current_color))
        foo, bar, orig_v = colorsys.rgb_to_hsv(*unpack_css_color(module._orig_color))

        v *= rate
        v = 80 if v < 80 else v
        ret = pack_css_color(colorsys.hsv_to_rgb(h, s, v))
        module._orig_color = current_color
        return ret
    else:
        module._orig_color = current_color
        return current_color

class ColorModule:
    # dynamically re-base the module base classes on this class, if
    # Status get's the color_decay=True param
    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, nv):
        if "color" in nv:
            self._original_color = nv["color"]

        self._output = nv