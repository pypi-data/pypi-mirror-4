======
README
======

The source files used for generate the vocabulary and translation locaes are
taken from the debian iso codes files form the public ftp server:
http://pkg-isocodes.alioth.debian.org/downloads/

This files are licenced as LGPL

If you need to update to the newest source, download the newest source files
and copy the iso_639 folder to the source folder in this package. After that
you can run the ``extract``buildout script with bin/extract. This will generate
the required vocabulary csv source files, copy the *.po files to the right 
LC_MESSAGES folders and generate the *.mo files. Note; this will require a
working msgfmt script installation.

For more information about the ISO 639-2 standard see the following resources:

http://en.wikipedia.org/wiki/ISO_639

http://en.wikipedia.org/wiki/ISO_639-1

http://www.loc.gov/standards/iso639-2/php/code_list.php


ISO639Alpha2LanguageVocabulary
------------------------------

Let's test the language vocabulary.

  >>> import p01.vocabulary.language
  >>> vocab = p01.vocabulary.language.ISO639Alpha2LanguageVocabulary(None)
  >>> len(vocab)
  185

  >>> for item in vocab:
  ...     '%s %s %s' % (item.value, item.token, item.title)
  u'aa aa Afar'
  u'ab ab Abkhazian'
  u'af af Afrikaans'
  u'ak ak Akan'
  u'sq sq Albanian'
  u'am am Amharic'
  u'ar ar Arabic'
  u'an an Aragonese'
  u'hy hy Armenian'
  u'as as Assamese'
  u'av av Avaric'
  u'ae ae Avestan'
  u'ay ay Aymara'
  u'az az Azerbaijani'
  u'ba ba Bashkir'
  u'bm bm Bambara'
  u'eu eu Basque'
  u'be be Belarusian'
  u'bn bn Bengali'
  u'bh bh Bihari'
  u'bi bi Bislama'
  u'bs bs Bosnian'
  u'br br Breton'
  u'bg bg Bulgarian'
  u'my my Burmese'
  u'ca ca Catalan; Valencian'
  u'ch ch Chamorro'
  u'ce ce Chechen'
  u'zh zh Chinese'
  u'cu cu Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic'
  u'cv cv Chuvash'
  u'kw kw Cornish'
  u'co co Corsican'
  u'cr cr Cree'
  u'cs cs Czech'
  u'da da Danish'
  u'dv dv Divehi; Dhivehi; Maldivian'
  u'nl nl Dutch; Flemish'
  u'dz dz Dzongkha'
  u'en en English'
  u'eo eo Esperanto'
  u'et et Estonian'
  u'ee ee Ewe'
  u'fo fo Faroese'
  u'fj fj Fijian'
  u'fi fi Finnish'
  u'fr fr French'
  u'fy fy Western Frisian'
  u'ff ff Fulah'
  u'ka ka Georgian'
  u'de de German'
  u'gd gd Gaelic; Scottish Gaelic'
  u'ga ga Irish'
  u'gl gl Galician'
  u'gv gv Manx'
  u'el el Greek, Modern (1453-)'
  u'gn gn Guarani'
  u'gu gu Gujarati'
  u'ht ht Haitian; Haitian Creole'
  u'ha ha Hausa'
  u'he he Hebrew'
  u'hz hz Herero'
  u'hi hi Hindi'
  u'ho ho Hiri Motu'
  u'hr hr Croatian'
  u'hu hu Hungarian'
  u'ig ig Igbo'
  u'is is Icelandic'
  u'io io Ido'
  u'ii ii Sichuan Yi; Nuosu'
  u'iu iu Inuktitut'
  u'ie ie Interlingue; Occidental'
  u'ia ia Interlingua (International Auxiliary Language Association)'
  u'id id Indonesian'
  u'ik ik Inupiaq'
  u'it it Italian'
  u'jv jv Javanese'
  u'ja ja Japanese'
  u'kl kl Kalaallisut; Greenlandic'
  u'kn kn Kannada'
  u'ks ks Kashmiri'
  u'kr kr Kanuri'
  u'kk kk Kazakh'
  u'km km Central Khmer'
  u'ki ki Kikuyu; Gikuyu'
  u'rw rw Kinyarwanda'
  u'ky ky Kirghiz; Kyrgyz'
  u'kv kv Komi'
  u'kg kg Kongo'
  u'ko ko Korean'
  u'kj kj Kuanyama; Kwanyama'
  u'ku ku Kurdish'
  u'lo lo Lao'
  u'la la Latin'
  u'lv lv Latvian'
  u'li li Limburgan; Limburger; Limburgish'
  u'ln ln Lingala'
  u'lt lt Lithuanian'
  u'lb lb Luxembourgish; Letzeburgesch'
  u'lu lu Luba-Katanga'
  u'lg lg Ganda'
  u'mk mk Macedonian'
  u'mh mh Marshallese'
  u'ml ml Malayalam'
  u'mi mi Maori'
  u'mr mr Marathi'
  u'ms ms Malay'
  u'mg mg Malagasy'
  u'mt mt Maltese'
  u'mo mo Moldavian; Moldovan'
  u'mn mn Mongolian'
  u'na na Nauru'
  u'nv nv Navajo; Navaho'
  u'nr nr Ndebele, South; South Ndebele'
  u'nd nd Ndebele, North; North Ndebele'
  u'ng ng Ndonga'
  u'ne ne Nepali'
  u'nn nn Norwegian Nynorsk; Nynorsk, Norwegian'
  u'nb nb Bokm\xe5l, Norwegian; Norwegian Bokm\xe5l'
  u'no no Norwegian'
  u'ny ny Chichewa; Chewa; Nyanja'
  u'oc oc Occitan (post 1500)'
  u'oj oj Ojibwa'
  u'or or Oriya'
  u'om om Oromo'
  u'os os Ossetian; Ossetic'
  u'pa pa Panjabi; Punjabi'
  u'fa fa Persian'
  u'pi pi Pali'
  u'pl pl Polish'
  u'pt pt Portuguese'
  u'ps ps Pushto; Pashto'
  u'qu qu Quechua'
  u'rm rm Romansh'
  u'ro ro Romanian'
  u'rn rn Rundi'
  u'ru ru Russian'
  u'sg sg Sango'
  u'sa sa Sanskrit'
  u'si si Sinhala; Sinhalese'
  u'sk sk Slovak'
  u'sl sl Slovenian'
  u'se se Northern Sami'
  u'sm sm Samoan'
  u'sn sn Shona'
  u'sd sd Sindhi'
  u'so so Somali'
  u'st st Sotho, Southern'
  u'es es Spanish; Castilian'
  u'sc sc Sardinian'
  u'sr sr Serbian'
  u'ss ss Swati'
  u'su su Sundanese'
  u'sw sw Swahili'
  u'sv sv Swedish'
  u'ty ty Tahitian'
  u'ta ta Tamil'
  u'tt tt Tatar'
  u'te te Telugu'
  u'tg tg Tajik'
  u'tl tl Tagalog'
  u'th th Thai'
  u'bo bo Tibetan'
  u'ti ti Tigrinya'
  u'to to Tonga (Tonga Islands)'
  u'tn tn Tswana'
  u'ts ts Tsonga'
  u'tk tk Turkmen'
  u'tr tr Turkish'
  u'tw tw Twi'
  u'ug ug Uighur; Uyghur'
  u'uk uk Ukrainian'
  u'ur ur Urdu'
  u'uz uz Uzbek'
  u've ve Venda'
  u'vi vi Vietnamese'
  u'vo vo Volap\xfck'
  u'cy cy Welsh'
  u'wa wa Walloon'
  u'wo wo Wolof'
  u'xh xh Xhosa'
  u'yi yi Yiddish'
  u'yo yo Yoruba'
  u'za za Zhuang; Chuang'
  u'zu zu Zulu'


