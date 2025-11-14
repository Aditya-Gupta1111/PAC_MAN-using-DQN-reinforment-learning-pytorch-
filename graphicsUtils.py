import sys
import math
import time
import tkinter

# Determine if running on Windows
_WINDOWS = sys.platform == 'win32'

# Global graphics state
_root_window = None
_canvas = None
_canvas_xs = None
_canvas_ys = None
_bg_color = None

# Key handling state
_keysdown = {}
_keyswaiting = {}
_got_release = None

_leftclick_loc = None
_rightclick_loc = None
_ctrl_leftclick_loc = None


# ------------------------------------------------------------
#  COLOR / UTILITY FUNCTIONS
# ------------------------------------------------------------

def formatColor(r, g, b):
    """Convert float RGB values (0–1) to Tkinter color string."""
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def colorToVector(color):
    """Convert #RRGGBB string into a normalized (r,g,b) vector."""
    return [int(color[1:3], 16)/256.0,
            int(color[3:5], 16)/256.0,
            int(color[5:7], 16)/256.0]


def sleep(secs):
    """Sleep while letting Tkinter update UI."""
    global _root_window
    if _root_window is None:
        time.sleep(secs)
    else:
        _root_window.update_idletasks()
        _root_window.after(int(1000 * secs), _root_window.quit)
        _root_window.mainloop()


# ------------------------------------------------------------
#  WINDOW CREATION
# ------------------------------------------------------------

def begin_graphics(width=640, height=480, color=formatColor(0, 0, 0), title=None):
    """Create the main Tkinter window and drawing canvas."""

    global _root_window, _canvas, _canvas_xs, _canvas_ys, _bg_color

    if _root_window is not None:
        _root_window.destroy()

    _canvas_xs = width - 1
    _canvas_ys = height - 1
    _bg_color = color

    _root_window = tkinter.Tk()
    _root_window.protocol('WM_DELETE_WINDOW', _destroy_window)
    _root_window.title(title or 'Graphics Window')
    _root_window.resizable(0, 0)

    _canvas = tkinter.Canvas(_root_window, width=width, height=height)
    _canvas.pack()
    draw_background()
    _canvas.update()

    # Bind events
    _root_window.bind("<KeyPress>", _keypress)
    _root_window.bind("<KeyRelease>", _keyrelease)
    _root_window.bind("<FocusIn>", _clear_keys)
    _root_window.bind("<FocusOut>", _clear_keys)
    _root_window.bind("<Button-1>", _leftclick)
    _root_window.bind("<Button-2>", _rightclick)
    _root_window.bind("<Button-3>", _rightclick)
    _root_window.bind("<Control-Button-1>", _ctrl_leftclick)
    _clear_keys()


def draw_background():
    """Fill background with the given window color."""
    polygon([(0, 0),
             (0, _canvas_ys),
             (_canvas_xs, _canvas_ys),
             (_canvas_xs, 0)],
            _bg_color, fillColor=_bg_color, filled=True, smoothed=False)


def _destroy_window(event=None):
    sys.exit(0)


def end_graphics():
    """Close window cleanly."""
    global _root_window, _canvas
    try:
        sleep(1)
        if _root_window is not None:
            _root_window.destroy()
    finally:
        _root_window = None
        _canvas = None
        _clear_keys()


# ------------------------------------------------------------
#  DRAWING PRIMITIVES
# ------------------------------------------------------------

def polygon(coords, outlineColor, fillColor=None, filled=True, smoothed=True, behind=0, width=1):
    """Draw a polygon."""
    if fillColor is None and filled:
        fillColor = outlineColor
    if not filled:
        fillColor = ""

    flat = [coord for xy in coords for coord in xy]
    poly = _canvas.create_polygon(flat, outline=outlineColor,
                                  fill=fillColor, smooth=smoothed, width=width)
    if behind > 0:
        _canvas.tag_lower(poly, behind)
    return poly


def square(pos, r, color, filled=True, behind=0):
    x, y = pos
    coords = [(x - r, y - r), (x + r, y - r),
              (x + r, y + r), (x - r, y + r)]
    return polygon(coords, color, color if filled else "", filled, False, behind)


def circle(pos, r, outlineColor, fillColor,
           endpoints=None, style='pieslice', width=2):
    """Draw an arc or full circle."""
    x, y = pos
    x0, x1 = x - r - 1, x + r
    y0, y1 = y - r - 1, y + r

    if endpoints is None:
        start, end = 0, 359
    else:
        start, end = endpoints
        while start > end:
            end += 360

    return _canvas.create_arc(x0, y0, x1, y1,
                              outline=outlineColor,
                              fill=fillColor,
                              extent=end-start,
                              start=start,
                              style=style,
                              width=width)


