======
README
======

The source files used for generate the vocabulary and translation locaes are
taken from the debian iso codes files form the public ftp server:
http://pkg-isocodes.alioth.debian.org/downloads/

This files are licenced as LGPL

If you need to update to the newest source, download the newest source files
and copy the iso_3166 folder to the source folder in this package. After that
you can run the ``extract``buildout script with bin/extract. This will generate
the requiredvocabulary csv source files, copy the *.po files to the right 
LC_MESSAGES folders and generate the *.mo files. Note; this will require a
working msgfmt script installation.

For more information about the ISO 3166-1 standard see the following resources:

http://en.wikipedia.org/wiki/ISO_3166-2

http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2


ISO3166Alpha2CountryVocabulary
------------------------------

This is a country vocabulary uses the ``ISO 3166 ALPHA-2 code`` country codes.

Let's test the country vocabulary.

  >>> from pprint import pprint
  >>> import p01.vocabulary.country
  >>> vocab = p01.vocabulary.country.ISO3166Alpha2CountryVocabulary(None)
  >>> len(vocab)
  250

  >>> for item in vocab:
  ...     '%s %s %s' % (item.value, item.token, item.title)
  u'AF AF Afghanistan'
  u'AX AX \xc5land Islands'
  u'AL AL Albania'
  u'DZ DZ Algeria'
  u'AS AS American Samoa'
  u'AD AD Andorra'
  u'AO AO Angola'
  u'AI AI Anguilla'
  u'AQ AQ Antarctica'
  u'AG AG Antigua and Barbuda'
  u'AR AR Argentina'
  u'AM AM Armenia'
  u'AW AW Aruba'
  u'AU AU Australia'
  u'AT AT Austria'
  u'AZ AZ Azerbaijan'
  u'BS BS Bahamas'
  u'BH BH Bahrain'
  u'BD BD Bangladesh'
  u'BB BB Barbados'
  u'BY BY Belarus'
  u'BE BE Belgium'
  u'BZ BZ Belize'
  u'BJ BJ Benin'
  u'BM BM Bermuda'
  u'BT BT Bhutan'
  u'BO BO Bolivia'
  u'BQ BQ Bonaire, Sint Eustatius and Saba'
  u'BA BA Bosnia and Herzegovina'
  u'BW BW Botswana'
  u'BV BV Bouvet Island'
  u'BR BR Brazil'
  u'IO IO British Indian Ocean Territory'
  u'BN BN Brunei Darussalam'
  u'BG BG Bulgaria'
  u'BF BF Burkina Faso'
  u'BI BI Burundi'
  u'KH KH Cambodia'
  u'CM CM Cameroon'
  u'CA CA Canada'
  u'CV CV Cape Verde'
  u'KY KY Cayman Islands'
  u'CF CF Central African Republic'
  u'TD TD Chad'
  u'CL CL Chile'
  u'CN CN China'
  u'CX CX Christmas Island'
  u'CC CC Cocos (Keeling) Islands'
  u'CO CO Colombia'
  u'KM KM Comoros'
  u'CG CG Congo'
  u'CD CD Congo, The Democratic Republic of the'
  u'CK CK Cook Islands'
  u'CR CR Costa Rica'
  u"CI CI C\xf4te d'Ivoire"
  u'HR HR Croatia'
  u'CU CU Cuba'
  u'CW CW Cura\xe7ao'
  u'CY CY Cyprus'
  u'CZ CZ Czech Republic'
  u'DK DK Denmark'
  u'DJ DJ Djibouti'
  u'DM DM Dominica'
  u'DO DO Dominican Republic'
  u'EC EC Ecuador'
  u'EG EG Egypt'
  u'SV SV El Salvador'
  u'GQ GQ Equatorial Guinea'
  u'ER ER Eritrea'
  u'EE EE Estonia'
  u'ET ET Ethiopia'
  u'FK FK Falkland Islands (Malvinas)'
  u'FO FO Faroe Islands'
  u'FJ FJ Fiji'
  u'FI FI Finland'
  u'FR FR France'
  u'GF GF French Guiana'
  u'PF PF French Polynesia'
  u'TF TF French Southern Territories'
  u'GA GA Gabon'
  u'GM GM Gambia'
  u'GE GE Georgia'
  u'DE DE Germany'
  u'GH GH Ghana'
  u'GI GI Gibraltar'
  u'GR GR Greece'
  u'GL GL Greenland'
  u'GD GD Grenada'
  u'GP GP Guadeloupe'
  u'GU GU Guam'
  u'GT GT Guatemala'
  u'GG GG Guernsey'
  u'GN GN Guinea'
  u'GW GW Guinea-Bissau'
  u'GY GY Guyana'
  u'HT HT Haiti'
  u'HM HM Heard Island and McDonald Islands'
  u'VA VA Holy See (Vatican City State)'
  u'HN HN Honduras'
  u'HK HK Hong Kong'
  u'HU HU Hungary'
  u'IS IS Iceland'
  u'IN IN India'
  u'ID ID Indonesia'
  u'IR IR Iran, Islamic Republic of'
  u'IQ IQ Iraq'
  u'IE IE Ireland'
  u'IM IM Isle of Man'
  u'IL IL Israel'
  u'IT IT Italy'
  u'JM JM Jamaica'
  u'JP JP Japan'
  u'JE JE Jersey'
  u'JO JO Jordan'
  u'KZ KZ Kazakhstan'
  u'KE KE Kenya'
  u'KI KI Kiribati'
  u"KP KP Korea, Democratic People's Republic of"
  u'KR KR Korea, Republic of'
  u'KW KW Kuwait'
  u'KG KG Kyrgyzstan'
  u"LA LA Lao People's Democratic Republic"
  u'LV LV Latvia'
  u'LB LB Lebanon'
  u'LS LS Lesotho'
  u'LR LR Liberia'
  u'LY LY Libya'
  u'LI LI Liechtenstein'
  u'LT LT Lithuania'
  u'LU LU Luxembourg'
  u'MO MO Macao'
  u'MK MK Macedonia, Republic of'
  u'MG MG Madagascar'
  u'MW MW Malawi'
  u'MY MY Malaysia'
  u'MV MV Maldives'
  u'ML ML Mali'
  u'MT MT Malta'
  u'MH MH Marshall Islands'
  u'MQ MQ Martinique'
  u'MR MR Mauritania'
  u'MU MU Mauritius'
  u'YT YT Mayotte'
  u'MX MX Mexico'
  u'FM FM Micronesia, Federated States of'
  u'MD MD Moldova'
  u'MC MC Monaco'
  u'MN MN Mongolia'
  u'ME ME Montenegro'
  u'MS MS Montserrat'
  u'MA MA Morocco'
  u'MZ MZ Mozambique'
  u'MM MM Myanmar'
  u'NA NA Namibia'
  u'NR NR Nauru'
  u'NP NP Nepal'
  u'NL NL Netherlands'
  u'NC NC New Caledonia'
  u'NZ NZ New Zealand'
  u'NI NI Nicaragua'
  u'NE NE Niger'
  u'NG NG Nigeria'
  u'NU NU Niue'
  u'NF NF Norfolk Island'
  u'MP MP Northern Mariana Islands'
  u'NO NO Norway'
  u'OM OM Oman'
  u'PK PK Pakistan'
  u'PW PW Palau'
  u'PS PS Palestinian Territory, Occupied'
  u'PA PA Panama'
  u'PG PG Papua New Guinea'
  u'PY PY Paraguay'
  u'PE PE Peru'
  u'PH PH Philippines'
  u'PN PN Pitcairn'
  u'PL PL Poland'
  u'PT PT Portugal'
  u'PR PR Puerto Rico'
  u'QA QA Qatar'
  u'RE RE R\xe9union'
  u'RO RO Romania'
  u'RU RU Russian Federation'
  u'RW RW Rwanda'
  u'BL BL Saint Barth\xe9lemy'
  u'SH SH Saint Helena, Ascension and Tristan da Cunha'
  u'KN KN Saint Kitts and Nevis'
  u'LC LC Saint Lucia'
  u'MF MF Saint Martin (French part)'
  u'PM PM Saint Pierre and Miquelon'
  u'VC VC Saint Vincent and the Grenadines'
  u'WS WS Samoa'
  u'SM SM San Marino'
  u'ST ST Sao Tome and Principe'
  u'SA SA Saudi Arabia'
  u'SN SN Senegal'
  u'RS RS Serbia'
  u'SC SC Seychelles'
  u'SL SL Sierra Leone'
  u'SG SG Singapore'
  u'SX SX Sint Maarten (Dutch part)'
  u'SK SK Slovakia'
  u'SI SI Slovenia'
  u'SB SB Solomon Islands'
  u'SO SO Somalia'
  u'ZA ZA South Africa'
  u'GS GS South Georgia and the South Sandwich Islands'
  u'ES ES Spain'
  u'LK LK Sri Lanka'
  u'SD SD Sudan'
  u'SR SR Suriname'
  u'SS SS South Sudan'
  u'SJ SJ Svalbard and Jan Mayen'
  u'SZ SZ Swaziland'
  u'SE SE Sweden'
  u'CH CH Switzerland'
  u'SY SY Syrian Arab Republic'
  u'TW TW Taiwan'
  u'TJ TJ Tajikistan'
  u'TZ TZ Tanzania, United Republic of'
  u'TH TH Thailand'
  u'TL TL Timor-Leste'
  u'TG TG Togo'
  u'TK TK Tokelau'
  u'TO TO Tonga'
  u'TT TT Trinidad and Tobago'
  u'TN TN Tunisia'
  u'TR TR Turkey'
  u'TM TM Turkmenistan'
  u'TC TC Turks and Caicos Islands'
  u'TV TV Tuvalu'
  u'UG UG Uganda'
  u'UA UA Ukraine'
  u'AE AE United Arab Emirates'
  u'GB GB United Kingdom'
  u'US US United States'
  u'UM UM United States Minor Outlying Islands'
  u'UY UY Uruguay'
  u'UZ UZ Uzbekistan'
  u'VU VU Vanuatu'
  u'VE VE Venezuela'
  u'VN VN Viet Nam'
  u'VG VG Virgin Islands, British'
  u'VI VI Virgin Islands, U.S.'
  u'WF WF Wallis and Futuna'
  u'EH EH Western Sahara'
  u'YE YE Yemen'
  u'ZM ZM Zambia'
  u'ZW ZW Zimbabwe'
  u'XK XK Kosovo'