The vocabulary allow us to get a term by token:

  >>> term = vocab.getTermByToken('de')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.token
  'de'

  >>> term.value
  u'de'

  >>> term.title
  u'German'

Or we can get a term by value:

  >>> term = vocab.getTerm('de')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.token
  'de'

  >>> term.value
  u'de'

  >>> term.title
  u'German'


MessageFactory
--------------

The package provides an own message factory using the iso639 doamin:

  >>> from p01.vocabulary.language.i18n import MessageFactory as _iso639_
  >>> _iso639_
  <zope.i18nmessageid.message.MessageFactory object at ...>

  >>> text = _iso639_('German', default=u'German')
  >>> text
  u'German'

  >>> text.domain
  'iso639'

  >>> text.default
  u'German'

  >>> text.mapping is None
  True


The translations given from the debian iso files are available. Let's register
the german and french catalog and an iso639 translation domain:

  >>> import os
  >>> import zope.i18n
  >>> import zope.i18n.interfaces
  >>> import zope.i18n.translationdomain
  >>> import zope.i18n.gettextmessagecatalog
  >>> domain = zope.i18n.translationdomain.TranslationDomain('iso639')
  >>> dePath = os.path.join(os.path.dirname(p01.vocabulary.language.__file__),
  ...     'locales', 'de', 'LC_MESSAGES', 'iso639.mo')
  >>> frPath = os.path.join(os.path.dirname(p01.vocabulary.language.__file__),
  ...     'locales', 'fr', 'LC_MESSAGES', 'iso639.mo')
  >>> catalog = zope.i18n.gettextmessagecatalog.GettextMessageCatalog('de',
  ...     'default', dePath)
  >>> domain.addCatalog(catalog)
  >>> catalog = zope.i18n.gettextmessagecatalog.GettextMessageCatalog('fr',
  ...     'default', frPath)
  >>> domain.addCatalog(catalog)
  >>> zope.component.provideUtility(domain,
  ...     zope.i18n.interfaces.ITranslationDomain, name='iso639')

Now we can translate to german:

  >>> zope.i18n.translate(text, target_language='de')
  u'Deutsch'

or to french:

  >>> zope.i18n.translate(text, target_language='fr')
  u'Allemand'
