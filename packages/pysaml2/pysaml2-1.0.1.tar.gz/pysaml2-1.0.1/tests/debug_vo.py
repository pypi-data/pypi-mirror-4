from saml2.client import Saml2Client
from saml2.config import SPConfig
from saml2.time_util import str_to_time, in_a_while

SESSION_INFO_PATTERN = {"ava":{}, "came from":"", "not_on_or_after":0,
                        "issuer":"", "session_id":-1}
__author__ = 'rolandh'

conf = SPConfig()
conf.load_file("server_conf")
sp = Saml2Client(conf)

vo_name = conf.vorg.keys()[0]
vo = conf.vorg[vo_name]

aas = vo.members_to_ask("abcdefgh")
print aas

def add_derek_info(sp):
    not_on_or_after = str_to_time(in_a_while(days=1))
    session_info = SESSION_INFO_PATTERN.copy()
    session_info["ava"] = {"givenName":["Derek"], "umuselin":["deje0001"]}
    session_info["issuer"] = "urn:mace:example.com:saml:idp"
    session_info["name_id"] = "abcdefgh"
    session_info["not_on_or_after"] = not_on_or_after
    # subject_id, entity_id, info, timestamp
    sp.users.add_information_about_person(session_info)

add_derek_info(sp)

aas = vo.members_to_ask("abcdefgh")
print aas

aas = vo.members_to_ask("0123456")
print aas
