from ftw.colorbox.interfaces import IColorboxSettings
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.i18n import translate


class InitializeColorbox(BrowserView):

    def __call__(self):
        """ Generates the colorbox javascript code.
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IColorboxSettings)

        download_link = ''
        if settings.show_link:
            download_link = """
                var dl_link = link.attr('href').split('/');
                dl_link.pop(dl_link.lenght);
                link.attr('title', link.attr('title') +
                    " <a href='"+dl_link.join('/')+"/download_image'>%s</a>");
            """ % translate(u'download',
                            domain='ftw.colorbox',
                            context=self.request)

        return """
            function initializeSimplelayoutColorbox(element) {
                element.attr('rel', 'colorbox');
                element.colorbox({
                    %s
                });
            }
            jQuery(function($) {
                var link = jq('.sl-img-wrapper a');
                if (link.length !== 0){
                %s
                initializeSimplelayoutColorbox(link);
                }
            });
        """ % (
            ','.join(settings.colorbox_config),
            download_link)