def line(here, there, color=formatColor(0, 0, 0), width=2):
    return _canvas.create_line(
        here[0], here[1], there[0], there[1], fill=color, width=width
    )


def text(pos, color, contents, font='Helvetica', size=12,
         style='normal', anchor="nw"):
    x, y = pos
    font = (font, str(size), style)
    return _canvas.create_text(x, y, fill=color,
                               text=contents, font=font, anchor=anchor)


def changeText(obj_id, newText, font=None, size=12, style='normal'):
    _canvas.itemconfigure(obj_id, text=newText)
    if font:
        _canvas.itemconfigure(obj_id, font=(font, f"-{size}", style))


def changeColor(obj_id, newColor):
    _canvas.itemconfigure(obj_id, fill=newColor)


def refresh():
    _canvas.update_idletasks()


# ------------------------------------------------------------
#  MOVEMENT
# ------------------------------------------------------------

def move_to(obj, x, y=None):
    """Move object to absolute (x,y)."""
    if y is None:
        try:
            x, y = x
        except Exception:
            raise ValueError("Invalid coordinates for move_to")

    coords = _canvas.coords(obj)
    cx, cy = coords[0], coords[1]

    dx = x - cx
    dy = y - cy

    _canvas.move(obj, dx, dy)
    refresh()


def move_by(obj, delta, lift=False):
    """Move object by a delta (dx, dy)."""
    dx, dy = delta
    _canvas.move(obj, dx, dy)
    refresh()
    if lift:
        _canvas.tag_raise(obj)


def moveCircle(obj, pos, r, endpoints=None):
    """Move + update arc drawing."""
    x, y = pos
    x0, x1 = x - r - 1, x + r
    y0, y1 = y - r - 1, y + r

    if endpoints is None:
        start, end = 0, 359
    else:
        start, end = endpoints
        while start > end:
            end += 360

    edit(obj, ('start', start), ('extent', end - start))
    move_to(obj, x0, y0)


def edit(obj, *args):
    """Generic update to Tk canvas object config."""
    _canvas.itemconfigure(obj, **dict(args))


# ------------------------------------------------------------
#  KEY HANDLING
# ------------------------------------------------------------

def _keypress(event):
    global _got_release
    _keysdown[event.keysym] = 1
    _keyswaiting[event.keysym] = 1
    _got_release = None


def _keyrelease(event):
    global _got_release
    _keysdown.pop(event.keysym, None)
    _got_release = True


def _clear_keys(event=None):
    global _keysdown, _keyswaiting, _got_release
    _keysdown = {}
    _keyswaiting = {}
    _got_release = None


def keys_pressed():
    """Return currently held-down keys."""
    if _root_window:
        _root_window.dooneevent(tkinter._tkinter.DONT_WAIT)
        if _got_release:
            _root_window.dooneevent(tkinter._tkinter.DONT_WAIT)
    return list(_keysdown.keys())


def keys_waiting():
    """Return keys that were pressed since last call."""
    global _keyswaiting
    keys = list(_keyswaiting.keys())
    _keyswaiting = {}
    return keys


def wait_for_keys():
    """Block until some key is pressed."""
    keys = []
    while not keys:
        keys = keys_pressed()
        sleep(0.05)
    return keys


# ------------------------------------------------------------
#  MOUSE HANDLING
# ------------------------------------------------------------

def _leftclick(event):
    global _leftclick_loc
    _leftclick_loc = (event.x, event.y)


def _rightclick(event):
    global _rightclick_loc
    _rightclick_loc = (event.x, event.y)


def _ctrl_leftclick(event):
    global _ctrl_leftclick_loc
    _ctrl_leftclick_loc = (event.x, event.y)


def wait_for_click():
    """Wait for mouse click."""
    global _leftclick_loc, _rightclick_loc, _ctrl_leftclick_loc
    while True:
        if _leftclick_loc:
            loc = _leftclick_loc
            _leftclick_loc = None
            return loc, 'left'
        if _rightclick_loc:
            loc = _rightclick_loc
            _rightclick_loc = None
            return loc, 'right'
        if _ctrl_leftclick_loc:
            loc = _ctrl_leftclick_loc
            _ctrl_leftclick_loc = None
            return loc, 'ctrl_left'
        sleep(0.05)


# ------------------------------------------------------------
#  EXPORT
# ------------------------------------------------------------

def writePostscript(filename):
    """Save canvas to PostScript."""
    with open(filename, 'w') as f:
        f.write(_canvas.postscript(pageanchor='sw', y='0', x='0'))

# ------------------------------------------------------------
#  CANVAS OBJECT REMOVAL
# ------------------------------------------------------------

def remove_from_screen(obj_id):
    """Delete a canvas object by its ID."""
    global _canvas
    if _canvas:
        _canvas.delete(obj_id)