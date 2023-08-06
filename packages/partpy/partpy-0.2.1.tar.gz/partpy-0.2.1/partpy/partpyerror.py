"""Custom exception for classes inheriting SourceString or Matcher."""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'


class PartpyError(Exception):
    """Takes a SourceString or Matcher derived object and an optional message.

    When converted to a string will display the previous and current line
    with line numbers and a '^' under the current position of the object with
    the optional message on the following line.
    """
    def __init__(self, obj, msg = None):
        super(PartpyError, self).__init__(obj, msg)
        self.partpymsg = msg
        self.partpyobj = obj

    def __repr__(self):
        output = [str(line) for line in \
            self.partpyobj.get_surrounding_lines(1, 0)]

        padding = 1
        if self.partpyobj.row < 1000:
            padding = 2
        if self.partpyobj.row < 100:
            padding = 3
        if self.partpyobj.row < 10:
            padding = 4

        output.append(' ' * (self.partpyobj.col + padding + 1) + '^' + '\n')
        if self.partpymsg:
            output.append(self.partpymsg)

        return ''.join(output)

    def __str__(self):
        return self.__repr__()
