"""
 Copyright 2012 Robert Steed
 
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


"""This script recreates the winxp startmenu from the directory contents of 'All users'/startmenu 
and $userprofile$/startmenu. It can save the structure and the program icons to a pickled file
and later reload from the file. So this is mostly useful for remembering which programs that 
you had installed on another computer and how your start menu looked."""


##Load directory contents
##merge directory contents
##create wx menu using tree ctrl.

from win32com.shell import shell, shellcon
from win32con import FILE_ATTRIBUTE_NORMAL
#import string
import wx
import os
#import images
#from itertools import chain
import pickle
import base64
    
def file_to_iconbitmap(extension):
    """dot is mandatory in extension"""

    flags = shellcon.SHGFI_SMALLICON | \
            shellcon.SHGFI_ICON | \
            shellcon.SHGFI_USEFILEATTRIBUTES

    retval, info = shell.SHGetFileInfo(extension,
                             FILE_ATTRIBUTE_NORMAL,
                             flags)
    # non-zero on success
    assert retval

    hicon, iicon, attr, display_name, type_name = info

    # Get the bitmap
    icon = wx.EmptyIcon()
    icon.SetHandle(hicon)
    #icon.SetWidth(16)
    #icon.SetHeight(16)
    return wx.BitmapFromIcon(icon)
    
def file_to_icondata0(extension):
    """dot is mandatory in extension"""

    flags = shellcon.SHGFI_SMALLICON | \
            shellcon.SHGFI_ICON | \
            shellcon.SHGFI_USEFILEATTRIBUTES

    retval, info = shell.SHGetFileInfo(extension,
                             FILE_ATTRIBUTE_NORMAL,
                             flags)
    # non-zero on success
    assert retval

    hicon, iicon, attr, display_name, type_name = info

    # Get the bitmap
    icon = wx.EmptyIcon()
    icon.SetHandle(hicon)
    icon.SetWidth(16)
    icon.SetHeight(16)
    bmp=wx.BitmapFromIcon(icon)
    img=wx.ImageFromBitmap(bmp)
    if img.HasMask(): 
        img.InitAlpha()
    #print "hasMask",img.HasMask()
    #print "hasAlpha",img.HasAlpha()
    str=img.GetData()
    data=str.encode("base64")
    alpha=img.GetAlphaData().encode("base64")
    #img2.SetMaskColour(1,2,3)
    return data,alpha
 
def file_to_icondata(path): 
    loc=wx.IconLocation(path,0)
    icon=wx.IconFromLocation(loc)
    bmp=wx.BitmapFromIcon(icon)
    
    #icon.SetWidth(16)
    #icon.SetHeight(16)
    img=bmp.ConvertToImage() #wx.ImageFromBitmap(bmp)
    if img.HasMask(): 
        img.InitAlpha()
    #print "hasMask",img.HasMask()
    #print "hasAlpha",img.HasAlpha()
    str=img.GetData()
    data=str.encode("base64")
    alpha=img.GetAlphaData().encode("base64")

    return data,alpha
    
#--------------------------------------------------------------------------------------------------------------------------------------
#Creating a python structure of the start menu
#A set of nested lists, each entry is a tuple. Program tuples are (name,index) where index is the indice to an array of metadata or icons.
#Folder tuples are (name,index,{files:[],dirs:[]}) where the list is the subfolder; normal index=1 for folders

#Winxp creates the startmenu from information in two locations, "All Users" and in the user profile. It also gets the ordering of the startmenu 
#from the registry but I'm not going to get involved with that.

def save_start_menu(dlg=None):
    start=['Start',1,{'files':[],'dirs':[]}] # start menu structure 
    icons=[] #flat array of icon data
    
    AllUsers= os.path.expandvars('%ALLUSERSPROFILE%' +os.path.sep+'Start Menu')
    CurrentUsers=os.path.expandvars('%USERPROFILE%' +os.path.sep+'Start Menu')
        
    count=0
    for location in AllUsers,CurrentUsers:
        for root,dirs,files in os.walk(location):
            current=_find_place(root.replace(location,'Start',1),start)
        
            for f in files:
                count+=1
                if dlg!=None: dlg.Update(count, f)
                #
                fullpath = os.path.join(root,f)
                #icon = file_to_iconbitmap(fullpath)
                icon=file_to_icondata0(fullpath)
                icons.append(icon)
                current['files'].append( (f,len(icons)-1) )
            
            for d in dirs:
                #folder might already exist so need to check for folder name
                if not [1 for entry in current['dirs'] if len(entry)==3 and entry[0]==d]:
                    current['dirs'].append( (d,1,{'files':[],'dirs':[]}) )
                
            current['files'].sort()
            current['dirs'].sort()
    
    return start,icons
            
def _find_place(root,startstruct):
    cur=startstruct
    for folder in root.split(os.path.sep)[1:]:#finds the directory in our startmenu replica.
        cur=[d for d in cur[2]['dirs'] if d[0]==folder][0] #takes first result which should always be only result.
    return cur[2]

#-------------------------------------------------------------------------------------------------------------------------------------

class TreeCtrlPanel(wx.Panel):
    def __init__(self, parent, id):
        # Use the WANTS_CHARS style so the panel doesn't eat the Return key.
        wx.Panel.__init__(self, parent, id, style=wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        tID = wx.NewId()
        self.tree = wx.TreeCtrl(self, tID, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE)
        #
        self.treestruct=[] # a secondary store of the tree structure as a nested list 
        #(first item of each sublist=name of directory), unused in the panel but kept around for future.
        #loading icons
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        fldridx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, isz))
        fileidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        fileidx2= il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER,isz))
        self.tree.SetImageList(il)
        self.il = il
        #Initial tree
        self.root = self.tree.AddRoot("Start")
        #self.tree.SetPyData(self.root, None)
        self.tree.SetItemImage(self.root, fldridx, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, fldropenidx, wx.TreeItemIcon_Expanded)
        #
        self.tree.Expand(self.root)
        
    def newtree(self,startstruct,icons):
        ##reference icons
        fldridx,fldropenidx,fileidx,fileidx2=0,1,2,3
        ##delete old tree
        self.tree.DeleteAllItems()
        ##new tree 
        self.root=self.tree.AddRoot("Start")
        #self.tree.SetPyData(self.root, None) # needed if I want to sort entries.
        self.tree.SetItemImage(self.root, fldridx, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, fldropenidx, wx.TreeItemIcon_Expanded)
        ##
        self._maketree(startstruct[2],self.root,icons)

    def _maketree(self,curdir,treepos,icons):
        ##reference icons
        fldridx,fldropenidx,fileidx,fileidx2=0,1,2,3
        for d in curdir['dirs']:
            item = self.tree.AppendItem(treepos,d[0])
            #self.tree.SetPyData(item, None) #not using this at the moment.
            self.tree.SetItemImage(item, fldridx, wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(item, fldropenidx, wx.TreeItemIcon_Expanded)
            self._maketree(d[2],item,icons) #recursion

        for f in curdir['files']:
            item = self.tree.AppendItem(treepos, f[0].rsplit('.',1)[0]) #os.path.splitext(file)[0])
            #self.tree.SetPyData(item, None) #not using this at the moment.
            imagedata = base64.b64decode(icons[f[1]][0])
            icon= wx.ImageFromData(16,16,imagedata)
            icon.SetAlphaData(base64.b64decode(icons[f[1]][1]))
            icon2=icon.ConvertToBitmap()
            iconindex = self.il.Add(icon2)
            self.tree.SetItemImage(item, iconindex, wx.TreeItemIcon_Normal)
            #self.tree.SetItemImage(item, fileidx2, wx.TreeItemIcon_Selected)
                                            
    def OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)

#---------------------------------------------------------------------------

#Setup frame and menubar
class MyFrame(wx.Frame):
    def __init__(self,parent,id):
        wx.Frame.__init__(self,parent,id,'startmenu snapshot',size=(400,200))
        self.CreateStatusBar()
        self.SetStatusText("applet for remembering old startmenus")
        
        ##
        
        menubar=wx.MenuBar()
        menu1=wx.Menu()
        menu1.Append(101,"&Open Saved Start Menu","open a saved startmenu")        
        menu1.Append(102,"&Show Current Start Menu","Show current user's startmenu")
        menu1.Append(103,"&Save Current Start Menu","save current user's startmenu to a file")
        menu1.Append(104,"&Quit","")
        menubar.Append(menu1,"&File")
        self.SetMenuBar(menubar)
        
        self.Bind(wx.EVT_MENU, self.OpenFile, id=101)
        self.Bind(wx.EVT_MENU, self.ShowStart, id=102)
        self.Bind(wx.EVT_MENU, self.SaveFile, id=103)
        self.Bind(wx.EVT_MENU, self.CloseWindow, id=104)
        
        ##
        self.treectrl=TreeCtrlPanel(self,wx.ID_ANY)
        
    def ShowStart(self,event):
        #progress bar
        AllUsers= os.path.expandvars('%ALLUSERSPROFILE%' +os.path.sep+'Start Menu')
        CurrentUsers=os.path.expandvars('%USERPROFILE%' +os.path.sep+'Start Menu')
        max=0
        for location in AllUsers,CurrentUsers:
            for root,dirs,files in os.walk(location):
                max+=len(files)
    
        dlg = wx.ProgressDialog("Loading Start Menu",
                "Loading Start Menu",
                maximum = max,
                parent=self,
                style =  wx.PD_ELAPSED_TIME
                            #|wx.PD_CAN_ABORT
                            #| wx.PD_APP_MODAL
                            #| wx.PD_ESTIMATED_TIME
                            #| wx.PD_REMAINING_TIME
                )
        
        startstruct,icons=save_start_menu(dlg=dlg)
        dlg.Destroy()
        
        self.treectrl.newtree(startstruct,icons)
    
    def OpenFile(self,event):
        dlg = wx.FileDialog(
            self, message="Choose a startmenu snapshot file to load",
            defaultDir=os.getcwd(), 
            style=wx.OPEN  | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            filepath=dlg.GetPath()
            #load from pickled file start menu structure
            fobj=file(filepath,'rb')
            startstruct=pickle.load(fobj)
            icons=pickle.load(fobj)
            fobj.close()
            self.treectrl.newtree(startstruct,icons)
        dlg.Destroy()
        
    def SaveFile(self,event):
        dlg = wx.FileDialog(
            self, message="Choose a filename to save to",
            defaultDir=os.getcwd(), 
            defaultFile="",
            style=wx.SAVE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            filepath=dlg.GetPath()
            startstruct,icons=save_start_menu()
            fobj=file(filepath,'wb')
            pickle.dump(startstruct,fobj)
            pickle.dump(icons,fobj)
            fobj.close()
            #save pickled file of start menu structure
        dlg.Destroy()
        
    def CloseWindow(self, event):
        self.Close()
        


#---------------------------------------------------------------------------
    
    
if __name__=="__main__":
    app=wx.App(False)
    frame=MyFrame(None,wx.ID_ANY)
    frame.Show(True)
    app.MainLoop()
    
    #import cProfile
    #cProfile.run("app.MainLoop()","profile0")
    
