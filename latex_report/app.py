"""Streamlit editor for the existing PyLaTeX report generator."""
from pathlib import Path
from types import SimpleNamespace
import shutil
import tempfile
import streamlit as st
from main import ROOT, SECTIONS, read_section, build

st.set_page_config(page_title="LaTeX Report Studio", page_icon="📄", layout="wide")
st.title("LaTeX Report Studio")
st.caption("Write your report in the browser, generate a PDF using the existing Python/LaTeX engine, and download it.")

if "report_text" not in st.session_state:
    st.session_state.report_text = {name: read_section(name) for name in SECTIONS}

with st.sidebar:
    st.header("Report settings")
    title = st.text_input("Title", "Vacuum System Report")
    author = st.text_input("Author", "Research Team")
    include_figure = st.checkbox("Include figure in Results", value=True)
    caption = st.text_input("Figure caption", "Total sales by store.", disabled=not include_figure)
    uploaded = st.file_uploader("Upload a PNG or JPG figure", type=["png", "jpg", "jpeg"], disabled=not include_figure)
    st.caption("Without an upload, the bundled sample figure is used.")

st.subheader("Write your report")
tabs = st.tabs([name.title() for name in SECTIONS])
for tab, name in zip(tabs, SECTIONS):
    with tab:
        st.session_state.report_text[name] = st.text_area(
            f"{name.title()} text", value=st.session_state.report_text[name],
            height=320, key=f"editor_{name}",
            help="Plain text. Separate paragraphs with blank lines. Special LaTeX characters are escaped automatically."
        )

if not shutil.which("pdflatex"):
    st.error("LaTeX is not installed on this server. For Streamlit Community Cloud, add packages.txt at the repository root and redeploy.")

if st.button("Generate PDF", type="primary", use_container_width=True):
    with st.spinner("Compiling PDF (requires pdflatex on the server)…"):
        try:
            with tempfile.TemporaryDirectory(prefix="streamlit_latex_") as folder:
                folder = Path(folder)
                figure_path = ROOT / "images" / "total_sales_by_store.png"
                if include_figure and uploaded is not None:
                    figure_path = folder / ("uploaded" + Path(uploaded.name).suffix.lower())
                    figure_path.write_bytes(uploaded.getvalue())
                output = folder / "report.pdf"
                args = SimpleNamespace(title=title, author=author, output=str(output),
                                       figure=str(figure_path), caption=caption,
                                       no_figure=not include_figure)
                build(args, sections_override=st.session_state.report_text)
                st.session_state.pdf_bytes = output.read_bytes()
            st.success("PDF generated successfully!")
        except (Exception, SystemExit) as exc:
            st.error(f"Could not generate PDF: {exc}")

if st.session_state.get("pdf_bytes"):
    st.download_button("Download PDF", data=st.session_state.pdf_bytes,
                       file_name="report.pdf", mime="application/pdf", use_container_width=True)
    st.caption("If you edit the text, click Generate PDF again to update the download.")
