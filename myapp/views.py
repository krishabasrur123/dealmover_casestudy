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

page_num_patterns = re.compile(
    r"""
    \bPage\s+(\d+)\b |               # Captures "Page 12"
    \b(\d+)\s+of\s+\d+\b |           # Captures "12 of 50"
    ^\s*(\d{1,3})[.)-]?\s*$ |        # Captures "12.", "12)", "12-"
    Form\s+10-K\s+(\d{1,3})\b        # Captures "Form 10-K 12"
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE
)


def find_item_8(results_dict):
    print("=== Searching for Item 8 ===")
    financial_statements_page_num = None
    for key, page in results_dict.items():
        item8_text = ITEM8_PATTERN.search(page)
        if item8_text:
            financial_statements_page_num = item8_text.group(1)
            print(f"Found Item 8 on page {key} -> points to page {financial_statements_page_num}")
            break
    
    return financial_statements_page_num 

def find_consolidated_statements(financial_statement_page_number, results_dict):
    print("=== Searching for Consolidated Statements after Item 8 ===")
    consolidated_table_of_content_page_num = None
    found_financial_statements = None
    page_content = results_dict.get(financial_statement_page_number)
        

    m = TOC_PATTERN.search(page_content or "")
    if m:
        consolidated_table_of_content_page_num = m.group(2)
        print(f"Found TOC entry '{m.group(1)}' pointing to page {consolidated_table_of_content_page_num}")
    return consolidated_table_of_content_page_num
    
def handle_uploaded_file(uploaded_file, end_date):
    results = {}
    financial_statement_page_number=None
    consolidated_statement_num=None
    # Step 1 — read all pages into results
    with pdfplumber.open(uploaded_file) as pdf:
        for physical_index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            m = page_num_patterns.search(text)
            if m:
                printed_number = next((g for g in m.groups() if g), None)
            else:
                printed_number = None
            key = printed_number if printed_number else f"p{physical_index}"
            results[key] = text
            print(f"[DEBUG] Page {physical_index} => stored as key '{key}' (printed: {printed_number})")

    
            if key == "10" :
                financial_statement_page_number = find_item_8(results)
                if not financial_statement_page_number:
                    print("Item 8 not found")
                    return None

    # Step 3 — find the consolidated statements page number
            if key == str(financial_statement_page_number):
                consolidated_statement_num = find_consolidated_statements(financial_statement_page_number, results)
                if not consolidated_statement_num:
                    print("Consolidated Statements not found")
                    return None

    # Step 4 — return that page's text
            if key == str(consolidated_statement_num):
                return results.get(str(consolidated_statement_num))
        return "Not Found"   
            
            



    

def upload_file(request):
    if request.method == "POST":
        form = UploadPDFForm(request.POST, request.FILES)
        uploaded_file = request.FILES.get("file")

        if form.is_valid() and uploaded_file and uploaded_file.name.lower().endswith(".pdf"):
            period_end_date = form.cleaned_data.get("period_end_date")
            extracted_pages = handle_uploaded_file(uploaded_file, period_end_date)

            return HttpResponse(
                f"<h2>Extracted Text:</h2><pre>{json.dumps(extracted_pages, indent=2, ensure_ascii=False)}</pre>"
            )
        else:
            return HttpResponseBadRequest("Invalid form or not a PDF file.")
    else:
        return render(request, "upload.html", {"form": UploadPDFForm()})

class Financial_InfoViewSet(viewsets.ModelViewSet):
    queryset = financial_info.objects.all()
    serializer_class = Financial_InfoSerializers
