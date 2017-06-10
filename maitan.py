#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
try:
  import os
except:
  print >> sys.stderr, 'Error(@import os)'
  sys.exit(1)

try:
  import subprocess
except:
  print >> sys.stderr, 'Error(@import subprocess)'
  sys.exit(1)

try:
  import tempfile
except:
  print >> sys.stderr, 'Error(@import tempfile)'
  sys.exit(1)

try:
  import shutil 
except:
  print >> sys.stderr, 'Error(@import shutil)'
  sys.exit(1)

try:
  import pygtk
except:
  print >> sys.stderr, 'Error(@import pygtk): PyGTK is not installed'
  sys.exit(1)

try:
  pygtk.require('2.0')
except:
  print >> sys.stderr, 'Error(@import pygtk.require(2.0)): PyGTK is not installed'
  sys.exit(1)

try:
  import gtk
except:
  print >> sys.stderr, 'Error(@import gtk): PyGTK is not installed'
  sys.exit(1)
if gtk.pygtk_version < (2,2,0):
  print >> sys.stderr, 'PyGTK >= 2.2.0 required'
  sys.exit(1)


class LaTeXCompiler:
  """
  LaTeX Compilers
  """
  def __init__(self):
    self.latex_command="latex"
    self.latex_option="-halt-on-error -interaction=nonstopmode"
    self.dvipng_command="dvipng"
    self.dvipng_option="-T tight -bg Transparent"


  def cdAndExact(self,dirname,cmd):
    p=subprocess.Popen(cmd, shell=True, cwd=dirname,stdout=subprocess.PIPE, stderr=subprocess.PIPE,close_fds=True)
    (out,err)=p.communicate()
    return (p.returncode,dirname,cmd,out,err)

  def tex2png(self,dirname,filename):
    log=[]

    base,ext=os.path.splitext(filename)
    cmd=self.latex_command+" "+self.latex_option+" "+base
    result=self.cdAndExact(dirname,cmd)
    log.append(result)
    if result[0]==0:
      cmd=self.dvipng_command+" "+self.dvipng_option+" "+base
      result=self.cdAndExact(dirname,cmd)
      log.append(result)
      if result[0]==0:
        return (dirname,base+"1.png",log)
      else:
        return (dirname,None,log)
    else:
      return (dirname,None,log)


