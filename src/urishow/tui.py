import functools
import os
import curses
import curses.ascii


class _State:
    def __init__(self, height, width, top, bottom, current):
        self.height  = height   # Total height of the window.
        self.width   = width    # Total width  of the window.
        self.top     = top      # Lowest  index from uris shown.
        self.bottom  = bottom   # Highest index from uris shown.
        self.current = current  # Currently selected index from uris.


def _draw_header(window, width, num_uris):
    header  = 'UriShow: {} matches'.format(num_uris)
    header += ' ' * (width - len(header))
    window.addstr(0, 0, header, curses.A_REVERSE)


def _draw_content(window, state, uris):
    for index, uri in enumerate(uris[state.top:state.bottom]):
        line = '{:>7} {}'.format(index + state.top + 1, uri)
        if len(line) > state.width:
            offset = 12
            split = int(state.width / 2) + offset
            line = line[:split] + '...' + line[len(line) - split + offset * 2 + 3:]
        window.addstr(index + 2, 0, line)
    window.addstr(state.current - state.top + 2, 0, '-> ', curses.A_REVERSE)


def _draw(window, state, uris):
    _draw_header(window, state.width, len(uris))
    _draw_content(window, state, uris)
    window.refresh()


def _handle_move(window, state, uris, dy):
    if state.current + dy >= 0 and state.current + dy < len(uris):
        state.current += dy

    if   dy == -1:  # scroll up
        if state.current < state.top:
            window.clear()
            state.top    -= 1
            state.bottom -= 1
    elif dy ==  1:  # scroll down
        if state.current > state.bottom - 1:
            window.clear()
            state.top    += 1
            state.bottom += 1


def _handle_resize(window, state, uris):
    window.clear()
    height, width = window.getmaxyx()

    # If the bottom element is not shown yet show more on the bottom, otherwise
    # show more elements at the top.
    if state.bottom < len(uris) - 1:
        state.bottom += height - state.height
    else:
        state.top    -= height - state.height

    state.height  = height
    state.width   = width


def _receiver(window, state, uris):
    while True:
        _draw(window, state, uris)

        c = window.getch()
        if   c == curses.KEY_RESIZE:
            _handle_resize(window, state, uris)
        elif c == ord('k') or c == curses.KEY_UP:
            _handle_move(window, state, uris, -1)
        elif c == ord('j') or c == curses.KEY_DOWN:
            _handle_move(window, state, uris,  1)
        elif c == ord('q') or c == 27:  # esc
            return None
        elif c == 10 or c == 13:  # enter
            return uris[state.current]


def _init(uris, window):
    """
    Initialize settings for curses, init the state and listen for key presses.
    """
    try:
        curses.use_default_colors()
        curses.curs_set(0)

        height, width = window.getmaxyx()
        state = _State(height, width, 0, height - 3, 0)
        return _receiver(window, state, uris)
    finally:
        curses.curs_set(2)


def show(uris):
    """
    Show all the given urls and return the ones selected by the user.
    """
    os.environ.setdefault('ESCDELAY', '25')  # no delay when pressing esc
    return curses.wrapper(functools.partial(_init, uris))

print(show(['https://www.{:03d}.example.com '.format(num + 1) + '0123456789' * 10 for num in range(100)]))
