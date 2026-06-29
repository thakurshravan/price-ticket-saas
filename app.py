import streamlit as st
import pandas as pd
import qrcode
from fpdf import FPDF
import io
from PIL import Image

st.set_page_config(page_title="SaaS Bulk Label Generator", layout="wide")

# --- SIDEBAR: GLOBAL CONFIGURATION & CUSTOMIZATION ---
st.sidebar.header("⚙️ Ticket Customization Engine")

# 1. Layout Category Selector (Includes Retail Labels and ISO A-Series)
size_category = st.sidebar.radio(
    "1. Select Layout Category", 
    ["Standard Retail Labels", "ISO A-Series Formats (Signage & Displays)"]
)

# Populate templates based on selected section
if size_category == "Standard Retail Labels":
    SIZE_TEMPLATES = {
        "60x40 mm (Standard Shelf Edge)": {"w": 60, "h": 40, "qr_size": 20},
        "40x50 mm (Hang Tag)": {"w": 40, "h": 50, "qr_size": 18},
        "80x50 mm (Large Display)": {"w": 80, "h": 50, "qr_size": 25}
    }
    max_title_font = 14
    max_price_font = 24
    default_title = 10
    default_price = 16
else:
    SIZE_TEMPLATES = {
        "A7 (74x105 mm) Pocket Sign": {"w": 74, "h": 105, "qr_size": 30},
        "A6 (105x148 mm) Counter Display": {"w": 105, "h": 148, "qr_size": 45},
        "A5 (148x210 mm) Table Tent": {"w": 148, "h": 210, "qr_size": 60},
        "A4 (210x297 mm) Large Poster Sign": {"w": 210, "h": 297, "qr_size": 80}
    }
    max_title_font = 48
    max_price_font = 72
    default_title = 24
    default_price = 42

selected_size = st.sidebar.selectbox("2. Select Target Dimensions", list(SIZE_TEMPLATES.keys()))
dimensions = SIZE_TEMPLATES[selected_size]

# 2. Dynamic Color Customization
st.sidebar.subheader("Color Palette")
primary_color = st.sidebar.color_picker("Text & Accent Color", "#000000")
bg_style = st.sidebar.selectbox("Ticket Background Style", ["Plain White", "Light Border Box", "Solid Accent Header"])

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

p_r, p_g, p_b = hex_to_rgb(primary_color)

# 3. Typography Adjustments
st.sidebar.subheader("Typography")
font_choice = st.sidebar.selectbox("Select Font Family", ["Arial", "Helvetica", "Courier"])
title_size = st.sidebar.slider("Product Name Font Size", 8, max_title_font, default_title)
price_size = st.sidebar.slider("Price Font Size", 12, max_price_font, default_price)

# --- MAIN INTERFACE ---
st.title("🎟️ Custom SaaS Bulk Price Ticket Generator")
st.write("Configure dimensions/branding on the sidebar, choose your input method below, and export clean print-ready vector PDFs.")

# Dual Input Processing Layout via Tabs
tabs = st.tabs(["📊 Excel Automation Pipeline", "🖼️ Single Image Ticket Converter"])

