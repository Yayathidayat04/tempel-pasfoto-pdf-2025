import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

# Konversi mm ke pixel (72 dpi PDF ≈ 2.83 px/mm)
def mm_to_px(mm):
    return mm * 2.83

def tempel_foto(pdf_file, foto_file, x_mm, y_mm, width_mm, height_mm):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    img = Image.open(foto_file)

    # Konversi ke PNG dalam memori
    img_io = io.BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    x = mm_to_px(x_mm)
    y = mm_to_px(y_mm)
    w = mm_to_px(width_mm)
    h = mm_to_px(height_mm)

    for page in doc:  # Semua halaman
        rect = fitz.Rect(x, y, x + w, y + h)
        page.insert_image(rect, stream=img_io.getvalue())

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    return output

st.set_page_config(page_title="Tempel Pasfoto ke PDF", layout="wide")
st.title("📎 Tempel Pasfoto ke PDF")

col1, col2 = st.columns(2)

with col1:
    pdf_file = st.file_uploader("📄 Unggah file PDF", type=["pdf"])
    if pdf_file:
        st.write("🔍 Preview Halaman Pertama PDF:")
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=100)
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, caption="Halaman 1", use_column_width=True)
        doc.close()

with col2:
    foto_file = st.file_uploader("🖼️ Unggah Pasfoto (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if foto_file:
        st.image(foto_file, caption="Preview Pasfoto", width=200)

st.markdown("## 📐 Posisi & Ukuran Pasfoto")

# POSISI
col3, col4 = st.columns(2)
with col3:
    x_mm = st.number_input("📍 Posisi X (mm)", value=10.0)
with col4:
    y_mm = st.number_input("📍 Posisi Y (mm)", value=10.0)

# OPSI UKURAN FOTO
ukuran_opsi = st.selectbox("🖼️ Pilih Ukuran Pasfoto:", ["Pilih manual", "3 x 4 cm", "4 x 6 cm"])

if ukuran_opsi == "3 x 4 cm":
    width_mm = 30.0
    height_mm = 40.0
elif ukuran_opsi == "4 x 6 cm":
    width_mm = 40.0
    height_mm = 60.0
else:
    col5, col6 = st.columns(2)
    with col5:
        width_mm = st.number_input("Lebar Pasfoto (mm)", value=35.0)
    with col6:
        height_mm = st.number_input("Tinggi Pasfoto (mm)", value=45.0)

if st.button("🖨️ Tempel Pasfoto ke PDF") and pdf_file and foto_file:
    pdf_file.seek(0)
    output_pdf = tempel_foto(pdf_file, foto_file, x_mm, y_mm, width_mm, height_mm)
    st.success("✅ Pasfoto berhasil ditempel!")

    # Preview hasil akhir
    st.subheader("🖼️ Preview Hasil Akhir")
    final_doc = fitz.open(stream=output_pdf.getvalue(), filetype="pdf")
    preview_page = final_doc.load_page(0)
    preview_pix = preview_page.get_pixmap(dpi=100)
    preview_img = preview_pix.tobytes("png")
    st.image(preview_img, caption="Halaman 1 - Hasil Akhir", use_column_width=True)
    final_doc.close()

    st.download_button("📥 Unduh PDF Hasil", data=output_pdf, file_name="hasil.pdf", mime="application/pdf")
