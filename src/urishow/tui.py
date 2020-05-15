import functools
import os
import curses
import curses.ascii


class _State:
    """
    A class to represent the current state of the window and pointer.
    """

    OFFSET_TOP    = 2
    OFFSET_BOTTOM = 1
    OFFSET_TOTAL  = OFFSET_TOP + OFFSET_BOTTOM

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
    """
    Draw as much uris as there is space for plus the pointer.
    """
    for index, uri in enumerate(uris[state.top:state.bottom + 1]):
        line = '{:>7} {}'.format(index + state.top + 1, uri)
        if len(line) > state.width - 2:  # apply wrapping if the line is too long
            offset = 10  # an offset for the '...'
            split = int(state.width / 2) + offset
            line = line[:split] + '...' + line[len(line) - split + offset * 2 + 5:]
            window.addstr(index + _State.OFFSET_TOP, state.width - 1, '>')
        window.addstr(index + _State.OFFSET_TOP, 0, line)
    window.addstr(state.current - state.top + _State.OFFSET_TOP, 0, '-> ', curses.A_REVERSE)


def _draw(window, state, uris):
    _draw_header(window, state.width, len(uris))
    _draw_content(window, state, uris)
    window.refresh()


def _valid_uri(uri, uris):
    """
    Make sure that the given uri is within the range of possible values.
    """
    if uri >= len(uris):
        return len(uris) - 1
    if uri < 0:
        return 0
    return uri


def _handle_resize(window, state, uris):
    """
    When growing, if the bottom element is not shown yet show more on the
    bottom, otherwise show more elements at the top. When shrinking chop of
    from the bottom if that is necessary.
    """
    window.clear()

    height, width = window.getmaxyx()
    diff          = height - state.height
    state.height  = height
    state.width   = width

    if diff > 0:  # growing
        if state.bottom < len(uris) - 1:
            state.bottom = _valid_uri(state.bottom + diff, uris)
        elif state.top > 0:
            state.top = _valid_uri(state.top - diff, uris)
    elif diff < 0:  # shrinking
        if height - _State.OFFSET_TOTAL <= state.bottom - state.top:
            new = state.bottom + diff
            state.bottom = new if new >= state.top else state.top


def _handle_jump(window, state, uris, pos):
    """
    Jump to the given position.
    """
    if pos < 0 or pos >= len(uris):
        return

    if   state.current > pos:  # jump up
        if pos < state.top:
            window.clear()
            lines = state.bottom - state.top
            state.top    = pos
            state.bottom = pos + lines
        state.current = pos
    elif state.current < pos:  # jump down
        if pos > state.bottom:
            window.clear()
            lines = state.bottom - state.top
            state.bottom = pos
            state.top    = pos - lines
        state.current = pos


def _receiver(window, state, uris):
    while True:
        _draw(window, state, uris)

        c = window.getch()
        if   c == ord('k') or c == curses.KEY_UP:
            _handle_jump(window, state, uris, state.current - 1)
        elif c == ord('j') or c == curses.KEY_DOWN:
            _handle_jump(window, state, uris, state.current + 1)
        elif c == ord('u'):
            lines = int((state.bottom - state.top) / 2)
            _handle_jump(window, state, uris, _valid_uri(state.current - lines, uris))
        elif c == ord('d'):
            lines = int((state.bottom - state.top) / 2)
            _handle_jump(window, state, uris, _valid_uri(state.current + lines, uris))
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
        maxlines = height - _State.OFFSET_TOTAL
        bottom   = maxlines - 1 if maxlines < len(uris) else len(uris) - 1
        state    = _State(height, width, 0, bottom, 0)

        # Start receiving key presses and get the selected uri.
        return _receiver(window, state, uris)
    finally:
        curses.curs_set(2)


def show(uris):
    """
    Show all the given urls and return the ones selected by the user.
    """
    os.environ.setdefault('ESCDELAY', '25')  # no delay when pressing esc
    return curses.wrapper(functools.partial(_init, uris))

print(show(['https://www.{:03d}.example.com '.format(num + 1) for num in range(100)]))
