import streamlit as st
import pandas as pd
import qrcode
import io
import base64

st.set_page_config(page_title="Mini Tag Price Label Generator", layout="wide")

if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0

# --- GLOBAL UTILITY LOGIC ---
def generate_qr_base64(url):
    if pd.isna(url) or not str(url).strip():
        url = "https://example.com"
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(str(url))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def process_logo_to_base64(uploaded_logo):
    if uploaded_logo is not None:
        try:
            return base64.b64encode(uploaded_logo.getvalue()).decode()
        except:
            return None
    return None

# --- SIDEBAR: COMPACT CONFIGURATION ENGINE ---
st.sidebar.header("🎨 Mini Tag Layout Engine")

# Locked down exclusively to mini retail tags to protect alignment accuracy
MINI_SIZE_TEMPLATES = {
    "60x40 mm (Standard Retail Shelf Bzl)": {"w": 60, "h": 40, "qr_size": 13},
    "40x50 mm (Vertical Product Hang Tag)": {"w": 40, "h": 50, "qr_size": 11},
    "80x50 mm (Large Counter Slot Display)": {"w": 80, "h": 50, "qr_size": 16}
}

selected_size = st.sidebar.selectbox("1. Target Label Template", list(MINI_SIZE_TEMPLATES.keys()))
dimensions = MINI_SIZE_TEMPLATES[selected_size]

primary_color = st.sidebar.color_picker("Text & Accent Color", "#8a1515")
font_choice = st.sidebar.selectbox("Select Font Family", ["Arial", "Helvetica", "Courier"])
title_size = st.sidebar.slider("Product Name Font Size (pt)", 7, 16, 9)
price_size = st.sidebar.slider("Price Font Size (pt)", 12, 28, 16)
show_was_price = st.sidebar.checkbox("Show Strikethrough 'Was' Price Row", value=True)

