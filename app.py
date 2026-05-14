import streamlit as st
import pandas as pd
from streamlit_gps_location import gps_location_button
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import date
import io
from PIL import Image as PILImage

# Page configuration
st.set_page_config(
    page_title="Field Report App",
    layout="centered"
)

st.title("🔬 Field Scientific Report")

# --- 1. User Information ---
st.subheader("1. Researcher Information")
researcher_name = st.text_input("Researcher name")
discovery_title = st.text_input("Title of the discovery")
description = st.text_area("Description / Observations")

# --- 2. GPS Location ---
st.subheader("2. GPS Location")
location_data = gps_location_button(buttonText="Get my location")

latitude = None
longitude = None

if location_data is not None:
    latitude = location_data.get('latitude')
    longitude = location_data.get('longitude')

    if latitude is not None and longitude is not None:
        st.success(f"📍 Lat: {latitude}, Lon: {longitude}")
        map_data = pd.DataFrame({'lat': [latitude], 'lon': [longitude]})
        st.map(map_data)
else:
    st.info("Press 'Get my location' to capture GPS coordinates.")

# --- 3. Visual Evidence ---
st.subheader("3. Visual Evidence")
photo = st.camera_input("Take a photo as evidence")

# --- 4. Generate PDF ---
st.subheader("4. Generate Report")

if st.button("Generate PDF Report", use_container_width=True):
    # Validation
    errors = []
    if not researcher_name:
        errors.append("Researcher name is required.")
    if not discovery_title:
        errors.append("Discovery title is required.")
    if not description:
        errors.append("Description / observations are required.")
    if latitude is None or longitude is None:
        errors.append("GPS location is required.")
    if photo is None:
        errors.append("A photo is required.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        # Build PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'FieldTitle',
            parent=styles['Title'],
            fontSize=16,
            textColor=colors.white,
            backColor=colors.HexColor('#2e7d32'),
            alignment=1,
            spaceAfter=0,
            spaceBefore=0,
            leading=28,
        )

        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            fontName='Helvetica-Bold',
        )

        normal_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
        )

        story = []

        # Header bar
        story.append(Paragraph("FIELD REPORT", title_style))
        story.append(Spacer(1, 0.5*cm))

        # Researcher + Date on same line using a table
        from reportlab.platypus import Table, TableStyle
        today = date.today().strftime("%d/%m/%Y")
        header_data = [
            [Paragraph(f"<b>Researcher:</b> {researcher_name}", normal_style),
             Paragraph(f"<b>Date:</b> {today}", normal_style)]
        ]
        header_table = Table(header_data, colWidths=[9*cm, 6*cm])
        story.append(header_table)
        story.append(Spacer(1, 0.2*cm))

        # Coordinates
        story.append(Paragraph(f"Coordinates: Lat {latitude:.5f}, Lon {longitude:.5f}", normal_style))
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        story.append(Spacer(1, 0.3*cm))

        # Discovery
        story.append(Paragraph(f"Finding: {discovery_title}", label_style))
        story.append(Paragraph("Observations:", label_style))
        story.append(Paragraph(description, normal_style))
        story.append(Spacer(1, 0.5*cm))

        # Photo
        img_bytes = photo.getvalue()
        pil_img = PILImage.open(io.BytesIO(img_bytes))
        img_buffer = io.BytesIO()
        pil_img.save(img_buffer, format="JPEG")
        img_buffer.seek(0)

        rl_img = RLImage(img_buffer, width=8*cm, height=10*cm, kind='proportional')
        story.append(rl_img)

        doc.build(story)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Download PDF Report",
            data=buffer,
            file_name=f"field_report_{discovery_title.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
