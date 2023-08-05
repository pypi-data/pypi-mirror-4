from tw.dojo.core import DojoBase, DojoCSSLink
from tw.core import JSLink

tree_css = DojoCSSLink(
    basename = 'dijit/themes/tundra/Tree'
    )

dijit_css = DojoCSSLink(
    basename = 'dijit/themes/dijit'
)

#lazy_store_js = JSLink(modname='tw.dojo'
#                         'static/twdojo/LazyLoadStore.js')

class DojoTreeFilePicker(DojoBase):
    require = [
      "dojox.data.JsonRestStore",
      "dijit.Tree",
      "dijit.ColorPalette",
      "dijit.Menu",
      "dojo.parser",
    ]
    dojoType = 'dijit.Tree'
    params = ['id', 
              'attrs', 
              'jsId', 
              'cssclass', 
              'url'
              ]
    delayScroll = "true"
    css = [tree_css, dijit_css]
#    javascript = [lazy_store_js]
    cssclass=""
    rowsPerPage = 20
    columns = []
    columnReordering = "true"
    columnResizing="false"
    include_dynamic_js_calls = True
    action='.json'
    model = None
    actions = True
    template = "genshi:tw.dojo.templates.dojotreepicker"
    
class DojoTreeFileOnlyCheckboxPicker(DojoTreeFilePicker):
    require = [
      "dojox.data.JsonRestStore",
      "dijit.Tree",
      "dijit.ColorPalette",
      "dijit.Menu",
      "dojo.parser",
      "twdojo.CheckedTree",
    ]
    dojoType="twdojo.FileOnlyCheckedTree"
    template = "genshi:tw.dojo.templates.dojotreecheckboxpicker"
    
class DojoTreeCheckboxPicker(DojoTreeFilePicker):
    require = [
      "dojox.data.JsonRestStore",
      "dijit.Tree",
      "dijit.ColorPalette",
      "dijit.Menu",
      "dojo.parser",
      "twdojo.CheckedTree",
    ]
    dojoType="twdojo.CheckedTree"
    template = "genshi:tw.dojo.templates.dojotreecheckboxpicker"