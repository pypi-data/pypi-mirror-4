#
# mkb/esxmon.py
#


#Once ESXi comes back up open the vSphere client as you need to enable OEM CIM providers.
#
#   1. Choose the Configuration tab on the host
#   2. Click Advanced Settings under the Software section
#   3. In the dialog that appears click "UserVars" on the left
#   4. Change the value of CIMOEMProvidersEnabled to 1
#   5. Click OK
#From here if you have access to the ESXi console hit  and select Restart Management Agents. Otherwise you will need to reboot the host again.

import os, string, subprocess, fnmatch, platform
import posixpath
import urllib, urllib2

from datetime import datetime, timedelta

#import paramiko
import pywbem

from archiver import *
import cron

test_class='VMware_Controller'
#test_class='CIM_Memory' # to simulate failure

default_class_list=[
    'CIM_Sensor', 
    'CIM_PowerSupply',
    'CIM_Chassis', 
    'CIM_ComputerSystem',
    'CIM_NumericSensor',
    'CIM_Memory',
    'CIM_PhysicalMemory',
    'CIM_Processor', 
    'CIM_LogRecord',
    'CIM_RecordLog',
    'CIM_EthernetPort',

    'CIM_SoftwareIdentity', 
    
    'OMC_SMASHFirmwareIdentity',
    'OMC_DiscreteSensor', 
    'OMC_Fan', 
    'OMC_PowerSupply',

    'OMC_RawIpmiSensor',
    'OMC_RawIpmiEntity',
    
    'VMware_StorageExtent',
    'VMware_Controller',
    'VMware_StorageVolume',
    'VMware_Battery',
    'VMware_SASSATAPort',
]

ExitUnknown = -1
ExitOK = 0
ExitWarning = 1
ExitCritical = 2

