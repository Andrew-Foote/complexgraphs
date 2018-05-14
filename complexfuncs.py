import pygame, pygame.font
import sys
import math, cmath
from fractions import Fraction

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        raise ValueError

GRAPH_WIDTH = 8
GRAPH_HEIGHT = 8

def transform_coords(x, y, w, h, nw, nh):
    """Transforms the coordinates of a rect into a 10-by-10 complex plane.
    (x, y) are the original pixel coordinates, (w, h) is the number of pixels
    within the display, nw is the magnitude of the maximum real part shown on
    the complex plane, nh is the magnitude of the maximum imaginary part shown
    on the complex plane."""
    return ((((x / w) - 0.5) * nw), (((h - y) / h) - 0.5) * nh)
            
def cmplx_to_str(re, im = None):
    if re == "undefined":
        return re
    if im == None:
        if isinstance(re, tuple):
            return cmplx_to_str(re[0], re[1])
        elif isinstance(re, complex):
            return cmplx_to_str(re.real, re.imag)
    else:
        impart = ("i" if abs(im) == 1 else str(round(abs(im), 5)) + " i")
        if re == 0 and im == 0:
            s = "0"
        elif re == 0:
            s = impart
        else:
            s = str(round(re, 5))
            if im > 0:
                s += " + " + impart
            elif im < 0:
                s += " - " + impart
        return s
        
class Textbox(pygame.Surface):
    def __init__(self, font, *args):
        pygame.Surface.__init__(self, *args)
        self.font = font
        self.text = ""
        self.ts = None
    
    def write(self, text, colour = (0, 0, 0), antialias = True):
        self.text = text
        self.colour = colour
        self.antialias = antialias
        self.ts = self.font.render(self.text, antialias, colour)
    
    def update(self):
        if self.ts == None:
            pass
        else:
            self.blit(self.ts, (0, 0))
            
def is_within(point, surface, offset):
    """Tests whether a point is within the surface"""
    return (point[0] >= offset[0] and point[0] < offset[0] + surface.get_width() \
            and point[1] >= offset[1] and point[1] < offset[1] + surface.get_height())

def math_gamma(x):
    p = 1
    for i in range(int(x.real)):
        p *= (i + 1)
    return p
        
def math_choose(n, k):
    p = 1
    for i in range(int(k.real)):
        p *= (n - i)
    return p / math_fact(k)

def math_weierstrauss(x):
    y = 0
    n = 0
    for i in range(100):
        y += 0.8**n * cmath.cos(5**n * math.pi * x)
    return y        
    
class CGrapher:
    H_DOFFSET = 20
    V_DOFFSET = 20
    def __init__(self, width, height):
        self.font = pygame.font.Font(None, 18)
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), 0, 32)
        pygame.display.set_caption("Complex Graph")
        self.display = pygame.Surface((width - CGrapher.H_DOFFSET, height - CGrapher.V_DOFFSET))
        self.txt_function = Textbox(self.font, ((width - CGrapher.H_DOFFSET) / 2 - 20, CGrapher.V_DOFFSET))
        self.txt_editfunc = Textbox(self.font, (30, CGrapher.V_DOFFSET))
        self.txt_coords = Textbox(self.font, ((width - CGrapher.H_DOFFSET) / 2 - 10, CGrapher.V_DOFFSET))
        self.func = "sin(x)"
        self.output = {}
            
    def draw_graph(self):
        for i in range(self.width - CGrapher.H_DOFFSET):
            for j in range(self.height - CGrapher.V_DOFFSET):
                (re, im) = transform_coords(i, j, self.width - CGrapher.H_DOFFSET, self.height - CGrapher.V_DOFFSET, GRAPH_WIDTH, GRAPH_HEIGHT)
                try:
                    y = self.do_func(self.func, complex(re, im))
                    self.output[complex(re, im)] = complex(y)
                    r = math.floor((math.erf(y.real) + 1) * 128)
                    #r = math.floor(abs(y.real / math.sqrt(y.real ** 2 + 1) * 255))
                    g = 0
                    b = math.floor((math.erf(y.imag) + 1) * 128)
                    #b = math.floor(abs(y.imag / math.sqrt(y.imag ** 2 + 1) * 255))
                except (ValueError, ZeroDivisionError):                
                    self.output[complex(re, im)] = "undefined"
                    r, g, b = 0, 0, 0
                    
                if r >= 256:
                    r = 255
                if b >= 256:
                    b = 255
                self.display.set_at((i, j), (r, g, b))
        pygame.image.save(self.display, "_complexfuncs.py_display.bmp")
        self.txt_function.write("f(x) = " + self.func)

    def do_func(self, funcstr, x):
        return eval(funcstr, {"x": x,
            "e": cmath.e, "pi": cmath.pi, "i": 1j, "exp": cmath.exp,
            "sin": cmath.sin, "cos": cmath.cos, "tan": cmath.tan, "sinh": cmath.sinh, "cosh": cmath.cosh, "tanh": cmath.tanh,
            "sec": lambda x: 1 / cmath.cos(x), "csc": lambda x: 1 / cmath.sin(x), "cot": lambda x: cmath.cos(x) / cmath.sin(x),
            "sech": lambda x: 1 / cmath.cosh(x), "csch": lambda x: 1 / cmath.sinh(x), "coth": lambda x: cmath.cosh(x) / cmath.sinh(x),
            "arcsin": cmath.asin, "arccos": cmath.acos, "arctan": cmath.atan, "arsinh": cmath.asinh, "arcosh": cmath.acosh, "artanh": cmath.atanh,
            "arcsec": lambda x: cmath.acos(1 / x), "arccsc": lambda x: cmath.asin(1 / x), "arccot": lambda x: cmath.atan(1 / x),
            "arsech": lambda x: cmath.acosh(1 / x), "arcsch": lambda x: cmath.asinh(1 / x), "arcoth": lambda x: cmath.atanh(1 / x),
            "abs": abs, "sgn": sign, "arg": cmath.phase, "cis": lambda x: cmath.cos(x) + 1j * cmath.sin(x),
            "pow": pow, "sqrt": cmath.sqrt, "nrt": lambda x, n: x**(1/n), "log": cmath.log, "ln": lambda x: cmath.log(x),
            "floor": math.floor, "ceil": math.ceil, "trunc": math.trunc, "round": round,
            "gamma": math_gamma, "weierstrauss": math_weierstrauss, "choose": math_choose, "max": max, "min": min
        }, {})

    def mainloop(self):
        self.font.set_bold(True)
        self.txt_editfunc.write("Edit")
        self.font.set_bold(False)
        while True:
            self.screen.fill((255, 255, 255))
            self.txt_function.fill((255, 255, 255))
            self.txt_editfunc.fill((255, 255, 255))
            self.txt_coords.fill((255, 255, 255))
            self.screen.blit(self.display, (0, 0))
            self.txt_function.update()
            self.txt_editfunc.update()
            self.txt_coords.update()
            self.screen.blit(self.txt_function, (2, (self.height - CGrapher.V_DOFFSET + 4)))
            self.screen.blit(self.txt_editfunc, ((self.width - CGrapher.H_DOFFSET) / 2 - 50, self.height - CGrapher.V_DOFFSET + 4))
            self.screen.blit(self.txt_coords, ((self.width - CGrapher.H_DOFFSET) / 2 + 10, self.height - CGrapher.V_DOFFSET + 4))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEMOTION:
                    (i, j) = event.pos
                    if i < self.width - CGrapher.H_DOFFSET and j < self.height - CGrapher.V_DOFFSET:
                        (re, im) = transform_coords(i, j, self.width - CGrapher.H_DOFFSET, self.height - CGrapher.V_DOFFSET, GRAPH_WIDTH, GRAPH_HEIGHT)
                        op = self.output[complex(re, im)]
                        self.txt_coords.write("f(" + cmplx_to_str(re, im) + ") = " + cmplx_to_str(op))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print(event.pos)
                    if is_within(event.pos, self.txt_editfunc, ((self.width - CGrapher.H_DOFFSET) / 2 - 50, (self.height - CGrapher.V_DOFFSET) + 4)):
                        self.func = input("New function: ")
                        self.draw_graph()
            pygame.display.flip()

        