# --- TAB 1: EXCEL AUTOMATION PIPELINE ---
with tabs[0]:
    st.markdown("📥 **Excel Format Requirement:** Columns must contain: `SKU`, `Product Name`, `Price`, `URL`")
    uploaded_file = st.file_uploader("Upload Product Excel File (.xlsx)", type=["xlsx"], key="excel_uploader")
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()
            st.success("⚡ Data payload imported successfully!")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric(label="Total Tickets to Process", value=len(df))
            with col2:
                st.write("Data Preview:")
                st.dataframe(df.head(3), height=120)
            
            required_cols = ["SKU", "Product Name", "Price", "URL"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"Execution Halted. Missing columns inside Excel: {missing_cols}")
            else:
                if st.button("🚀 Render Custom Tickets Portfolio", key="btn_excel"):
                    orient = 'L' if dimensions['w'] > dimensions['h'] else 'P'
                    w, h = dimensions['w'], dimensions['h']
                    pdf = FPDF(orientation=orient, unit='mm', format=(w, h))
                    pdf.set_auto_page_break(auto=False, margin=0)
                    header_height = max(12, int(h * 0.15)) if bg_style == "Solid Accent Header" else 0
                    
                    for idx, row in df.iterrows():
                        pdf.add_page()
                        
                        if bg_style == "Solid Accent Header":
                            pdf.set_fill_color(p_r, p_g, p_b)
                            pdf.rect(0, 0, w, header_height, 'F')
                            text_r, text_g, text_b = 255, 255, 255
                        else:
                            text_r, text_g, text_b = p_r, p_g, p_b
                            
                        if bg_style == "Light Border Box":
                            pdf.set_draw_color(p_r, p_g, p_b)
                            pdf.set_linewidth(max(0.4, h * 0.005))
                            margin_offset = max(1.5, w * 0.02)
                            pdf.rect(margin_offset, margin_offset, w - (margin_offset * 2), h - (margin_offset * 2))
                        
                        # QR Generation
                        qr = qrcode.QRCode(box_size=1, border=0)
                        qr.add_data(str(row['URL']))
                        qr.make(fit=True)
                        qr_img = qr.make_image(fill_color="black", back_color="white")
                        img_buffer = io.BytesIO()
                        qr_img.save(img_buffer, format="PNG")
                        img_buffer.seek(0)
                        
                        # Layout Drawings
                        pdf.set_text_color(text_r, text_g, text_b)
                        pdf.set_font(font_choice, 'B', size=title_size)
                        title_y = (header_height / 2) - (title_size * 0.35) if header_height > 0 else max(4, h * 0.05)
                        pdf.set_xy(max(4, w * 0.05), max(3.5, title_y))
                        pdf.cell(w - max(8, w * 0.1), title_size * 0.5, text=str(row['Product Name'])[:40], new_x="LMARGIN", new_y="NEXT", align='L')
                        
                        pdf.set_text_color(p_r, p_g, p_b)
                        sku_font_size = max(8, int(title_size * 0.6))
                        pdf.set_font(font_choice, '', size=sku_font_size)
                        sku_y = (header_height + max(4, h * 0.03)) if header_height > 0 else (title_y + (title_size * 0.5) + max(2, h * 0.02))
                        pdf.set_xy(max(4, w * 0.05), sku_y)
                        pdf.cell(w - max(8, w * 0.1), sku_font_size * 0.5, text=f"SKU: {row['SKU']}", new_x="LMARGIN", new_y="NEXT", align='L')
                        
                        qr_dim = dimensions['qr_size']
                        pdf.image(img_buffer, x=w - qr_dim - max(4, w * 0.05), y=h - qr_dim - max(4, h * 0.05), w=qr_dim, h=qr_dim)
                        
                        pdf.set_font(font_choice, 'B', size=price_size)
                        pdf.set_xy(max(4, w * 0.05), h - (price_size * 0.4) - max(6, h * 0.05))
                        pdf.cell(w - qr_dim - max(12, w * 0.1), price_size * 0.4, text=f"AED {row['Price']:.2f}", align='L')
                    
                    st.balloons()
                    st.download_button(
                        label="📥 Download Print-Ready Dynamic PDF",
                        data=bytes(pdf.output()),
                        file_name="custom_bulk_tickets.pdf",
                        mime="application/pdf"
                    )
        except Exception as e:
            st.error(f"Fatal Parser Error: {e}")

