import streamlit as st
import pandas as pd
import qrcode
from fpdf import FPDF
import io

st.set_page_config(page_title="SaaS Bulk Label Generator", layout="wide")

# --- SIDEBAR: SAAS CONFIGURATION & CUSTOMIZATION ---
st.sidebar.header("🎨 Ticket Customization Engine")

# 1. Preset Size Selection
SIZE_TEMPLATES = {
    "60x40 mm (Standard Shelf Edge)": {"w": 60, "h": 40, "qr_size": 20},
    "40x50 mm (Hang Tag)": {"w": 40, "h": 50, "qr_size": 18},
    "80x50 mm (Large Display)": {"w": 80, "h": 50, "qr_size": 25}
}
selected_size = st.sidebar.selectbox("1. Select Target Ticket Size", list(SIZE_TEMPLATES.keys()))
dimensions = SIZE_TEMPLATES[selected_size]

# 2. Dynamic Color Customization
st.sidebar.subheader("Color Palette")
primary_color = st.sidebar.color_picker("Text & Accent Color", "#000000")
bg_style = st.sidebar.selectbox("Ticket Background Style", ["Plain White", "Light Border Box", "Solid Accent Header"])

# Helper function to convert Hex string (#RRGGBB) to RGB Tuple
def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

p_r, p_g, p_b = hex_to_rgb(primary_color)

# 3. Typography Adjustments
st.sidebar.subheader("Typography")
font_choice = st.sidebar.selectbox("Select Font Family", ["Arial", "Helvetica", "Courier"])
title_size = st.sidebar.slider("Product Name Font Size", 8, 14, 10)
price_size = st.sidebar.slider("Price Font Size", 12, 24, 16)

# --- MAIN INTERFACE ---
st.title("🎟️ Custom SaaS Bulk Price Ticket Generator")
st.write("Upload an Excel file, configure dimensions/branding on the sidebar, and export clean print-ready vector PDFs.")

st.markdown("💡 **Excel Format Requirement:** Your spreadsheet columns must contain: `SKU`, `Product Name`, `Price`, `URL`")

uploaded_file = st.file_uploader("Upload Product Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        
        # FIX: Strip any accidental trailing or leading spaces from the column headers!
        df.columns = df.columns.str.strip()
        
        st.success("✨ Data payload imported successfully!")
        
        # UI Previews
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="Total Tickets to Process", value=len(df))
        with col2:
            st.write("Data Preview (Cleaned Columns):")
            st.dataframe(df.head(3), height=120)
        
        # Validation checks
        required_cols = ["SKU", "Product Name", "Price", "URL"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"Execution Halted. Missing columns inside Excel: {missing_cols}")
        else:
            if st.button("🚀 Render Custom Tickets Portfolio"):
                
                # Determine Layout Orientation (Landscape 'L' if width > height, else Portrait 'P')
                orient = 'L' if dimensions['w'] > dimensions['h'] else 'P'
                w, h = dimensions['w'], dimensions['h']
                
                # Setup FPDF instance 
                pdf = FPDF(orientation=orient, unit='mm', format=(w, h))
                pdf.set_auto_page_break(auto=False, margin=0)
                
                for idx, row in df.iterrows():
                    pdf.add_page()
                    
                    # --- THEME STYLING ENGINE ---
                    # Draw solid background header blocks if selected
                    if bg_style == "Solid Accent Header":
                        pdf.set_fill_color(p_r, p_g, p_b)
                        pdf.rect(0, 0, w, 12, 'F')
                        text_r, text_g, text_b = 255, 255, 255 # White text over dark header
                    else:
                        text_r, text_g, text_b = p_r, p_g, p_b
                        
                    # Draw a border frame around the page if frame style is active
                    if bg_style == "Light Border Box":
                        pdf.set_draw_color(p_r, p_g, p_b)
                        pdf.set_linewidth(0.4)
                        pdf.rect(1.5, 1.5, w - 3, h - 3)
                    
                    # --- QR ENGINE CONFIGURATION ---
                    qr = qrcode.QRCode(box_size=1, border=0)
                    qr.add_data(str(row['URL']))
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    img_buffer = io.BytesIO()
                    qr_img.save(img_buffer, format="PNG")
                    img_buffer.seek(0)
                    
                    # --- CORE CANVAS DRAWINGS ---
                    # 1. Product Title Text
                    pdf.set_text_color(text_r, text_g, text_b)
                    pdf.set_font(font_choice, 'B', size=title_size)
                    pdf.set_xy(4, 3.5)
                    pdf.cell(w - 8, 5, text=str(row['Product Name'])[:25], new_x="LMARGIN", new_y="NEXT", align='L')
                    
                    # Reset text color back to user choice for lower areas if changed by header rule
                    pdf.set_text_color(p_r, p_g, p_b)
                    
                    # 2. SKU Placement
                    pdf.set_font(font_choice, '', size=8)
                    pdf.set_xy(4, 11 if bg_style == "Solid Accent Header" else 9)
                    pdf.cell(w - 8, 4, text=f"SKU: {row['SKU']}", new_x="LMARGIN", new_y="NEXT", align='L')
                    
                    # 3. Dynamic QR Engine Positioning
                    qr_dim = dimensions['qr_size']
                    pdf.image(img_buffer, x=w - qr_dim - 4, y=h - qr_dim - 4, w=qr_dim, h=qr_dim)
                    
                    # 4. Large Premium Price Layout
                    pdf.set_font(font_choice, 'B', size=price_size)
                    pdf.set_xy(4, h - 12)
                    pdf.cell(w - qr_dim - 8, 8, text=f"AED {row['Price']:.2f}", align='L')
                
                # Compress into raw bytes safely in memory
                pdf_output = pdf.output()
                
                st.balloons()
                st.download_button(
                    label="📥 Download Print-Ready Dynamic PDF",
                    data=pdf_output,
                    file_name="custom_bulk_tickets.pdf",
                    mime="application/pdf"
                )
                
    except Exception as e:
        st.error(f"Fatal Parser Error encountered processing the Excel document: {e}")
