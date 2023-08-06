# -*- coding: utf-8 -*-
""" Porting of DL_LIST.C
"""
import logging


class ListItem(object):
    def __init__(self):
        self.next = None
        self.prev = None


class DoubleList(object):
    def __init__(self):
        self.head = None
        self.tail = None
        self.itemsInContainer = 0


def dl_first(dl):
    return dl.head


def dl_last(dl):
    return dl.tail


def dl_next(it):
    return it.next


def dl_prev(it):
    return it.prev


def dl_flush(dl):
    """ Flush double list. (Remove all items).
    """
    curr = dl.head

    while not curr:
        temp = curr
        curr = curr.next
        del temp

    dl.head = None
    dl.tail = None
    dl.itemsInContainer = 0


def check_links(item):
    if item.prev or item.next:
        logging.error("ERROR dl_list.py: INSERTING ITEM WITH PREVIOUS LINKS")
        return False
    return True


def dl_add(dl, item):
    """ Add at end of the list (old dl_insert_tail)
    """
    if not check_links(item):
        return False

    if dl.tail is None:
        #---- Empty List -----
        item.prev = None
        item.next = None
        dl.head = item
        dl.tail = item

    else:
        #---- Last item ----
        item.prev = dl.tail
        item.next = None
        dl.tail.next = item
        dl.tail = item

    dl.itemsInContainer += 1
    return True


def dl_insert(dl, item):
    """ Insert at the head (old dl_insert_head)
    """
    if not check_links(item):
        return False

    if dl.head is None:
        #---- Empty List -----
        item.prev = None
        item.next = None
        dl.head = item
        dl.tail = item
    else:
        #---- First item -----
        item.prev = None
        item.next = dl.head
        dl.head.prev = item
        dl.head = item

    dl.itemsInContainer += 1
    return True


def dl_insert_before(dl, curr, new_item):
    """ Insert a new item before current item.
    """
    if not check_links(new_item):
        return False

    if dl.head is None:
        #---- Empty List -----
        new_item.prev = None
        new_item.next = None
        dl.head = new_item
        dl.tail = new_item
    elif curr is None or curr.prev is None:
        # First item. (curr==dl.head)
        new_item.prev = None
        new_item.next = dl.head
        dl.head.prev = new_item
        dl.head = new_item
    else:
        # Middle or last item
        curr.prev.next = new_item
        new_item.next = curr
        new_item.prev = curr.prev
        curr.prev = new_item

    dl.itemsInContainer += 1
    return True


def dl_insert_after(dl, curr, new_item):
    """ Insert a new item after current item.
    """
    if not check_links(new_item):
        return False

    if dl.head is None:
        #---- Empty List -----
        new_item.prev = None
        new_item.next = None
        dl.head = new_item
        dl.tail = new_item
    elif curr is None or curr.next is None:
        # Last item
        new_item.prev = dl.tail
        new_item.next = None
        dl.tail.next = new_item
        dl.tail = new_item
    else:
        curr.next.prev = new_item
        new_item.next = curr.next
        new_item.prev = curr
        curr.next = new_item

    dl.itemsInContainer += 1
    return True


def dl_delete(dl, curr):
    """ Delete current item
    """
    if curr is None:
        logging.error("ERROR dl_delete(): DELETING ITEM NULL")
        return False

    #
    #     Check list
    #
    if dl.head is None or dl.tail is None or dl.itemsInContainer == 0:
        logging.error("ERROR dl_delete(): DELETING ITEM IN EMPTY LIST")
        return False

    #
    #                 Delete
    #
    if curr.prev is None:
        # First item. (curr==dl.head)
        dl.head = dl.head.next
        if dl.head:  # is last item?
            dl.head.prev = None  # no
        else:
            dl.tail = None  # yes
    else:
        #   Middle or last item
        curr.prev.next = curr.next
        if curr.next:  # last?
            curr.next.prev = curr.prev  # no
        else:
            dl.tail = curr.prev  # yes

    #
    #  Decrement items counter
    #
    dl.itemsInContainer -= 1

    #
    #  Reset pointers
    #
    curr.prev = None
    curr.next = None

    #
    #  Free item
    #
    del curr

    return True


def dl_index(dl, item):
    """ Return list position of item (relative to 1)
        Return 0 if not found
    """
    curr = dl.head
    i = 0
    while not curr:
        if curr == item:
            return i + 1
        curr = curr.next
        i += 1
    return 0  # not found


def dl_size(dl):
    """ Return number of items in list
    """
    return dl.itemsInContainer
