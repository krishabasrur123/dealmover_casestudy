Here is a list of assumptions and doubts I had and what I did to solve them.

1. Whether revenue and cost of sales are always found under Item 8: Financial Statements and Supplementary Data, and would it always be in a table of content, and if other headlines would appear how they did in all other 10_K's, just like in the given 10-K 

Decision: I went with the standard strict outline of how a 10-K should be: a strict standard for finding revenue in a 10-K means only looking in Item 8 and then Consolidated Statements of Operations and extracting canonical line names like “Revenues,” “Total Revenues,” or “Cost of Revenues/Cost of Sales.” The parser must also match the exact period end date in the table and return an error if the values or labels are missing.

Limitations: Documents that don't match the standard format, for example they don't have a table of content where Item 8 is written, and a table of content for where consolidated statements of income is written, and may not have the years, page numbers, or financial details in the way my regex wanted is rejected.

2. Revenue and Cost of Sales can be described with various synonyms and how can we handle for that variability.

Decision: I used a open source python NLP library, that given a list of keywords, it scores the Consolidated Statements section to find the line that closely matches those keywords. For example if the keyword is revenue, we would match revenue, income more than any other words. 

Limitations: This approach relies heavily on the keyword list and the scoring method. If the 10-K uses an unusual synonym not included in the keywords (e.g., “Turnover” instead of “Revenue”), the model may miss it. Similarly, if multiple line items contain overlapping words (e.g., “Other Income”), the parser may incorrectly prioritize the wrong line.

3. Edge cases
What to do if the uploaded document is not a 10-K, is in an unsupported format, or doesn’t contain the requested end date.

Decision: If the file is not formatted according to the requirements (ex: not a 10-K pdf) we give a error in the form of an alert, and if the year is out of range, we give a error in the spreadsheet given back

Limitations: At times revenue and COS may be present in the document in a different format or style, but the parser would reject it and output a Error message.


4. Performance
How to optimize parsing speed

Decisions:
For the 10-K case study, I chose to use regex rather than a table parser because the structure of Item 8 and the Consolidated Statements of Operations is consistent enough that regex is both faster and simpler to implement. To avoid processing the entire PDF unnecessarily, I first locate the page numbers where the relevant sections appear and only parse those pages. I also explored optimizations such as multiprocessing and concurrency to speed up large-file parsing, but due to time constraints I was not able to fully implement them.

Limitations:
Parsing speed decreases significantly for large 10-K PDFs because even with targeted page extraction, regex still requires scanning through large text blocks. If the section headers are ambiguous or mis-extracted, the parser may fall back to reading more pages than necessary, further slowing performance.
