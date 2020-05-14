import curses
import curses.ascii
import functools


class Event:
    UP   = -1
    DOWN =  1


class State:
    def __init__(self, height, width, top, bottom, current):
        self.height  = height
        self.width   = width
        self.top     = top
        self.bottom  = bottom
        self.current = current


def _draw_header(window, num_uris):
    header = 'UriShow: {} matches (Press q or ctrl-c to Quit)'.format(num_uris)
    window.addstr(0, 0, header, curses.A_REVERSE)


def _draw_content(window, state, uris):
    for index, uri in enumerate(uris[state.top:state.bottom]):
        window.addstr(index + 2, 0, '{:>7} {}'.format(index + state.top + 1, uri))
    window.addstr(state.current - state.top + 2, 0, '-> ', curses.A_REVERSE)


def _draw(window, state, uris):
    # window.clear()
    _draw_header(window, len(uris))
    _draw_content(window, state, uris)
    window.refresh()


def _handler(window, state, uris, event):
    if state.current + event >= 0 and state.current + event < len(uris):
        state.current += event

    if   event == Event.UP:
        if state.current < state.top:
            window.clear()
            state.top    -= 1
            state.bottom -= 1
    elif event == Event.DOWN:
        if state.current > state.bottom - 1:
            window.clear()
            state.top    += 1
            state.bottom += 1


def _receiver(window, state, uris):
    while True:
        _draw(window, state, uris)

        c = window.getch()
        if   c == ord('k'):
            _handler(window, state, uris, Event.UP)
        elif c == ord('j'):
            _handler(window, state, uris, Event.DOWN)
        elif c == ord('q'):
            return None
        elif c == 10 or c == 13:  # enter
            return uris[state.current]


def _init(uris, window):
    try:
        curses.use_default_colors()
        curses.curs_set(0)
        window.notimeout(False)

        height, width = window.getmaxyx()
        state = State(width, height, 0, height - 3, 0)
        return _receiver(window, state, uris)
    finally:
        curses.curs_set(2)


def show(uris):
    """
    Show all the given urls and return the ones selected by the user.
    """
    return curses.wrapper(functools.partial(_init, uris))

print(show(['https://www.{}.example.com'.format(num + 1) for num in range(100)]))