class MaitanSettingDialog(gtk.Dialog):
  def __init__(self, setup,title=None, parent=None, flags=gtk.DIALOG_MODAL,
               buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)):
    gtk.Dialog.__init__(self, title, parent, flags, buttons)
    page = []
    tabs = ("Document", "Compile Option")
    note = gtk.Notebook()
    for i in range(len(tabs)):
      page.append(gtk.VBox())
      note.append_page(page[i], gtk.Label(tabs[i]))

    textbuf=gtk.TextBuffer()
    textbuf.set_text(setup.preamble)
    self.textbuf_preamble = textbuf 
    textview = gtk.TextView(textbuf)
    textview.set_wrap_mode(gtk.WRAP_CHAR)
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    sw.add(textview)
    page[0].pack_start(sw)
    page[0].pack_start(gtk.HSeparator())

    textbuf=gtk.TextBuffer()
    textbuf.set_text(setup.begin_document)
    self.textbuf_begin_document = textbuf 
    textview = gtk.TextView(textbuf)
    textview.set_wrap_mode(gtk.WRAP_CHAR)
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    sw.add(textview)
    page[0].pack_start(sw)
    page[0].pack_start(gtk.HSeparator())

    textbuf=gtk.TextBuffer()
    textbuf.set_text(setup.default_document)
    self.textbuf_default_document = textbuf 
    textview = gtk.TextView(textbuf)
    textview.set_wrap_mode(gtk.WRAP_CHAR)
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    sw.add(textview)
    page[0].pack_start(sw)
    page[0].pack_start(gtk.HSeparator())

    textbuf=gtk.TextBuffer()
    textbuf.set_text(setup.end_document)
    self.textbuf_end_document = textbuf 
    textview = gtk.TextView(textbuf)
    textview.set_wrap_mode(gtk.WRAP_CHAR)
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    sw.add(textview)
    page[0].pack_start(sw)

    frame=gtk.Frame("LaTeX")
    page[1].pack_start(frame)
    vbox=gtk.VBox()
    frame.add(vbox)
    hbox=gtk.HBox()
    vbox.pack_start(hbox)
    hbox.pack_start(gtk.Label("Command: "),expand=False, fill=False)
    self.entry_latex_command = gtk.Entry()
    hbox.pack_start(self.entry_latex_command)
    self.entry_latex_command.set_text(setup.latex_command)

    hbox=gtk.HBox()
    vbox.pack_start(hbox)
    hbox.pack_start(gtk.Label("Default Options: "),expand=False, fill=False)
    self.entry_latex_options = gtk.Entry()
    hbox.pack_start(self.entry_latex_options)
    self.entry_latex_options.set_text(setup.latex_options)

    frame=gtk.Frame("Dvi2png")
    page[1].pack_start(frame)
    vbox=gtk.VBox()
    frame.add(vbox)
    hbox=gtk.HBox()
    vbox.pack_start(hbox)
    hbox.pack_start(gtk.Label("Command: "),expand=False, fill=False)
    self.entry_dvipng_command = gtk.Entry()
    hbox.pack_start(self.entry_dvipng_command)
    self.entry_dvipng_command.set_text(setup.dvipng_command)


    (op,res)=("-D",340)
    if "resolution" in setup.dvipng_options:
      (op,res)=setup.dvipng_options["resolution"]
    hbox=gtk.HBox()
    vbox.pack_start(hbox)
    hbox.pack_start(gtk.Label("Resolution: "), expand=False, fill=False)
    self.entry_dvipng_resolution_option = gtk.Entry()
    hbox.pack_start(self.entry_dvipng_resolution_option)
    self.entry_dvipng_resolution_option.set_text(op)
    self.resolution=gtk.Adjustment(value=res,lower=8, upper=20000, step_incr=50)
    sb=gtk.SpinButton(self.resolution)
    hbox.pack_start(sb)

    hbox=gtk.HBox()
    vbox.pack_start(hbox)
    hbox.pack_start(gtk.Label("Options: "),expand=False, fill=False)
    self.entry_dvipng_options = gtk.Entry()
    hbox.pack_start(self.entry_dvipng_options)
    if "userdefinedoptions" in setup.dvipng_options:
      self.entry_dvipng_options.set_text(setup.dvipng_options["userdefinedoptions"])

    self.vbox.pack_start(note)
    self.show_all()
  def get_values(self):
    r={}
    textbuf=self.textbuf_preamble
    r["preamble"]=textbuf.get_text(textbuf.get_start_iter(),textbuf.get_end_iter())
    textbuf=self.textbuf_begin_document
    r["begin_document"]=textbuf.get_text(textbuf.get_start_iter(),textbuf.get_end_iter())
    textbuf=self.textbuf_default_document
    r["default_document"]=textbuf.get_text(textbuf.get_start_iter(),textbuf.get_end_iter())
    textbuf=self.textbuf_end_document
    r["end_document"]=textbuf.get_text(textbuf.get_start_iter(),textbuf.get_end_iter())

    r["latex_command"]=self.entry_latex_command.get_text()
    r["latex_options"]=self.entry_latex_options.get_text()
    r["dvipng_command"]=self.entry_dvipng_command.get_text()
    r["dvipng_options"]=self.entry_dvipng_options.get_text()
    r["dvipng_resolution"]=(self.entry_dvipng_resolution_option.get_text(),self.resolution.get_value())
    return r