The vocabulary allow us to get a term by token:

  >>> term = vocab.getTermByToken('CH')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.token
  'CH'

  >>> term.value
  u'CH'

  >>> term.title
  u'Switzerland'

Or we can get a term by value:

  >>> term = vocab.getTerm('CH')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.token
  'CH'

  >>> term.value
  u'CH'

  >>> term.title
  u'Switzerland'


ISO3166Alpha3CountryVocabulary
------------------------------

This is a country vocabulary uses the ``ISO 3166 ALPHA-3 code`` country codes.

Let's test the country vocabulary.

  >>> vocab = p01.vocabulary.country.ISO3166Alpha3CountryVocabulary(None)
  >>> len(vocab)
  250

  >>> for item in vocab:
  ...     '%s %s %s' % (item.value, item.token, item.title)
  u'AFG AFG Afghanistan'
  u'ALA ALA \xc5land Islands'
  u'ALB ALB Albania'
  u'DZA DZA Algeria'
  u'ASM ASM American Samoa'
  u'AND AND Andorra'
  u'AGO AGO Angola'
  u'AIA AIA Anguilla'
  u'ATA ATA Antarctica'
  u'ATG ATG Antigua and Barbuda'
  u'ARG ARG Argentina'
  u'ARM ARM Armenia'
  u'ABW ABW Aruba'
  u'AUS AUS Australia'
  u'AUT AUT Austria'
  u'AZE AZE Azerbaijan'
  u'BHS BHS Bahamas'
  u'BHR BHR Bahrain'
  u'BGD BGD Bangladesh'
  u'BRB BRB Barbados'
  u'BLR BLR Belarus'
  u'BEL BEL Belgium'
  u'BLZ BLZ Belize'
  u'BEN BEN Benin'
  u'BMU BMU Bermuda'
  u'BTN BTN Bhutan'
  u'BOL BOL Bolivia'
  u'BES BES Bonaire, Sint Eustatius and Saba'
  u'BIH BIH Bosnia and Herzegovina'
  u'BWA BWA Botswana'
  u'BVT BVT Bouvet Island'
  u'BRA BRA Brazil'
  u'IOT IOT British Indian Ocean Territory'
  u'BRN BRN Brunei Darussalam'
  u'BGR BGR Bulgaria'
  u'BFA BFA Burkina Faso'
  u'BDI BDI Burundi'
  u'KHM KHM Cambodia'
  u'CMR CMR Cameroon'
  u'CAN CAN Canada'
  u'CPV CPV Cape Verde'
  u'CYM CYM Cayman Islands'
  u'CAF CAF Central African Republic'
  u'TCD TCD Chad'
  u'CHL CHL Chile'
  u'CHN CHN China'
  u'CXR CXR Christmas Island'
  u'CCK CCK Cocos (Keeling) Islands'
  u'COL COL Colombia'
  u'COM COM Comoros'
  u'COG COG Congo'
  u'COD COD Congo, The Democratic Republic of the'
  u'COK COK Cook Islands'
  u'CRI CRI Costa Rica'
  u"CIV CIV C\xf4te d'Ivoire"
  u'HRV HRV Croatia'
  u'CUB CUB Cuba'
  u'CUW CUW Cura\xe7ao'
  u'CYP CYP Cyprus'
  u'CZE CZE Czech Republic'
  u'DNK DNK Denmark'
  u'DJI DJI Djibouti'
  u'DMA DMA Dominica'
  u'DOM DOM Dominican Republic'
  u'ECU ECU Ecuador'
  u'EGY EGY Egypt'
  u'SLV SLV El Salvador'
  u'GNQ GNQ Equatorial Guinea'
  u'ERI ERI Eritrea'
  u'EST EST Estonia'
  u'ETH ETH Ethiopia'
  u'FLK FLK Falkland Islands (Malvinas)'
  u'FRO FRO Faroe Islands'
  u'FJI FJI Fiji'
  u'FIN FIN Finland'
  u'FRA FRA France'
  u'GUF GUF French Guiana'
  u'PYF PYF French Polynesia'
  u'ATF ATF French Southern Territories'
  u'GAB GAB Gabon'
  u'GMB GMB Gambia'
  u'GEO GEO Georgia'
  u'DEU DEU Germany'
  u'GHA GHA Ghana'
  u'GIB GIB Gibraltar'
  u'GRC GRC Greece'
  u'GRL GRL Greenland'
  u'GRD GRD Grenada'
  u'GLP GLP Guadeloupe'
  u'GUM GUM Guam'
  u'GTM GTM Guatemala'
  u'GGY GGY Guernsey'
  u'GIN GIN Guinea'
  u'GNB GNB Guinea-Bissau'
  u'GUY GUY Guyana'
  u'HTI HTI Haiti'
  u'HMD HMD Heard Island and McDonald Islands'
  u'VAT VAT Holy See (Vatican City State)'
  u'HND HND Honduras'
  u'HKG HKG Hong Kong'
  u'HUN HUN Hungary'
  u'ISL ISL Iceland'
  u'IND IND India'
  u'IDN IDN Indonesia'
  u'IRN IRN Iran, Islamic Republic of'
  u'IRQ IRQ Iraq'
  u'IRL IRL Ireland'
  u'IMN IMN Isle of Man'
  u'ISR ISR Israel'
  u'ITA ITA Italy'
  u'JAM JAM Jamaica'
  u'JPN JPN Japan'
  u'JEY JEY Jersey'
  u'JOR JOR Jordan'
  u'KAZ KAZ Kazakhstan'
  u'KEN KEN Kenya'
  u'KIR KIR Kiribati'
  u"PRK PRK Korea, Democratic People's Republic of"
  u'KOR KOR Korea, Republic of'
  u'KWT KWT Kuwait'
  u'KGZ KGZ Kyrgyzstan'
  u"LAO LAO Lao People's Democratic Republic"
  u'LVA LVA Latvia'
  u'LBN LBN Lebanon'
  u'LSO LSO Lesotho'
  u'LBR LBR Liberia'
  u'LBY LBY Libya'
  u'LIE LIE Liechtenstein'
  u'LTU LTU Lithuania'
  u'LUX LUX Luxembourg'
  u'MAC MAC Macao'
  u'MKD MKD Macedonia, Republic of'
  u'MDG MDG Madagascar'
  u'MWI MWI Malawi'
  u'MYS MYS Malaysia'
  u'MDV MDV Maldives'
  u'MLI MLI Mali'
  u'MLT MLT Malta'
  u'MHL MHL Marshall Islands'
  u'MTQ MTQ Martinique'
  u'MRT MRT Mauritania'
  u'MUS MUS Mauritius'
  u'MYT MYT Mayotte'
  u'MEX MEX Mexico'
  u'FSM FSM Micronesia, Federated States of'
  u'MDA MDA Moldova'
  u'MCO MCO Monaco'
  u'MNG MNG Mongolia'
  u'MNE MNE Montenegro'
  u'MSR MSR Montserrat'
  u'MAR MAR Morocco'
  u'MOZ MOZ Mozambique'
  u'MMR MMR Myanmar'
  u'NAM NAM Namibia'
  u'NRU NRU Nauru'
  u'NPL NPL Nepal'
  u'NLD NLD Netherlands'
  u'NCL NCL New Caledonia'
  u'NZL NZL New Zealand'
  u'NIC NIC Nicaragua'
  u'NER NER Niger'
  u'NGA NGA Nigeria'
  u'NIU NIU Niue'
  u'NFK NFK Norfolk Island'
  u'MNP MNP Northern Mariana Islands'
  u'NOR NOR Norway'
  u'OMN OMN Oman'
  u'PAK PAK Pakistan'
  u'PLW PLW Palau'
  u'PSE PSE Palestinian Territory, Occupied'
  u'PAN PAN Panama'
  u'PNG PNG Papua New Guinea'
  u'PRY PRY Paraguay'
  u'PER PER Peru'
  u'PHL PHL Philippines'
  u'PCN PCN Pitcairn'
  u'POL POL Poland'
  u'PRT PRT Portugal'
  u'PRI PRI Puerto Rico'
  u'QAT QAT Qatar'
  u'REU REU R\xe9union'
  u'ROU ROU Romania'
  u'RUS RUS Russian Federation'
  u'RWA RWA Rwanda'
  u'BLM BLM Saint Barth\xe9lemy'
  u'SHN SHN Saint Helena, Ascension and Tristan da Cunha'
  u'KNA KNA Saint Kitts and Nevis'
  u'LCA LCA Saint Lucia'
  u'MAF MAF Saint Martin (French part)'
  u'SPM SPM Saint Pierre and Miquelon'
  u'VCT VCT Saint Vincent and the Grenadines'
  u'WSM WSM Samoa'
  u'SMR SMR San Marino'
  u'STP STP Sao Tome and Principe'
  u'SAU SAU Saudi Arabia'
  u'SEN SEN Senegal'
  u'SRB SRB Serbia'
  u'SYC SYC Seychelles'
  u'SLE SLE Sierra Leone'
  u'SGP SGP Singapore'
  u'SXM SXM Sint Maarten (Dutch part)'
  u'SVK SVK Slovakia'
  u'SVN SVN Slovenia'
  u'SLB SLB Solomon Islands'
  u'SOM SOM Somalia'
  u'ZAF ZAF South Africa'
  u'SGS SGS South Georgia and the South Sandwich Islands'
  u'ESP ESP Spain'
  u'LKA LKA Sri Lanka'
  u'SDN SDN Sudan'
  u'SUR SUR Suriname'
  u'SSD SSD South Sudan'
  u'SJM SJM Svalbard and Jan Mayen'
  u'SWZ SWZ Swaziland'
  u'SWE SWE Sweden'
  u'CHE CHE Switzerland'
  u'SYR SYR Syrian Arab Republic'
  u'TWN TWN Taiwan'
  u'TJK TJK Tajikistan'
  u'TZA TZA Tanzania, United Republic of'
  u'THA THA Thailand'
  u'TLS TLS Timor-Leste'
  u'TGO TGO Togo'
  u'TKL TKL Tokelau'
  u'TON TON Tonga'
  u'TTO TTO Trinidad and Tobago'
  u'TUN TUN Tunisia'
  u'TUR TUR Turkey'
  u'TKM TKM Turkmenistan'
  u'TCA TCA Turks and Caicos Islands'
  u'TUV TUV Tuvalu'
  u'UGA UGA Uganda'
  u'UKR UKR Ukraine'
  u'ARE ARE United Arab Emirates'
  u'GBR GBR United Kingdom'
  u'USA USA United States'
  u'UMI UMI United States Minor Outlying Islands'
  u'URY URY Uruguay'
  u'UZB UZB Uzbekistan'
  u'VUT VUT Vanuatu'
  u'VEN VEN Venezuela'
  u'VNM VNM Viet Nam'
  u'VGB VGB Virgin Islands, British'
  u'VIR VIR Virgin Islands, U.S.'
  u'WLF WLF Wallis and Futuna'
  u'ESH ESH Western Sahara'
  u'YEM YEM Yemen'
  u'ZMB ZMB Zambia'
  u'ZWE ZWE Zimbabwe'
  u'XKV XKV Kosovo'

