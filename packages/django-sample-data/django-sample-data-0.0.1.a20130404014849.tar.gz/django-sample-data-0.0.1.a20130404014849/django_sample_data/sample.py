# -*- coding: utf-8 -*-
import decimal
import os
import pickle
import string
from functools import wraps
from random import choice, randrange, randint


_counters = {}
def infinite():
    i = 0
    while 1:
        yield i
        i = i + 1

def sequence(prefix):
    if prefix not in _counters:
        _counters[prefix] = infinite()
    yield "{0}-{1}".format(prefix, next(_counters[prefix]))

def nextname(prefix):
    if prefix not in _counters:
        _counters[prefix] = infinite()
    return "{0}-{1}".format(prefix, next(_counters[prefix]))


def text(length, choices=string.ascii_uppercase):
    return ''.join(choice(choices) for x in range(length))


def rtext(maxlength, minlength=1, choices=string.ascii_uppercase):
    return ''.join(choice(choices) for x in range(randint(minlength, maxlength)))


def name():
    return rtext(30, 10).capitalize()


def fullname():
    return "%s %s" % (name(), name())


def num(length):
    return text(length, choices=string.digits)


def hexnum(length):
    return text(length, choices=string.hexdigits)


def country():
    codes = [(name, i2, i3, inum) for name, i2, i3, inum, _ in get_cache()]
    return choice(codes)


def amount(start=1, stop=None):
    s = start * 1000
    return decimal.Decimal(randrange(s, stop)) / 100


def iso2():
    codes = [c for _, c, _, _, _ in get_cache()]
    return choice(codes)


def iso3():
    codes = [c for _, _, c, _, _ in get_cache()]
    return choice(codes)


def isonum():
    codes = [c for _, _, _, c, _ in get_cache()]
    return choice(codes)


def lang():
    # http://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt
    codes = 'aar abk ace ach ada ady afa afh afr ain aka akk alb ale alg alt amh ang anp ' \
            'apa ara arc arg arm arn arp art arw asm ast ath aus ava ave awa aym aze bad ' \
            'bai bak bal bam ban baq bas bat bej bel bem ben ber bho bih bik bin bis bla ' \
            'bnt bos bra bre btk bua bug bul bur byn cad cai car cat cau ceb cel cha chb ' \
            'che chg chi chk chm chn cho chp chr chu chv chy cmc cop cor cos cpe cpf cpp ' \
            'cre crh crp csb cus cze dak dan dar day del den dgr din div doi dra dsb dua ' \
            'dum dut dyu dzo efi egy eka elx eng enm epo est ewe ewo fan fao fat fij fil ' \
            'fin fiu fon fre frm fro frr frs fry ful fur gaa gay gba gem geo ger gez gil ' \
            'gla gle glg glv gmh goh gon gor got grb grc gre grn gsw guj gwi hai hat hau ' \
            'haw heb her hil him hin hit hmn hmo hrv hsb hun hup iba ibo ice ido iii ijo ' \
            'iku ile ilo ina inc ind ine inh ipk ira iro ita jav jbo jpn jpr jrb kaa kab ' \
            'kac kal kam kan kar kas kau kaw kaz kbd kha khi khm kho kik kin kir kmb kok ' \
            'kom kon kor kos kpe krc krl kro kru kua kum kur kut lad lah lam lao lat lav ' \
            'lez lim lin lit lol loz ltz lua lub lug lui lun luo lus mac mad mag mah mai ' \
            'mak mal man mao map mar mas may mdf mdr men mga mic min mis mkh mlg mlt mnc ' \
            'mni mno moh mon mos mul mun mus mwl mwr myn myv nah nai nap nau nav nbl nde ' \
            'ndo nds nep new nia nic niu nno nob nog non nor nqo nso nub nwc nya nym nyn ' \
            'nyo nzi oci oji ori orm osa oss ota oto paa pag pal pam pan pap pau peo per ' \
            'phi phn pli pol pon por pra pro pus qaa-qtz que raj rap rar roa roh rom rum ' \
            'run rup rus sad sag sah sai sal sam san sas sat scn sco sel sem sga sgn shn ' \
            'sid sin sio sit sla slo slv sma sme smi smj smn smo sms sna snd snk sog som ' \
            'son sot spa srd srn srp srr ssa ssw suk sun sus sux swa swe syc syr tah tai ' \
            'tam tat tel tem ter tet tgk tgl tha tib tig tir tiv tkl tlh tli tmh tog ton ' \
            'tpi tsi tsn tso tuk tum tup tur tut tvl twi tyv udm uga uig ukr umb und urd ' \
            'uzb vai ven vie vol vot wak wal war was wel wen wln wol xal xho yao yap yid ' \
            'yor ypk zap zbl zen zgh zha znd zul zun zxx zza'
    return choice(codes)