if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    a = CGrapher(520, 520)
    a.draw_graph()
    a.mainloop()
#    func = "nrt(x, 5)"
#    WIDTH, HEIGHT = 520, 520
#    DWIDTH, DHEIGHT = 500, 500
#    pygame.init()
#    pygame.font.init()
#    txtfont = pygame.font.Font(None, 18)
#    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
#    display = pygame.Surface((DWIDTH, DHEIGHT))
#    txt_function = Textbox(txtfont, (DWIDTH / 2 - 20, 20))
#    txt_editfunc = Textbox(txtfont, (30, 20))
#    txt_coords = Textbox(txtfont, (DWIDTH / 2 - 10, 20))
#    pygame.display.set_caption("Complex Graph")
#    output = {}
#    for i in range(DWIDTH):
#        for j in range(DHEIGHT):
#            (re, im) = transform_coords(i, j, DWIDTH, DHEIGHT, 10, 10)
#            try:
#                y = do_func(func, complex(re, im))
#            except ValueError:
#                y = complex(0, 0)
#            except ZeroDivisionError:
#                y = complex(0, 0)
#            output[complex(re, im)] = complex(y)
#            b = int(y.real / math.sqrt(y.real ** 2 + 1) * 256)
#            g = int(y.imag / math.sqrt(y.imag ** 2 + 1) * 256)
#            if abs(b) >= 256:
#                b = sign(b) * 255
#            if abs(g) >= 256:
#                g = sign(g) * 255
#            display.set_at((i, j), (0, abs(g), abs(b)))
#    pygame.image.save(display, "_complexfuncs.py_display.bmp")
#    txt_function.write("f(x) = " + func)
#    txtfont.set_bold(True)
#    txt_editfunc.write("Edit")
#    txtfont.set_bold(False)
#    while True:
#        screen.fill((255, 255, 255))
#        txt_function.fill((255, 255, 255))
#        txt_editfunc.fill((255, 255, 255))
#        txt_coords.fill((255, 255, 255))
#        screen.blit(display, (0, 0))
#        txt_function.update()
#        txt_editfunc.update()
#        txt_coords.update()
#        screen.blit(txt_function, (2, DHEIGHT + 4))
#        screen.blit(txt_editfunc, (DWIDTH / 2 - 50, DHEIGHT + 4))
#        screen.blit(txt_coords, (DWIDTH / 2 + 10, DHEIGHT + 4))
#        for event in pygame.event.get():
#            if event.type == pygame.QUIT:
#                pygame.display.quit()
#                sys.exit()
#            elif event.type == pygame.MOUSEMOTION:
#                (i, j) = event.pos
#                if i < DWIDTH and j < DHEIGHT:
#                    (re, im) = transform_coords(i, j, DWIDTH, DHEIGHT, 10, 10)
#                    op = output[complex(re, im)]
#                    txt_coords.write("f(" + cmplx_to_str(re, im) + ") = " + cmplx_to_str(op))
#            elif event.type == pygame.MOUSEBUTTONDOWN:
#                print(event.pos)
#                if is_within(event.pos, txt_editfunc, (DWIDTH / 2 - 50, DHEIGHT + 4)):
#                    func = input("What do you want it to be? ")
#        pygame.display.flip()
