from django.shortcuts import render, HttpResponse, redirect
from .models import financial_info
from .forms import UploadPDFForm
from .serializers import Financial_InfoSerializers
from django.http import HttpResponseBadRequest

from rest_framework import viewsets
import PyPDF2


# render http pages

def handle_uploaded_file(uploaded_file, end_date):
    reader = PyPDF2.PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""
    return full_text


def upload_file(request, ):
    if request.method == "POST":
        form = UploadPDFForm(request.POST, request.FILES)
        uploaded_file = request.FILES["file"]
        if form.is_valid() and uploaded_file.name.lower().endswith('.pdf'):
            period_end_date = form.cleaned_data.get("period_end_date")

            extracted_text = handle_uploaded_file(request.FILES["file"], period_end_date)

            return HttpResponse(f"<h2>Extracted Text:</h2><pre>{extracted_text}</pre>")
        else:
            return HttpResponseBadRequest("Invalid form or not a PDF file.")
        
    else:
        
        return render(request, "upload.html", {"form": UploadPDFForm()})


class Financial_InfoViewSet(viewsets.ModelViewSet):
     queryset= financial_info.objects.all()
     serializer_class = Financial_InfoSerializers

