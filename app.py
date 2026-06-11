import streamlit as st
import pandas as pd
import qrcode
import io
import base64

st.set_page_config(page_title="SaaS Bulk Label Generator", layout="wide")

if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0

# --- SIDEBAR: CONFIGURATION ---
st.sidebar.header("🎨 Ticket Customization Engine")

SIZE_TEMPLATES = {
    "60x40 mm (Standard Shelf Edge)": {"w": 60, "h": 40, "qr_size": 18},
    "40x50 mm (Hang Tag)": {"w": 40, "h": 50, "qr_size": 15},
    "80x50 mm (Large Display)": {"w": 80, "h": 50, "qr_size": 22},
    "Custom Size...": None
}

selected_size = st.sidebar.selectbox("1. Select Target Ticket Size", list(SIZE_TEMPLATES.keys()))

if selected_size == "Custom Size...":
    st.sidebar.markdown("📐 **Enter Manual Dimensions (in mm):**")
    custom_w = st.sidebar.number_input("Ticket Width (mm)", min_value=10, max_value=200, value=60, step=1)
    custom_h = st.sidebar.number_input("Ticket Height (mm)", min_value=10, max_value=200, value=40, step=1)
    custom_qr = st.sidebar.number_input("QR Code Size (mm)", min_value=5, max_value=min(custom_w, custom_h)-5, value=18, step=1)
    dimensions = {"w": custom_w, "h": custom_h, "qr_size": custom_qr}
else:
    dimensions = SIZE_TEMPLATES[selected_size]

st.sidebar.subheader("Color Palette")
primary_color = st.sidebar.color_picker("Text & Accent Color", "#000000")
bg_style = st.sidebar.selectbox("Ticket Background Style", ["Plain White", "Light Border Box", "Solid Accent Header"])

st.sidebar.subheader("Typography")
font_choice = st.sidebar.selectbox("Select Font Family", ["Arial", "Helvetica", "Courier"])
title_size = st.sidebar.slider("Product Name Font Size", 8, 20, 12)
price_size = st.sidebar.slider("Price Font Size", 14, 32, 20)

# --- MAIN INTERFACE LAYOUT ---
st.title("🎟️ Custom SaaS Bulk Price Ticket Generator")
st.write("Upload a file, customize styles, and print directly onto standard A4 sticker sheets.")

# Helper function to generate QR codes as Base64 strings for raw HTML display
def generate_qr_base64(url):
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- DATA IMPORT ENGINE ---
def clear_file_callback():
    st.session_state["file_uploader_key"] += 1

uploaded_file = st.file_uploader(
    "Upload Product File (.xlsx or .csv)", 
    type=["xlsx", "csv"], 
    key=f"file_uploader_{st.session_state['file_uploader_key']}"
)

