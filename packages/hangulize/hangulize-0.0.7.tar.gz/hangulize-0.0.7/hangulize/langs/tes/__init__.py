# -*- coding: utf-8 -*-
from hangulize import *


class German(Language):
    """For conversion of abstract German to more phonetic representation."""

    __iso639__ = {1: 'de', 2: 'tes', 3: 'tes'}
    
    vowels = u'ieǣāouyøɪɛæaɔʊʏœəɐˈˌ' + u'̃'
    lv = u'ieǣāouyø' #'long' vowels
    plv = u'iː', u'eː', u'ɛː', u'aː', u'oː', u'uː', u'yː', u'øː' # stressed 'long' vowels
    rlv = u'ieɛaouyø' #unstressed 'long' vowels
    sv = u'ɪɛæaɔʊʏœ' #'short' vowels
    nv = u'ɛ̃', u'ã', u'ɔ̃', u'œ̃' #nasalized vowels
    nhv = u'eǣāoøɛæaɔ' #non-high vowels
    cs = u'mnpbtdkɡFʦʧʣʤfvszʃʒjxχrʁhʋlçŋw'
    stp = u'pbtdkɡ' #stops
    afr = u'Fʦʧʣʤ' #affricates
    fri = u'fvszʃʒjxχ' #fricatives
    obs = stp + afr + fri #obstruents
    obsj = stp + afr + u'fvszʃʒxχ' #obstruents minus j
    osl = u'pbɡkfvʃ' #forms onset cluster with l
    osr = osl + u'td' #forms onset cluster with r
    osw = u'kʦʃ' #forms onset cluster with ʋ
    oss = u'pk' #forms onset cluster with s
    son = u'lmnŋrʁ' #sonants
    vop = u'bdɡʣʤvzʒjʋ' #voiced (or lenis) obstruent
    vlp = u'ptkʦʧfsʃçf' #voiceless (or fortis) obstruent
    l = u'ieǣāouyøɪɛæaɔʊʏəmnpbtdkɡFʦʧʣʤfvszʃʒjxχrʁhʋlçŋw' + u'̯' #letters
    
    notation = Notation([
        (u'p͜f', u'F'), #represent phonemic affricates by unitary symbols
        (u't͜s', u'ʦ'),
        (u't͜ʃ', u'ʧ'),
        (u'd͜z', u'ʣ'),
        (u'd͜ʒ', u'ʤ'),
        (u'{<obsj>|l|m|n}r{~@}', u'ər'), #identify syllabic consonants
        (u'{<obsj>|m|n}l{~@}', u'əl'),
        (u'{<obsj>|n}m{~@}', u'əm'),
        (u'{<obsj>|m}n{~@}', u'ən'),
        (u'{@}ʃ{pl@|pr@|tr@}', u'·ʃ'), #syllabify ʃ- onset
        (u'{@<cs>}ʃ{pl@|pr@|tr@}', u'·ʃ'),
        (u'{@<cs><cs>}ʃ{pl@|pr@|tr@}', u'·ʃ'),
        (u'{@<cs><cs><cs>}ʃ{pl@|pr@|tr@}', u'·ʃ'),
        (u'{@<cs><cs><cs><cs>}ʃ{pl@|pr@|tr@}', u'·ʃ'),
        (u'{@}ʃ{p@|t@}', u'·ʃ'),
        (u'{@<cs>}ʃ{p@|t@}', u'·ʃ'),
        (u'{@<cs><cs>}ʃ{p@|t@}', u'·ʃ'),
        (u'{@<cs><cs><cs>}ʃ{p@|t@}', u'·ʃ'),
        (u'{@<cs><cs><cs><cs>}ʃ{p@|t@}', u'·ʃ'),
        (u'{@}<osr>{r@}', u'·<osr>'), #syllabify onsets with r
        (u'{@<cs>}<osr>{r@}', u'·<osr>'),
        (u'{@<cs><cs>}<osr>{r@}', u'·<osr>'),
        (u'{@<cs><cs><cs>}<osr>{r@}', u'·<osr>'),
        (u'{@<cs><cs><cs><cs>}<osr>{r@}', u'·<osr>'),
        (u'{@}<osl>{l@}', u'·<osl>'), #syllabify onsets with l
        (u'{@<cs>}<osl>{l@}', u'·<osl>'),
        (u'{@<cs><cs>}<osl>{l@}', u'·<osl>'),
        (u'{@<cs><cs><cs>}<osl>{l@}', u'·<osl>'),
        (u'{@<cs><cs><cs><cs>}<osl>{l@}', u'·<osl>'),
        (u'{@}<osw>{ʋ@}', u'·<osw>'), #syllabify onsets with ʋ
        (u'{@<cs>}<osw>{ʋ@}', u'·<osw>'),
        (u'{@<cs><cs>}<osw>{ʋ@}', u'·<osw>'),
        (u'{@<cs><cs><cs>}<osw>{ʋ@}', u'·<osw>'),
        (u'{@<cs><cs><cs><cs>}<osw>{ʋ@}', u'·<osw>'),
        (u'{@}<oss>{s@}', u'·<oss>'), #syllabify onsets with s
        (u'{@<cs>}<oss>{s@}', u'·<oss>'),
        (u'{@<cs><cs>}<oss>{s@}', u'·<oss>'),
        (u'{@<cs><cs><cs>}<oss>{s@}', u'·<oss>'),
        (u'{@<cs><cs><cs><cs>}<oss>{s@}', u'·<oss>'),
        (u'{@}ɡ{w@}', u'·ɡ'), #syllabify ɡw onsets
        (u'{@<cs>}ɡ{w@}', u'·ɡ'),
        (u'{@<cs><cs>}ɡ{w@}', u'·ɡ'),
        (u'{@<cs><cs><cs>}ɡ{w@}', u'·ɡ'),
        (u'{@<cs><cs><cs><cs>}ɡ{w@}', u'·ɡ'),
        (u'@(<cs>*?)<cs>{@}', ur'\1\2·\4'), #syllabify simple onsets
        (u'{<obsj>|l|m|n|r}ə', u''), #remove temporary ə for syllabic consonants
        (u'{~@}i{<nhv>|u|ʊ}', u'i̯'), #identify glides
        (u'{~@}i{ˈ<nhv>|ˌ<nhv>|ˈu|ˌu|ˈʊ|ˌʊ}', u'i̯'),
        (u'{~@}u{<nhv>|i|ɪ}', u'u̯'),
        (u'{~@}u{ˈ<nhv>|ˌ<nhv>|ˈi|ˌi|ˈɪ|ˌɪ}', u'u̯'),
        (u'<lv>{@}', u'<lv>·'),
        (u'<sv>{@}', u'<sv>·'),
        (u'<nv>{@}', u'<nv>·'),
        (u'{<nhv>|ʊ}·i', u'i'), #identify diphthongs
        (u'{<nhv>}·u', u'u'),
        (u'ɔ·y', u'ɔy'),
        (u'{i|y|u}·ə', u'ə'),
        (u'{ˈ|ˌ}<lv>', u'<plv>'), #vowels
        (u'{ˈ|ˌ}<nv>', u'<nv>ː'),
        (u'<lv>{~ː}', u'<rlv>'),
        (u'{~ˈ|ˌ}ɛ$', u'ə'), #identify schwas
        (u'{~ˈ|ˌ}ɛ{-}', u'ə'),
        (u'{~ˈ|ˌ}ɛ{·<cs>@}', u'ə'),
        (u'{~ˈ|ˌ}ɛ{·<osl>l@}', u'ə'),
        (u'{~ˈ|ˌ}ɛ{·<osr>r@}', u'ə'),
        (u'{~ˈ|ˌ}ɛ{·<osw>ʋ@}', u'ə'),
        (u'{~ˈ|ˌ}ɛ{·ʃ}', u'ə'),
        (u'{~ˈ|ˌ}ɛ{<son>}', u'ə'),
        (u'{~ˈ|ˌ}ɛz{~<cs>}', u'əz'),
        (u'æ', u'ɛ'), #replace æ
        (u'mm', u'm'), #simplify double cons within lexeme
        (u'nn', u'n'),
        (u'pp', u'p'),
        (u'bb', u'b'),
        (u'tt', u't'),
        (u'dd', u'd'),
        (u'kk', u'k'),
        (u'ɡɡ', u'ɡ'),
        (u'ff', u'f'),
        (u'zz', u's'),
        (u'rr', u'r'),
        (u'll', u'l'),
        (u'm·m', u'·m'),
        (u'n·n', u'·n'),
        (u'p·p', u'·p'),
        (u'b·b', u'·b'),
        (u't·t', u'·t'),
        (u'd·d', u'·d'),
        (u'k·k', u'·k'),
        (u'ɡ·ɡ', u'·ɡ'),
        (u'f·f', u'·f'),
        (u'z·z', u'·s'),
        (u'r·r', u'·r'),
        (u'l·l', u'·l'),
        (u'nɡ{~@}', u'ŋ'), #ŋ part one
        (u'nk', u'ŋk'),
        (u'ɪɡ$', u'ɪx'), #-ɪɡ as -ɪç
        (u'ɪɡ-', u'ɪx-'),
        (u'<vop>$', u'<vlp>'), #coda devoicing or fortition
        (u'b{·<son>}', u'B'), #exceptions
        (u'd{·<son>}', u'D'),
        (u'ɡ{·<son>}', u'G'),
        (u'<vop>{·|-}', u'<vlp>'),
        (u'B', u'b'),
        (u'D', u'd'),
        (u'G', u'ɡ'),
        (u'<vop>{<vlp>}', u'<vlp>'), #regressive devoicing
        (u'<vop>{<vlp>}', u'<vlp>'),
        (u'<vop>{<vlp>}', u'<vlp>'),
        (u'ʋ', u'v'), #replace ʋ
        (u'w', u'u̯'), #replace w
        (u'{a|ɔ|ʊ|u}x', u'χ'), #ach-Laut and ich-Laut
        (u'{a|ɔ|ʊ|u}·x', u'·χ'),
        (u'{aː|oː|uː}x', u'χ'),
        (u'{aː|oː|uː}·x', u'·χ'),
        (u'x', u'ç'),
        (u'χ', u'x'),
        (u'-', u'·'),
        (u'·{<l>*ˈ}', u'·`'), #move primary accent mark to left edge of syllable
        (u'^ˈ', u'`'),
        (u'^<l>{<l>*ˈ}', u'`<l>'),
        (u'ˈ', u''),
        (u'`', u'ˈ'),
        (u'·{<l>*ˌ}', u'·`'), #move secondary accent mark to left edge of syllable
        (u'^ˌ', u'`'),
        (u'^<l>{<l>*ˌ}', u'`<l>'),
        (u'ˌ', u''),
        (u'`', u'ˌ'),
        (u'n·ɡ{~<rlv>}', u'ŋ·'), #ŋ part two
        (u'n·k{~<rlv>}', u'ŋ·k'),
        (u'n{·ˈɡ|·ˈk|·ˌɡ|·ˌk}', u'ŋ'),
        (u'{<obsj>|m|n|ŋ}l{~@}', u'l̩'), #syllabic l
        (u'{<obsj>|m|n|ŋ}əl', u'l̩'),
        (u'{<obsj>}m{~@}', u'm̩'), #syllabic m
        (u'{<obsj>}əm', u'm̩'),
        (u'{<obsj>}n{~@}', u'n̩'), #syllabic n
        (u'{<obsj>}ən', u'n̩'),
        (u'ər', u'ɐ'), #r vocalization
        (u'{<obs>}r{~@}', u'ɐ'),
        (u'{ː}r', u'ɐ̯'),
        (u'r', u'ʁ'),
        (u'·ˈ<vowels>{~̯}', u'·ˈʔ<vowels>'), #insert ʔ for vowel-initial medial syllables
        (u'·ˌ<vowels>{~̯}', u'·ˌʔ<vowels>'),
        (u'F', u'p͜f'), #restore p͜f
        (u'{<nhv>}i', u'ɪ̯'), #diphthongs
        (u'{<nhv>}u', u'ʊ̯'),
        (u'ɔy', u'ɔʏ̯'),
        (u'ˌ{<l>*·ˈ}', u''), #remove secondary stress from syllable adjacent to one with primary stress
        (u'(ˈ<l>+·)ˌ', ur'\1'),
        (u'·', u'.'),
    ])

    def normalize(self, string):
        additional = {
            u'ǣ': u'ǣ', u'ā': u'ā', u'ø': u'ø', u'I': u'ɪ', u'E': u'ɛ',
            u'æ': u'æ', u'O': u'ɔ', u'U': u'ʊ', u'Y': u'ʏ', u'œ': u'œ',
            u'~': u'̃', u'g': u'ɡ', u'_': u'͜', u'c': u'ʦ', u'C': u'ʧ',
            u'ʣ': u'ʣ', u'ʤ': u'ʤ', u'S': u'ʃ', u'Z': u'ʒ', u'X': u'χ',
            u'V': u'ʋ', u"'": u'ˈ', u'"': u'ˌ', u'|': u'|', u'F': u'F',
            u'@': u'ə', u'̯': u'̯'
        }
        return normalize_roman(string, additional)


__lang__ = German