The vocabulary allow us to get a term by token:

  >>> term = vocab.getTermByToken('CHE')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.token
  'CHE'

  >>> term.value
  u'CHE'

  >>> term.title
  u'Switzerland'

Or we can get a term by value:

  >>> term = vocab.getTerm('CHE')
  >>> term
  <zope.schema.vocabulary.SimpleTerm object at ...>

  >>> term.token
  'CHE'

  >>> term.value
  u'CHE'

  >>> term.title
  u'Switzerland'


alpha2to3
---------

  >>> from p01.vocabulary.country import alpha2to3
  >>> pprint(alpha2to3)
  {u'AD': u'AND',
   u'AE': u'ARE',
   u'AF': u'AFG',
   u'AG': u'ATG',
   u'AI': u'AIA',
   u'AL': u'ALB',
   u'AM': u'ARM',
   u'AO': u'AGO',
   u'AQ': u'ATA',
   u'AR': u'ARG',
   u'AS': u'ASM',
   u'AT': u'AUT',
   u'AU': u'AUS',
   u'AW': u'ABW',
   u'AX': u'ALA',
   u'AZ': u'AZE',
   u'BA': u'BIH',
   u'BB': u'BRB',
   u'BD': u'BGD',
   u'BE': u'BEL',
   u'BF': u'BFA',
   u'BG': u'BGR',
   u'BH': u'BHR',
   u'BI': u'BDI',
   u'BJ': u'BEN',
   u'BL': u'BLM',
   u'BM': u'BMU',
   u'BN': u'BRN',
   u'BO': u'BOL',
   u'BQ': u'BES',
   u'BR': u'BRA',
   u'BS': u'BHS',
   u'BT': u'BTN',
   u'BV': u'BVT',
   u'BW': u'BWA',
   u'BY': u'BLR',
   u'BZ': u'BLZ',
   u'CA': u'CAN',
   u'CC': u'CCK',
   u'CD': u'COD',
   u'CF': u'CAF',
   u'CG': u'COG',
   u'CH': u'CHE',
   u'CI': u'CIV',
   u'CK': u'COK',
   u'CL': u'CHL',
   u'CM': u'CMR',
   u'CN': u'CHN',
   u'CO': u'COL',
   u'CR': u'CRI',
   u'CU': u'CUB',
   u'CV': u'CPV',
   u'CW': u'CUW',
   u'CX': u'CXR',
   u'CY': u'CYP',
   u'CZ': u'CZE',
   u'DE': u'DEU',
   u'DJ': u'DJI',
   u'DK': u'DNK',
   u'DM': u'DMA',
   u'DO': u'DOM',
   u'DZ': u'DZA',
   u'EC': u'ECU',
   u'EE': u'EST',
   u'EG': u'EGY',
   u'EH': u'ESH',
   u'ER': u'ERI',
   u'ES': u'ESP',
   u'ET': u'ETH',
   u'FI': u'FIN',
   u'FJ': u'FJI',
   u'FK': u'FLK',
   u'FM': u'FSM',
   u'FO': u'FRO',
   u'FR': u'FRA',
   u'GA': u'GAB',
   u'GB': u'GBR',
   u'GD': u'GRD',
   u'GE': u'GEO',
   u'GF': u'GUF',
   u'GG': u'GGY',
   u'GH': u'GHA',
   u'GI': u'GIB',
   u'GL': u'GRL',
   u'GM': u'GMB',
   u'GN': u'GIN',
   u'GP': u'GLP',
   u'GQ': u'GNQ',
   u'GR': u'GRC',
   u'GS': u'SGS',
   u'GT': u'GTM',
   u'GU': u'GUM',
   u'GW': u'GNB',
   u'GY': u'GUY',
   u'HK': u'HKG',
   u'HM': u'HMD',
   u'HN': u'HND',
   u'HR': u'HRV',
   u'HT': u'HTI',
   u'HU': u'HUN',
   u'ID': u'IDN',
   u'IE': u'IRL',
   u'IL': u'ISR',
   u'IM': u'IMN',
   u'IN': u'IND',
   u'IO': u'IOT',
   u'IQ': u'IRQ',
   u'IR': u'IRN',
   u'IS': u'ISL',
   u'IT': u'ITA',
   u'JE': u'JEY',
   u'JM': u'JAM',
   u'JO': u'JOR',
   u'JP': u'JPN',
   u'KE': u'KEN',
   u'KG': u'KGZ',
   u'KH': u'KHM',
   u'KI': u'KIR',
   u'KM': u'COM',
   u'KN': u'KNA',
   u'KP': u'PRK',
   u'KR': u'KOR',
   u'KW': u'KWT',
   u'KY': u'CYM',
   u'KZ': u'KAZ',
   u'LA': u'LAO',
   u'LB': u'LBN',
   u'LC': u'LCA',
   u'LI': u'LIE',
   u'LK': u'LKA',
   u'LR': u'LBR',
   u'LS': u'LSO',
   u'LT': u'LTU',
   u'LU': u'LUX',
   u'LV': u'LVA',
   u'LY': u'LBY',
   u'MA': u'MAR',
   u'MC': u'MCO',
   u'MD': u'MDA',
   u'ME': u'MNE',
   u'MF': u'MAF',
   u'MG': u'MDG',
   u'MH': u'MHL',
   u'MK': u'MKD',
   u'ML': u'MLI',
   u'MM': u'MMR',
   u'MN': u'MNG',
   u'MO': u'MAC',
   u'MP': u'MNP',
   u'MQ': u'MTQ',
   u'MR': u'MRT',
   u'MS': u'MSR',
   u'MT': u'MLT',
   u'MU': u'MUS',
   u'MV': u'MDV',
   u'MW': u'MWI',
   u'MX': u'MEX',
   u'MY': u'MYS',
   u'MZ': u'MOZ',
   u'NA': u'NAM',
   u'NC': u'NCL',
   u'NE': u'NER',
   u'NF': u'NFK',
   u'NG': u'NGA',
   u'NI': u'NIC',
   u'NL': u'NLD',
   u'NO': u'NOR',
   u'NP': u'NPL',
   u'NR': u'NRU',
   u'NU': u'NIU',
   u'NZ': u'NZL',
   u'OM': u'OMN',
   u'PA': u'PAN',
   u'PE': u'PER',
   u'PF': u'PYF',
   u'PG': u'PNG',
   u'PH': u'PHL',
   u'PK': u'PAK',
   u'PL': u'POL',
   u'PM': u'SPM',
   u'PN': u'PCN',
   u'PR': u'PRI',
   u'PS': u'PSE',
   u'PT': u'PRT',
   u'PW': u'PLW',
   u'PY': u'PRY',
   u'QA': u'QAT',
   u'RE': u'REU',
   u'RO': u'ROU',
   u'RS': u'SRB',
   u'RU': u'RUS',
   u'RW': u'RWA',
   u'SA': u'SAU',
   u'SB': u'SLB',
   u'SC': u'SYC',
   u'SD': u'SDN',
   u'SE': u'SWE',
   u'SG': u'SGP',
   u'SH': u'SHN',
   u'SI': u'SVN',
   u'SJ': u'SJM',
   u'SK': u'SVK',
   u'SL': u'SLE',
   u'SM': u'SMR',
   u'SN': u'SEN',
   u'SO': u'SOM',
   u'SR': u'SUR',
   u'SS': u'SSD',
   u'ST': u'STP',
   u'SV': u'SLV',
   u'SX': u'SXM',
   u'SY': u'SYR',
   u'SZ': u'SWZ',
   u'TC': u'TCA',
   u'TD': u'TCD',
   u'TF': u'ATF',
   u'TG': u'TGO',
   u'TH': u'THA',
   u'TJ': u'TJK',
   u'TK': u'TKL',
   u'TL': u'TLS',
   u'TM': u'TKM',
   u'TN': u'TUN',
   u'TO': u'TON',
   u'TR': u'TUR',
   u'TT': u'TTO',
   u'TV': u'TUV',
   u'TW': u'TWN',
   u'TZ': u'TZA',
   u'UA': u'UKR',
   u'UG': u'UGA',
   u'UM': u'UMI',
   u'US': u'USA',
   u'UY': u'URY',
   u'UZ': u'UZB',
   u'VA': u'VAT',
   u'VC': u'VCT',
   u'VE': u'VEN',
   u'VG': u'VGB',
   u'VI': u'VIR',
   u'VN': u'VNM',
   u'VU': u'VUT',
   u'WF': u'WLF',
   u'WS': u'WSM',
   u'XK': u'XKV',
   u'YE': u'YEM',
   u'YT': u'MYT',
   u'ZA': u'ZAF',
   u'ZM': u'ZMB',
   u'ZW': u'ZWE'}