class MaitanMainWindow(gtk.Window):
  def __init__(self,maitansetup,*args, **kwargs):
    gtk.Window.__init__(self,*args, **kwargs)

    if(maitansetup):
      self.setup=maitansetup
    else:
      self.setup=MaitanSetup()

    accelgroup = gtk.AccelGroup()
    self.add_accel_group(accelgroup)
    item_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT, accelgroup)
    menu_file = gtk.Menu()
    menu_file.add(item_quit)
    self.item_file = gtk.MenuItem('_File')
    self.item_file.props.submenu = menu_file
    menubar = gtk.MenuBar()
    menubar.append(self.item_file)

    self.textbuf = gtk.TextBuffer()
    self.textbuf.set_text(self.setup.get_default_document())
    self.textview = gtk.TextView(self.textbuf)
    self.textview.set_wrap_mode(gtk.WRAP_CHAR)
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    sw.add(self.textview)

    self.button_cut = gtk.Button(stock=gtk.STOCK_EXECUTE)
    self.button_paste = gtk.Button(stock=gtk.STOCK_PREFERENCES)
    self.button_clear = gtk.Button(stock=gtk.STOCK_CLEAR)

    notebook = gtk.Notebook()
    notebook.set_tab_pos(gtk.POS_BOTTOM)

    vbox_img = gtk.VBox()  
    notebook.append_page(vbox_img,gtk.Label("Image"))

    hbox_imgctl = gtk.HBox() 
    self.zoom_ratio=gtk.Adjustment(value=30,lower=5, upper=200, step_incr=5)
    self.zoom_ratio.connect('value-changed', self.draw_image)
    sb=gtk.SpinButton(self.zoom_ratio)
    hbox_imgctl.pack_end(sb, expand=False, fill=False)
    hbox_imgctl.pack_end(gtk.Label("Zoom for preview (%): "), expand=False, fill=False)

    self.image = gtk.Image()
    self.image_exists=False
    self.image.set_from_stock(gtk.STOCK_DIALOG_ERROR,gtk.ICON_SIZE_DIALOG)

    self.imagebuf=None

    sw_img = gtk.ScrolledWindow()
    sw_img.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    sw_img.add_with_viewport(self.image)

    vbox_img.pack_start(sw_img, expand=True, fill=True)
    vbox_img.pack_start(hbox_imgctl, expand=False, fill=False)

    self.textbuf_log = gtk.TextBuffer()
    self.textview_log = gtk.TextView(self.textbuf_log)
    self.textview_log.set_wrap_mode = gtk.WRAP_CHAR
    self.textview_log.set_editable(False)

    sw_log = gtk.ScrolledWindow()
    sw_log.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    sw_log.add(self.textview_log)
    notebook.append_page(sw_log,gtk.Label("Log"))

    hbox_btn = gtk.HButtonBox()  
    hbox_btn.pack_start(self.button_cut, expand=False, fill=False)
    hbox_btn.pack_start(self.button_clear, expand=False, fill=False)
    hbox_btn.pack_start(self.button_paste, expand=False, fill=False)

    box = gtk.VBox(spacing=3)  

    box.pack_start(sw)
    box.pack_start(hbox_btn, expand=False, fill=False)

    paned=gtk.VPaned()
    paned.add1(box)
    paned.add2(notebook)

    vbox = gtk.VBox()  
    vbox.pack_start(menubar, expand=False, fill=False)
    vbox.pack_start(paned)

    self.clipboard = gtk.Clipboard()
    self.clipboard_primary = gtk.Clipboard(selection='PRIMARY')
    self.connect('delete_event', gtk.main_quit)
    item_quit.connect('activate', gtk.main_quit)
    self.button_cut.connect('clicked', self.on_button_cut_clicked)
    self.button_paste.connect('clicked', self.on_button_paste_clicked)
    self.button_clear.connect('clicked', self.on_button_clear_clicked)
