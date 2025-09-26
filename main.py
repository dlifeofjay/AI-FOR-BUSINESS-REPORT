from data_loader import entry_db, clean_data, curr_prev_mon
from report_generator import generate_nl_report, generate_pdf_report, plot_top_products
from utils import send_email
from datetime import datetime

def main():
    df_raw = entry_db()
    df_clean = clean_data(df_raw)
    current_df, prev_df = curr_prev_mon(df_clean)

   
    report_text = generate_nl_report(current_df, prev_df)

    
    chart1 = plot_top_products(current_df)
    charts = [chart1]   

    
    pdf_path = generate_pdf_report(report_text, charts=charts)

 
    month_year = datetime.today().strftime("%B %Y")
    send_email(
        subject=f"Monthly Business Report for {month_year}",
        body="Please find attached the monthly business report.",
        attachment_path=pdf_path
    )

if __name__ == "__main__":
    main()
