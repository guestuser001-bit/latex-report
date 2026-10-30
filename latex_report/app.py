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

latex_executable = shutil.which("pdflatex")
if not latex_executable:
    st.error("pdflatex is missing from the server. On Streamlit Community Cloud, check that packages.txt is committed at the GitHub repository root and rebuild/redeploy the app.")
else:
    st.sidebar.success(f"LaTeX available: {latex_executable}")
with st.sidebar.expander("Deployment diagnostics"):
    st.code(f"pdflatex: {latex_executable or 'NOT FOUND'}\npackages.txt: {(ROOT / 'packages.txt').is_file()}\napp.py: {Path(__file__).resolve()}")
    st.caption("packages.txt being present here does not prove that its packages were installed. Check the deployment logs.")

if st.button("Generate PDF", type="primary", use_container_width=True, disabled=not latex_executable):
    st.session_state.pop("pdf_bytes", None)
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
    st.subheader("Generated PDF")
    st.success("Your report is ready. Download it using the button below.")
    st.download_button(
        label="Download PDF",
        data=st.session_state["pdf_bytes"],
        file_name="report.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="download_report_pdf",
        on_click="ignore",
    )
    st.subheader("PDF preview")
    st.caption("The preview uses Streamlit's native PDF viewer rather than a browser-blocked data URL.")
    if hasattr(st, "pdf"):
        st.pdf(st.session_state["pdf_bytes"], height=780)
    else:
        st.info("For an inline PDF preview, upgrade Streamlit to a version that supports st.pdf. The download button above works independently.")
    st.caption("If you edit the report, click Generate PDF again to update the PDF.")
