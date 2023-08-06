import random
from django_sample_data.storage import load_data

_cache = {}

def get_firstnames( language, gender ):
    fn = load_data(language, "firstnames_%s.txt" % gender)
    return  fn

def get_lastnames( language):
    fn = load_data(language, "lastnames.txt")
    return  fn

def first_name(languages=None, genders=None):
    """
        return a random first name
    :return:

    >>> from mock import patch
    >>> with patch('%s.load_data' % __name__, lambda *args: ['aaa']):
    ...     first_name()
    'Aaa'
    >>> with patch('%s.load_data' % __name__, lambda lang,gender: ['%s_%s'% (lang, gender)]) as load_data:
    ...     first_name('it', 'm')
    ...     load_data.assert_called_with(None, None, None)
    """
    choices = []
    languages = languages or ['en']
    genders = genders or ['m', 'f']
    for lang in languages:
        for gender in genders:
            samples = get_firstnames(lang, gender)
            choices.extend(samples)
    return random.choice(choices).title()


def last_name(languages=None):
    """
        return a random first name
    :return:

    >>> from mock import patch
    >>> with patch('%s.load_data' % __name__, lambda *args: ['aaa']):
    ...     first_name()
    'Aaa'
    >>> with patch('%s.load_data' % __name__, lambda lang,gender: ['%s_%s'% (lang, gender)]) as load_data:
    ...     first_name('it', 'm')
    ...     load_data.assert_called_with(None, None, None)
    """
    choices = []
    languages = languages or ['en']
    for lang in languages:
        samples = get_lastnames(lang)
        choices.extend(samples)
    return random.choice(choices).title()
