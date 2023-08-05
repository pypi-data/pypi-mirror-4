#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009, MARIMORE LLC Tokyo, Japan.
# Contributed by 
#       Iqbal Abdullah <iqbal@marimore.co.jp>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
#   *   Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#   *   Redistributions in binary form must reproduce the above copyright notice, 
#       this list of conditions and the following disclaimer in the documentation 
#       and/or other materials provided with the distribution.
#   *   Neither the name of the MARIMORE LLC nor the names of its contributors 
#       may be used to endorse or promote products derived from this software 
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Verifying utilities for JP mobile 
"""

__author__      = "Iqbal Abdullah <iqbal@marimore.co.jp>"
__date__        = "$LastChangedDate$"
__version__     = "$LastChangedRevision$"

import pickle

# Use iplib from http://erlug.linux.it/~da/soft/iplib/
from iplib import CIDR

from mamopublic.jp.mobemail import get_mobile_email_domains

IP_DATA_FILE = "../../data/ip.dat"

CONST_HTTP_META_CARRIER    = "HTTP_X_MOGO_CARRIER"
CONST_HTTP_META_BROWSER    = "HTTP_X_MOGO_BROWSER"
CONST_HTTP_META_LOCALE     = "HTTP_X_MOGO_LOCALE"

CONST_SESSION_DATA         = "MOBILE_SESSION"

CONST_IPHONE_UID           = "IPHONE_FIXED"
CONST_ANDROID_UID          = "ANDROID_FIXED"

def is_mobile_ip(ip):
    """
    Checks if an IP is coming from a mobile gateway.

    Possible carrier names are:
        1. DOCOMO
        2. EZWEB
        3. SOFTBANK
        4. WILLCOM

    Possible browsers:
        1. MOBILE
        2. PC

    @type ip: string
    @param ip: The IP address of a client
    @rtype: tuple
    @return: A four element tuple with the first element being a boolean True if 
             the IP is from a mobile gateway, the second is a string with
             the carrier name, the third a string with the browser type 
             and the fourth will be a string with the locale info. 
             If ip is not a mobile ip, all string will be set to None.
             i.e (True, 'DOCOMO', 'MOBILE', 'JP'), (False, None, None, None) or
             (True, 'SOFTBANK', 'PC', 'MY')
    """
    try:
        fd = open(mogodef.MOGO_IP_DATA_FILE, 'rb')
        ipdata_list = pickle.load(fd)
        fd.close()

        for ipdata in ipdata_list:
            iprange = ipdata['ip']
            locale  = ipdata['locale']
            browser = ipdata['browser']
            carrier = ipdata['carrier']

            cidr = CIDR(iprange)
            if cidr.is_valid_ip(ip):
                return (True, carrier, browser, locale)

    except Exception, e:
        pass

    return (False, None, None, None)

def is_mobile_ua(ua):
    """
    Checks if an agent is a mobile.

    Possible carrier names are:
        1. DOCOMO
        2. EZWEB
        3. SOFTBANK
        4. WILLCOM

    Possible browsers:
        1. MOBILE
        2. PC

    @type ua: string
    @param ua: The IP address of a client
    @rtype: tuple
    @return: A four element tuple with the first element being a boolean True if 
             the IP is from a mobile gateway, the second is a string with
             the carrier name, the third a string with the browser type 
             and the fourth will be a string with the locale info. 
             If ip is not a mobile ip, all string will be set to None.
             i.e (True, 'DOCOMO', 'MOBILE', 'JP'), (False, None, None, None) or
             (True, 'SOFTBANK', 'PC', 'MY')
    """

    _ua_dict = {
        "DoCoMo/"       :  "DOCOMO",
        "Docomo"        :  "DOCOMO",
        "HT-03A"        :  "DOCOMO",
        "SO-01B"        :  "DOCOMO",
        "UP.Browser"    :  "EZWEB",
        "KDDI-"         :  "EZWEB",
        "J-PHONE"       :  "SOFTBANK",
        "Vodafone"      :  "SOFTBANK",
        "MOT-"          :  "SOFTBANK",
        "SoftBank"      :  "SOFTBANK",
        "iPhone"        :  "SOFTBANK",
        "HTC"           :  "SOFTBANK",
        "MOTEMULATOR"   :  "SOFTBANK",
        "Semulator"     :  "SOFTBANK",
        "Vemulator"     :  "SOFTBANK",
        "PDXGW"         :  "WILLCOM",
        "DDIPOCKET"     :  "WILLCOM",
        "WILLCOM"       :  "WILLCOM",
    }

    for l in _ua_dict.keys():
        if ua.find(l) > -1:
            return (True, _ua_dict[l], "MOBILE", "JP")

    return (False, None, None, None)


def is_mobile_email_domain(domain):
    """
    Checks if a domain name is a valid keitai email domain

    @type domain: string
    @param domain: The domain name
    @rtype: boolean
    @return: True if domain is a valid keitai email domain, False otherwise
    """

    dictionary_of_domains = get_mobile_email_domains()
    for carrier in dictionary_of_domains.keys():
        domain_list = dictionary_of_domains[carrier]
        if domain in domain_list:
            return True

    return False


def is_mobile_phone_number(mn):
    """
    Verifies that a number is a valid mobile phone number

    @type domain: string
    @param domain: The number, without hyphens
    @rtype: boolean
    @return: True if number is a valid number, False otherwise
    """

    _LENGTH = 11
    _VALID_PREFIXES = ( "090", "080", "070", )

    if len(mn) != _LENGTH:
        return False

    if mn[:3] in _VALID_PREFIXES:
        return True

    return False


if __name__ == '__main__':

    # TEST

    print is_mobile_ip("210.153.84.16")
    print is_mobile_ip("122.212.11.154")
    print is_mobile_ip("123.108.237.29")
    print is_mobile_ip("210.153.84.1")
    print is_mobile_ip("210.136.161.98")
    print is_mobile_ip("210.153.86.16")
    print is_mobile_ip("210.153.86.13")
    print is_mobile_ip("210.153.84.11")
    print is_mobile_ip("121.111.231.74")

    ua = "SoftBank/1.0/911T/TJ002/SN354018016346748 Browser/NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1"
    print is_mobile_ua(ua)
    ua = "DoCoMo/2.0 SH901iS(c100;TB;W24H12)"
    print is_mobile_ua(ua)
    ua = "Vodafone/1.0/V905SH/SHJ002 Browser/VF-NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1"
    print is_mobile_ua(ua)
    ua = "KDDI-TS3M UP.Browser/6.2_7.2.7.1.K.2.225 (GUI) MMP/2.0"
    print is_mobile_ua(ua)

    print 'gmail.com is mobile', is_mobile_email_domain('gmail.com')
    print 'ezweb.ne.jp is mobile', is_mobile_email_domain('ezweb.ne.jp')
    print 'emnet.ne.jp is mobile', is_mobile_email_domain('emnet.ne.jp')
    print 'docomo.ne.jp is mobile', is_mobile_email_domain('docomo.ne.jp')
    print 'yahoo.com is mobile', is_mobile_email_domain('yahoo.com')

    print "N", is_mobile_phone_number('09012345678')
    print "N", is_mobile_phone_number('08012345678')
    print "N", is_mobile_phone_number('07012345678')
    print "N", is_mobile_phone_number('03321456434')
    print "N", is_mobile_phone_number('0701234567')
    print "N", is_mobile_phone_number('090-3214-7865')
    print "N", is_mobile_phone_number('0903214786556')
