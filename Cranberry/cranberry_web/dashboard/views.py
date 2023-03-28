from django.shortcuts import render

# Create your views here.
def dashboard(request):
    return render(request, '/home/khj/catkin_ws/src/Cranberry/cranberry_web/dashboard/templates/index.html', {}) # 항목을 추가합니다.
    