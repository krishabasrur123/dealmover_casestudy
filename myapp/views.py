from django.shortcuts import render, HttpResponse
from .models import financial_info
from .forms import UploadPDFForm
from .serializers import Financial_InfoSerializers
from django.http import HttpResponseBadRequest
from rest_framework import viewsets
import pdfplumber
import regex as re
import json

ITEM8_PATTERN = re.compile(
    r'Item\s+8[:.;]?\s*Financial Statements(?: and Supplementary Data)?[.:;]?\s+(\d{1,3})',
    re.IGNORECASE
)


TOC_PATTERN = re.compile(
    r'(Consolidated\s+Statements\s+of\s+(?:Income|Earnings|Operations|Profit\s+and\s+Loss))\s+(\d{1,3})',
    re.IGNORECASE
)

page_num_patterns = [
    re.compile(r'\bPage\s+(\d+)\b', re.IGNORECASE),
    re.compile(r'\b(\d+)\s+of\s+\d+\b', re.IGNORECASE),
    re.compile(r'^\s*(\d{1,3})[.)-]?\s*$', re.MULTILINE),
    re.compile(r'Form\s+10-K\s+(\d{1,3})\b', re.IGNORECASE)
]

def find_financial_section(results_dict):
    print("=== Searching for Item 8 ===")
    item8_page_num = None
    for key, text in results_dict.items():
        m = ITEM8_PATTERN.search(text)
        if m:
            item8_page_num = m.group(1)
            print(f"Found Item 8 on page {key} -> points to page {item8_page_num}")
            break
    if not item8_page_num:
        raise ValueError("Item 8 not found")

    print("=== Searching for Consolidated Statements after Item 8 ===")
    toc_page_num = None
    found_item8 = False
    for pg in sorted(results_dict.keys(), key=lambda x: int(re.sub(r'\D','0',x))):
        if pg == item8_page_num:
            found_item8 = True
        if found_item8:
            m = TOC_PATTERN.search(results_dict[pg] or "")
            if m:
                toc_page_num = m.group(2)
                print(f"Found TOC entry '{m.group(1)}' pointing to page {toc_page_num}")
                break
    if not toc_page_num:
        raise ValueError("Could not find Consolidated Statements section after Item 8")

    if toc_page_num not in results_dict:
        raise ValueError(f"Page {toc_page_num} not found in extracted pages")

    print(f"Returning text from page {toc_page_num}")
    return results_dict[toc_page_num]

def handle_uploaded_file(uploaded_file, end_date):
    results = {}
    with pdfplumber.open(uploaded_file) as pdf:
        for physical_index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            printed_number = None

            for pat in page_num_patterns:
                m = pat.search(text)
                if m:
                    printed_number = m.group(1)
                    break

            key = printed_number if printed_number else f"p{physical_index}"
            results[key] = text

            print(f"[DEBUG] Page {physical_index} => stored as key '{key}' (printed: {printed_number})")

    print(f"Total pages captured: {len(results)}")
    return results

def upload_file(request):
    if request.method == "POST":
        form = UploadPDFForm(request.POST, request.FILES)
        uploaded_file = request.FILES.get("file")

        if form.is_valid() and uploaded_file and uploaded_file.name.lower().endswith(".pdf"):
            period_end_date = form.cleaned_data.get("period_end_date")
            extracted_pages = handle_uploaded_file(uploaded_file, period_end_date)
            extracted_data = find_financial_section(extracted_pages)

            return HttpResponse(
                f"<h2>Extracted Text:</h2><pre>{json.dumps(extracted_data, indent=2, ensure_ascii=False)}</pre>"
            )
        else:
            return HttpResponseBadRequest("Invalid form or not a PDF file.")
    else:
        return render(request, "upload.html", {"form": UploadPDFForm()})

class Financial_InfoViewSet(viewsets.ModelViewSet):
    queryset = financial_info.objects.all()
    serializer_class = Financial_InfoSerializers
