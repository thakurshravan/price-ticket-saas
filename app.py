import streamlit as st
import pandas as pd
import qrcode
from qrcode.main import QRCode
from fpdf import FPDF
import io

st.set_page_config(page_title="SaaS Bulk Label Generator", layout="wide")

if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0

# --- SIDEBAR: CONFIGURATION ---
st.sidebar.header("🎨 Ticket Customization Engine")

SIZE_TEMPLATES = {
    "60x40 mm (Standard Shelf Edge)": {"w": 60, "h": 40, "qr_size": 20},
    "40x50 mm (Hang Tag)": {"w": 40, "h": 50, "qr_size": 18},
    "80x50 mm (Large Display)": {"w": 80, "h": 50, "qr_size": 25},
    "Custom Size...": None
}

selected_size = st.sidebar.selectbox("1. Select Target Ticket Size", list(SIZE_TEMPLATES.keys()))

if selected_size == "Custom Size...":
    st.sidebar.markdown("📐 **Enter Manual Dimensions (in mm):**")
    custom_w = st.sidebar.number_input("Ticket Width (mm)", min_value=10, max_value=300, value=70, step=1)
    custom_h = st.sidebar.number_input("Ticket Height (mm)", min_value=10, max_value=300, value=40, step=1)
    custom_qr = st.sidebar.number_input("QR Code Size (mm)", min_value=5, max_value=min(custom_w, custom_h)-5, value=20, step=1)
    dimensions = {"w": custom_w, "h": custom_h, "qr_size": custom_qr}
else:
    dimensions = SIZE_TEMPLATES[selected_size]

st.sidebar.subheader("Color Palette")
primary_color = st.sidebar.color_picker("Text & Accent Color", "#000000")
bg_style = st.sidebar.selectbox("Ticket Background Style", ["Plain White", "Light Border Box", "Solid Accent Header"])

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

p_r, p_g, p_b = hex_to_rgb(primary_color)

st.sidebar.subheader("Typography")
font_choice = st.sidebar.selectbox("Select Font Family", ["Arial", "Helvetica", "Courier"])
title_size = st.sidebar.slider("Product Name Font Size", 6, 14, 9)
price_size = st.sidebar.slider("Price Font Size", 12, 24, 16)

# --- MAIN INTERFACE ---
st.title("🎟️ Custom SaaS Bulk Price Ticket Generator")
st.write("Upload an Excel or CSV file, customize templates on the sidebar, and print dynamic price tickets.")

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
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            if len(df.columns) == 1 and ',' in df.columns[0]:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
        
        df.columns = df.columns.astype(str).str.strip()
        
        mapped_cols = {}
        for col in df.columns:
            col_lower = col.lower()
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
            st.error(f"Execution Halted. Could not auto-detect columns for: {missing_targets}")
        else:
            st.success("✨ Data payload mapped successfully!")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric(label="Total Tickets to Process", value=len(df))
            with col2:
                st.write("Mapped Data Fields Preview:")
                preview_df = pd.DataFrame({
                    "SKU": df[mapped_cols["SKU"]],
                    "Product Name": df[mapped_cols["Product Name"]],
                    "Price": df[mapped_cols["Price"]],
                    "URL": df[mapped_cols["URL"]]
                })
                st.dataframe(preview_df.head(3), height=120)

            if st.button("🚀 Render Custom Tickets Portfolio"):
                
                orient = 'L' if dimensions['w'] > dimensions['h'] else 'P'
                w, h = dimensions['w'], dimensions['h']
                qr_dim = dimensions['qr_size']
                
                pdf = FPDF(orientation=orient, unit='mm', format=(w, h))
                pdf.set_margin(0)
                pdf.set_auto_page_break(False)
                
                progress_bar = st.progress(0)
                total_rows = len(df)
                
                for idx, row in df.iterrows():
                    pdf.add_page()
                    
                    row_sku = str(row[mapped_cols["SKU"]])
                    row_name = str(row[mapped_cols["Product Name"]])
                    row_url = str(row[mapped_cols["URL"]])
                    raw_price = row[mapped_cols["Price"]]
                    
                    if bg_style == "Solid Accent Header":
                        pdf.set_fill_color(p_r, p_g, p_b)
                        pdf.rect(0, 0, w, 10, 'F')
                        text_r, text_g, text_b = 255, 255, 255
                        start_y = 1.5
                    else:
                        text_r, text_g, text_b = p_r, p_g, p_b
                        start_y = 2.5
                        
                    if bg_style == "Light Border Box":
                        pdf.set_draw_color(p_r, p_g, p_b)
                        pdf.set_linewidth(0.4)
                        pdf.rect(1.5, 1.5, w - 3, h - 3)
                    
                    qr = QRCode(box_size=1, border=0)
                    qr.add_data(row_url)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    img_buffer = io.BytesIO()
                    qr_img.save(img_buffer, format="PNG")
                    img_buffer.seek(0)
                    
                    allowed_text_width = w - qr_dim - 8
                    
                    # 1. Product Name Rendering (FIXED: Swapped out .text for ultra-stable .cell)
                    pdf.set_text_color(text_r, text_g, text_b)
                    pdf.set_font(font_choice, 'B', size=title_size)
                    pdf.set_xy(4, start_y)
                    
                    # Clean title truncation to prevent boundary overflows
                    short_name = row_name[:40] + "..." if len(row_name) > 40 else row_name
                    pdf.cell(allowed_text_width, 4, text=short_name, align='L')
                    
                    pdf.set_text_color(p_r, p_g, p_b)
                    
                    # 2. SKU Rendering (FIXED)
                    pdf.set_font(font_choice, '', size=8)
                    pdf.set_xy(4, start_y + 6)
                    pdf.cell(allowed_text_width, 4, text=f"SKU: {row_sku}", align='L')
                    
                    # 3. Barcode Placement
                    pdf.image(img_buffer, x=w - qr_dim - 4, y=h - qr_dim - 4, w=qr_dim, h=qr_dim)
                    
                    # 4. Price Rendering (FIXED)
                    pdf.set_font(font_choice, 'B', size=price_size)
                    pdf.set_xy(4, h - 10)
                    try:
                        price_val = float(raw_price)
                        price_text = f"AED {price_val:.2f}"
                    except:
                        price_text = f"AED {raw_price}"
                        
                    pdf.cell(allowed_text_width, 6, text=price_text, align='L')
                    
                    progress_bar.progress((idx + 1) / total_rows)
                
                pdf_output = pdf.output()
                st.balloons()
                st.download_button(
                    label="📥 Download Clean Layout PDF",
                    data=pdf_output,
                    file_name="bulk_custom_tickets.pdf",
                    mime="application/pdf"
                )
                
    except Exception as e:
        st.error(f"Fatal Parser Error: {e}")
