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


def _valid_uri(uri, uris):
    """
    Make sure that the given uri is within the range of possible values.
    """
    uri = len(uris) - 1 if uri >= len(uris) else uri
    uri = 0 if uri < 0 else uri
    return uri


def _draw_header(window, width, text):
    header  = 'UriShow: ' + text
    header += ' ' * (width - len(header))
    window.addstr(0, 0, header[:width], curses.A_REVERSE)


def _draw_content(window, state, uris):
    """
    Draw as much uris as there is space for plus the pointer.
    """
    for index, uri in enumerate(uris[state.top:state.bottom + 1]):
        line_head = '{:>7} '.format(index + state.top + 1)
        if len(line_head + uri) > state.width - 2:  # apply wrapping
            split = int((state.width - len(line_head)) / 2)
            uri = uri[:split] + '...' + uri[len(uri) - split + 5:]
            window.addstr(index + _State.OFFSET_TOP, state.width - 1, '>')
        window.addstr(index + _State.OFFSET_TOP, 0, line_head)
        effect = curses.A_UNDERLINE if index + state.top == state.current else curses.A_NORMAL
        window.addstr(index + _State.OFFSET_TOP, len(line_head), uri[:state.width - len(line_head)], effect)
    window.addstr(state.current - state.top + _State.OFFSET_TOP, 0, '-> ', curses.A_REVERSE)


def _draw(window, state, uris):
    if state.width > 8 and state.height > 3:
        _draw_header(window, state.width, '{} matches'.format(len(uris)))
        _draw_content(window, state, uris)
        window.refresh()


def _draw_help(window, state):
    """
    Show the help menu with all the keybindings.
    """
    window.clear()
    text = \
    """
    KEYBINDINGS
    k - up
    j - down
    u - up   half page
    d - down half page
    K - up   full page
    J - down full page
    g - first
    G - last
    H - top
    M - middle
    L - bottom
    h - help
    q - exit
    enter - select"""
    lines = text.count('\n')
    longest = 0
    for line in text.split('\n'):
        longest = len(line) if len(line) > longest else longest

    if lines + _State.OFFSET_TOTAL <= state.height and state.width > longest:
        _draw_header(window, state.width, 'help')
        window.addstr(0 + _State.OFFSET_TOP - 1, 0, text)
        window.refresh()
    elif state.width > 8 and state.height > 1:
        _draw_header(window, state.width, 'please resize')


def _handle_help(window, state, uris):
    """
    Show the help menu until a key is pressed.
    """
    _draw_help(window, state)
    c = window.getch()
    window.clear()
    if c == curses.KEY_RESIZE:
        _handle_resize(window, state, uris)
        return _handle_help(window, state, uris)


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
        if state.bottom < len(uris) - 1 and state.bottom + diff < height - _State.OFFSET_TOTAL:
            state.bottom = _valid_uri(state.bottom + diff, uris)
        elif state.top > 0:
            state.top = _valid_uri(state.top - diff, uris)
    elif diff < 0:  # shrinking
        if height - _State.OFFSET_TOTAL <= state.bottom - state.top:
            new = state.bottom + diff
            state.bottom = new if new >= state.top else state.top
            state.current = state.bottom if state.current > state.bottom else state.current


def _handle_jump(window, state, uris, pos):
    """
    Jump to the given position.
    """
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
            _handle_jump(window, state, uris, _valid_uri(state.current - 1, uris))
        elif c == ord('j') or c == curses.KEY_DOWN:
            _handle_jump(window, state, uris, _valid_uri(state.current + 1, uris))
        elif c == ord('u'):
            lines = int((state.bottom - state.top) / 2)
            _handle_jump(window, state, uris, _valid_uri(state.current - lines, uris))
        elif c == ord('d'):
            lines = int((state.bottom - state.top) / 2)
            _handle_jump(window, state, uris, _valid_uri(state.current + lines, uris))
        elif c == ord('K'):
            lines = state.bottom - state.top
            _handle_jump(window, state, uris, _valid_uri(state.current - lines, uris))
        elif c == ord('J'):
            lines = state.bottom - state.top
            _handle_jump(window, state, uris, _valid_uri(state.current + lines, uris))
        elif c == ord('g') or c == curses.KEY_HOME:
            _handle_jump(window, state, uris, 0)
        elif c == ord('G') or c == curses.KEY_END:
            _handle_jump(window, state, uris, len(uris) - 1)
        elif c == ord('H'):
            _handle_jump(window, state, uris, _valid_uri(state.top, uris))
        elif c == ord('M'):
            lines = int((state.bottom - state.top) / 2)
            _handle_jump(window, state, uris, _valid_uri(state.top + lines, uris))
        elif c == ord('L'):
            _handle_jump(window, state, uris, _valid_uri(state.bottom, uris))
        elif c == ord('h'):
            c = _handle_help(window, state, uris)
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
        bottom = _valid_uri(height - _State.OFFSET_TOTAL - 1, uris)
        state  = _State(height, width, 0, bottom, 0)

        return _receiver(window, state, uris)
    finally:
        curses.curs_set(2)


def show(uris):
    """
    Show all the given urls and return the ones selected by the user.
    """
    os.environ.setdefault('ESCDELAY', '25')  # no delay when pressing esc
    return curses.wrapper(functools.partial(_init, uris))

print(show(['https://www.{:03d}.example.com/'.format(num + 1) + '0123456789' * 8 for num in range(100)]))
