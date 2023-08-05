#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

  product:  Feng Shui 
  
  Copyright (C) 2012 Cornelius Kölbel
  contact:  http://www.cornelinux.de
            corny@cornelinux.de

  Description:  This tool ....

'''



import pygtk
pygtk.require("2.0")
import gtk
import gettext
_ = gettext.gettext
import pickle
import fengshui
import pango
import sys, os
import platform

GLADEFILE = "main.glade"
PACK_NAME = "fengshui"
# Determine Resourcedir
resourceDirsLinux = ( '.',
        sys.prefix+'/share/%s/' % PACK_NAME,
        '/usr/local/share/%s/' % PACK_NAME)
resourceDirsWindows = ( sys.prefix+'\\share\\%s\\' % PACK_NAME,
        'C:\\python26\\share\\%s\\' % PACK_NAME)        

system=platform.system()                    
RESOURCEDIR="FAIL"                    
if system=="Linux":
    for dir in resourceDirsLinux:
        if os.path.isfile(dir+GLADEFILE):
            RESOURCEDIR=dir
            break
    if RESOURCEDIR=="FAIL":
        print "Unable to find any glade file"
        sys.exit(1)
elif system=="Windows":
    LOCALE_DIR = sys.prefix + "\\share\\locale"
    for dir in resourceDirsWindows:
        if os.path.isfile(dir+GLADEFILE):
            RESOURCEDIR=dir
            break
    if RESOURCEDIR=="FAIL":
        print "Unable to find any glade file"
        sys.exit(1)
else:
    print "This program is only know to run on windows and Linux."
    print "You are running ", system
    sys.exit(1)
    

class Person(object):
    '''
    type = 0: house
         = 1: person
    '''
    def __init__(self, name, givenname, type=1,
                    sex=0, 
                    birthdate="", 
                    birthtime="",
                    location="",
                    longitude=""):
        self.sex = sex
        self.type = type
        self.name = name
        self.givenname = givenname
        self.birthdate = birthdate
        self.birthtime = birthtime
        self.location = location
        self.longitude = longitude
        
    def dump(self):
        return "type: %i, name: %s, givenname: %s, birthdate: %s, location: %s" % (self.type,
                                                                                   self.name, 
                                                                                   self.givenname,
                                                                                   self.birthdate,
                                                                                   self.location)
        
        
class PersonList(object):
    
    def __init__(self):
        self.pList = []
        self.current_location = 0
        
    def _find(self, name, givenname):
        '''
        returns the person Object witht he given
            type and
            name and
            givenname
        '''
        for p in self.pList:
            if name == p.name and  givenname == p.givenname:
                return p
        return None
        
        
    def append(self, p):
        '''
        Appends a person to the list, but checks, that there will be only one 
        instance of this person
        '''
        
        # TODO
        person_exist = self._find(p.name, p.givenname)
        
        if person_exist:
            print "Person already exist: %s" % person_exist
            self.remove(person_exist)
        
        self.pList.append(p)
        
        
    def remove(self, p):
        '''
        removes the given person/object from the List of persons 
        '''
        person = self._find(p.name, p.givenname)
        self.pList.remove(person)
        
    
    
    def __iter__(self):
        '''
        returns the iterator itself
        '''
        return self
    
    def next(self):
        '''
        returns the next element
        '''
        if self.current_location >= len(self.pList):
            self.current_location = 0
            raise StopIteration
        else:
            self.current_location += 1
            return self.pList[self.current_location-1]
            
    def __len__(self):
        return len(self.pList)


class FengShuiGUI(object):
    
    def __init__(self):
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(RESOURCEDIR + "/" + GLADEFILE)
        
        self.builder.connect_signals(self)
        
        self.window = self.widget("FengShuiMainWindow")
        self.objectlist = self.widget('liststoreObject')
        
        self.person_list = PersonList()
        self.filename = ""
        
        
    def set_title(self, title):
        self.window.set_title("FengShui - %s" % title)
        
    def set_status1(self, text):
        self.widget("labelStatus1").set_text(text)
        
    def widget(self, name):
        return self.builder.get_object(name)
    
    
    def new_object(self, widget):
        '''
        clear all input entries
        '''
        self.widget('entryObjectGivenname').set_text("")
        self.widget('entryObjectSurname').set_text("")
        self.widget('entryObjectBirthdate').set_text("")
        self.widget('entryObjectBirthtime').set_text("")
        self.widget('entryObjectLocation').set_text("")
        self.widget('entryObjectLongitude').set_text("")
        self.widget('comboboxObjectType').set_active(-1)
        self.widget('comboboxObjectSex').set_active(-1)
    
    def _get_person(self):
        person = Person( name=self.widget("entryObjectSurname").get_text(),
                         givenname=self.widget("entryObjectGivenname").get_text(),
                         type=self.widget("comboboxObjectType").get_active(),
                         birthdate=self.widget("entryObjectBirthdate").get_text(),
                         birthtime=self.widget("entryObjectBirthtime").get_text(),
                         location=self.widget("entryObjectLocation").get_text(),
                         longitude=self.widget("entryObjectLongitude").get_text(),
                         sex=self.widget("comboboxObjectSex").get_active(),
                          )
        return person
    
    
    def _set_person(self, p):
        self.widget("entryObjectSurname").set_text(p.name)
        self.widget("entryObjectGivenname").set_text(p.givenname)
        self.widget("entryObjectBirthdate").set_text(p.birthdate)
        self.widget("entryObjectBirthtime").set_text(p.birthtime)
        self.widget("entryObjectLocation").set_text(p.location)
        self.widget("entryObjectLongitude").set_text(str(p.longitude))
        self.widget("comboboxObjectType").set_active(int(p.type))
        self.widget("comboboxObjectSex").set_active(int(p.sex))
    
    def _dump_person(self, person):
        print person
        print self.person_list
        print self.person_list.pList
        print len( self.person_list )
        
        for p in self.person_list:
            print p.dump()
        
    
    def save_object(self, widget):
        '''
        creates a new object and adds it to the object list
        '''
        person = self._get_person()
        self.person_list.append(person)
        self._dump_person(person)
        
        self.fill_treeview()
        
    def fill_treeview(self,widget=None):
        self.objectlist.clear()
        
        for person in self.person_list:        
            try:
                self.objectlist.append( [person.type,
                                     person.name,
                                     person.givenname,
                                     person.birthdate,
                                     person.birthtime,
                                     person.location,
                                     person.longitude,
                                     person.sex] )
            except AttributeError, e:
                print "ERROR filling treeview: %s" % str(e)
                
            
        
    def delete_object(self, widget):
        '''
        deletes the selected object
        '''
        person = self._get_person()
        self.person_list.remove(person)
        self._dump_person(person)
        self.fill_treeview()
        
        
    def object_clicked(self, widget):
        '''
        This function is called by the signal row-activated on the person treeview
        '''
        liststore, treeiter = self.widget("treeviewObject").get_selection().get_selected()
        
        
        print liststore.get(treeiter,0,1,2,3,4,5,6,7)
        self._set_person(Person(name        =liststore.get_value(treeiter,1),
                                givenname   =liststore.get_value(treeiter,2),
                                type        =liststore.get_value(treeiter,0),
                                birthdate   =liststore.get_value(treeiter,3),
                                birthtime   =liststore.get_value(treeiter,4),
                                location    =liststore.get_value(treeiter,5),
                                longitude   =liststore.get_value(treeiter,6),
                                sex         =int(liststore.get_value(treeiter,7))
                                ))        


    '''
    ------------------------------------------------------------------------------------------------------------
    File Operations
    '''
        
    def save_as(self, widget):
        chooser = gtk.FileChooserDialog(title=_("Save as..."),
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE_AS,gtk.RESPONSE_OK)
                                        )
        
        '''
        dialog.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("Images")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/gif")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.gif")
        filter.add_pattern("*.tif")
        filter.add_pattern("*.xpm")
        dialog.add_filter(filter)
        '''
        
        chooser.set_do_overwrite_confirmation(True)
        
        response = chooser.run()
        
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            print "saving %s" % filename 
            file_pi = open(filename, 'w') 
            pickle.dump(self.person_list, file_pi) 
            self.filename = filename
            self.set_status1(_("save file %s") % self.filename)
            self.set_title(self.filename)
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        chooser.destroy()
        
    def save(self, widget):
        file_pi = open(self.filename, 'w') 
        pickle.dump(self.person_list, file_pi)
        self.set_status1(_("save file %s") % self.filename)
        self.set_title(self.filename)
         
        
    def open(self,widget):
        chooser = gtk.FileChooserDialog(title=_("Open file"),
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
                                                                    
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            filehandler = open(filename, 'r')
            try: 
                object = pickle.load(filehandler)
                self.person_list = object
            except Exception,e:
                print "ERROR LOADING FILE! %s" % str(e)
            self.fill_treeview()
            self.filename = filename
            self.set_status1(_("loaded file %s") % self.filename)
            self.set_title(self.filename)
        
            
        chooser.destroy()

    '''
    --------------------------------------------------------------------------
    Feng Shui tools
    '''
    def info_dialog(self, text):
        md = gtk.MessageDialog(parent=None,
                               flags=gtk.DIALOG_DESTROY_WITH_PARENT, 
                               type=gtk.MESSAGE_INFO,
                               buttons=gtk.BUTTONS_CLOSE, 
                               message_format=text)
        md.run()
        md.destroy()
        
    def fengshui_minggua(self, widget):
        '''
        calculates ming gua for current person
        '''
        p = self._get_person()
        gua = fengshui.ming_gua(p.sex, p.birthdate)
        
        self.info_dialog(_("The Ming Gua number for %s %s is %i") % (p.givenname, p.name, gua))

    def fengshui_flying_stars(self, widget):
        '''
        calculates flying stars for a house.
        '''
        p = self._get_person()
        if p.type == 0:
            year = fengshui.get_year_from_date(p.birthdate)
            facing = float(p.longitude)
            fstars = fengshui.flying_stars(year, facing)
            
            text = fengshui.dump_stars(fstars)
            
            text += "\n%s%s" % (fstars['direction'],fstars['sector'])
            self.widget("textbufferFlyingStars").set_text(text)

            self.widget("dialogFlyingStars").show()
            self.widget("textviewFlyingStars").set_buffer(self.widget("textbufferFlyingStars"))
            self.widget("textviewFlyingStars").modify_font(pango.FontDescription('monospace 18'))
            
            
        else:
            self.info_dialog(_("You can only caluclate flying stars for buildings!")) 
        
        
    def dialog_flying_stars_close(self, widget):
        self.widget("dialogFlyingStars").hide()
            
    def quit(self, widget):
        gtk.main_quit()


        

if __name__ == "__main__":
    app = FengShuiGUI()
    app.window.show()
    gtk.main()