#    self.clipboard.connect('owner-change', self.on_clipboard_owner_change)
    self.add(vbox)
    self.set_size_request(350, 300)

  def on_button_cut_clicked(self, widget):
    dirname=tempfile.mkdtemp()
    filename="x2.tex"
    body=self.textbuf.get_text(self.textbuf.get_start_iter(),self.textbuf.get_end_iter())
    f = open(os.path.join(dirname,filename), 'w')
    f.write(self.setup.get_tex_document(body))
    f.close()
    (dirname,pngfile,log)=self.setup.latex_compiler.tex2png(dirname,filename)
    self.textbuf_log.set_text("\n".join([dirname+"$"+str(val)+"$ "+cmd+"\n"+result+"\n"+val2+"\n" for (val,dirname,cmd,val2,result) in log]))
    if pngfile:
      self.image_exists=True
      self.pixbuf=gtk.gdk.pixbuf_new_from_file(os.path.join(dirname,pngfile))
      self.clipboard.set_image(self.pixbuf)
      self.clipboard_primary.set_image(self.pixbuf)
      self.draw_image(self)
    else:
      self.image_exists=False
      self.image.set_from_stock(gtk.STOCK_DIALOG_ERROR,gtk.ICON_SIZE_DIALOG)
      self.clipboard.set_text("")
    shutil.rmtree(dirname)

  def draw_image(self, widget):
    if self.image_exists:
      r=self.zoom_ratio.get_value()
      w=int(self.pixbuf.get_width()*r/100)
      h=int(self.pixbuf.get_height()*r/100)
      if w>0 and h>0:
        pixb=self.pixbuf.scale_simple(w,h, gtk.gdk.INTERP_BILINEAR)
        self.image.set_from_pixbuf(pixb)

  def on_button_paste_clicked(self, widget):
    dlg = MaitanSettingDialog(self.setup,"Title", self)
    try:
      if dlg.run() == gtk.RESPONSE_ACCEPT:
        val=dlg.get_values()
        self.setup.setup_by_dictionary(val)
    finally:
      dlg.destroy()
  def on_button_clear_clicked(self, widget):
    self.textbuf.set_text(self.setup.get_default_document())



class MaitanSetup:
  def __init__(self):
    self.set_as_default()

  def load_from_file(self,setupfiledir):
    pass
  def save_to_file(self,setupfiledir):
    pass

  def get_tex_document(self,document):
    r=self.preamble+"\n"+self.begin_document+"\n"+document+"\n"+self.end_document
    return r
  def get_default_document(self):
    return self.default_document
  def setup_by_dictionary(self,dic):
    key="preamble"
    if key in dic:
      self.preamble=dic[key]
    key="begin_document"
    if key in dic:
      self.begin_document=dic[key]
    key="end_document"
    if key in dic:
      self.end_document=dic[key]
    key="default_document"
    if key in dic:
      self.default_document=dic[key]

#    latex_compiler setup
    key="latex_command"
    if key in dic:
      self.latex_command=dic[key]
      self.latex_compiler.latex_command=dic[key]
    key="latex_options"
    if key in dic:
      self.latex_options=dic[key]
      self.latex_compiler.latex_option=self.latex_options
    key="dvipng_command"
    if key in dic:
      self.dvipng_command=dic[key]
      self.latex_compiler.dvipng_command=dic[key]
    key="dvipng_options"
    if key in dic:
      self.dvipng_options["userdefinedoptions"]=dic[key]
    key="dvipng_resolution"
    if key in dic:
      self.dvipng_options["resolution"]=dic[key]

    options=[]
    if "resolution" in self.dvipng_options:
      (op,res)=self.dvipng_options["resolution"]
      options.append(op+" "+str(res))
    if "userdefinedoptions" in self.dvipng_options:
      options.append(self.dvipng_options["userdefinedoptions"])
    self.latex_compiler.dvipng_option=" ".join(options)


  def set_as_default(self):
    self.latex_compiler=LaTeXCompiler()
    self.dvipng_options={}
    dic={"preamble":"\\documentclass{amsart}\n\\newcommand{\\RR}{\\mathbb{R}}\n\\usepackage{color}\n\\newcommand{\\dummybaseline}[1][j]{{\\color{white}\\setbox0=\\hbox{#1}\\rule[-\\the\\dp0]{0.01pt}{0.01pt}}}",
     "begin_document":"\\begin{document}\n\\thispagestyle{empty}",
     "default_document":"\\begin{align*}\nA\n\\dummybaseline\\end{align*}",
     "end_document":"\\end{document}",
     "latex_command":"latex",
     "latex_options":"-halt-on-error -interaction=nonstopmode",
     "dvipng_command":"dvipng",
     "dvipng_options":"-T tight -bg Transparent",
     "dvipng_resolution": ("-D", 340)
     }
    #-D150 300 600 1200
    self.setup_by_dictionary(dic)


if __name__ == '__main__':
  maitansetup=MaitanSetup()
#  setupfiledir=
#  maitansetup.load_from_file(setupfiledir)
  win = MaitanMainWindow(maitansetup)
  win.show_all()
  gtk.main()
#  maitansetup.save_to_file(setupfiledir)

