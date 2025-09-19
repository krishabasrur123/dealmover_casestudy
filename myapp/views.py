from django.shortcuts import render, HttpResponse
from .models import financial_info
from .forms import UploadPDFForm
from rest_framework.decorators import api_view
from .serializers import ExtractRequestSerializer
from rest_framework.response import Response
from django.http import HttpResponseBadRequest
from rest_framework import viewsets
import pdfplumber
import spacy
import regex as re

  
ITEM8_PATTERN = re.compile(
    r'Item\s+8[:.;]?\s*Financial Statements(?: and Supplementary Data)?[.:;]?\s+(\d{1,3})',
    re.IGNORECASE
)
revenue_keywords = [
    "revenue",
    "revenues",
    "net sales",
    "total revenue",
    "net operating revenues",
    "net operating revenue"
    "net revenue",
    "sales",
]
 
cost_keywords = [ "cost of sales ","cost of revenues"]



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

def extract_years(text):
    lines = text.split("\n")
    candidate_lines = []

    for line in lines:
        if re.search(r'(Fiscal|Year Ended|in millions)', line, re.IGNORECASE):
            candidate_lines.append(line)

    if not candidate_lines:
        candidate_lines = [line for line in lines if re.search(r'\b(19|20)\d{2}\b', line)]

    years = []
    for line in candidate_lines:
        found = re.findall(r'\b(19|20)\d{2}\b', line)
        years.extend(found)
    return years

def find_financial_terms(text, keyword_list):
    print("=== Searching for financial terms ===")
    nlp = spacy.load("en_core_web_md")

    # Normalize keywords to lowercase and convert to spaCy docs
    targets = [nlp(k.lower()) for k in keyword_list]

    # Split text into lines and filter relevant ones
    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip() and (re.search(r'\d', line) or 'Year Ended' in line)
    ]

    best_line = None
    best_score = 0.0
    found_years = []

    for line in lines:
        print("Original:", line)

       
        years_in_line = re.findall(r'\b(?:19|20)\d{2}\b', line)
        found_years.extend(years_in_line)

       
        line_clean = re.sub(r'[\d$.,:;()\[\]{}\-]+', '', line)
        print("Cleaned:", line_clean)

        line_doc = nlp(line_clean.lower())
        score = max(line_doc.similarity(t) for t in targets)

        if score > best_score:
            print("New best score:", score)
            best_line = line
            best_score = score

    
    matches = re.findall(r'\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?', best_line)
    cleaned = [re.sub(r'[^\d.]', '', m) for m in matches]
    

    return {
        "best_line": best_line,
        "values": cleaned[:3],
        "score": best_score,
        "years": found_years
    }
        

    




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

            if key == str(financial_statement_page_number):
                consolidated_statement_num = find_consolidated_statements(financial_statement_page_number, results)
                if not consolidated_statement_num:
                    print("Consolidated Statements not found")
                    return None

            if key == str(consolidated_statement_num):
                return results.get(str(consolidated_statement_num))
        return "Not Found"   
            
            




def revenue_cos_returns(data, period_end_date):
    year = str(period_end_date.year)
    result={}
    for key in ["revenue", "cost"]:
        years = data[key].get("years", [])
        values = data[key].get("values", [])

        if not years or not values:
            result[key] = f"Cannot be extracted: no {key} years or values found."
            continue

        if str(year) in years:
            idx = years.index(str(year))
            result[key] = values[idx]
        else:
            result[key] = f"Cannot be extracted: year {year} not found."

    return result


@api_view(['POST'])
def extract_view(request):
    serializer = ExtractRequestSerializer(data=request.data)
    if serializer.is_valid():
        uploaded_file = serializer.validated_data['file']
        period_end_date = serializer.validated_data.get('period_end_date')

        extracted_pages = handle_uploaded_file(uploaded_file, period_end_date)
        if not extracted_pages:
            return Response({"error": "Could not extract relevant pages."}, status=400)

        combined = {
            "revenue": find_financial_terms(extracted_pages, revenue_keywords),
            "cost": find_financial_terms(extracted_pages, cost_keywords)
        }

        output = revenue_cos_returns(combined, period_end_date)

        if period_end_date:
            output = revenue_cos_returns(combined, period_end_date)
        else:
            output = {
                "revenue": combined["revenue"].get("values", [None])[0],
                "cos": combined["cost"].get("values", [None])[0]
            }

        
        return Response({
            "period_end_date": str(period_end_date) if period_end_date else None,
            "results": {
                "revenue": output.get("revenue"),
                "cos": output.get("cost")
            }
        })
    return Response(serializer.errors, status=400)