class ESXMon(Archiver):
    
    name='esxmon'

    types=dict( mon='mon')
    
    NS = 'root/cimv2'


    interpret=dict( HealthState = {
                        0  : ExitOK,        # Unknown
                        5  : ExitOK,        # OK
                        10 : ExitWarning,    # Degraded
                        15 : ExitWarning,    # Minor
                        20 : ExitCritical,    # Major
                        25 : ExitCritical,    # Critical
                        30 : ExitCritical,    # Non-recoverable Error
                    },
                    OperationalStatus = {
                        0  : ExitOK,            # Unknown
                        1  : ExitCritical,      # Other
                        2  : ExitOK,            # OK
                        3  : ExitWarning,       # Degraded
                        4  : ExitWarning,       # Stressed
                        5  : ExitWarning,       # Predictive Failure
                        6  : ExitCritical,      # Error
                        7  : ExitCritical,      # Non-Recoverable Error
                        8  : ExitWarning,       # Starting
                        9  : ExitWarning,       # Stopping
                        10 : ExitCritical,      # Stopped
                        11 : ExitOK,            # In Service
                        12 : ExitWarning,       # No Contact
                        13 : ExitCritical,      # Lost Communication
                        14 : ExitCritical,      # Aborted
                        15 : ExitOK,            # Dormant
                        16 : ExitCritical,      # Supporting Entity in Error
                        17 : ExitOK,            # Completed
                        18 : ExitOK,            # Power Mode
                        19 : ExitOK,            # DMTF Reserved
                        20 : ExitOK             # Vendor Reserved
                    })

    # -----------------------------------------------------------------------
    def __init__(self):
        Archiver.__init__(self)
        
        self.url=None
        self.login=None
        self.password=None

        self.class_list=[]
        self.class_include=[]
        self.class_exclude=[]
        self.property_exclude=[]
        
        self.classData = {} # Dictionary to cache class metadata
        
        self.verbose=True
        self.friendly_value=False
        
    # -----------------------------------------------------------------------
    def load(self, job, manager):
        
        log=manager.log
        now=manager.now
        
        errors, warnings, extra={}, {}, ''

        for name in ('url', 'login', 'password'):
            value=job.get(name, None)
            if not value:
                errors[name]='option mandatory'
            else:
                setattr(self, name, value)
                if name=='password':
                    self.register_password(value)

        self.verbose=boolean.get(job.get('verbose', 'yes').lower(), None)
        if self.verbose==None:
            errors['verbose']='boolean must have value in (on, yes, true, 1, off, no, false and 0)'

        self.mail_when=job.get('mail_when', 'always').lower()
        try:
            self.mail_when=int(self.mail_when)
        except ValueError:
            if not self.mail_when in ('always', 'change', 'status', 'never'):
                errors['mail_when']='must be a frequency in hours or a string in "always" or "change" or "status" or "never"'
            
        self.friendly_value=boolean.get(job.get('friendly_value', 'no').lower(), None)
        if self.friendly_value==None:
            errors['friendly_value']='boolean must have value in (on, yes, true, 1, off, no, false and 0)'

        for name in ('class_list', 'class_include', 'class_exclude', 'property_exclude'):
            value=job.get(name, None)
            try:
                lst=quoted_string_list(job.get(name, ''))
            except ValueError:
                errors[name]='not a valid quoted string list'
            else:
                setattr(self, name, lst)
                
        if not self.class_list:
            self.class_list=default_class_list
            
        class_include_warnings=[]
        for cls in self.class_include:
            if not cls in self.class_list:
                self.class_list.append(cls)
            else:
                class_include_warnings.append(cls)
                
        class_exclude_warnings=[]
        for cls in self.class_exclude:
            if cls in self.class_list:
                self.class_list.remove(cls)
            else:
                class_exclude_warnings.append(cls)
                
        if class_include_warnings:
            warnings['class_include']='classes already in the list: '+','.join(class_include_warnings)
            
        if class_exclude_warnings:
            warnings['class_exclude']='classes not in the list: '+','.join(class_exclude_warnings)
                    
        if not errors:
            # upload and setup files on the VMWARE server
            extra='class list: '+', '.join(self.class_list)
            
            # make a try 
            wbemclient=pywbem.WBEMConnection(self.url, (self.login, self.password), self.NS)
            try:
                _instance_list=wbemclient.EnumerateInstances(test_class)
            except pywbem.cim_operations.CIMError, e:
                if e.args[0]==0:
                    log.exception('maybe something wrong with URL "%s": %s', self.url, e[1])
                    errors['url']='maybe something wrong with URL "%s": %s' % (self.url, e[1])
                elif e.args[0]==pywbem.CIM_ERR_NOT_FOUND:
                    pass # The requested object could not be found.
                else:
                    errors['url']="Unknown CIM Error: code=%s, msg=%s" % (e[0], e[1])
                    log.error("Unknown CIM Error: code=%s, msg=%s", e[0], e[1])
            except pywbem.cim_http.AuthError, e: 
                log.error("Authentication error: %s", e)
                errors['login']="Authentication error: %s" % (e,)

        return errors, warnings, extra

    # -----------------------------------------------------------------------
    def friendlyValue(self, client, instance, propertyName):
       # Start out with a default empty string, in case we don't have a mapping
       mapping=None
    
       if instance.classname not in self.classData:
          # Fetch the class metadata if we don't already have it in the cache
          self.classData[instance.classname]=client.GetClass(instance.classname, IncludeQualifiers=True)
    
       # Now scan through the qualifiers to look for ValueMap/Values sets
       qualifiers=self.classData[instance.classname].properties[propertyName].qualifiers
       if 'ValueMap' in qualifiers.keys() and 'Values' in qualifiers.keys():
          vals=qualifiers['Values'].value
          valmap=qualifiers['ValueMap'].value
          value=instance[propertyName]
          # Find the matching value and convert to the friendly string
          if isinstance(value, (list, tuple)):
              mapping=[]
              for v in value:
                  for i in range(0,len(valmap)-1):
                     if str(valmap[i]) == str(v):
                         mapping.append(vals[i])
                         break
              mapping=' ('+', '.join(mapping)+')'
         
          else:
              for i in range(0,len(valmap)-1):
                 if str(valmap[i])==str(value):
                     mapping=vals[i]
                     break
       return mapping

    # -----------------------------------------------------------------------
    def run(self, command, job, manager):

        log=manager.log
        now=manager.now

        start=int(time.time())
        log.info('start url=%s', self.url)

        global_status, data, error=ExitOK, '', ''

        wbemclient=pywbem.WBEMConnection(self.url, (self.login, self.password), self.NS)

        for cls in self.class_list:
            try:
                instance_list=wbemclient.EnumerateInstances(cls)
            except pywbem.cim_operations.CIMError, e:
                if e.args[0]==pywbem.CIM_ERR_NOT_FOUND:
                    log.warning('class not found: %s (%s)', cls, e.args[1])
                    continue
                else:
                    log.exception('Unexpected error enumerating class %s', cls)
                    continue
                
            buggy=False
            for instance in instance_list:
                try:
                    elementName=instance['ElementName']
                except KeyError:
                    if not buggy:
                        log.error('Skip unknown buggy instance in class %s', cls)
                        buggy=True
                    continue
                title='===== %s %s =====' % (cls, elementName)
                for propertyName in sorted(instance.keys()):
                    fullPropertyName="%s.%s.%s" % (cls, elementName, propertyName)
                    try:
                        if propertyName in self.property_exclude or fullPropertyName in self.property_exclude or "%s.%s" % (cls, propertyName) in self.property_exclude:
                            log.debug('skip property "%s"', fullPropertyName)
                            continue
                        if not self.verbose and propertyName not in ('OperationalStatus', 'HealthState'):
                            continue
                        if instance[propertyName] is None:
                            # skip over null properties
                            continue
                        value=None
                        if self.friendly_value:
                            try:
                                value=self.friendlyValue(wbemclient, instance, propertyName)
                            except Exception, e:
                                log.exception('Retrieving friendly value for class.instance.property="%s"', fullPropertyName)
    
                        if value==None:
                            value=instance[propertyName]
                            if isinstance(value, (list, tuple)):
                                value='('+', '.join(map(str, value))+')'
                            else:
                                value=str(value)
                               
                        status=None
                        if propertyName in ('OperationalStatus', 'HealthState'):
                            status=ExitOK
                            values=instance[propertyName]
                            if not isinstance(values, (list, tuple)):
                                values=[values, ]
                            for v in values:
                                s=self.interpret[propertyName].get(v, ExitUnknown)
                                status=max(status, s)
                            if status!=ExitOK:
                                error+='%s %s %s: %s\n' % (cls, elementName, propertyName, value)
                                log.info('ERROR %s %s %s: %s', cls, elementName, propertyName, value)
                            global_status=max(global_status, status)
                        if title:
                            data+=title+'\n'
                            title=''
                            
                        if status==ExitOK:
                            status='OK ' 
                        elif status==None:
                            status='   '
                        else:
                            status='ERR'
    
                        data+='%s\t%s=%s\n' % (status, propertyName, value) 
                    except Exception, e:
                        log.exception('Unexpected error handling class.instance.property="%s"', fullPropertyName)
                        

        end=int(time.time())
        
        if global_status==ExitOK:
            backup_status='OK'
        else:
            backup_status='ERR'

        log.info('status: %s', backup_status)

        log.debug('=========== output.txt ===========')
        for line in data.split('\n'):
            log.debug('> %s',line)
        
        status=u''
        attachments=[ # the type, subtype and coding is not used
                       ('output.txt', None, data, 'text', 'plain', 'utf-8'),
                    ]
        
        if error:
            attachments.insert(0, ('error.txt', None, error, 'text', 'plain', 'utf-8'))

        status=u''
        status+='name=%s\r\n' % job['name']
        status+='program=%s\r\n' % self.name
        status+='version=%s\r\n' % self.__version__
        status+='status=%s\r\n' % backup_status
        status+='hostname=%s\r\n' % manager.hostname
        
        status+='exit_code=%d\r\n' % global_status
        status+='start=%s\r\n' % time.ctime(start)
        status+='end=%s\r\n' % time.ctime(end)
        status+='start_epoch=%d\r\n' % start
        status+='end_epoch=%d\r\n' % end

        # do I need to send an email or alert MagiKmon ?
        prev_values, magikmon, registry={}, job['magikmon'], None

        if self.mail_when in ('never', ):
            job['mail']=False # sorry for cheating
            log.info('never send any email')
        
        if not self.mail_when in ('always', 'never') or magikmon:
            try:
                import hashlib
                md5sum=hashlib.md5(data).hexdigest()
            except ImportError:
                import md5
                md5sum=md5.new(data).hexdigest()
    
            if sys.platform in ('win32', ):
                import windows
                registry=windows.Registry(job['name'])
            else:
                registry=UnixRegistry(job['name'])
                
            prev_values=registry.LoadValues()
            registry.SaveValues(dict(status=backup_status, md5sum=md5sum, last=int(time.time())))

            # check if I need to send an email
            if not self.mail_when in ('always', 'never'):
                changed_status=prev_values.get('mail.status', '<UNK>')!=backup_status
                changed_md5sum=prev_values.get('mail.md5sum', '<md5>')!=md5sum
                expired=isinstance(self.mail_when, int) and (time.time()-int(prev_values.get('mail.last', 0)))>self.mail_when
                log.debug('mail status changed=%r   report changed=%r   time expired=%r', changed_status, changed_md5sum, expired)
                if self.mail_when=='always' or expired or (isinstance(self.mail_when, int) and (changed_status or changed_md5sum)) or (self.mail_when=='change' and (changed_status or changed_md5sum)) or (self.mail_when=='status' and changed_status):
                    # send an email
                    registry.SaveValues({'mail.status':backup_status, 'mail.md5sum':md5sum, 'mail.last':int(time.time())})
                else:
                    # don't send the email ! 
                    job['mail']=False # sorry for cheating
                    log.info('don\'t send any email because the status has not changed')

            # update MagiKmon, no more then once per hour except when something changed !
            if magikmon:
                
                changed_status=prev_values.get('magikmon.status', '<UNK>')!=backup_status
                changed_md5sum=prev_values.get('magikmon.md5sum', '<md5>')!=md5sum
                expired=(time.time()-int(prev_values.get('magikmon.last', 0)))>3300
                # log.debug('magikmon status %r %r', prev_values.get('magikmon.status', '<UNK>'), backup_status)
                # log.debug('magikmon md5sum %r %r', prev_values.get('magikmon.md5sum', '<md5>'), md5sum)
                log.debug('magikmon status changed=%r   report changed=%r   time expired=%r', changed_status, changed_md5sum, expired)
                if changed_status or changed_md5sum or expired:
                    pass # send
                else:
                    log.info('don\'t update MagiKmon status this time')
                    magikmon=None

        if magikmon:
            data=urllib.urlencode(dict(status=backup_status, payload=data))
            try:
                try:
                    urllib2.urlopen(magikmon, data, timeout=30)
                except TypeError:
                    # python 2.4
                    urllib2.urlopen(magikmon, data)
            except Exception, e:
                log.exception('error updating MagiKmon status: %s', e)
            else:
                log.debug('MagiKmon updated: %s', magikmon)
                registry.SaveValues({'magikmon.status':backup_status, 'magikmon.md5sum':md5sum, 'magikmon.last':int(time.time())})
        
        if registry:
            registry.Close()
        
        return backup_status, status, attachments
