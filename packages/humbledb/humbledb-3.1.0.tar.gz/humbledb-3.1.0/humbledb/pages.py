import random
import datetime

from nose.tools import ok_, eq_

from humbledb import Mongo, Document, Embed


class Paginated(Document):
    pages = 'p'

    def new_page(self):
        """ Create a new page. """
        # Get the current number of pages
        pages = self.pages or 0
        pages += 1
        # Create a new page object for inserting
        page = self.Page()
        page.page = pages
        page.size = 0
        page._id = '{}{}{}'.format(self._id, page._separator, pages)
        # Pad the document if we have a padding value
        if self._padding:
            page['padding'] = '0' * self._padding
        # Create the new document

    def append(self, entry):
        pass


class BasePage(Document):
    _separator = '#'
    _padding = 0

    parent_id = 'i'
    page = 'p'
    size = 's'
    entries = 'e'


class Group(Paginated):
    config_database = 'test'
    config_collection = 'groups'

    owner = 'o'
    name = 'n'
    created = 'c'

    class Page(BasePage):
        config_database = 'test'
        config_collection = 'group_members'

        users = Embed(BasePage.entries)
        users.name = 'n'
        users.added = 'a'



# Tests
#######

# Cache the list of dictionary words
WORDS = []


def setup():
    # Load the list of dictionary words
    with open('/tmp/brit-a-z.txt') as words:
        WORDS.extend(w.strip() for w in words.readlines())

    # Create a group for working with
    group = Group()
    group._id = 'nose/test'
    group.owner = 'nose'
    group.name = 'test'
    group.created = datetime.datetime.now()
    with Mongo:
        group_id = Group.save(group)


def teardown():
    with Mongo:
        Group.remove()
        Group.Page.remove()


def _word():
    """ Return a random dictionary word. """
    return random.choice(WORDS)


def test_insert_twice_fails():
    g = Group()
    g._id = 'test'
    with Mongo:
        ok_(Group.insert(g))
        ok_(Group.insert(g))

