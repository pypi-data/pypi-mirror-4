from tastypie.resources import ModelResource
from sorl.thumbnail import get_thumbnail
from pin.models import Post
from tastypie.paginator import Paginator

class PostResource(ModelResource):
    
    thumb_size = "100x100"
    
    class Meta:
        queryset = Post.objects.all().order_by('-id')
        resource_name = 'post'
        allowed_methods = ['get']
        paginator_class = Paginator
        
    def dispatch(self, request_type, request, **kwargs):
        self.thumb_size = request.GET.get('thumb_size', '100x100')
        #thumb_size = kwargs.pop('thumb_size')
        #print thumb_size
        
        return super(PostResource, self).dispatch(request_type, request, **kwargs)

    def dehydrate(self, bundle):
        print bundle
        id=bundle.data['id']
        o_image = bundle.data['image']
        im = get_thumbnail(o_image, self.thumb_size, crop='center', quality=99)
        bundle.data['thumbnail'] = im
        bundle.data['permalink'] = '/pin/%d/' % (int(id))
        
        return bundle
