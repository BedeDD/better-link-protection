#!/usr/bin/python
# -*- coding: utf-8 -*-

""" TIMER

    1.1.0
        Bugfixes in permission check and improved link detection and logging

    1.0.2
        Add missing field to settings
    1.0.1
        Fix permit check

    1.0.0
        Initial private release

"""

#---------------------------------------
# Script Import Libraries
#---------------------------------------
import clr
clr.AddReference("IronPython.Modules.dll")

import os
import codecs
import json
import time
from datetime import datetime, timedelta
import ctypes
import re

#---------------------------------------
# Script Information
#---------------------------------------
ScriptName = "BetterLinkProtection"
Website = "http://www.twitch.tv/lampe385"
Description = "Improved link protection for chat."
Creator = "Lampe385"
Version = "1.1.0"

#---------------------------------------
# Script Variables
#---------------------------------------

# Settings file location
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

# Compiled regex to verify set times in settings
LinkVerification = re.compile(r"([\d\w\-\. ]+)([0-9a-z ]+)(\.[a-z]{2,})", re.IGNORECASE)

# used for permit check every second
TimeElapsed = None
# Tick timestamp
TimeStampTick = None

TldList = [
    '.arpa','.com','.org','.net','.int','.edu','.gov','.mil','.ac','.ad','.ae','.af','.ag','.ai',
    '.al','.am','.ao','.aq','.ar','.as','.at','.au','.aw','.ax','.az','.ba','.bb','.bd','.be','.bf',
    '.bg','.bh','.bi','.bj','.bm','.bn','.bo','.br','.bs','.bt','.bw','.by','.bz','.ca','.cc','.cd',
    '.cf','.cg','.ch','.ci','.ck','.cl','.cm','.cn','.co','.cr','.cu','.cv','.cw','.cx','.cy','.cz',
    '.de','.dj','.dk','.dm','.do','.dz','.ec','.ee','.eg','.er','.es','.et','.eu','.fi','.fj','.fk',
    '.fm','.fo','.fr','.ga','.gd','.ge','.gf','.gg','.gh','.gi','.gl','.gm','.gn','.gp','.gq','.gr',
    '.gs','.gt','.gu','.gw','.gy','.hk','.hm','.hn','.hr','.ht','.hu','.id','.ie','.il','.im','.in',
    '.io','.iq','.ir','.is','.it','.je','.jm','.jo','.jp','.ke','.kg','.kh','.ki','.km','.kn','.kp',
    '.kr','.kw','.ky','.kz','.la','.lb','.lc','.li','.lk','.lr','.ls','.lt','.lu','.lv','.ly','.ma',
    '.mc','.md','.me','.mg','.mh','.mk','.ml','.mm','.mn','.mo','.mp','.mq','.mr','.ms','.mt','.mu',
    '.mv','.mw','.mx','.my','.mz','.na','.nc','.ne','.nf','.ng','.ni','.nl','.no','.np','.nr','.nu',
    '.nz','.om','.pa','.pe','.pf','.pg','.ph','.pk','.pl','.pm','.pn','.pr','.ps','.pt','.pw','.py',
    '.qa','.re','.ro','.rs','.ru','.rw','.sa','.sb','.sc','.sd','.se','.sg','.sh','.si','.sk','.sl',
    '.sm','.sn','.so','.sr','.ss','.st','.su','.sv','.sx','.sy','.sz','.tc','.td','.tf','.tg','.th',
    '.tj','.tk','.tl','.tm','.tn','.to','.tr','.tt','.tv','.tw','.tz','.ua','.ug','.uk','.us','.uy',
    '.uz','.va','.vc','.ve','.vg','.vi','.vn','.vu','.wf','.ws','.ye','.yt','.za','.zm','.zw',
    '.academy','.accountant','.accountants','.active','.actor','.ads','.adult','.aero','.africa',
    '.agency','.airforce','.amazon','.analytics','.apartments','.app','.archi','.army','.art','.associates',
    '.attorney','.auction','.audible','.audio','.author','.auto','.autos','.aws','.baby','.band','.bank',
    '.bar','.barefoot','.bargains','.baseball','.basketball','.beauty','.beer','.berlin','.best','.bestbuy',
    '.bet','.bible','.bid','.bike','.bingo','.bio','.biz','.black','.blackfriday','.blockbuster','.blog',
    '.blue','.boo','.book','.boots','.bot','.boutique','.box','.broadway','.broker','.build','.builders',
    '.business','.buy','.buzz','.cab','.cafe','.call','.cam','.camera','.camp','.cancerresearch','.capital',
    '.car','.cards','.care','.career','.careers','.cars','.case','.cash','.casino','.catering','.catholic',
    '.center','.cern','.ceo','.cfd','.channel','.chat','.cheap','.christmas','.church','.cipriani','.circle',
    '.city','.claims','.cleaning','.click','.clinic','.clothing','.cloud','.club','.coach','.codes','.coffee',
    '.college','.community','.company','.compare','.computer','.condos','.construction','.consulting','.contact',
    '.contractors','.cooking','.cool','.coop','.country','.coupon','.coupons','.courses','.credit','.creditcard',
    '.cruise','.cricket','.cruises','.dad','.dance','.data','.date','.dating','.day','.deal','.deals','.degree','.delivery',
    '.democrat','.dental','.dentist','.design','.dev','.diamonds','.diet','.digital','.direct',
    '.directory','.discount','.diy','.docs','.doctor','.dog','.domains','.dot','.download','.drive','.duck',
    '.earth','.eat','.eco','.education','.email','.energy','.engineer','.engineering','.enterprises','.equipment',
    '.esq','.estate','.events','.exchange','.expert','.exposed','.express','.fail','.faith','.family','.fan',
    '.fans','.farm','.fashion','.fast','.feedback','.film','.final','.finance','.financial','.fire','.fish',
    '.fishing','.fit','.fitness','.flights','.florist','.flowers','.fly','.foo','.food','.foodnetwork','.football','.forsale',
    '.forum','.foundation','.free','.frontdoor','.fun','.fund','.furniture','.futbol','.fyi','.gallery','.game',
    '.games','.garden','.gay','.gdn','.gift','.gifts','.gives','.glass','.global','.gold','.golf','.gop',
    '.graphics','.green','.gripe','.grocery','.group','.guide','.guitars','.guru','.hair','.hangout','.health',
    '.healthcare','.help','.here','.hiphop','.hiv','.hockey','.holdings','.holiday','.homegoods','.homes','.homesense',
    '.horse','.hospital','.host','.hosting','.hot','.hotels','.house','.how','.ice','.icu','.industries','.info',
    '.ing','.ink','.institute','.insurance','.insure','.international','.investments','.jewelry','.jobs','.joy','.kim','.kitchen',
    '.land','.latino','.law','.lawyer','.lease','.legal','.lgbt','.life','.lifeinsurance','.lighting','.like',
    '.limited','.limo','.link','.live','.living','.loan','.loans','.locker','.lol','.lotto','.love','.ltd','.luxury',
    '.makeup','.management','.map','.market','.marketing','.markets','.mba','.med','.media','.meet','.meme',
    '.memorial','.men','.menu','.mint','.mobi','.mobile','.mobily','.moe','.mom','.money','.monster','.mortgage','.motorcycles',
    '.mov','.movie','.museum','.music','.name','.navy','.network','.new','.news','.ngo','.ninja','.now','.ntt',
    '.observer','.off','.org','.one','.ong','.onl','.online','.ooo','.open','.organic','.origins','.page','.partners','.parts',
    '.party','.pay','.pet','.pharmacy','.phone','.photo','.photography','.photos','.physio','.pics','.pictures','.pid',
    '.pin','.pink','.pizza','.place','.plumbing','.plus','.poker','.porn','.post','.press','.prime','.pro',
    '.productions','.prof','.promo','.properties','.property','.protection','.pub','.qpon','.racing','.radio','.read',
    '.realestate','.realtor','.realty','.recipes','.red','.rehab','.reit','.rent','.rentals','.repair','.report',
    '.republican','.rest','.restaurant','.review','.reviews','.rich','.rip','.rocks','.rodeo','.room',
    '.rugby','.run','.safe','.sale','.save','.scholarships','.school','.science','.search','.secure','.security',
    '.select','.services','.sex','.sexy','.shoes','.shop','.shopping','.show','.showtime','.silk','.singles','.site','.ski','.skin',
    '.sky','.sling','.smile','.soccer','.social','.software','.solar','.solutions','.song','.space','.spot','.spreadbetting',
    '.storage','.store','.stream','.studio','.study','.style','.sucks','.supplies','.supply','.support','.surf','.surgery','.systems',
    '.talk','.tattoo','.tax','.taxi','.team','.tech','.technology','.tel','.tennis','.theater','.theatre','.tickets','.tips',
    '.tires','.today','.tools','.top','.tours','.town','.toys','.trade','.trading','.training','.travel','.travelersinsurance',
    '.trust','.tube','.tunes','.uconnect','.university','.vacations','.ventures','.vet','.video','.villas','.vip','.vision',
    '.vodka','.vote','.voting','.voyage','.wang','.watch','.watches','.weather','.webcam','.website','.wed','.wedding','.whoswho',
    '.wiki','.win','.wine','.winners','.work','.works','.world','.wow','.wtf','.xxx','.xyz','.yachts','.yoga','.you',
    '.zero','.zone','.ren','.shouji','.tushu','.wanggou','.weibo','.xihuan','.xin','.arte','.clinique','.luxe','.maison','.moi',
    '.rsvp','.sarl','.epost','.gmbh','.haus','.immobilien','.jetzt','.kaufen','.kinder','.reise','.reisen','.schule','.versicherung',
    '.desi','.shiksha','.casa','.immo','.moda','.voto','.bom','.passagens','.abogado','.futbol','.gratis','.hoteles',
    '.juegos','.ltda','.soy','.tienda','.uno','.viajes','.vuelos','.africa','.capetown','.durban','.joburg','.abudhabi',
    '.arab','.asia','.doha','.dubai','.krd','.kyoto','.nagoya','.okinawa','.osaka','.ryukyu','.taipei','.tatar','.tokyo',
    '.yokohama','.alsace','.amsterdam','.bar','.bcn','.barcelona','.bayern','.berlin','.brussels','.budapest','.bzh','.cat','.cologne',
    '.corsica','.cymru','.eus','.frl','.gal','.gent','.hamburg','.helsinki','.irish','.ist','.istanbul','.koeln','.london',
    '.madrid','.moscow','.nrw','.paris','.ruhr','.saarland','.scot','.stockholm','.swiss','.tirol','.vlaanderen','.wales',
    '.wien','.zuerich','.boston','.miami','.nyc','.quebec','.vegas','.kiwi','.melbourne','.sydney','.lat','.rio',
    '.aaa','.aarp','.abarth','.abb','.abbott','.abbvie','.abc','.accenture','.aco','.aeg','.aetna','.afl','.agakhan','.aig','.aigo','.airbus',
    '.airtel','.akdn','.alfaromeo','.alibaba','.alipay','.allfinanz','.allstate','.ally','.alstom','.americanexpress',
    '.amex','.amica','.android','.anz','.aol','.apple','.aquarelle','.aramco','.audi','.auspost','.axa',
    '.azure','.baidu','.bananarepublic','.barclaycard','.barclays','.basketball','.bauhaus','.bbc','.bbt','.bbva','.bcg','.bentley',
    '.bharti','.bing','.blanco','.bloomberg','.bms','.bmw','.bnl','.bnpparibas','.boehringer','.bond','.booking','.bosch',
    '.bostik','.bradesco','.bridgestone','.brother','.bugatti','.cal','.calvinklein','.canon','.capitalone','.caravan','.cartier','.cba','.cbn',
    '.cbre','.cbs','.cern','.cfa','.chanel','.chase','.chintai','.chrome','.chrysler','.cisco','.citadel','.citi',
    '.citic','.clubmed','.comcast','.commbank','.creditunion','.crown','.crs','.csc','.cuisinella','.dabur','.datsun','.dealer',
    '.dell','.deloitte','.delta','.dhl','.discover','.dish','.dnp','.dodge','.dunlop','.dupont','.dvag','.edeka','.emerck',
    '.epson','.ericsson','.erni','.esurance','.etisalat','.eurovision','.everbank','.extraspace','.fage','.fairwinds','.farmers','.fedex','.ferrari',
    '.ferrero','.fiat','.fidelity','.firestone','.firmdale','.flickr','.flir','.flsmidth','.ford','.fox','.fresenius','.forex',
    '.frogans','.frontier','.fujitsu','.fujixerox','.gallo','.gallup','.gap','.gbiz','.gea','.genting','.giving','.gle','.globo',
    '.gmail','.gmo','.gmx','.godaddy','.goldpoint','.goodyear','.goog','.google','.grainger','.guardian','.gucci','.hbo','.hdfc',
    '.hdfcbank','.hermes','.hisamitsu','.hitachi','.hkt','.honda','.honeywell','.hotmail','.hsbc','.hughes','.hyatt','.hyundai','.ibm',
    '.ieee','.ifm','.ikano','.imdb','.infiniti','.intel','.intuit','.ipiranga','.iselect','.itau','.itv','.iveco','.jaguar','.java','.jcb','.jcp',
    '.jeep','.jpmorgan','.juniper','.kddi','.kerryhotels','.kerrylogistics','.kerryproperties','.kfh','.kia','.kinder','.kindle','.komatsu','.kpmg',
    '.kred','.kuokgroup','.lacaixa','.ladbrokes','.lamborghini','.lancaster','.lancia','.lancome','.landrover','.lanxess','.lasalle','.latrobe','.lds',
    '.leclerc','.lego','.liaison','.lexus','.lidl','.lifestyle','.lilly','.lincoln','.linde','.lipsy','.lixil',
    '.locus','.lotte','.lpl','.lplfinancial','.lundbeck','.lupin','.macys','.maif','.man','.mango','.marriott',
    '.maserati','.mattel','.mckinsey','.metlife','.microsoft','.mini','.mit','.mitsubishi','.mlb','.mma','.monash','.mormon',
    '.moto','.movistar','.msd','.mtn','.mtr','.mutual','.nadex','.nationwide','.natura','.nba','.nec','.netflix',
    '.neustar','.newholland','.nexus','.nfl','.nhk','.nico','.nike','.nikon','.nissan','.nissay','.nokia','.northwesternmutual','.norton',
    '.nra','.ntt','.obi','.office','.omega','.oracle','.orange','.otsuka','.ovh','.panasonic','.pccw','.pfizer',
    '.philips','.piaget','.pictet','.ping','.pioneer','.play','.playstation','.pohl','.politie','.praxi','.prod',
    '.progressive','.pru','.prudential','.pwc','.quest','.qvc','.redstone','.reliance','.rexroth','.ricoh','.rmit',
    '.rocher','.rogers','.rwe','.safety','.sakura','.samsung','.sandvik','.sandvikcoromant','.sanofi','.sap','.saxo','.sbi',
    '.sbs','.sca','.scb','.schaeffler','.schmidt','.schwarz','.scjohnson','.scor','.seat','.sener',
    '.ses','.sew','.seven','.sfr','.seek','.shangrila','.sharp','.shaw','.shell','.shriram','.sina',
    '.sky','.skype','.smart','.sncf','.softbank','.sohu','.sony','.spiegel','.stada','.staples','.star',
    '.starhub','.statebank','.statefarm','.statoil','.stc','.stcgroup','.suzuki','.swatch','.swiftcover','.symantec','.taobao',
    '.target','.tatamotors','.tdk','.telecity','.telefonica','.temasek','.teva','.tiffany','.tjx','.toray',
    '.toshiba','.total','.toyota','.travelchannel','.travelers','.tui','.tvs','.ubs','.unicom','.uol',
    '.ups','.vanguard','.verisign','.vig','.viking','.virgin','.visa','.vista','.vistaprint','.vivo',
    '.volkswagen','.volvo','.walmart','.walter','.weatherchannel','.weber','.weir','.williamhill','.windows','.wme',
    '.wolterskluwer','.woodside','.wtc','.xbox','.xerox','.xfinity','.yahoo','.yamaxun','.yandex','.yodobashi','.youtube',
    '.zappos','.zara','.zip','.zippo','.onion','.test'
]

