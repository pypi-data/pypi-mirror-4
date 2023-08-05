##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved. 
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                      
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__version__   = '$ Revision 0.0 $'[11:-2]

import logging
from operator import itemgetter
import os
import time
from string import join
from random import randint
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.interfaces import IPloneSiteRoot
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, package_home

from urllib2 import urlopen, urlparse, HTTPError

class LoadTestTool(UniqueObject, SimpleItem):
    """ Load Test Tool """

    id = 'portal_loadtesttool'
    title = 'Load testing tool for eduCommons'
    meta_type = 'Load Testing Tool'
    toolicon = 'tool.gif'
    plone_tool = 1

    manage_options = ({ 'label' : 'Overview', 'action' : 'manage_overview' },
                      { 'label' : 'Load Content', 'action' : 'manage_loadcontent' },
                      { 'label' : 'Run Test', 'action' : 'manage_runtest' },
                      )

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'manage_overview')
    security.declareProtected(ManagePortal, 'manage_loadcontent')
    security.declareProtected(ManagePortal, 'manage_runtest')
    security.declareProtected(ManagePortal, 'manage_results')

    manage_overview = DTMLFile(os.path.join('www','overview'), globals())
    manage_loadcontent = DTMLFile(os.path.join('www', 'loadcontent'), globals())
    manage_runtest = DTMLFile('www/runtest', globals())
    manage_results = DTMLFile('www/results', globals())
    manage_testresults = DTMLFile('www/testresults', globals())
    
    security.declareProtected(ManagePortal, 'loadcontent')
    def loadcontent(self, REQUEST=None, divisions=0, courses=0, objects=0):
        """ Load test content """
        out = []
        context = self.portal_url.getPortalObject()
        imgdata = self._getTestContent('test.jpg')
        filedata = self._getTestContent('test.pdf')
        docdata = self._getTestContent('test.html')
        for x in range(1, int(divisions) + 1):
            div = self._createObject(context,
                                     'Division',
                                     'division',
                                     title='Division',
                                     index=x,
                                     template='@@division_view',
                                     out=out)
            if div:
                for y in range(1, int(courses) + 1):
                    course = self._createObject(div,
                                                'Course',
                                                'course',
                                                title='Course',
                                                index=y,
                                                template='@@course_view',
                                                out=out)
                    course.setCourseId('%d_%.3d' %(x, y))
                    course.setTerm('%s%s' %(['Spring', 'Summer', 'Fall'][randint(0,2)],
                                            ['2006', '2007', '2008', '2009'][randint(0, 3)]))
                    if course:
                        if not getattr(course, 'syllabus', None):
                            self._createObject(course,
                                               'Document',
                                               'syllabus',
                                               title='Syllabus',
                                               template='@@syllabus_view',
                                               out=out)
                        if not getattr(course, 'aboutprof', None):
                            self._createObject(course,
                                               'Document',
                                               'aboutprof',
                                               title='About the Professor',
                                               template='@@aboutprof_view',
                                               out=out)
                        if not getattr(course, 'schedule', None):
                            self._createObject(course,
                                               'Document',
                                               'schedule',
                                               title='Schedule',
                                               template='@@schedule_view',
                                               out=out)
                        for z in range(1, int(objects) + 1):
                            otype = z%3
                            if otype == 0:
                                self._createObject(course,
                                                   'Image',
                                                   'test.jpg',
                                                   title='Test Image',
                                                   index=z,
                                                   image=imgdata,
                                                   out=out)
                            elif otype == 1:
                                self._createObject(course,
                                                   'File',
                                                   'test.pdf',
                                                   title='Test File',
                                                   index=z,
                                                   file=filedata,
                                                   out=out)
                            else:
                                self._createObject(course,
                                                   'Document',
                                                   'test.html',
                                                   title='Test Document',
                                                   index=z,
                                                   document=docdata,
                                                   out=out)

        return self.manage_results(self, out=out)

    security.declareProtected(ManagePortal, 'runtest')
    def runtest(self, REQUEST=None):
        """ Run load test """
        reps = int(REQUEST['reps'])
        urls = REQUEST['urls'].split('\r\n')
        results ={}
        out = []        

        #analyze incoming URLs
        urls, external_urls = self._getLocalURLs(urls)
        
        obj_load_times, obj_error_count, error_urls, error_count, total_time = self._loadURLs(reps, urls)

        #generate avg, shortest, longest load times
        for k, v in obj_load_times.items():
            v.sort()
            shortest = '%.4fsec' % v[0]
            longest = '%.4fsec' % v[-1]
            avg = '%.4fsec' % (float(sum(v)) / len(v))
            results[k] = [avg, shortest, longest]

        #append total errors per object
        for k, v in obj_error_count.items():            
            results[k].append(v)
                    
        results = sorted(results.items(), key=itemgetter(1), reverse=True)                    

        for result in results:
            if not result[0] in error_urls:
                out.append((result[0], result[1]))        
            else:
                out.append((result[0]+'*', result[1]))            
    
        return self.manage_testresults(self, out=out, external_urls=external_urls, reps=reps, total_reps=reps*(len(urls)), total_time=total_time, error_count = error_count )

    def _getTestContent(self, fn):
        """ Get content for test course objects """
        path = package_home(globals())
        filepath = os.path.join(path, 'www', fn)
        f = open(filepath)
        filedata = f.read()
        f.close()
        return filedata        

    def _createObject(self, context, type, id, **args):
        """ Create an object """
        if args.has_key('title'):
            title = args['title']
        else:
            title = type
        if args.has_key('description'):
            desc = args['description']
        else:
            desc = 'This is a %s' %type
        if args.has_key('index'):
            tmp = id.split('.')
            tmp[0] += '%d' %args['index']
            id = join(tmp, '.')
            title = '%s %d' %(title, args['index'])
            desc = '%s %d' %(desc, args['index'])
        obj = getattr(context, id, None)
        if obj:
            return obj
        else:
            _createObjectByType(type, context, id=id, title=title, description=desc)
            obj = getattr(context, id)
            if obj:
                if args.has_key('template'):
                    tmpl = obj.restrictedTraverse(str(args['template']))
                    text = tmpl(obj)
                    obj.setText(text)
                elif args.has_key('image'):
                    obj.setImage(args['image'])
                elif args.has_key('file'):
                    obj.setFile(args['file'])
                elif args.has_key('document'):
                    obj.setText(args['document'])
                self._workflowObject(obj)
                if args.has_key('out'):
                    args['out'].append(('Created %s' %title, logging.INFO))
                return obj
        return None

    def _workflowObject(self, context):
        """ Put object and sub objects through the workflow. """
        wftool = getToolByName(context, 'portal_workflow')
        if wftool.getInfoFor(context, 'review_state') != 'Published':
            wftool.doActionFor(context, 'submit')
            wftool.doActionFor(context, 'release')
            wftool.doActionFor(context, 'publish')    

    def _getLocalURLs(self, urls):
        """ analyze incoming URLS, drop external URLs and rebuild relative paths  """
        #ensure all URLs are local
        external_urls = []
        for url in urls:
            if self.portal_url() not in url:                
                #check parts for rellinks
                parts = urlparse.urlsplit(url)                
                if parts[0] != '' and parts[1] != '':
                    #remove external urls from the list
                    external_urls += [url,]                             
                else:
                    path = parts[2]
                    if not path.startswith('/'):
                        path = '/%s' % path
                    abs_url = self.portal_url() + path
                    url_index = urls.index(url)
                    urls.pop(url_index)
                    urls.insert(url_index, abs_url)
        #remove external URLs
        urls = filter(lambda a,external_urls=external_urls:not a in external_urls, urls)
        return urls, external_urls

    def _loadURLs(self, reps, urls):
        """ load urls sequentially and store load times and HTTPError counts per URL. Return as dictionaries """ 
        count = 1
        obj_load_times = {}
        obj_error_count = {}        
        error_urls = []
        error_count = 0
        total_time = 0
        while count <= reps:
            for url in urls:
                errors = 0
                try:
                    start, end = self._httpGetTime(url)
                except HTTPError:
                    start = end = 0
                    if url not in error_urls:
                        error_urls += [url,]
                    errors += 1
                elapsed = end - start    
                total_time += elapsed
                if obj_load_times.has_key(url):
                    obj_load_times[url].append(elapsed)
                    obj_error_count[url] += errors
                else:
                    obj_load_times[url] = [elapsed, ]
                    obj_error_count[url] = errors                    
                error_count += errors
            count += 1                        
        return obj_load_times, obj_error_count, error_urls, error_count, total_time
        
            
    def _httpGetTime(self, url):
        """ Get load time for the url """
        data = ''
        start = time.time()
        f = urlopen(url)
        data = f.read()
        f.close()
        end = time.time()
        return start, end 
        

InitializeClass(LoadTestTool)
        
