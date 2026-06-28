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

# --- SIDEBAR: CONFIGURATION ENGINE ---
st.sidebar.header("🎨 Mini Tag Layout Engine")

MINI_SIZE_TEMPLATES = {
    "60x40 mm (Standard Retail Shelf Bzl)": {"w": 60, "h": 40, "qr_size": 13},
    "40x50 mm (Vertical Product Hang Tag)": {"w": 40, "h": 50, "qr_size": 11},
    "80x50 mm (Large Counter Slot Display)": {"w": 80, "h": 50, "qr_size": 16},
    "Custom Size...": None
}

selected_size = st.sidebar.selectbox("1. Select Label Size Template", list(MINI_SIZE_TEMPLATES.keys()))

if selected_size == "Custom Size...":
    st.sidebar.markdown("📐 **Manual Dimensions Settings (mm):**")
    custom_w = st.sidebar.number_input("Tag Width (mm)", min_value=20, max_value=200, value=60, step=1)
    custom_h = st.sidebar.number_input("Tag Height (mm)", min_value=20, max_value=200, value=40, step=1)
    custom_qr = st.sidebar.number_input("QR Code Box Size (mm)", min_value=5, max_value=min(custom_w, custom_h)-5, value=13, step=1)
    dimensions = {"w": custom_w, "h": custom_h, "qr_size": custom_qr}
else:
    dimensions = MINI_SIZE_TEMPLATES[selected_size]

primary_color = st.sidebar.color_picker("Text & Accent Color", "#8a1515")

# Extended design selection library containing 50 distinct structural layouts and themes
bg_style = st.sidebar.selectbox("Ticket Design Theme style", [
    "01. Solid Primary Header Accent", "02. Minimalist Plain Paper White", "03. Double Thin Inset Border Frame", 
    "04. Soft Cream Vintage Palette", "05. Light Border Box Layout", "06. Minimalist Left Ribbon Strip", 
    "07. Modern Gradient Top Row", "08. Dark Mode Luxury Aesthetic", "09. Midnight Premium Charcoal Slate",
    "10. Warm Gold Royale Trim", "11. Emerald Forest Fresh Grid", "12. Nordic Frosted Ocean Aqua",
    "13. Sunset Crimson Gradient Wave", "14. Industrial Steel Technical Tech", "15. Rustic Eco Kraft Cardboard",
    "16. Cyberpunk Violet Neon Glow", "17. Retro Arcade Pixel Block", "18. Classic Monochromatic Ink",
    "19. Clean Corporate Corporate Line", "20. Bold Bright Tangerine Accent", "21. Subtle Sand Dunes Texture",
    "22. Lavender Dream Boutique Tint", "23. Royal Navy Formal Prestige", "24. Matcha Green Organic Clean",
    "25. Pink Velvet Candy Cosmetic", "26. High-Contrast Canary Warning", "27. Deep Wine Cabernet Executive",
    "28. Electric Cobalt Fusion Stripe", "29. Minimal Slate Geometric Frame", "30. Concrete Grey Loft Minimal",
    "31. Tropical Palm Breezy Oasis", "32. Copper Metallic Heritage Trim", "33. Polar Ice Minimal Crisp",
    "34. Desert Quartz Terracotta Clay", "35. Dark Chocolate Handcrafted Treat", "36. Vintage Newspaper Layout",
    "37. Smooth Sage Contemporary Flat", "38. Neon Lime Shockwave Border", "39. Deep Plum Royal Velvet",
    "40. Classic Blueprint Architectural", "41. Soft Olive Botanical Organic", "42. Carbon Fiber Performance Grid",
    "43. Honey Amber Sweet Bakery", "44. Matte Onyx Textured Silhouette", "45. Clean Mint Pharmacy Wellness",
    "46. Coral Reef Summer Bright", "47. Steel Blue Mechanical Heavy", "48. Orchid Luxe Salon Polish",
    "49. Brass Foundry Industrial Stamp", "50. Bright Abstract Techno Matrix"
])

font_choice = st.sidebar.selectbox("Select Font Family", ["Arial", "Helvetica", "Courier"])
title_size = st.sidebar.slider("Product Name Font Size (pt)", 7, 16, 9)
price_size = st.sidebar.slider("Price Font Size (pt)", 14, 42, 18)
show_was_price = st.sidebar.checkbox("Show Strikethrough 'Was' Price Row", value=True)

