# Terminal-editable Python LaTeX Report

## Setup

Install a LaTeX distribution (MacTeX on macOS or TeX Live on Linux), then run:

```bash
cd python_latex_report_terminal
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py build
```

On macOS, if `pdflatex` is missing, run `export PATH="/Library/TeX/texbin:$PATH"`.

## Edit the report directly from Terminal

```bash
python main.py edit introduction
python main.py edit theory
python main.py edit results
python main.py edit conclusion
```

The default editor is `nano`. Save with **Ctrl+O**, Enter, then exit with **Ctrl+X**. You can also use `EDITOR=vim python main.py edit introduction`.

The text is stored in `sections/*.txt`. Blank lines create paragraph breaks. LaTeX special characters in plain text are escaped automatically.

## Build a new PDF

```bash
python main.py build
python main.py build --title "My Report" --author "Your Name"
python main.py build --figure images/total_sales_by_store1.png --caption "New chart"
python main.py build --no-figure
python main.py build --output output/custom.pdf
```

The generated file is `output/report.pdf` by default. The original `report/` Python modules are retained as reference; the editable `sections/` text files are used by the new generator.

## Quick view

```bash
python main.py show introduction
```

## Write the report in Streamlit (browser UI)

After installing dependencies and a TeX distribution with `pdflatex`:

```bash
streamlit run app.py
```

Open the local address printed in your terminal (usually `http://localhost:8501`). Edit the four report sections, change the title/author, optionally upload a chart, click **Generate PDF**, and then **Download PDF**. The app reuses `main.py` for compilation. Text edits in the browser are session-local; they do not overwrite `sections/*.txt`. To edit those files permanently, use `python main.py edit introduction` etc.

**Note:** Streamlit Cloud does not automatically include `pdflatex`. Deploy on a machine/container with TeX Live installed, or add TeX installation to your deployment setup.


## Deploy to Streamlit Community Cloud

1. Upload the **contents of this folder** (not the ZIP or the containing folder) to the root of a GitHub repository. Keep `app.py`, `requirements.txt`, and `packages.txt` at repository root.
2. Go to https://share.streamlit.io/ and choose **Create app** → **Deploy from GitHub**.
3. Choose your repository and `main` branch; set the main file to `app.py`. Deploy.
4. Wait for system packages (including `pdflatex`) and Python dependencies to install.
5. Enter a short report and click **Generate PDF** then **Download PDF**.

`packages.txt` is for Debian/Ubuntu system packages on Community Cloud, not pip. The TeX Live packages can make the first deployment slow. If your hosting provider does not support `packages.txt`, use a Docker-based host with TeX Live installed.

**Privacy and storage:** This app does not implement authentication or permanent report storage. Report text lives in the browser session; generated PDFs are held in session memory. Do not enter confidential material into a public deployment.

**Local test:** Install `requirements.txt` with pip, install `pdflatex` separately, then run `streamlit run app.py`.


## Fix: `pdflatex not found` on Streamlit Community Cloud

1. In GitHub, verify that `packages.txt` is **at the repository root**, beside `app.py`, and contains the TeX Live packages. Uploading the ZIP file itself is not enough; upload its **extracted contents**.
2. Verify the deployed repository, branch, and main file path (`app.py`) in Streamlit Cloud.
3. Rebuild/redeploy the app so system packages are installed; check build logs for `apt`/TeX Live installation errors. A simple browser refresh will not install missing packages.
4. Expand **Deployment diagnostics** in the app. It should show `pdflatex: /usr/bin/pdflatex` (or another executable path).
5. If it still says NOT FOUND, check the build logs before attempting to generate a PDF.

**Local use:** `packages.txt` is only for the cloud Linux environment. Install TeX Live/MacTeX/MiKTeX separately on your computer and ensure `pdflatex` is on PATH.


## Local browser launch and PDF preview

Install dependencies, then run `python3 run_local.py` (macOS/Linux) or `python run_local.py` (Windows). The launcher waits for Streamlit to become healthy and opens `http://localhost:8501` in your default browser. Stop with Ctrl+C. You can still use `streamlit run app.py` normally.

Click **Generate PDF** to compile the report and show an embedded PDF preview above the Download PDF button. Some browsers block embedded data-URI PDFs; use the download button as a fallback. A working `pdflatex` installation is required to compile PDFs.


## Chrome-safe PDF download

The PDF is downloaded with Streamlit's native `st.download_button` and stored in session state. The inline preview uses `st.pdf` rather than a `data:` iframe, which Chrome may block. Run with `python -m streamlit run app.py`. If you have an older Streamlit installation, run `python -m pip install -r requirements.txt --upgrade`.
