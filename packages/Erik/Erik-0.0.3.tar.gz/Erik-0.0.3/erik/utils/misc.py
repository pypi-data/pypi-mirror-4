from signal import signal

def confirm(prompt=None, default=False, timeout=0):
    """prompts for yes or no from the user. Returns True for yes and
    False for no.

    'default' should be set to the default value assumed by the caller when
    user simply types ENTER.

    :param timeout: (int) If set, prompt will return default.

    >>> confirm(prompt='Create Directory?', default=True)
    Create Directory? [y]|n:
    True
    >>> confirm(prompt='Create Directory?', default=False)
    Create Directory? [n]|y:
    False
    >>> confirm(prompt='Create Directory?', default=False)
    Create Directory? [n]|y: y
    True
    """
    class TimeOutException(Exception): pass
    def timed_out(signum, frame):
        "called when stdin read times out"
        raise TimeOutException('Timed out')
    signal.signal(signal.SIGALRM, timed_out)

    if prompt is None:
        prompt = 'Confirm'

    if default:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

    while True:
        signal.alarm(timeout)
        try:
            ans = raw_input(prompt)
            signal.alarm(0)
            if not ans:
                return default
            if ans not in ['y', 'Y', 'yes', 'n', 'no', 'N']:
                print 'please enter y or n.'
                continue
            if ans in ['y','yes','Yes']:
                return True
            if ans in ['n','no','N']:
                return False
        except TimeOutException:
            print "Confirmation timed out after {0}s, returning default of '{1}'".format(timeout,'yes' if default else 'no')
            return default
