from django.shortcuts import render
from django.http import JsonResponse
from .models import BasePictures
from django.views.decorators.http import require_http_methods

# Create your views here.
def picture_func(request):
    return render(request, "image-load.html")

@require_http_methods(["GET"])
def get_picture(request):

    picture_id = request.GET.get('picture', None)
    
    if picture_id:
        try:
            picture_id = int(picture_id) - 1
            picture = BasePictures.objects.get(picture_id=picture_id)
            return JsonResponse({'url': picture.url})
        except BasePictures.DoesNotExist:
            return JsonResponse({'error': 'Button not found'}, status=404)
    else:
        return JsonResponse({'error': 'No button name provided'}, status=400)