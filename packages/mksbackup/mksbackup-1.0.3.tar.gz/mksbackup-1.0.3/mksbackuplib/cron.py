#!/usr/bin/env python

import re


class CronException(Exception):
    pass

class Cron:
    
    modifier={ '1st':1, '2nd':2, '3rd':3, '4th':4, '5th':5, 'first':1, 'second':2, 'last':0 }
    
    month_lst=['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    dayofweek_lst=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    dayofmonth_lst=[str(x) for x in range(1,32)]


    unique_re=re.compile('.+')
    range_re=re.compile('([^-/]+)[-]([^-/]+)')
    simple_step_re=re.compile('([^-/]+)/([0-9]+)')
    step_re=re.compile('([^-/]+)[-]([^-/]+)/([0-9]+)')
    week_selector_re=re.compile ('w(mon|tue|wed|thu|fri|sat|sun)([0-9]*)/([0-9]+)')
    
    def __init__(self, selector):
        self.daysofmonth=set()
        self.daysofweek=set()
        self.months=set()
        self.firstdayofweek=None
        self.weekdivisor=None
        self.weekselector=None
        
        for period in selector.split(','):
            period=period.strip()
            first, last, step=None, None, '0'

            match=self.week_selector_re.match(period)
            if match:
                if self.firstdayofweek!=None:
                    raise CronException, 'week selector already set: %s' % (period,)
                self.firstdayofweek, self.weekselector, self.weekdivisor=match.groups()
                if self.weekselector:
                    self.weekselector=int(self.weekselector)
                else:
                    self.weekselector=None
                self.firstdayofweek=self.dayofweek_lst.index(self.firstdayofweek)
                self.weekdivisor=int(self.weekdivisor)
            else:
                while True:
                    match=self.step_re.match(period)
                    if match:
                        first, last, step=match.groups()
                        break
                    
                    match=self.simple_step_re.match(period)
                    if match:
                        first, step=match.groups()
                        break
    
                    match=self.range_re.match(period)
                    if match:
                        first, last=match.groups()
                        step='1'
                        break
                    
                    first=period
                    break
                
                found, size=False, 0
                for cls, pset in [(self.month_lst, self.months), (self.dayofweek_lst, self.daysofweek), (self.dayofmonth_lst, self.daysofmonth) ]:
                    try:
                        f=cls.index(first)
                    except ValueError:
                        continue
                    
                    found=pset
                    size=len(cls)
    
                    if last:
                        try:
                            l=cls.index(last)+1
                        except ValueError:
                            raise CronException, '%s not in the same range as %s' % (last, first)
                    else:
                        l=len(cls)+1
    
                    try:
                        s=int(step)
                    except ValueError:
                        raise CronException, '%s not a valid step' % (step,)
                    else:
                        if s==0:
                            l=f+1
                            s=1
                    
                if found==False:
                    raise CronException, '%s unknown' % (first,)
                
                if f>l:
                    l+=size
    
                #print period, f, l, s, range(f,l,s)
                    
                found|=set(x%size for x in range(f,l,s))
            

    def __str__(self):
        st=''
        for cls, pset in [(self.month_lst, self.months), (self.dayofweek_lst, self.daysofweek), (self.dayofmonth_lst, self.daysofmonth) ]:
            if pset:
                for i, dsp in enumerate(cls):
                    if i in pset:
                        st+=dsp+','
                        
        if self.firstdayofweek:
            if self.weekselector!=None:
                st+='(w%d-%d/%d)' % (self.firstdayofweek, self.weekselector, self.weekdivisor,)
            else:
                st+='(w%d/%d)' % (self.firstdayofweek, self.weekdivisor,)
        return st
            


if False:
    
    c=Cron('mon-fri')
    print c, '\n'
    
    c=Cron('sun-mon')
    print c, '\n'
    
    c=Cron('sun,mon-fri/2,sat')
    print c, '\n'
    
    c=Cron('jan-dec/2,thu/2,1-31/2')
    print c, '\n'
    
    c=Cron('w0/2')
    print c, '\n'
    
    c=Cron('w1/2')
    print c, '\n'

    c=Cron('sun,wsun0/2')
    print c, '\n'

    c=Cron('mon-sat,wsun0/2')
    print c, '\n'