alpha3to2
---------

  >>> from p01.vocabulary.country import alpha3to2
  >>> pprint(alpha3to2)
  {u'ABW': u'AW',
   u'AFG': u'AF',
   u'AGO': u'AO',
   u'AIA': u'AI',
   u'ALA': u'AX',
   u'ALB': u'AL',
   u'AND': u'AD',
   u'ARE': u'AE',
   u'ARG': u'AR',
   u'ARM': u'AM',
   u'ASM': u'AS',
   u'ATA': u'AQ',
   u'ATF': u'TF',
   u'ATG': u'AG',
   u'AUS': u'AU',
   u'AUT': u'AT',
   u'AZE': u'AZ',
   u'BDI': u'BI',
   u'BEL': u'BE',
   u'BEN': u'BJ',
   u'BES': u'BQ',
   u'BFA': u'BF',
   u'BGD': u'BD',
   u'BGR': u'BG',
   u'BHR': u'BH',
   u'BHS': u'BS',
   u'BIH': u'BA',
   u'BLM': u'BL',
   u'BLR': u'BY',
   u'BLZ': u'BZ',
   u'BMU': u'BM',
   u'BOL': u'BO',
   u'BRA': u'BR',
   u'BRB': u'BB',
   u'BRN': u'BN',
   u'BTN': u'BT',
   u'BVT': u'BV',
   u'BWA': u'BW',
   u'CAF': u'CF',
   u'CAN': u'CA',
   u'CCK': u'CC',
   u'CHE': u'CH',
   u'CHL': u'CL',
   u'CHN': u'CN',
   u'CIV': u'CI',
   u'CMR': u'CM',
   u'COD': u'CD',
   u'COG': u'CG',
   u'COK': u'CK',
   u'COL': u'CO',
   u'COM': u'KM',
   u'CPV': u'CV',
   u'CRI': u'CR',
   u'CUB': u'CU',
   u'CUW': u'CW',
   u'CXR': u'CX',
   u'CYM': u'KY',
   u'CYP': u'CY',
   u'CZE': u'CZ',
   u'DEU': u'DE',
   u'DJI': u'DJ',
   u'DMA': u'DM',
   u'DNK': u'DK',
   u'DOM': u'DO',
   u'DZA': u'DZ',
   u'ECU': u'EC',
   u'EGY': u'EG',
   u'ERI': u'ER',
   u'ESH': u'EH',
   u'ESP': u'ES',
   u'EST': u'EE',
   u'ETH': u'ET',
   u'FIN': u'FI',
   u'FJI': u'FJ',
   u'FLK': u'FK',
   u'FRA': u'FR',
   u'FRO': u'FO',
   u'FSM': u'FM',
   u'GAB': u'GA',
   u'GBR': u'GB',
   u'GEO': u'GE',
   u'GGY': u'GG',
   u'GHA': u'GH',
   u'GIB': u'GI',
   u'GIN': u'GN',
   u'GLP': u'GP',
   u'GMB': u'GM',
   u'GNB': u'GW',
   u'GNQ': u'GQ',
   u'GRC': u'GR',
   u'GRD': u'GD',
   u'GRL': u'GL',
   u'GTM': u'GT',
   u'GUF': u'GF',
   u'GUM': u'GU',
   u'GUY': u'GY',
   u'HKG': u'HK',
   u'HMD': u'HM',
   u'HND': u'HN',
   u'HRV': u'HR',
   u'HTI': u'HT',
   u'HUN': u'HU',
   u'IDN': u'ID',
   u'IMN': u'IM',
   u'IND': u'IN',
   u'IOT': u'IO',
   u'IRL': u'IE',
   u'IRN': u'IR',
   u'IRQ': u'IQ',
   u'ISL': u'IS',
   u'ISR': u'IL',
   u'ITA': u'IT',
   u'JAM': u'JM',
   u'JEY': u'JE',
   u'JOR': u'JO',
   u'JPN': u'JP',
   u'KAZ': u'KZ',
   u'KEN': u'KE',
   u'KGZ': u'KG',
   u'KHM': u'KH',
   u'KIR': u'KI',
   u'KNA': u'KN',
   u'KOR': u'KR',
   u'KWT': u'KW',
   u'LAO': u'LA',
   u'LBN': u'LB',
   u'LBR': u'LR',
   u'LBY': u'LY',
   u'LCA': u'LC',
   u'LIE': u'LI',
   u'LKA': u'LK',
   u'LSO': u'LS',
   u'LTU': u'LT',
   u'LUX': u'LU',
   u'LVA': u'LV',
   u'MAC': u'MO',
   u'MAF': u'MF',
   u'MAR': u'MA',
   u'MCO': u'MC',
   u'MDA': u'MD',
   u'MDG': u'MG',
   u'MDV': u'MV',
   u'MEX': u'MX',
   u'MHL': u'MH',
   u'MKD': u'MK',
   u'MLI': u'ML',
   u'MLT': u'MT',
   u'MMR': u'MM',
   u'MNE': u'ME',
   u'MNG': u'MN',
   u'MNP': u'MP',
   u'MOZ': u'MZ',
   u'MRT': u'MR',
   u'MSR': u'MS',
   u'MTQ': u'MQ',
   u'MUS': u'MU',
   u'MWI': u'MW',
   u'MYS': u'MY',
   u'MYT': u'YT',
   u'NAM': u'NA',
   u'NCL': u'NC',
   u'NER': u'NE',
   u'NFK': u'NF',
   u'NGA': u'NG',
   u'NIC': u'NI',
   u'NIU': u'NU',
   u'NLD': u'NL',
   u'NOR': u'NO',
   u'NPL': u'NP',
   u'NRU': u'NR',
   u'NZL': u'NZ',
   u'OMN': u'OM',
   u'PAK': u'PK',
   u'PAN': u'PA',
   u'PCN': u'PN',
   u'PER': u'PE',
   u'PHL': u'PH',
   u'PLW': u'PW',
   u'PNG': u'PG',
   u'POL': u'PL',
   u'PRI': u'PR',
   u'PRK': u'KP',
   u'PRT': u'PT',
   u'PRY': u'PY',
   u'PSE': u'PS',
   u'PYF': u'PF',
   u'QAT': u'QA',
   u'REU': u'RE',
   u'ROU': u'RO',
   u'RUS': u'RU',
   u'RWA': u'RW',
   u'SAU': u'SA',
   u'SDN': u'SD',
   u'SEN': u'SN',
   u'SGP': u'SG',
   u'SGS': u'GS',
   u'SHN': u'SH',
   u'SJM': u'SJ',
   u'SLB': u'SB',
   u'SLE': u'SL',
   u'SLV': u'SV',
   u'SMR': u'SM',
   u'SOM': u'SO',
   u'SPM': u'PM',
   u'SRB': u'RS',
   u'SSD': u'SS',
   u'STP': u'ST',
   u'SUR': u'SR',
   u'SVK': u'SK',
   u'SVN': u'SI',
   u'SWE': u'SE',
   u'SWZ': u'SZ',
   u'SXM': u'SX',
   u'SYC': u'SC',
   u'SYR': u'SY',
   u'TCA': u'TC',
   u'TCD': u'TD',
   u'TGO': u'TG',
   u'THA': u'TH',
   u'TJK': u'TJ',
   u'TKL': u'TK',
   u'TKM': u'TM',
   u'TLS': u'TL',
   u'TON': u'TO',
   u'TTO': u'TT',
   u'TUN': u'TN',
   u'TUR': u'TR',
   u'TUV': u'TV',
   u'TWN': u'TW',
   u'TZA': u'TZ',
   u'UGA': u'UG',
   u'UKR': u'UA',
   u'UMI': u'UM',
   u'URY': u'UY',
   u'USA': u'US',
   u'UZB': u'UZ',
   u'VAT': u'VA',
   u'VCT': u'VC',
   u'VEN': u'VE',
   u'VGB': u'VG',
   u'VIR': u'VI',
   u'VNM': u'VN',
   u'VUT': u'VU',
   u'WLF': u'WF',
   u'WSM': u'WS',
   u'XKV': u'XK',
   u'YEM': u'YE',
   u'ZAF': u'ZA',
   u'ZMB': u'ZM',
   u'ZWE': u'ZW'}

  >>> alpha2to3.get('CH')
  u'CHE'

  >>> alpha3to2.get('CHE')
  u'CH'

  >>> alpha3to2.get(alpha2to3.get('CH'))
  u'CH'

  >>> alpha2to3.get(alpha3to2.get('CHE'))
  u'CHE'


