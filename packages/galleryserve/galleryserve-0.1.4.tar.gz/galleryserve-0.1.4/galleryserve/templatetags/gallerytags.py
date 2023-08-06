from django.template import Library, Node
from galleryserve.models import Item, Gallery

register = Library()
	
class GalleryserveNode(Node):
     def __init__(self, gallery_name):
          self.gallery_name = gallery_name
     def render(self, context):
          try:
              gallery = Gallery.objects.get(title=self.gallery_name)
              if gallery.random:
                  items = Item.objects.filter(gallery__title = gallery.title).order_by('?')
              else:
                  items = Item.objects.filter(gallery__title = gallery.title)
              context['gallery'] = items
          except:
              pass
          return ''
          
@register.tag('get_gallery')
def get_gallery(parser, token):
     bits = token.contents.split()
     if len(bits) != 2:
         raise TemplateSyntaxError, "get_gallery takes exactly 1 arguments"
     return GalleryserveNode(bits[1])
