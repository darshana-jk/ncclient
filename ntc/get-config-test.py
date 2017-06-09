#!/usr/bin/env python
import sys
import logging
from ncclient import manager
from xml.etree import ElementTree

log = logging.getLogger(__name__)

from ncclient.xml_ import *

#from pudb import set_trace; set_trace()

NS_IETF_INTERFACES = "urn:ietf:params:xml:ns:yang:ietf-interfaces"
def create_xpath_1(sel):

    if not isinstance(sel, basestring):
        raise Exception('select string should be string type')

    NC_ENV = "{%s}" % BASE_NS_1_0
    IETF_ENV = "{%s}" % NS_IETF_INTERFACES
    NSMAP = { 'ns0':BASE_NS_1_0, 'if':NS_IETF_INTERFACES }

    filter=etree.Element(NC_ENV+"filter",nsmap=NSMAP)
    filter.set("type", "xpath")
    filter.set("select", '/if:{0}'.format(sel))
    print(etree.tostring(filter, pretty_print=True))
    return filter


# get-config --source startup --filter-xpath /ietf-interfaces:interfaces/interface[name='UNI-1']/description
#<filter type="xpath" xmlns:if="urn:ietf:params:xml:ns:yang:ietf-interfaces" select="/if:interfaces/interface[name='UNI-1']/description"/>


# Template edit-config filter for ietf-interfaces/interface container.
edcfg_config_str = """
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>UNI-2</name>
                <enabled>false</enabled>
            </interface>
        </interfaces>
    </config>
"""

edit_config_ietf_interface_template = """
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>%s</name>
                <enabled>%s</enabled>
            </interface>
        </interfaces>
    </config>
"""

exec_conf_prefix = """
      <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
        <configure xmlns="http://www.cisco.com/nxos:1.0:vlan_mgr_cli">
          <__XML__MODE__exec_configure>
"""

exec_conf_postfix = """
          </__XML__MODE__exec_configure>
        </configure>
      </config>
"""

def _check_edit_config_response(rpc_obj, snippet_name):
    log.debug("RPCReply for %s is %s" % (snippet_name, rpc_obj.xml))
    #TODO: modify
    xml_str = rpc_obj.xml
    if "<nc:ok/>" in xml_str:
        log.info("%s successful" % snippet_name)
    else:
        log.error("Cannot successfully execute: %s" % snippet_name)

def enable_vlan(mgr, vlanid, vlanname):
    confstr = cmd_vlan_conf_snippet % (vlanid, vlanname) 
    confstr = exec_conf_prefix + confstr + exec_conf_postfix
    mgr.edit_config(target='running', config=confstr)

def perform_test(host, port, user, password, source):

    with manager.connect(host=host,
            port=port,
            username=user,
            password=password,
            timeout=10,
            hostkey_verify=False) as conn:

        ## lock test
        #with conn.locked("startup"):
        #    print 'Locked running'

        ## get opetation
        #result = conn.get()


        ## get-config opetation for candidate.
        #result=conn.get_config(source)
        #print '================ Get config data xml ==============='
        #print result.data_xml
        #print '================ Get config data xml ==============='
        #return 0

        #print 'Showing \'system\' hierarchy ...'
        #output = result.xpath('data/configuration/system')[0]
        #print to_xml(output)


        # get-config with filter to pass to get_config
        #root_filter = create_xpath_1("interfaces")
        #root_filter = create_xpath_1("interfaces/interface[name='UNI-1']")
        #root_filter = create_xpath_1("interfaces/interface[name='UNI-1']/description")
        #filtered_result = conn.get_config(source, filter=root_filter)
        #print(etree.tostring(filtered_result, pretty_print=True))
        #print filtered_result.data_xml


        ## edit-config with filter.
        confstr = edit_config_ietf_interface_template % ("UNI-1","false")
        #print confstr
        rpc_obj = conn.edit_config(target='running', config=confstr, error_option = "rollback-on-error")
        _check_edit_config_response(rpc_obj, "confstr")

        return 0


        print 'Configured Interfaces...'
        print '%-15s %-30s' % ('Name', 'Description')
        print '-' * 40
        interfaces = result.xpath('data/configuration/interfaces/interface')
        for i in interfaces:
            if i.tag == 'interface':
                interface = i.xpath('name')[0].text
                try:
                    description = i.xpath('description')[0].text
                except IndexError:
                    description = None
                print '%-15s %-30s' % (interface, description)
                units = i.xpath('unit')
                for u in units:
                    unit = u.xpath('name')[0].text
                    try:
                        u_desc = u.xpath('description')[0].text 
                    except IndexError:
                        u_desc = None
                    print '   %-12s %-30s' % (unit, u_desc)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    perform_test('127.0.0.1', 830, 'darshana', 'salmal10', 'startup')
