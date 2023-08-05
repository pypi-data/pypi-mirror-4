#!/usr/bin/python
#dhnicon.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#

import os
import sys

USE_TRAY_ICON = True
LABEL = 'DataHaven.NET'
    
_IconObject = None
_ControlFunc = None

#------------------------------------------------------------------------------ 

def init(icons_path, icons_dict):
    global _IconObject
    global USE_TRAY_ICON
    if not USE_TRAY_ICON:
        return

    import wx
    
    from twisted.internet import reactor


    def create_menu_item(menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item
    
    
    class MyTaskBarIcon(wx.TaskBarIcon):
        def __init__(self, icons_path, icons_dict, current_icon_name=None):
            super(MyTaskBarIcon, self).__init__()
            self.icons = {}
            for name, filename in icons_dict.items():
                self.icons[name] = wx.IconFromBitmap(wx.Bitmap(os.path.join(icons_path, filename)))
            if len(self.icons) == 0:
                self.icons['default'] = ''
            if current_icon_name is not None and current_icon_name in self.icons.keys():
                self.current = current_icon_name
            else:                
                self.current = self.icons.keys()[0]
            self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
            self.select_icon(self.current)
        
        def CreatePopupMenu(self):
            menu = wx.Menu()
            create_menu_item(menu, 'show', self.on_show)
            create_menu_item(menu, 'hide', self.on_hide)
            menu.AppendSeparator()
            create_menu_item(menu, 'restart', self.on_restart)
            create_menu_item(menu, 'shutdown', self.on_exit)
            self.menu = menu
            return menu

        def on_left_down(self, event):
            control('show')
            
        def on_show(self, event):
            control('show')
            
        def on_hide(self, event):
            control('hide')
            
        def on_restart(self, event):
            control('restart')
            
        def on_exit(self, event):
            control('exit')
            
        def select_icon(self, icon_name):
            if icon_name in self.icons.keys():
                self.current = icon_name
                self.SetIcon(self.icons.get(self.current, self.icons.values()[0]), LABEL)
                    
    class MyApp(wx.App):
        def __init__(self, icons_path, icons_dict):
            self.icons_path = icons_path
            self.icons_dict = icons_dict
            wx.App.__init__(self, False)
            
        def OnInit(self):
            self.trayicon = MyTaskBarIcon(self.icons_path, self.icons_dict)
            return True
        
        def OnExit(self):
            self.trayicon.Destroy() 
            
        def SetIcon(self, name):
            self.trayicon.select_icon(name)
    
        
    _IconObject = MyApp(icons_path, icons_dict) 
    reactor.registerWxApp(_IconObject)


def control(cmd):
    global _ControlFunc
    if _ControlFunc is not None:
        _ControlFunc(cmd)


def set(name):
    global _IconObject
    if _IconObject is not None:
        _IconObject.SetIcon(name)
        

def SetControlFunc(f):
    global _ControlFunc
    _ControlFunc = f

#------------------------------------------------------------------------------ 

if __name__ == "__main__":
    def test_control(cmd):
        print cmd
        if cmd == 'exit':
            reactor.stop()
        
    from twisted.internet import wxreactor
    wxreactor.install()
    from twisted.internet import reactor
    icons_dict = {
            'red':      'icon-red.png',
            'green':    'icon-green.png',
            'gray':     'icon-gray.png',
            }
    init(sys.argv[1], icons_dict)
    SetControlFunc(test_control)
    reactor.run()
    
    
    