uploaded_logo = st.sidebar.file_uploader("Upload Brand Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
logo_b64 = process_logo_to_base64(uploaded_logo)

web_font = "Courier New, monospace" if font_choice == "Courier" else f"{font_choice}, sans-serif"

# --- MAIN INTERFACE DISPLAY ---
st.title("🎟️ Retail Batch Mini Price Tag Generator")
st.write("Layout system optimized strictly for high-accuracy standard millimeter thermal and shelf edge feeds.")

# --- LIVE PREVIEW WINDOW ---
st.subheader("👀 Live Ticket Sample Preview")

preview_price_html = f"""
<table style="border-collapse: collapse; border: none; margin: 0; padding: 0; font-family: {web_font}; text-align: left;">
    <tbody>
"""
if show_was_price:
    preview_price_html += f"""
        <tr>
            <td style="padding: 0 4px 0 0; font-size: {price_size - 5}px; color: #888; font-weight: bold; line-height: 1;">AED</td>
            <td style="padding: 0; font-size: {price_size - 4}px; color: #888; text-decoration: line-through; line-height: 1;">1839.00</td>
        </tr>
    """
preview_price_html += f"""
        <tr>
            <td style="padding: 0 4px 0 0; font-size: {price_size - 2}px; color: {primary_color}; font-weight: bold; line-height: 1;">AED</td>
            <td style="padding: 0; font-size: {price_size + 2}px; font-weight: bold; color: {primary_color}; line-height: 1;">1799.00</td>
        </tr>
    </tbody>
</table>
"""

preview_logo_html = f'<div style="position: absolute; top: 2px; right: 4px; max-width: 25%; max-height: 20%; display: flex; justify-content: flex-end; align-items: center; z-index: 20;"><img src="data:image/png;base64,{logo_b64}" style="max-width: 100%; max-height: 100%; object-fit: contain;" /></div>' if logo_b64 else ""

preview_html = f"""
<div style="width: {dimensions['w'] * 4}px; height: {dimensions['h'] * 4}px; border: 2px solid {primary_color}; background: #ffffff; border-radius: 4px; position: relative; font-family: {web_font}; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.15); margin-bottom: 20px;">
    {preview_logo_html}
    <div style="background: {primary_color}; padding: 2px 8px; display: flex; align-items: center; justify-content: center; text-align: center; height: 26%; box-sizing: border-box; overflow: hidden;">
        <div style="color: #ffffff; font-size: {title_size + 3}px; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; width: 100%;">
            <strong style="text-transform: uppercase; font-weight: 900;">GARMIN</strong>: FENIX 7 PRO SAPPHIRE SOLAR
        </div>
    </div>
    <div style="height: 74%; padding: 6px; box-sizing: border-box; display: flex; justify-content: space-between; align-items: stretch; gap: 4px;">
        <div style="width: 62%; display: flex; flex-direction: column; justify-content: space-between; text-align: left; overflow: hidden;">
            <div>
                <div style="color: #666; font-size: 10px; font-weight: bold; margin-bottom: 2px;">010-02935-00</div>
                <div style="color: #333; font-size: 9px; line-height: 1.25; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                    <strong style="text-transform: uppercase; font-weight: bold; display: block; margin-bottom: 1px; font-size: 9.5px;">PRODUCT HIGHLIGHTS:</strong>
                    • Unlimited battery life<br>• Detailed health features
                </div>
            </div>
            <div>{preview_price_html}</div>
        </div>
        <div style="width: 35%; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; overflow: hidden;">
            <div style="font-weight: bold; font-size: 10px; text-align: center; color: #666; margin-bottom: 2px; width: 100%; text-transform: uppercase;">SKU</div>
            <div style="width: {dimensions['qr_size'] * 4}px; height: {dimensions['qr_size'] * 4}px; background-image: url('data:image/png;base64,{generate_qr_base64("https://example.com")}'); background-size: cover; border: 1px solid #eee;"></div>
        </div>
    </div>
</div>
"""
st.markdown(preview_html, unsafe_allow_html=True)
st.divider()

# --- DATA IMPORT ENGINE ---
uploaded_file = st.file_uploader("Upload Product File (.xlsx or .csv)", type=["xlsx", "csv"], key=f"file_uploader_{st.session_state['file_uploader_key']}")

if uploaded_file is not None:
    if st.button("🗑️ Clear File & Reset Canvas"):
        st.session_state["file_uploader_key"] += 1
        st.rerun()

    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode('utf-8-sig', errors='ignore')))
        else:
            df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()))
        
        df.columns = df.columns.astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
        df = df.dropna(how='all')
        
        # Explicit structure dictionary mapping rules
        mapped = {}
        for col in df.columns:
            c_low = col.lower().strip()
            if "item code" in c_low: mapped["Item Code"] = col
            elif "description" in c_low: mapped["Product Name"] = col
            elif "highlight" in c_low: mapped["Highlights"] = col
            elif "brand" in c_low: mapped["Brand"] = col
            elif c_low == "now": mapped["Price"] = col
            elif c_low == "was": mapped["Was Price"] = col
            elif c_low == "sku": mapped["SKU"] = col
            elif "url" in c_low or "link" in c_low: mapped["URL"] = col

        required = ["Item Code", "Product Name", "Price", "SKU"]
        missing = [r for r in required if r not in mapped]

        if missing:
            st.error(f"Missing required spreadsheet columns: {missing}. Detected fields: {list(df.columns)}")
        else:
            st.success("✨ Spreadsheet file structure verified successfully!")
            st.dataframe(df.head(3), use_container_width=True)

            # --- GENERATION CONTAINER LOOP ---
            html_cards = ""
            for idx, row in df.iterrows():
                try:
                    p_val = float(row[mapped["Price"]])
                    formatted_price = f"{p_val:.2f}"
                except:
                    formatted_price = str(row[mapped["Price"]])

                try:
                    w_val = float(row[mapped["Was Price"]]) if "Was Price" in mapped else 0
                    formatted_was = f"{w_val:.2f}" if (w_val > 0 and not pd.isna(row[mapped["Was Price"]])) else ""
                except:
                    formatted_was = str(row[mapped["Was Price"]]) if "Was Price" in mapped else ""

                brand = str(row[mapped["Brand"]]).strip() if "Brand" in mapped else ""
                highlights = str(row[mapped["Highlights"]]).strip() if "Highlights" in mapped else ""
                highlights = highlights.replace('\n', '<br>')
                
                sku = str(row[mapped["SKU"]]).strip()
                item_code = str(row[mapped["Item Code"]]).strip()
                qr_b64 = generate_qr_base64(row[mapped["URL"]] if "URL" in mapped else "https://example.com")

                print_price_html = f"""
                <table style="border-collapse: collapse; border: none; margin: 0; padding: 0; font-family: {web_font}; text-align: left;">
                    <tbody>
                """
                if show_was_price and formatted_was:
                    print_price_html += f"""
                        <tr>
                            <td style="padding: 0 4px 0 0; font-size: {title_size - 1}pt; color: #888; font-weight: bold; line-height: 1;">AED</td>
                            <td style="padding: 0; font-size: {price_size - 4}pt; color: #888; text-decoration: line-through; line-height: 1;">{formatted_was}</td>
                        </tr>
                    """
                print_price_html += f"""
                        <tr>
                            <td style="padding: 0 4px 0 0; font-size: {title_size + 1}pt; color: {primary_color}; font-weight: bold; line-height: 1;">AED</td>
                            <td style="padding: 0; font-size: {price_size}pt; font-weight: bold; color: {primary_color}; line-height: 1;">{formatted_price}</td>
                        </tr>
                    </tbody>
                </table>
                """

                print_highlights_html = f"""
                <div style="color: #333; font-size: {title_size - 1.5}pt; line-height: 1.25; margin-top: 2px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                    <strong style="text-transform: uppercase; font-weight: bold; display: block; margin-bottom: 1px; font-size: {title_size - 1}pt;">PRODUCT HIGHLIGHTS:</strong>
                    {highlights}
                </div>
                """ if highlights else ""

                header_text_content = f'<strong style="text-transform: uppercase; font-weight: 900;">{brand}</strong>: {row[mapped["Product Name"]]}' if brand else str(row[mapped["Product Name"]])

                html_cards += f"""
                <div style="width: {dimensions['w']}mm; height: {dimensions['h']}mm; border: 1.5px solid {primary_color}; box-sizing: border-box; position: relative; background: #ffffff; font-family: {web_font}; overflow: hidden; display: inline-block; margin: 1mm; vertical-align: top; text-align: left;">
                    <div style="background: {primary_color}; padding: 2px 6px; display: flex; align-items: center; justify-content: center; text-align: center; height: 26%; box-sizing: border-box; overflow: hidden;">
                        <div style="color: #ffffff; font-size: {title_size}pt; line-height: 1.15; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; width: 100%;">{header_text_content}</div>
                    </div>
                    <div style="height: 74%; padding: 4px 6px; box-sizing: border-box; display: flex; justify-content: space-between; align-items: stretch; gap: 4px;">
                        <div style="width: 62%; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box; overflow: hidden;">
                            <div>
                                <div style="color: #666; font-size: {title_size - 1}pt; font-weight: bold; white-space: nowrap; line-height: 1;">{item_code}</div>
                                {print_highlights_html}
                            </div>
                            <div>{print_price_html}</div>
                        </div>
                        <div style="width: 35%; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; box-sizing: border-box; overflow: hidden;">
                            <div style="font-weight: bold; font-size: {title_size - 1}pt; text-align: center; color: #666; margin-bottom: 1mm; width: 100%; text-transform: uppercase; line-height: 1;">SKU</div>
                            <img src="data:image/png;base64,{qr_b64}" style="width: {dimensions['qr_size']}mm; height: {dimensions['qr_size']}mm; display: block;" />
                        </div>
                    </div>
                </div>
                """

            st.subheader("🖨️ Printable Mini Document Feed")
            iframe_content = f"""
            <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; font-family: sans-serif; text-align: center; background: #fafafa; }}
                    .print-btn {{ background-color: {primary_color}; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.15); margin: 20px auto; display: block; text-transform: uppercase; }}
                    .page-container {{ width: 210mm; padding: 4mm; margin: 0 auto; background: white; box-sizing: border-box; text-align: left; }}
                    @media print {{ .print-btn {{ display: none !important; }} body {{ background: white; }} .page-container {{ padding: 0; margin: 0; width: 100%; }} }}
                </style>
            </head>
            <body>
                <button class="print-btn" onclick="window.print()">🖨️ Print Bulk Mini Sheet</button>
                <div class="page-container">{html_cards}</div>
            </body>
            </html>
            """
            st.components.v1.html(iframe_content, height=600, scrolling=True)
    except Exception as e:
        st.error(f"Data Parser Error: {e}")