#---------------------------------------
# Script Classes
#---------------------------------------
class Settings(object):
    """ Load in saved settings file if available else set default values. """
    def __init__(self, settingsfile=None):
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")

                self.blpPermitDict = {}
        except:
            Parent.Log(ScriptName, "Could not load data from settingsfile: " + settingsfile)
            self.blpEnabled = False
            self.blpOnLinkDetected = "Links verboten! @{username} bitte frag vorher um Erlaubnis!"
            self.blpOnInfo = "BetterLinkProtection ist derzeit {onoffstate}."
            self.blpOnToggle = "BetterLinkProtection ist jetzt {onoffstate}."
            self.blpOnPermit = "@{username} hat jetzt {length} Sekunden, um einen Link zu posten."
            self.blpOnOffPermission = "Moderator"
            self.blpPermitPermission = "Moderator"
            self.blpLinkPermission = "Subscriber"
            self.blpDefaultPermitDuration = 30
            self.blpPermitDict = {}

    def Reload(self, jsondata):
        """ Reload settings from AnkhBot user interface by given json data. """
        self.__dict__ = json.loads(jsondata, encoding="utf-8")
        self.blpPermitDict = {}

    def Save(self, settingsfile):
        """ Save settings contained within to .json settings files. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")

#---------------------------------------
# Script Functions
#---------------------------------------
#---------------------------------------
# Chatbot Check Permission Function
#---------------------------------------
# Checks for minimum permission.
def MinimumPermission(data, permission, action):
    # Moderator or higher
    if permission == "Subscriber":
        ListPermission = ["Subscriber", "Moderator", "Editor", "Caster"]
    # Moderator or higher
    elif permission == "Moderator":
        ListPermission = ["Moderator", "Editor", "Caster"]
    # Editor or higher
    elif permission == "Editor":
        ListPermission = ["Editor", "Caster"]
    # Caster only
    elif permission == "Caster":
        ListPermission = ["Caster"]
    # defaults to caster only
    else:
        ListPermission = ["Caster"]

    Parent.Log(ScriptName, "{timestamp} Permission required '{minperm}' for action '{action}'".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),minperm=permission,action=action))
    Parent.Log(ScriptName, "{timestamp}   > Checking user '{user}' for one of permissions: {perms}".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),user=data.UserName,perms=ListPermission))
    Parent.Log(ScriptName, "{timestamp}   > Checking if '{minperm}' is in {perms}".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),minperm=permission,perms=ListPermission))

    for i in ListPermission:
        Parent.Log(ScriptName, "User has permission {perm}: {result}".format(perm=i,result=Parent.HasPermission(data.User, i, "")))
        if Parent.HasPermission(data.User, i, ""):
            return True

    return False

# Sets permit for chatter to be able to post a link in chat
# without getting purged
def Permit(person, permitlength):
    now = datetime.now()
    PermitEnd = now + timedelta(seconds=int(permitlength))
    ScriptSettings.blpPermitDict.update({person: str(PermitEnd)})
    Parent.SendStreamMessage(ScriptSettings.blpOnPermit.format(username=person, length=permitlength))

    return

# Checks whether the person posting the link has a permit to do so
# this is not needed if the person has blpLinkPermission
def PermitCheck(person):
    now = datetime.now()
    if person.lower() in ScriptSettings.blpPermitDict.keys():
        end_time = datetime.strptime(ScriptSettings.blpPermitDict[person], '%Y-%m-%d %H:%M:%S.%f')
        if now <= end_time:
            return True
        else:
            removePermit(person)
            return False # permit timed out
    return False # no permit at all

# removes a person from dict if included
def removePermit(person):
    if person.lower() in ScriptSettings.blpPermitDict.keys():
        ScriptSettings.blpPermitDict.pop(person, None)
    return
#---------------------------------------
# Chatbot Initialize Function
#---------------------------------------
def Init():

    # Load settings from file and verify
    global ScriptSettings
    ScriptSettings = Settings(SettingsFile)
    # ScriptSettings.Verify()

    global TimeElapsed
    TimeElapsed = timedelta(microseconds=-1)

    # Set initial tick timestamp
    global TimeStampTick
    TimeStampTick = time.time()

    # End of Init
    return

#---------------------------------------
# Chatbot Save Settings Function
#---------------------------------------
def ReloadSettings(jsondata):

    # Reload newly saved settings and verify
    ScriptSettings.Reload(jsondata)
    # ScriptSettings.Verify()

    # Set initial tick timestamp
    global TimeStampTick
    TimeStampTick = time.time()

    # End of ReloadSettings
    return

#---------------------------------------
#    Chatbot Script Unload Function
#---------------------------------------
def Unload():

    # End of Unload
    return

#---------------------------------------
# Chatbot Script Toggled Function
#---------------------------------------
def ScriptToggled(state):

    # Script is being disabled
    if not state:
        Unload()

    # End of ScriptToggled
    return

def ContainsTld(data):
    global LinkVerification
    global TldList
    tldMatch = re.search(LinkVerification, data.Message, re.IGNORECASE)

    if tldMatch and len([i for i in tldMatch.groups() if i in TldList]) > 0:
        Parent.Log(ScriptName, "{timestamp} Link in message is: {tld}".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),tld=tldMatch.group(0)))
        return True
    else:
        return False

# since we cannot delete a single message we need to purge for one 1s
def PurgeUser(data):
    Parent.SendStreamMessage("/timeout " + data.UserName + " 1s posting links without permission")
    Parent.SendStreamMessage(ScriptSettings.blpOnLinkDetected.format(username=data.UserName))
    return
#---------------------------------------
# Chatbot Execute Function
#---------------------------------------
# available commands
    #   - !blp on
    #   - !blp off
    #   - !blp info
    #   - !permit USERNAME [DURATION]
def Execute(data):

    # ========================
    # General Command Handling
    # ========================

    # info will be given all the time - regardless of the current script state
    # when asked for info only give info nothing else afterwards -> return
    if data.GetParam(0).lower() == '!blp' and data.GetParam(1).lower() == "info":
        # only if a user that is allowed to switch scripts state is asking for it
        if MinimumPermission(data, ScriptSettings.blpOnOffPermission, 'blpOnOffPermission - info (can be caused by Tick)'):
            if ScriptSettings.blpEnabled:
                Parent.SendStreamMessage(ScriptSettings.blpOnInfo.format(onoffstate="aktiv"))
            else:
                Parent.SendStreamMessage(ScriptSettings.blpOnInfo.format(onoffstate="nicht aktiv"))

        # end of info command
        return

    # blp is not running but someone wants to start it
    # when it's on - it's on -> return
    if not ScriptSettings.blpEnabled and MinimumPermission(data, ScriptSettings.blpOnOffPermission, 'blpOnOffPermission - on (can be caused by Tick)'):
        if data.GetParam(0).lower() == '!blp' and data.GetParam(1).lower() == 'on':
            ScriptSettings.blpEnabled = True
            ScriptToggled(ScriptSettings.blpEnabled)
            Parent.SendStreamMessage(ScriptSettings.blpOnToggle.format(onoffstate="aktiv"))

        # end of blp on command
        return

    # blp is running but someone wants to stop it
    # when it's off - it's off -> return
    if ScriptSettings.blpEnabled and MinimumPermission(data, ScriptSettings.blpOnOffPermission, 'blpOnOffPermission - off (can be caused by Tick)'):
        if data.GetParam(0).lower() == '!blp' and data.GetParam(1).lower() == 'off':
            ScriptSettings.blpEnabled = False
            ScriptToggled(ScriptSettings.blpEnabled)
            Parent.SendStreamMessage(ScriptSettings.blpOnToggle.format(onoffstate="nicht mehr aktiv"))

            # end of blp off command
            return

    # every command after HERE only is available when blp is running
    if not ScriptSettings.blpEnabled:
        return

    # ===============
    # PERMIT HANDLING
    # ===============

    # someone wants to give a permit to someone
    # when permit is set -> return
    if data.GetParam(0).lower() == '!permit':
        # check if caller is allowed to permit someone
        if MinimumPermission(data, ScriptSettings.blpPermitPermission, 'blpPermitPermission'):
            personToPermit = data.GetParam(1).lower()
            secondsToPermit = data.GetParam(2).lower()
            if not secondsToPermit:
             secondsToPermit = ScriptSettings.blpDefaultPermitDuration
            Permit(personToPermit, int(secondsToPermit))

        # end of permit command
        return

    # there is no link in the chat message
    if not ContainsTld(data):
        return

    # user is allowed to post link
    if MinimumPermission(data, ScriptSettings.blpLinkPermission, 'blpLinkPermission - "can post links check" (can be caused by Tick)'):
        return

    # from here on there IS a link in the chat message
    # do further checks from here on

    # not allowed and NO permits found (permit list is empty)
    if not ScriptSettings.blpPermitDict:
        PurgeUser(data)
        return

    # someone without minimum link posting permission sent a link BUT there are permits!
    if ScriptSettings.blpPermitDict:
        # check if user has permit
        if PermitCheck(data.UserName):
            # return if user HAS permit
            return
        else:
            PurgeUser(data)

        # end of permit check
        return

    # End of execute
    return

#---------------------------------------
# Chatbot Tick Function
#---------------------------------------
def Tick():

    if ScriptSettings.blpEnabled and (time.time() - TimeStampTick >= 1.0):

        # Set new timestamp for ~1 seconds tick
        global TimeStampTick
        TimeStampTick = time.time()

        # Add second to elapsed delta
        global TimeElapsed
        TimeElapsed = TimeElapsed + timedelta(seconds=1)

        # Save elapsed time to settings file every minute
        if TimeElapsed.total_seconds() % 60 == 0:
            SaveTimeDeltasToSettings()

    # End of Tick
    return