# --- TAB 2: SINGLE IMAGE TICKET CONVERTER ---
with tabs[1]:
    st.markdown("🖼️ **Image Label Feature:** Upload any item picture, add details manually below, and generate a styled display ticket.")
    
    img_file = st.file_uploader("Upload Product Image (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"], key="img_uploader")
    
    col_im1, col_im2 = st.columns(2)
    with col_im1:
        img_title = st.text_input("Product Title Line", "Premium Selected Item")
        img_sku = st.text_input("Product SKU Reference", "SKU-IMG-99")
    with col_im2:
        img_price = st.number_input("Price Value (AED)", min_value=0.0, value=29.99, step=0.01)
        img_url = st.text_input("Target QR Redirection Link", "https://price-ticket-saas.onrender.com")
        
    if img_file is not None:
        if st.button("🚀 Process Image to Vector Ticket", key="btn_img"):
            try:
                # Open image and handle potential color palette profiles cleanly
                raw_image = Image.open(img_file)
                if raw_image.mode in ("RGBA", "P"):
                    raw_image = raw_image.convert("RGB")
                
                processed_img_buffer = io.BytesIO()
                raw_image.save(processed_img_buffer, format="JPEG", quality=90)
                processed_img_buffer.seek(0)
                
                # PDF Initialization
                orient = 'L' if dimensions['w'] > dimensions['h'] else 'P'
                w, h = dimensions['w'], dimensions['h']
                pdf = FPDF(orientation=orient, unit='mm', format=(w, h))
                pdf.set_auto_page_break(auto=False, margin=0)
                pdf.add_page()
                
                header_height = max(12, int(h * 0.15)) if bg_style == "Solid Accent Header" else 0
                
                # Render Background Layout Settings
                if bg_style == "Solid Accent Header":
                    pdf.set_fill_color(p_r, p_g, p_b)
                    pdf.rect(0, 0, w, header_height, 'F')
                    text_r, text_g, text_b = 255, 255, 255
                else:
                    text_r, text_g, text_b = p_r, p_g, p_b
                    
                if bg_style == "Light Border Box":
                    pdf.set_draw_color(p_r, p_g, p_b)
                    pdf.set_linewidth(max(0.4, h * 0.005))
                    margin_offset = max(1.5, w * 0.02)
                    pdf.rect(margin_offset, margin_offset, w - (margin_offset * 2), h - (margin_offset * 2))
                
                # QR Generation
                qr = qrcode.QRCode(box_size=1, border=0)
                qr.add_data(img_url)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_buffer = io.BytesIO()
                qr_img.save(qr_buffer, format="PNG")
                qr_buffer.seek(0)
                
                # Draw Title Text
                pdf.set_text_color(text_r, text_g, text_b)
                pdf.set_font(font_choice, 'B', size=title_size)
                title_y = (header_height / 2) - (title_size * 0.35) if header_height > 0 else max(4, h * 0.05)
                pdf.set_xy(max(4, w * 0.05), max(3.5, title_y))
                pdf.cell(w - max(8, w * 0.1), title_size * 0.5, text=img_title[:40], new_x="LMARGIN", new_y="NEXT", align='L')
                
                # Draw SKU
                pdf.set_text_color(p_r, p_g, p_b)
                sku_font_size = max(8, int(title_size * 0.6))
                pdf.set_font(font_choice, '', size=sku_font_size)
                sku_y = (header_height + max(4, h * 0.03)) if header_height > 0 else (title_y + (title_size * 0.5) + max(2, h * 0.02))
                pdf.set_xy(max(4, w * 0.05), sku_y)
                pdf.cell(w - max(8, w * 0.1), sku_font_size * 0.5, text=f"SKU: {img_sku}", new_x="LMARGIN", new_y="NEXT", align='L')
                
                # Embed Uploaded Image
                qr_dim = dimensions['qr_size']
                img_display_w = max(15, int(w * 0.25))
                img_display_h = max(15, int(h * 0.25))
                pdf.image(processed_img_buffer, x=max(4, w * 0.05), y=sku_y + max(4, h * 0.04), w=img_display_w, h=img_display_h)
                
                # Embed QR Code
                pdf.image(qr_buffer, x=w - qr_dim - max(4, w * 0.05), y=h - qr_dim - max(4, h * 0.05), w=qr_dim, h=qr_dim)
                
                # Draw Price Text
                pdf.set_font(font_choice, 'B', size=price_size)
                pdf.set_xy(max(4, w * 0.05), h - (price_size * 0.4) - max(6, h * 0.05))
                pdf.cell(w - qr_dim - max(12, w * 0.1), price_size * 0.4, text=f"AED {img_price:.2f}", align='L')
                
                st.balloons()
                st.download_button(
                    label="📥 Download Photo-Converted Ticket",
                    data=bytes(pdf.output()),
                    file_name="converted_image_ticket.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Image Rendering Fault: {e}")
