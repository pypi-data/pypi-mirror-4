"""
    Implementations of form input controls
"""

import os

from forms import GetParam, UnpackParam, form

import wx
import wx.html


def TypeHandler(typeName):
    """ A metaclass generator. Returns a metaclass which
    will register it's class as the class that handles input type=typeName
    """
    def metaclass(name, bases, dict):
        klass = type(name, bases, dict)
        form.FormTagHandler.registerType(typeName.upper(), klass)
        return klass
    return metaclass


class FormControlMixin(object):
    """ Mixin provides some stock behaviors for
    form controls:
        Add self to the form fields
        Setting the name attribute to the name parameter in the tag
        Disabled attribute
        OnEnter and OnClick methods for binding by
        the actual control
    """
    def __init__(self, form, tag):
        if not form:
            return
        self.__form = form
        self.name = GetParam(tag, "NAME", None)
        form.fields.append(self)
        if tag.HasParam("DISABLED"):
            wx.CallAfter(self.Disable)

    def OnEnter(self, evt):
        self.__form.hitSubmitButton()

    def OnClick(self, evt):
        self.__form.submit(self if evt else None)


_ParentWindowObject = None
class SubmitButton(wx.Button, FormControlMixin):
    __metaclass__ = TypeHandler("SUBMIT")

    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        label = GetParam(tag, "VALUE", default="Submit Query")
        kwargs["label"] = label
        kwargs["style"] = wx.BU_EXACTFIT
        wx.Button.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        self.SetSize((int(GetParam(tag, "SIZE", default=-1)), -1))
        self.Path = None
        self.defaultPath = GetParam(tag, "PATH", default=os.path.expanduser('~'))
        if self.name:
            if self.name.lower().strip() == 'opendir':
                self.Bind(wx.EVT_BUTTON, self.OnClickOpenDir)
            elif self.name.lower().strip() == 'openfile':
                self.Bind(wx.EVT_BUTTON, self.OnClickOpenFile)
            elif self.name.lower().strip() == 'savefile':
                self.Bind(wx.EVT_BUTTON, self.OnClickSaveFile)
            else:
                self.Bind(wx.EVT_BUTTON, self.OnClick)
        else:
            self.Bind(wx.EVT_BUTTON, self.OnClick)

    def OnClickOpenDir(self, evt):
        global _ParentWindowObject
        _ParentWindowObject = self.Parent
        _ParentWindowObject.BlockRepaint()
        try:
            dialog = wx.DirDialog(self, "Choose a directory",
                style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON | wx.DD_DIR_MUST_EXIST,
                defaultPath = self.defaultPath,)
            if dialog.ShowModal() == wx.ID_OK:
                self.Path = dialog.GetPath()
            dialog.Destroy()
            _ParentWindowObject.UnblockRepaint()
            if self.Path is not None:
                self.OnClick(None)
        except:
            import traceback
            traceback.print_exc(500)
        finally:
            _ParentWindowObject.UnblockRepaint()

    def OnClickOpenFile(self, evt):
        global _ParentWindowObject
        _ParentWindowObject = self.Parent
        _ParentWindowObject.BlockRepaint()
        try:
            dialog = wx.FileDialog(self, "Select a file",
                style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
                defaultDir = os.path.dirname(UnpackParam(self.defaultPath, os.path.expanduser('~'))),
                defaultFile = os.path.basename(UnpackParam(self.defaultPath, os.path.expanduser('~'))),)
            if dialog.ShowModal() == wx.ID_OK:
                self.Path = dialog.GetPath()
            dialog.Destroy()
            _ParentWindowObject.UnblockRepaint()
            if self.Path is not None:
                self.OnClick(None)
        except:
            import traceback
            traceback.print_exc(500)
        finally:
            _ParentWindowObject.UnblockRepaint()

    def OnClickSaveFile(self, evt):
        global _ParentWindowObject
        _ParentWindowObject = self.Parent
        _ParentWindowObject.BlockRepaint()
        try:
            dialog = wx.FileDialog(self, "Select a filename and location",
                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                defaultDir = os.path.dirname(UnpackParam(self.defaultPath, os.path.expanduser('~'))),
                defaultFile = os.path.basename(UnpackParam(self.defaultPath, os.path.expanduser('~'))),
                )
            #dialog.SetFilename(os.path.basename(UnpackParam(self.defaultPath, os.path.expanduser('~'))))
            if dialog.ShowModal() == wx.ID_OK:
                self.Path = dialog.GetPath()
            dialog.Destroy()
            _ParentWindowObject.UnblockRepaint()
            if self.Path is not None:
                self.OnClick(None)
        except:
            import traceback
            traceback.print_exc(500)
        finally:
            _ParentWindowObject.UnblockRepaint()

    def GetValue(self):
        return self.Path


