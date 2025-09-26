from fpdf import FPDF
from openai import OpenAI
from utils import load_config
from datetime import datetime
import matplotlib.pyplot as plt


cfg = load_config()
client = OpenAI(api_key=cfg["openai_api_key"])

def aggregate_metrics(df):
    metrics = {}
    metrics["Total Revenue"] = df["Revenue"].sum()
    metrics["Total Orders"] = len(df)
    metrics["Average Order Value"] = df["Revenue"].mean()
    metrics["Total Quantity"] = df["Quantity"].sum()
    metrics["Top Products"] = df.groupby("ProductName")["Revenue"].sum().sort_values(ascending=False).head(5)
    metrics["Least Products"] = df.groupby("ProductName")["Revenue"].sum().sort_values(ascending=True).head(5)
    metrics["Top Cities"] = df.groupby("CityName")["Revenue"].sum().sort_values(ascending=False).head(5)
    metrics["Least Cities"] = df.groupby("CityName")["Revenue"].sum().sort_values(ascending=True).head(5)
    metrics["Top Salespersons"] = df.groupby("SalesPersonName")["Revenue"].sum().sort_values(ascending=False).head(5)
    return metrics

def compare_months(current_metrics, prev_metrics):
    comparison = {}
    for key in ["Total Revenue", "Total Orders", "Average Order Value"]:
        prev_val = prev_metrics.get(key, 0)
        curr_val = current_metrics.get(key, 0)
        diff = curr_val - prev_val
        perc = (diff / prev_val * 100) if prev_val != 0 else 0
        comparison[key] = {"current": curr_val, "previous": prev_val, "diff": diff, "percent_change": perc}
    return comparison

def plot_top_products(df, output_path="top_products.png"):
    top_products = (
        df.groupby("ProductName")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    plt.figure(figsize=(6, 4))
    top_products.plot(kind="bar", color="skyblue")
    plt.title("Top 5 Products by Revenue")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path

def generate_nl_report(current_df, prev_df):
    current_metrics = aggregate_metrics(current_df)
    prev_metrics = aggregate_metrics(prev_df)
    comparison = compare_months(current_metrics, prev_metrics)

    prompt = f"""
    Write a professional monthly sales report for Jay Grocery Store.
    Structure it with these sections:

    1. Executive Summary (1–2 concise paragraphs)
    2. Key Metrics Overview (present as a formatted table)
    3. Top 5 Products, Least 5 Products
    4. Top 5 Cities, Least 5 Cities
    5. Top 5 Salespersons
    6. Month-over-Month Comparison (clear narrative + numbers)
    7. Strategic Recommendations (bullet points, actionable)

    Use a formal, polished tone. Avoid casual phrases.
    Current month metrics: {current_metrics}
    Previous month metrics: {prev_metrics}
    Comparison: {comparison}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior business analyst at a consulting firm. "
                    "Your job is to write highly professional, concise, and structured business reports. "
                    "The tone must be formal, with clear section headings, tables, and bullet points when needed."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
    )

    return response.choices[0].message.content


def sanitize_text(text):
    """Sanitize text for FPDF by replacing unsupported characters with '?'."""
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_report(report_text, charts=None, output_path="Business_Report.pdf"):
    month_year = datetime.today().strftime("%B %Y")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 10, sanitize_text(f"Monthly Sales Report for {month_year}"), 0, 1, 'C')

    pdf.set_font("Arial", '', 12)
    pdf.ln(5)

    # Sanitize report text before adding it to the PDF
    pdf.multi_cell(0, 8, sanitize_text(report_text))

    if charts:
        for chart_path in charts:
            pdf.add_page()
            pdf.image(chart_path, x=20, y=40, w=170)

    pdf.output(output_path)
    return output_path
