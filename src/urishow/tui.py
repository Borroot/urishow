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
    for index, uri in enumerate(uris[state.top:state.bottom + 1]):
        line = '{:>7} {}'.format(index + state.top + 1, uri)
        if len(line) > state.width - 2:  # apply wrapping if the line is too long
            offset = 12  # an offset for the '...'
            split = int(state.width / 2) + offset
            line = line[:split] + '...' + line[len(line) - split + offset * 2 + 5:]
            window.addstr(index + 2, state.width - 1, '>')
        window.addstr(index + 2, 0, line)
    window.addstr(state.current - state.top + 2, 0, '-> ', curses.A_REVERSE)
    window.addstr(0, 0, '{} {} {} {} {}'.format(state.current, state.bottom, state.top, state.height, state.width))


def _draw(window, state, uris):
    _draw_header(window, state.width, len(uris))
    _draw_content(window, state, uris)
    window.refresh()


def _handle_move(window, state, uris, dy):
    """
    Move the pointer one line up or down if possible.
    """
    if state.current + dy >= 0 and state.current + dy < len(uris):
        state.current += dy

    if   dy == -1:  # scroll up
        if state.current < state.top:
            window.clear()
            state.top    -= 1
            state.bottom -= 1
    elif dy ==  1:  # scroll down
        if state.current > state.bottom:
            window.clear()
            state.top    += 1
            state.bottom += 1


def _handle_jump(window, state, uris, pos):
    """
    Jump to the given position.
    """
    if pos < 0 or pos >= len(uris):
        raise ValueError("Invalid value for 'pos'.")

    if   state.current > pos:  # jump up
        if pos < state.top:
            window.clear()
            diff = state.bottom - state.top
            state.top    = pos
            state.bottom = pos + diff
        state.current = pos
    elif state.current < pos:  # jump down
        if pos > state.bottom:
            window.clear()
            diff = state.bottom - state.top
            state.bottom = pos
            state.top    = pos - diff
        state.current = pos


def _handle_resize(window, state, uris):
    """
    When growing, if the bottom element is not shown yet show more on the
    bottom, otherwise show more elements at the top. When shrinking chop of
    from the bottom if that is necessary.
    """
    window.clear()
    height, width = window.getmaxyx()

    diff = height - state.height
    if diff > 0:  # growing
        if state.bottom < len(uris) - 1:
            new = state.bottom + diff
            state.bottom = new if new < len(uris) else len(uris) - 1
        elif state.top > 0:
            new = state.top - diff
            state.top = new if new >= 0 else 0
    elif diff < 0:  # shrinking
        if height - 4 < state.bottom - state.top:
            new = state.bottom + diff
            state.bottom = new if new >= state.top else state.top

    state.height  = height
    state.width   = width


def _receiver(window, state, uris):
    while True:
        _draw(window, state, uris)

        c = window.getch()
        if   c == ord('k') or c == curses.KEY_UP:
            _handle_move(window, state, uris, -1)
        elif c == ord('j') or c == curses.KEY_DOWN:
            _handle_move(window, state, uris,  1)
        elif c == ord('g'):
            _handle_jump(window, state, uris, 0)
        elif c == ord('G'):
            _handle_jump(window, state, uris, len(uris) - 1)
        elif c == ord('q') or c == 27:  # esc
            return None
        elif c == 10 or c == 13:  # enter
            return uris[state.current]
        elif c == curses.KEY_RESIZE:
            _handle_resize(window, state, uris)


def _init(uris, window):
    """
    Initialize settings for curses, init the state and listen for key presses.
    """
    try:
        curses.use_default_colors()
        curses.curs_set(0)

        # Calculate the intial values for the starting state.
        height, width = window.getmaxyx()
        bottom = height - 4 if height - 3 < len(uris) else len(uris) - 1
        state = _State(height, width, 0, bottom, 0)

        return _receiver(window, state, uris)
    finally:
        curses.curs_set(2)


def show(uris):
    """
    Show all the given urls and return the ones selected by the user.
    """
    os.environ.setdefault('ESCDELAY', '25')  # no delay when pressing esc
    return curses.wrapper(functools.partial(_init, uris))

print(show(['https://www.{:03d}.example.com '.format(num + 1) + '0123456789' * 10 for num in range(20)]))