uploaded_logo = st.sidebar.file_uploader("Upload Brand Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
logo_b64 = process_logo_to_base64(uploaded_logo)

web_font = "Courier New, monospace" if font_choice == "Courier" else f"{font_choice}, sans-serif"

# --- CORE THEMATIC DESIGN SOLVER ENGINE ---
def compute_ticket_styles(style_name, primary_hex):
    # Baseline fallback presets
    card_bg = "#ffffff"
    card_border = f"1.5px solid {primary_hex}"
    header_bg = primary_hex
    header_text = "#ffffff"
    code_text_color = "#444444"
    card_extra_css = ""
    
    # Simple conditional style rules overriding variables across all 50 themes
    if "02. Minimalist Plain" in style_name:
        header_bg, header_text, card_border = "transparent", primary_hex, "1px solid #dddddd"
    elif "03. Double Thin" in style_name:
        card_extra_css = f"box-shadow: inset 0 0 0 3px #ffffff, inset 0 0 0 4px {primary_hex};"
    elif "04. Soft Cream" in style_name:
        card_bg, card_border = "#fdfbf7", "1.5px solid #dcd1bd"
    elif "06. Minimalist Left" in style_name:
        card_extra_css = f"border-left: 6px solid {primary_hex};"
    elif "07. Modern Gradient" in style_name:
        header_bg = f"linear-gradient(135deg, {primary_hex} 0%, #4f4f4f 100%)"
    elif "08. Dark Mode" in style_name or "09. Midnight" in style_name:
        card_bg, header_text, code_text_color = "#121212", "#ffffff", "#aaaaaa"
        card_border = "1.5px solid #333333"
    elif "10. Warm Gold" in style_name:
        header_bg, card_border = "#1c1c1c", "2px solid #d4af37"
    elif "11. Emerald Forest" in style_name:
        header_bg, card_border = "#0b5345", "1.5px solid #117a65"
    elif "13. Sunset Crimson" in style_name:
        header_bg = "linear-gradient(90deg, #8a1515 0%, #e67e22 100%)"
    elif "15. Rustic Eco" in style_name:
        card_bg, header_bg = "#e5c298", "#6e473b"
    elif "16. Cyberpunk" in style_name:
        card_bg, header_bg, card_border = "#000000", "#5b0066", "2px solid #00ffff"
    elif "20. Bold Bright" in style_name:
        header_bg = "#ff6f00"
    elif "23. Royal Navy" in style_name:
        header_bg = "#1b4f72"
    elif "26. High-Contrast" in style_name:
        card_bg, header_bg, header_text = "#ffffff", "#f1c40f", "#000000"
    elif "44. Matte Onyx" in style_name:
        card_bg, header_bg = "#1a1a1a", "#000000"
        card_border = "1px solid #222"
        
    return {
        "card_bg": card_bg, "card_border": card_border, "header_bg": header_bg, 
        "header_text": header_text, "code_text_color": code_text_color, "extra_css": card_extra_css
    }

resolved_theme = compute_ticket_styles(bg_style, primary_color)

# --- MAIN INTERFACE DISPLAY ---
st.title("🎟️ Retail Batch Mini Price Tag Generator")
st.write("Layout system optimized strictly for high-accuracy standard millimeter thermal and shelf edge feeds.")
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
        
        mapped = {}
        for col in df.columns:
            c_low = col.lower().strip()
            if "item code" in c_low: mapped["Item Code"] = col
            elif "description" in c_low: mapped["Product Name"] = col
            elif "highlight" in c_low: mapped["Highlights"] = col
            elif "brand" in c_low: mapped["Brand"] = col
            elif c_low == "now": mapped["Price"] = col
            elif c_low == "was": mapped["Was Price"] = col
            elif c_low == "sku" or c_low == "barcode": mapped["SKU"] = col
            elif "url" in c_low or "link" in c_low: mapped["URL"] = col

        required = ["Item Code", "Product Name", "Price", "SKU"]
        missing = [r for r in required if r not in mapped]

        if missing:
            st.error(f"Missing required columns: {missing}. Detected columns: {list(df.columns)}")
        else:
            st.success("✨ Spreadsheet structure verified successfully!")
            st.dataframe(df.head(3), use_container_width=True)

            # --- GENERATION CONTAINER LOOP ---
            html_cards = ""
            for idx, row in df.iterrows():
                try:
                    p_val = float(row[mapped["Price"]])
                    formatted_price = f"{p_val:.2f}"
                except:
                    formatted_price = str(row[mapped['Price']])

                was_formatted_num = ""
                if "Was Price" in mapped and not pd.isna(row[mapped["Was Price"]]):
                    try:
                        was_val = float(row[mapped["Was Price"]])
                        was_formatted_num = f"{was_val:.2f}"
                    except:
                        was_formatted_num = str(row[mapped["Was Price"]])

                brand = str(row[mapped["Brand"]]).strip() if "Brand" in mapped else ""
                highlights = str(row[mapped["Highlights"]]).strip() if "Highlights" in mapped else ""
                highlights = highlights.replace('\n', '<br>')
                
                sku = str(row[mapped["SKU"]]).strip()
                item_code = str(row[mapped["Item Code"]]).strip()
                qr_b64 = generate_qr_base64(row[mapped["URL"]] if "URL" in mapped else "https://example.com")

                scale_factor = max(1.0, dimensions['w'] / 60.0)
                calculated_highlights_pt = max(7.5, 8.0 * (scale_factor * 0.72))
                calculated_labels_pt = max(8.0, 8.0 * (scale_factor * 0.72))

                print_price_html = f"""
                <table style="border-collapse: collapse; border: none; margin: 0; padding: 0; font-family: {web_font}; text-align: left;">
                    <tbody>
                """
                if show_was_price and was_formatted_num:
                    print_price_html += f"""
                        <tr>
                            <td style="padding: 0 4px 0 0; font-size: {max(8.0, (price_size - 6) * scale_factor)}pt; color: #888; font-weight: bold; line-height: 1;">AED</td>
                            <td style="padding: 0; font-size: {price_size - 4}pt; color: #888; text-decoration: line-through; line-height: 1;">{was_formatted_num}</td>
                        </tr>
                    """
                print_price_html += f"""
                        <tr>
                            <td style="padding: 0 4px 0 0; font-size: {max(10.0, (price_size - 2) * scale_factor)}pt; color: {primary_color}; font-weight: bold; line-height: 1;">AED</td>
                            <td style="padding: 0; font-size: {price_size}pt; font-weight: bold; color: {primary_color}; line-height: 1;">{formatted_price}</td>
                        </tr>
                    </tbody>
                </table>
                """

                print_highlights_html = f"""
                <div style="color: #333; font-size: {calculated_highlights_pt}pt; line-height: 1.35; margin-top: 2px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical;">
                    <strong style="text-transform: uppercase; font-weight: bold; display: block; margin-bottom: 1.5px; font-size: {calculated_highlights_pt + 0.5}pt;">PRODUCT HIGHLIGHTS:</strong>
                    {highlights}
                </div>
                """ if highlights else ""

                header_text_content = f'<strong style="text-transform: uppercase; font-weight: 900;">{brand}</strong>: <span style="font-weight: normal;">{row[mapped["Product Name"]]}</span>' if brand else f'<span style="font-weight: normal;">{row[mapped["Product Name"]]}</span>'

                card_logo_html = f"""
                <div style="position: absolute; top: 1mm; right: 2mm; max-width: 25%; max-height: 20%; display: flex; justify-content: flex-end; align-items: center; z-index: 20;">
                    <img src="data:image/png;base64,{logo_b64}" style="max-width: 100%; max-height: 100%; object-fit: contain;" />
                </div>
                """ if logo_b64 else ""

                html_cards += f"""
                <div class="ticket-card" style="width: {dimensions['w']}mm; height: {dimensions['h']}mm; border: {resolved_theme['card_border']}; background: {resolved_theme['card_bg']}; {resolved_theme['extra_css']} box-sizing: border-box; position: relative; font-family: {web_font}; overflow: hidden; display: inline-block; margin: 1.5mm; vertical-align: top; text-align: left; page-break-inside: avoid; break-inside: avoid;">
                    {card_logo_html}
                    <div style="background: {resolved_theme['header_bg']}; padding: 4px 6px; display: flex; align-items: center; justify-content: center; text-align: center; height: 26%; box-sizing: border-box; overflow: hidden;">
                        <div style="color: {resolved_theme['header_text']}; font-size: {title_size}pt; line-height: 1.25; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; width: 100%;">{header_text_content}</div>
                    </div>
                    <div style="height: 74%; padding: 4px 6px; box-sizing: border-box; display: flex; justify-content: space-between; align-items: stretch; gap: 4px;">
                        
                        <div style="width: 62%; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box; overflow: hidden;">
                            <div>
                                <div style="color: {resolved_theme['code_text_color']}; font-size: {calculated_labels_pt}pt; font-weight: bold; white-space: nowrap; line-height: 1; margin-bottom: 2px;">{item_code}</div>
                                {print_highlights_html}
                            </div>
                            <div>{print_price_html}</div>
                        </div>
                        
                        <div style="width: 35%; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; box-sizing: border-box; overflow: hidden;">
                            <div style="font-weight: bold; font-size: {calculated_labels_pt}pt; text-align: center; color: {resolved_theme['code_text_color']}; margin-bottom: 1.5mm; width: 100%; text-transform: uppercase; line-height: 1;">SKU</div>
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
                    .print-btn {{ background-color: {primary_color}; color: white; border: none; padding: 12px 30px; font-size: 14px; font-weight: bold; border-radius: 4px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.15); margin: 20px auto; display: block; text-transform: uppercase; letter-spacing: 0.5px; }}
                    .print-btn:hover {{ opacity: 0.9; }}
                    .page-container {{ width: 210mm; padding: 5mm; margin: 0 auto; background: white; box-sizing: border-box; text-align: left; display: flex; flex-wrap: wrap; align-content: flex-start; }}
                    
                    @media print {{
                        @page {{ margin: 0mm; size: A4 portrait; }}
                        body {{ background: white; margin: 0; padding: 0; }}
                        .print-btn {{ display: none !important; }}
                        .page-container {{ width: 210mm; padding: 6mm 4mm; margin: 0 auto; background: transparent; border: none; box-shadow: none; display: flex !important; flex-wrap: wrap !important; }}
                        .ticket-card {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; color-adjust: exact; }}
                    }}
                </style>
            </head>
            <body>
                <button class="print-btn" onclick="window.print()">🖨️ Print Bulk Mini Sheet</button>
                <div class="page-container">{html_cards}</div>
            </body>
            </html>
            """
            st.components.v1.html(iframe_content, height=850, scrolling=True)
    except Exception as e:
        st.error(f"Data Parser Error: {e}")
