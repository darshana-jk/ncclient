#!/usr/bin/env python
import sys
import logging
from ncclient.operations.rpc import *
from ncclient.operations.edit import *
from ncclient import manager
import ncclient.manager
import ncclient.transport
from ncclient.xml_ import *
from ncclient.operations import RaiseMode
from xml.etree import ElementTree
from lxml import etree
from ncclient.operations.errors import MissingCapabilityError
import copy

start_time = "1990-12-31T23:59:60Z"
stop_time = "1996-12-19T16:39:57-08:00"

# check this class:
#class TestSubscribe(unittest.TestCase):

#>>> from lxml import etree https://stackoverflow.com/questions/28054444/lxml-xml-document-with-multiple-namespaces
#>>> SOAPENV_NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope"
#>>> SOAPENV = "{%s}" % SOAPENV_NAMESPACE
#>>> ns0_NAMESPACE = "http://xmlns.CLT.com/consume/ENTBUS"
#>>> ns0 = "{%s}" % ns0_NAMESPACE
#>>> ns1_NAMESPACE = "http://xmlns.CLT.com/Core/ENTBUS"
#>>> ns1 = "{%s}" % ns1_NAMESPACE
#>>> ns2_NAMESPACE = "http://xmlns.CLT.com/output/EBO"
#>>> ns2 = "{%s}" % ns2_NAMESPACE
#>>> NSMAP = {'SoapEnv' : SOAPENV_NAMESPACE,'ns0':ns0_NAMESPACE,'ns1':ns1_NAMESPACE,'ns2':ns2_NAMESPACE}
#>>> envelope = etree.Element(SOAPENV + "Envelope", nsmap=NSMAP)
#>>> ConsumptionRequestENTBUS=etree.SubElement(envelope, ns0 + "ConsumptionRequestENTBUS", nsmap=NSMAP)
#>>> ENTBUS=etree.SubElement(ConsumptionRequestENTBUS, ns1 + "ENTBUS", nsmap=NSMAP)
#>>> ENTBUSHeader=etree.SubElement(ENTBUS, ns1 + "ENTBUSHeader", nsmap=NSMAP)
#>>> ENTBUSDetail=etree.SubElement(ENTBUSHeader, ns2 + "ENTBUSDetail", nsmap=NSMAP)
#>>> print(etree.tostring(envelope, pretty_print=True))
#<SoapEnv:Envelope xmlns:ns0="http://xmlns.CLT.com/consume/ENTBUS" xmlns:ns1="http://xmlns.CLT.com/Core/ENTBUS" xmlns:ns2="h
#ttp://xmlns.CLT.com/output/EBO" xmlns:SoapEnv="http://schemas.xmlsoap.org/soap/envelope">
#  <ns0:ConsumptionRequestENTBUS>
#    <ns1:ENTBUS>
#      <ns1:ENTBUSHeader>
#        <ns2:ENTBUSDetail/>
#      </ns1:ENTBUSHeader>
#    </ns1:ENTBUS>
#  </ns0:ConsumptionRequestENTBUS>
#</SoapEnv:Envelope>


#<?xml version="1.0" encoding="UTF-8"?>
#<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="82">
#   <get-config>
#      <source>
#         <running />
#      </source>
#      <filter xmlns:if="urn:ietf:params:xml:ns:yang:ietf-interfaces" type="xpath" select="/if:interfaces" />
#   </get-config>
#</rpc>
#<ns0:filter xmlns:ns0="urn:ietf:params:xml:ns:netconf:base:1.0" type="xpath">
#    <ns0:ietf-interfaces>
#        <ns0:interfaces />
#    </ns0:ietf-interfaces>
#</ns0:filter>

xml_get_config_reply_uni1 ="""
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
   <interface>
      <name>UNI-1</name>
      <description>VDSL Port 1</description>
      <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:fastdsl</type>
      <enabled>true</enabled>
      <line xmlns="urn:bbf:yang:bbf-fastdsl">
         <configured-mode>mode-vdsl</configured-mode>
         <line xmlns="urn:bbf:yang:bbf-vdsl">
            <test-mode>
               <power-management-state-forced>4</power-management-state-forced>
               <loop-diagnostics-mode-forced>2</loop-diagnostics-mode-forced>
               <auto-mode-cold-start-forced>0</auto-mode-cold-start-forced>
            </test-mode>
            <xtu-c>
               <update-test-ne>0</update-test-ne>
            </xtu-c>
            <xtu-r>
               <update-test-fe>0</update-test-fe>
            </xtu-r>
            <channel>
               <downstream-data-rate-profile>datarate_profile_ds</downstream-data-rate-profile>
               <upstream-data-rate-profile>datarate_profile_us</upstream-data-rate-profile>
               <impulse-noise-protection-delay-profile>noise_protection_profile</impulse-noise-protection-delay-profile>
            </channel>
            <line-spectrum-profile>spectrum_profile</line-spectrum-profile>
            <upstream-power-back-off-profile>upbo_profile</upstream-power-back-off-profile>
            <downstream-power-back-off-profile>dpbo_profile</downstream-power-back-off-profile>
            <radio-frequency-interference-profile>rf_interference_profile</radio-frequency-interference-profile>
            <noise-margin-profile>noise_profile</noise-margin-profile>
         </line>
      </line>
   </interface>
</interfaces>"""

edcfg_config_str = """
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>UNI1</name>
                <enabled>true</enabled>
            </interface>
        </interfaces>
    </config>
"""

NS_IETF_INTERFACES = "urn:ietf:params:xml:ns:yang:ietf-interfaces"

def create_xpath_1():
    NC_ENV = "{%s}" % BASE_NS_1_0
    IETF_ENV = "{%s}" % NS_IETF_INTERFACES
    NSMAP = { 'ns0':BASE_NS_1_0, 'if':NS_IETF_INTERFACES }

    filter=etree.Element(NC_ENV+"filter",nsmap=NSMAP)
    filter.set("type", "xpath")
    filter.set("select", "/if:interfaces")
    print(etree.tostring(filter, pretty_print=True))
    return filter

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    node = new_ele_ns("ietf-interfaces", "urn:ietf:params:xml:ns:yang:ietf-interfaces")
    xml = ElementTree.tostring(node)
    print xml

    # specify filter to pass to get_config
    root_filter = new_ele('filter')
    ietf_interfaces = sub_ele(root_filter, 'ietf-interfaces', ns="urn:ietf:params:xml:ns:yang:ietf-interfaces")
    xml = ElementTree.tostring(root_filter)
    print xml

    root = new_ele('config')
    configuration = sub_ele(root, 'configuration')
    system = sub_ele(configuration, 'system')
    location = sub_ele(system, 'location')
    sub_ele(location, 'building').text = "Main Campus, A"
    sub_ele(location, 'floor').text = "5"
    sub_ele(location, 'rack').text = "27"
    xml = ElementTree.tostring(root)
    print xml


    create_xpath_1()

    obj_get_config_reply_uni1 = RPCReply(xml_get_config_reply_uni1)
    obj_get_config_reply_uni1.parse()
    if not obj_get_config_reply_uni1.ok:
        raise ValueError("Errors parsing sample reply xml for get-config")
    #print obj_get_config_reply_uni1.xml

    obj_get_config_reply_uni1 = to_ele(xml_get_config_reply_uni1)
    #print(etree.tostring(obj_get_config_reply_uni1, pretty_print=True))

    node = new_ele("edit-config")
    node.append(validated_element(edcfg_config_str, ("config", qualify("config"))))
    print(etree.tostring(node, pretty_print=True))



