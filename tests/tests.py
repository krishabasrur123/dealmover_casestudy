import os
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile


from myapp.views import find_financial_terms
from myapp.views import find_item_8
from myapp.views import find_consolidated_statements
from myapp.views import handle_uploaded_file
from myapp.views import revenue_cos_returns
from myapp.views import extract_view
@pytest.fixture
def client():
    return APIClient()

def load_pdf(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, "rb") as f:
        return SimpleUploadedFile(filename, f.read(), content_type="application/pdf")

@pytest.fixture
def good_pdf():
    return load_pdf("good10k.pdf")

@pytest.fixture
def bad_pdf():
    return load_pdf("bad10k.pdf")


def test_extract_view_success(client, good_pdf):
    response = client.post(reverse("extract_view"), {"file": good_pdf})
    assert response.status_code == 200
    assert "results" in response.data
    assert "revenue" in response.data["results"]
    assert "cos" in response.data["results"]
    assert response.data["results"]["revenue"] is not None
    assert response.data["results"]["cos"] is not None


def test_values_properly_extracted(client, good_pdf):
    response = client.post(reverse("extract_view"), {"file": good_pdf})

    assert response.status_code == 200
    data = response.data

    assert isinstance(data, dict)

    assert data["period_end_date"] == [2022, 2023, 2024]
    assert data["results"]["revenue"] == ["282836", "307394", "350018"]
    assert data["results"]["cos"] == ["126203", "133332", "146306"] 




def test_revenue_extraction_test1():
    text = """
    Consolidated Statements of Income
    Year Ended 2022    $292,836.
    Year Ended 2023    $107,394?
    Year Ended 2024    $340,01.
    """
    result = find_financial_terms(text, ["revenue"])


    assert result["values"] != ["292836", "307394", "34001"]
    assert "2022" in result["years"]
    assert "2023" in result["years"]
    assert "2024" in result["years"]
    assert result["score"] > 0


def test_revenue_extraction_test2():
    text = """
    Consolidated Statements of Income
    Year Ended 2022    $292,836
    Year Ended 2023    $107,394
    Year Ended 2024    $340,01
    """
    result = find_financial_terms(text, ["revenue"])


    assert result["values"] != ["292836", "307394", "34001"]
    assert "2022" in result["years"]
    assert "2023" in result["years"]
    assert "2024" in result["years"]
    assert result["score"] > 0


def test_find_item_8_test1():
    results = {
        "10": "Item 8: Financial Statements                    15",
        "11": "Other content"
    }
    page = find_item_8(results)
    assert page == "15"

def test_find_item_8_test2():
    results = {
        "10": "Item 7: Management Discussion",
        "11": "Item 9: Changes in Accounting"
    }
    page = find_item_8(results)
    assert page is None


def test_find_consolidated_statements_test1():
    results = {
        "15": "Consolidated Statements of Earnings      Page 18"
    }
    page = find_consolidated_statements("15", results)
    assert page == "18"


def test_find_consolidated_statements_test2():
    results = {
        "15": "Consolidated Statements of Income      18."
    }
    page = find_consolidated_statements("15", results)
    assert page == "18"


def test_find_consolidated_statements_test3():
    results = {
        "15": "Consolidated Statements 18"
    }
    page = find_consolidated_statements("15", results)
    assert page != "18"