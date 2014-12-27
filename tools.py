
# -*- coding: utf-8 -*-

import array
import fcntl
import termios


def flatten(list_of_lists):
	return [item for sub_list in list_of_lists for item in sub_list]


def get_tty_size():
	size = array.array("B", [0, 0, 0, 0])
	fcntl.ioctl(0, termios.TIOCGWINSZ, size, True)
	return (size[0], size[2])