if uploaded_file is not None:
    if st.button("🗑️ Clear File & Reset Canvas", on_click=clear_file_callback):
        st.rerun()

    try:
        file_bytes = uploaded_file.getvalue()
        
        if uploaded_file.name.endswith('.csv'):
            data_str = file_bytes.decode('utf-8', errors='ignore')
            df = pd.read_csv(io.StringIO(data_str), header=None)
        else:
            df = pd.read_excel(io.BytesIO(file_bytes), header=None)
        
        df = df.dropna(how='all').dropna(axis=1, how='all')
        df.columns = df.iloc[0].astype(str).str.strip()
        df = df[1:].reset_index(drop=True)
        
        mapped_cols = {}
        for col in df.columns:
            col_lower = str(col).lower()
            if "sku" in col_lower:
                mapped_cols["SKU"] = col
            elif "product" in col_lower or "name" in col_lower or "title" in col_lower:
                mapped_cols["Product Name"] = col
            elif "price" in col_lower or "rate" in col_lower or "mrp" in col_lower:
                mapped_cols["Price"] = col
            elif "url" in col_lower or "link" in col_lower or "website" in col_lower:
                mapped_cols["URL"] = col

        required_targets = ["SKU", "Product Name", "Price", "URL"]
        missing_targets = [t for t in required_targets if t not in mapped_cols]
        
        if missing_targets:
            st.error(f"Execution Halted. Missing columns: {missing_targets}")
        else:
            st.success("✨ Data payload mapped successfully!")
            st.dataframe(df.head(3), use_container_width=True)

            # --- GENERATE PRINT SHEET CONTAINER ---
            st.subheader("🖨️ Generated Print Canvas")
            st.info("💡 **How to Print:** Click the link below to open the print layout window, then press **Ctrl + P** (or Cmd + P) and select **'Save as PDF'** or choose your **A4 Printer**!")

            # Build CSS for A4 Grid configuration
            web_font = "Courier New, monospace" if font_choice == "Courier" else f"{font_choice}, sans-serif"
            card_border = f"2px solid {primary_color}" if bg_style == "Light Border Box" else "1px solid #ddd"
            header_bg = primary_color if bg_style == "Solid Accent Header" else "transparent"
            header_text_color = "#ffffff" if bg_style == "Solid Accent Header" else primary_color

            # Generate HTML grid cards loop
            html_cards = ""
            for idx, row in df.iterrows():
                try:
                    price_val = float(row[mapped_cols["Price"]])
                    price_text = f"AED {price_val:.2f}"
                except:
                    price_text = f"AED {row[mapped_cols['Price']]}"

                qr_b64 = generate_qr_base64(str(row[mapped_cols["URL"]]))

                html_cards += f"""
                <div class="ticket-card" style="
                    width: {dimensions['w']}mm;
                    height: {dimensions['h']}mm;
                    border: {card_border};
                    box-sizing: border-box;
                    position: relative;
                    background: #fff;
                    font-family: {web_font};
                    overflow: hidden;
                    display: inline-block;
                    margin: 1mm;
                    vertical-align: top;
                ">
                    <div style="background-color: {header_bg}; padding: 6px; height: 35%; box-sizing: border-box;">
                        <div style="color: {header_text_color}; font-size: {title_size}pt; font-weight: bold; line-height: 1.1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            {row[mapped_cols["Product Name"]]}
                        </div>
                    </div>
                    <div style="position: absolute; top: 42%; left: 6px; color: {primary_color}; font-size: 8pt;">
                        SKU: {row[mapped_cols["SKU"]]}
                    </div>
                    <div style="position: absolute; bottom: 6px; left: 6px; color: {primary_color}; font-size: {price_size}pt; font-weight: bold;">
                        {price_text}
                    </div>
                    <img src="data:image/png;base64,{qr_b64}" style="
                        position: absolute;
                        bottom: 4px;
                        right: 4px;
                        width: {dimensions['qr_size']}mm;
                        height: {dimensions['qr_size']}mm;
                    " />
                </div>
                """

            # Full printable page layout document shell template
            full_print_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Print Price Tickets Portfolio</title>
                <style>
                    body {{ margin: 0; padding: 0; background: #f0f2f5; }}
                    .a4-page {{
                        width: 210mm;
                        min-height: 297mm;
                        padding: 10mm;
                        margin: 10mm auto;
                        background: white;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                        box-sizing: border-box;
                    }}
                    @media print {{
                        body {{ background: white; }}
                        .a4-page {{ margin: 0; padding: 10mm; box-shadow: none; page-break-after: always; }}
                        .no-print {{ display: none; }}
                    }}
                </style>
            </head>
            <body>
                <div class="no-print" style="background: #333; color: #fff; padding: 15px; text-align: center; font-family: sans-serif;">
                    <button onclick="window.print()" style="padding: 10px 20px; font-size: 16px; font-weight: bold; cursor: pointer; background: #00cc66; border: none; color: white; border-radius: 4px;">📂 Click Here to Open Print Interface</button>
                    <p style="margin: 5px 0 0 0; font-size: 12px; color: #ccc;">Make sure your print layout orientation matches your target choices!</p>
                </div>
                <div class="a4-page">
                    {html_cards}
                </div>
            </body>
            </html>
            """

            # Embed inside a web tab hyperlink using components
            b64_print = base64.b64encode(full_print_html.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64_print}" target="_blank" style="text-decoration: none;"><div style="background-color: #25d366; color: white; text-align: center; padding: 15px; font-weight: bold; font-size: 18px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); margin-bottom: 25px;">🌐 OPEN PRINT PORTFOLIO IN NEW TAB</div></a>'
            st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Fatal Parser Error: {e}")