MessageFactory
--------------

The package provides an own message factory using the iso3166 doamin:

  >>> from p01.vocabulary.country.i18n import MessageFactory as _iso3166_
  >>> _iso3166_
  <zope.i18nmessageid.message.MessageFactory object at ...>

  >>> text = _iso3166_('Switzerland')
  >>> text
  u'Switzerland'

  >>> text.domain
  'iso3166'

The translations given from the debian iso files are available. Let's register
the german and french catalog and an iso3166 translation domain:

  >>> import os
  >>> import zope.i18n
  >>> import zope.i18n.interfaces
  >>> import zope.i18n.translationdomain
  >>> import zope.i18n.gettextmessagecatalog
  >>> domain = zope.i18n.translationdomain.TranslationDomain('iso3166')
  >>> dePath = os.path.join(os.path.dirname(p01.vocabulary.country.__file__),
  ...     'locales', 'de', 'LC_MESSAGES', 'iso3166.mo')
  >>> frPath = os.path.join(os.path.dirname(p01.vocabulary.country.__file__),
  ...     'locales', 'fr', 'LC_MESSAGES', 'iso3166.mo')
  >>> catalog = zope.i18n.gettextmessagecatalog.GettextMessageCatalog('de',
  ...     'iso3166', dePath)
  >>> domain.addCatalog(catalog)
  >>> catalog = zope.i18n.gettextmessagecatalog.GettextMessageCatalog('fr',
  ...     'iso3166', frPath)
  >>> domain.addCatalog(catalog)
  >>> zope.component.provideUtility(domain,
  ...     zope.i18n.interfaces.ITranslationDomain, name='iso3166')

Now we can translate to german:

  >>> zope.i18n.translate(text, target_language='de')
  u'Schweiz'

or to french:

  >>> zope.i18n.translate(text, target_language='fr')
  u'Suisse'
