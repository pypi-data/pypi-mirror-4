from django.contrib import messages
from django_helpers.apps.image_manager.forms import AddImageFormRenderer, AddImageForm, Image
from django_helpers.templatetags.static_manger import add_css_file, add_js_file, add_jquery, add_jquery_ui
from django_helpers.helpers.views import render_to_response, redirect

__author__ = 'ajumell'

add_jquery()
add_jquery_ui()
add_css_file('css/image-manager/main.css')

add_js_file('fancybox/jquery.fancybox.pack.js')
add_css_file('fancybox/jquery.fancybox.css')



def generate_token(param):
    return param


def index(request):
    if request.method == 'POST':
        form = AddImageForm(request.POST, request.FILES)
        print form.is_multipart()
        if form.is_valid():
            print 'Called...'
            form.save()
            messages.success(request, 'Image added successfully.')
            form = AddImageForm()
        else:
            pass
    else:
        form = AddImageForm()
    return render_to_response('image-manager/display-images.html', request, {
        'form': AddImageFormRenderer(form, request),
        'images': Image.objects.all()
    })


def delete_image(request, image_id, image_slug):
    token = generate_token("%s-%s" % (image_id, image_slug))
    image = Image.objects.get(id=image_id, name=image_slug)
    if request.method == 'POST':
        request_token = request.POST['token']
        if token == request_token:
            option = request.POST['submit']
            if option == 'yes':
                image.delete()
                messages.info(request, 'Image deleted.')
            else:
                messages.info(request, 'Image deletion cancelled.')
            return redirect(index)
        else:
            pass
    return render_to_response('image-manager/delete-confirm.html',request, {
        'token': token,
        'image': image
    })
