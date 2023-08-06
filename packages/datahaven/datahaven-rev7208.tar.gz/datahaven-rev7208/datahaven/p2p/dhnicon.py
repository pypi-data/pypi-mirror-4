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

_IconsDict = {
    'red':      'icon-red.png',
    'green':    'icon-green.png',
    'gray':     'icon-gray.png',
    'yellow':   'icon-yellow.png',
}

#------------------------------------------------------------------------------ 

def init(icons_path, icons_dict):
    global _IconObject
    global USE_TRAY_ICON
    if not USE_TRAY_ICON:
        return

    import wx
    
    from twisted.internet import reactor


    def create_menu_item(menu, label, func, icon=None):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        if icon is not None:
            item.SetBitmap(wx.Bitmap(icon))
        menu.AppendItem(item)
        return item
    
    def icons_dict():
        global _IconsDict
        return _IconsDict
    
    class MyTaskBarIcon(wx.TaskBarIcon):
        def __init__(self, icons_path, current_icon_name=None):
            super(MyTaskBarIcon, self).__init__()
            self.icons_path = icons_path
            self.icons = {}
            for name, filename in icons_dict().items():
                self.icons[name] = wx.IconFromBitmap(wx.Bitmap(os.path.join(icons_path, filename)))
            if len(self.icons) == 0:
                self.icons['default'] = ''
            if current_icon_name is not None and current_icon_name in self.icons.keys():
                self.current = current_icon_name
            else:                
                self.current = self.icons.keys()[0]
            self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
            self.select_icon(self.current)

        def items_dict(self):
            return {
                'show':     os.path.join(self.icons_path, 'expand24x24.png'),
                'hide':     os.path.join(self.icons_path, 'collapse24x24.png'),
                'restart':  os.path.join(self.icons_path, 'restart24x24.png'), 
                'shutdown': os.path.join(self.icons_path, 'shutdown24x24.png'),}
        
        def CreatePopupMenu(self):
            menu = wx.Menu()
            icons = self.items_dict()
            create_menu_item(menu, 'show', self.on_show, icons.get('show', None))
            create_menu_item(menu, 'hide', self.on_hide, icons.get('hide', None))
            menu.AppendSeparator()
            create_menu_item(menu, 'restart', self.on_restart, icons.get('restart', None))
            create_menu_item(menu, 'shutdown', self.on_exit, icons.get('shutdown', None))
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
      
      
def state_changed(network, p2p, central):
    if 'DISCONNECTED' in [ network, p2p ]:
        set('gray')
        return
    if [ network, p2p, central ].count('CONNECTED') == 3:
        set('green')
        return
    set('gray')


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
    init(sys.argv[1])
    SetControlFunc(test_control)
    reactor.run()
    
    
    