class TextInput(wx.TextCtrl, FormControlMixin):
    __metaclass__ = TypeHandler("TEXT")

    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        style = kwargs.get("style", 0)
        if tag.HasParam("READONLY"):
            style |= wx.TE_READONLY
        if form:
            style |= wx.TE_PROCESS_ENTER
        kwargs["style"] = style
        wx.TextCtrl.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self.SetValue(GetParam(tag, "VALUE", ''))
        ml = int(GetParam(tag, "MAXLENGTH", 0))
        self.SetMaxLength(ml)
        if ml and len(self.GetValue()) > ml:
            self.SetValue(self.GetValue()[:ml])
        if tag.HasParam("SIZE"):
            size = max(int(tag.GetParam("SIZE")), 5)
            width = self.GetCharWidth() * size
            self.SetSize((width, -1))


class PasswordInput(TextInput):
    __metaclass__ = TypeHandler("PASSWORD")

    def __init__(self, parent, form, tag, parser):
        TextInput.__init__(self, parent, form, tag, parser, style=wx.TE_PASSWORD)


class Checkbox(wx.CheckBox, FormControlMixin):
    __metaclass__ = TypeHandler("CHECKBOX")

    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        wx.CheckBox.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        self.value = GetParam(tag, "VALUE", "1")
        if tag.HasParam("checked"):
            self.SetValue(True)
        #self.SetLabel(self.value)

    def GetValue(self):
        if self.IsChecked():
            return self.value
        else:
            return None


class Radio(wx.RadioButton, FormControlMixin):
    __metaclass__ = TypeHandler("RADIO")

    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        self.value = GetParam(tag, "VALUE", "1")
        wx.RadioButton.__init__(self, parent, label=self.value, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        if tag.HasParam("checked"):
            self.SetValue(True)
        self.SetLabel(self.value)

    def GetValue(self):
        if wx.RadioButton.GetValue(self):
            return self.value
        else:
            return None


class HiddenControl(wx.EvtHandler, FormControlMixin):
    __metaclass__ = TypeHandler("HIDDEN")

    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        wx.EvtHandler.__init__(self)
        FormControlMixin.__init__(self, form, tag)
        self.value = GetParam(tag, "VALUE", "")
        self.enabled = True

    def GetValue(self):
        return self.value

    def Disable(self):
        self.enabled = False

    def IsEnabled(self):
        return self.enabled


class TextAreaInput(wx.TextCtrl, FormControlMixin):
    __metaclass__ = TypeHandler("TEXTAREA")

    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        style = wx.TE_MULTILINE
        if tag.HasParam("READONLY"):
            style |= wx.TE_READONLY
        wx.TextCtrl.__init__(self, parent, style=style)
        FormControlMixin.__init__(self, form, tag)
        if tag.HasEnding():
            src = parser.GetSource()[tag.GetBeginPos():tag.GetEndPos1()]
        else:
            src = ''
        self.SetFont(wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT))
        self.SetValue(src)
        cols = int(GetParam(tag, "COLS", 22))
        width = int(float(self.GetCharWidth()) * cols)
        rows = int(GetParam(tag, "ROWS", 3))
        height = int(float(self.GetCharHeight()) * rows)
        self.SetSize((width, height))



