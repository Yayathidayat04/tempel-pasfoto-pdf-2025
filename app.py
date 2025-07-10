import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz  # PyMuPDF
from PIL import Image
import io

# Konversi mm ke pixel
def mm_to_px(mm):
    return mm * 2.83

def tempel_foto(pdf_file, foto_file, x, y, width_mm, height_mm):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    img = Image.open(foto_file)

    # Simpan gambar sebagai PNG di memori
    img_io = io.BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    # Ukuran pasfoto (dalam px)
    w = mm_to_px(width_mm)
    h = mm_to_px(height_mm)

    for page in doc:  # Hanya halaman pertama bisa disesuaikan
        rect = fitz.Rect(x, y, x + w, y + h)
        page.insert_image(rect, stream=img_io.getvalue())

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    return output

st.set_page_config(page_title="Pasfoto ke PDF Drag-Drop", layout="wide")
st.title("📎 Tempel Pasfoto ke PDF dengan Drag & Drop")

pdf_file = st.file_uploader("📄 Unggah file PDF", type=["pdf"])
foto_file = st.file_uploader("🖼️ Unggah Pasfoto (JPG/PNG)", type=["jpg", "jpeg", "png"])

# Opsi ukuran pasfoto
ukuran_opsi = st.selectbox("🖼️ Pilih Ukuran Pasfoto:", ["3 x 4 cm", "4 x 6 cm", "Manual"])
if ukuran_opsi == "3 x 4 cm":
    width_mm, height_mm = 30.0, 40.0
elif ukuran_opsi == "4 x 6 cm":
    width_mm, height_mm = 40.0, 60.0
else:
    width_mm = st.number_input("Lebar Pasfoto (mm)", value=35.0)
    height_mm = st.number_input("Tinggi Pasfoto (mm)", value=45.0)

if pdf_file and foto_file:
    # Preview halaman pertama PDF
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=100)
    pdf_image = Image.open(io.BytesIO(pix.tobytes("png")))
    doc.close()

    st.markdown("## 🖱️ Drag & Drop Pasfoto ke PDF")
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=1,
        stroke_color="#000",
        background_image=pdf_image,
        update_streamlit=True,
        height=pdf_image.height,
        width=pdf_image.width,
        drawing_mode="image",
        key="canvas",
    )

    # Ambil koordinat gambar yang digeser
    if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
        objek = canvas_result.json_data["objects"][-1]
        x = objek["left"]
        y = objek["top"]

        st.success(f"📍 Koordinat terpilih: X={int(x)} px, Y={int(y)} px")

        if st.button("🖨️ Tempel Pasfoto ke PDF"):
            pdf_file.seek(0)
            output = tempel_foto(pdf_file, foto_file, x, y, width_mm, height_mm)

            st.subheader("🖼️ Preview Hasil Akhir")
            final_doc = fitz.open(stream=output.getvalue(), filetype="pdf")
            preview_pix = final_doc.load_page(0).get_pixmap(dpi=100)
            st.image(preview_pix.tobytes("png"), caption="Halaman 1 - Hasil Akhir", use_column_width=True)
            final_doc.close()

            st.download_button("📥 Unduh PDF Hasil", data=output, file_name="hasil.pdf", mime="application/pdf")
    else:
        st.info("Geser pasfoto ke halaman PDF pada kanvas di atas.")
else:
    st.warning("Silakan unggah PDF dan pasfoto terlebih dahulu.")