def ipaddress(not_valid_class_A=None):
    not_valid = not_valid_class_A or [10, 127, 169, 172, 192]

    first = randrange(1, 256)
    while first in not_valid:
        first = randrange(1, 256)
    return ".".join([str(first), str(randrange(1, 256)),
                     str(randrange(1, 256)), str(randrange(1, 256))])


def indexno():
    return num(10)


def office_code():
    return '%s%s' % (iso2(), choice(['RB', 'CO']))


def email(*tlds):
    domains = tlds or ['wfp.org']
    return ("%s.%s@%s" % (text(10), text(10), choice(domains))).lower()


def currency():
    # refresh:
    # from pyquery import PyQuery as pq
    # p=pq(url='http://www.science.co.il/International/Currency-Codes.asp')
    # p('table.sortable')('tr')('td:eq(3)').text()
    return text(3)
    codes = ['AFN', 'ALL', 'DZD', 'USD', 'EUR', 'AOA', 'XCD', 'XCD', 'XCD', 'ARS', 'AMD', 'AWG', 'AUD', 'EUR', 'AZN',
             'BSD',
             'BHD', 'BDT', 'BBD', 'BYR', 'EUR', 'BZD', 'XOF', 'BMD', 'BTN', 'BOB', 'BAM', 'BWP', 'NOK', 'BRL', 'USD',
             'BND',
             'BGN', 'XOF', 'BIF', 'KHR', 'XAF', 'CAD', 'CVE', 'KYD', 'XAF', 'XAF', 'CLP', 'CNY', 'AUD', 'AUD', 'COP',
             'KMF',
             'XAF', 'CDF', 'NZD', 'CRC', 'HRK', 'CUP', 'EUR', 'CZK', 'DKK', 'DJF', 'XCD', 'DOP', 'ECS', 'EGP', 'SVC',
             'XAF',
             'ERN', 'EUR', 'ETB', 'EUR', 'FKP', 'DKK', 'FJD', 'EUR', 'EUR', 'EUR', 'EUR', 'XAF', 'GMD', 'GEL', 'EUR',
             'GHS',
             'GIP', 'GBP', 'EUR', 'DKK', 'XCD', 'EUR', 'USD', 'QTQ', 'GGP', 'GNF', 'GWP', 'GYD', 'HTG', 'AUD', 'HNL',
             'HKD',
             'HUF', 'ISK', 'INR', 'IDR', 'IRR', 'IQD', 'EUR', 'GBP', 'ILS', 'EUR', 'XOF', 'JMD', 'JPY', 'GBP', 'JOD',
             'KZT',
             'KES', 'AUD', 'KPW', 'KRW', 'KWD', 'KGS', 'LAK', 'LVL', 'LBP', 'LSL', 'LRD', 'LYD', 'CHF', 'LTL', 'EUR',
             'MOP',
             'MKD', 'MGF', 'MWK', 'MYR', 'MVR', 'XOF', 'EUR', 'USD', 'EUR', 'MRO', 'MUR', 'EUR', 'MXN', 'USD', 'MDL',
             'EUR',
             'MNT', 'EUR', 'XCD', 'MAD', 'MZN', 'MMK', 'NAD', 'AUD', 'NPR', 'EUR', 'ANG', 'XPF', 'NZD', 'NIO', 'XOF',
             'NGN',
             'NZD', 'AUD', 'USD', 'NOK', 'OMR', 'PKR', 'USD', 'PAB', 'PGK', 'PYG', 'PEN', 'PHP', 'NZD', 'PLN', 'XPF',
             'EUR',
             'USD', 'QAR', 'EUR', 'RON', 'RUB', 'RWF', 'SHP', 'XCD', 'XCD', 'EUR', 'XCD', 'WST', 'EUR', 'STD', 'SAR',
             'XOF',
             'RSD', 'SCR', 'SLL', 'SGD', 'EUR', 'EUR', 'SBD', 'SOS', 'ZAR', 'GBP', 'SSP', 'EUR', 'LKR', 'SDG', 'SRD',
             'NOK',
             'SZL', 'SEK', 'CHF', 'SYP', 'TWD', 'TJS', 'TZS', 'THB', 'XOF', 'NZD', 'TOP', 'TTD', 'TND', 'TRY', 'TMT',
             'USD',
             'AUD', 'GBP', 'UGX', 'UAH', 'AED', 'UYU', 'USD', 'USD', 'UZS', 'VUV', 'EUR', 'VEF', 'VND', 'USD', 'USD',
             'XPF',
             'MAD', 'YER', 'ZMW', 'ZWD']
    return choice(codes)


