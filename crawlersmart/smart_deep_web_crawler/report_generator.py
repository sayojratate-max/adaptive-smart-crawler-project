from pathlib import Path
from database import fetch_all_documents, fetch_document

OUTPUT_DIR = Path("output")
DOCS_DIR = OUTPUT_DIR / "docs"

def generate_report():
    OUTPUT_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)

    docs = fetch_all_documents()

    # Create detail pages
    for doc in docs:
        doc_id, source, title, summary, keywords, category = doc
        detail = fetch_document(doc_id)

        _, _, title_full, raw_text, summary_full, keywords_full, category_full = detail

        detail_html = f"""
        <html><head><title>{title_full}</title></head>
        <body>
        <h2>{title_full}</h2>
        <p><b>Source:</b> {source}</p>
        <p><b>Category:</b> {category_full}</p>
        <p><b>Keywords:</b> {keywords_full}</p>
        <h3>GenAI Summary</h3>
        <p>{summary_full}</p>
        <h3>Extracted Content</h3>
        <pre style="white-space: pre-wrap;">{raw_text}</pre>
        <a href="../report.html">⬅ Back</a>
        </body></html>
        """

        (DOCS_DIR / f"doc_{doc_id}.html").write_text(detail_html, encoding="utf-8")

    # Create main report
    rows_html = ""
    for doc in docs:
        doc_id, source, title, summary, keywords, category = doc
        rows_html += f"""
        <tr>
            <td>{doc_id}</td>
            <td><a href="docs/doc_{doc_id}.html">{title}</a></td>
            <td>{category}</td>
            <td>{keywords}</td>
            <td>{summary}</td>
        </tr>
        """

    report_html = f"""
    <html>
    <head>
        <title>Smart Deep Web Crawler Report</title>
    </head>
    <body>
        <h1>Smart Deep Web Crawler (GenAI Harvesting)</h1>
        <p><b>Total Documents:</b> {len(docs)}</p>

        <table border="1" cellpadding="8" cellspacing="0">
            <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Category</th>
                <th>Keywords</th>
                <th>GenAI Summary</th>
            </tr>
            {rows_html}
        </table>
    </body>
    </html>
    """

    (OUTPUT_DIR / "report.html").write_text(report_html, encoding="utf-8")

    print("✅ Report generated: output/report.html")
