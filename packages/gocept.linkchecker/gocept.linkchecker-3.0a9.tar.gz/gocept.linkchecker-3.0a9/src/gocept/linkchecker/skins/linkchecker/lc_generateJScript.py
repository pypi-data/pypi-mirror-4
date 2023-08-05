jscript = """
    function highlightBroken() {
          content = getContentArea();
          links = content.getElementsByTagName("a");
          for (i=0;i<links.length;i++) {
              link = links[i];
              link.style.color = link_colors[link.getAttribute('href')];
          }
    }

    registerPloneFunction(highlightBroken);

    link_colors = new Array();
"""

for link in context.portal_linkchecker.database.getLinksForObject(context):
    jscript += "link_colors['%s'] = '%s';\n" % (link.link, link.state)

return jscript
