import os
import urllib.parse
import subprocess
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Auto-Apply Assistant", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.25);
        padding: 14px 18px;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; color: #1f6feb; }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem; opacity: 0.75; text-transform: uppercase; letter-spacing: 0.04em; }
    .packet-card {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Auto-Apply Assistant")
st.caption("Human-in-the-loop ATS scoring, single-page resume tailoring, and global application tracker.")

STATUS_OPTIONS = ["Ready to Submit", "Applied", "Interviewing", "Rejected", "Skipped"]

with st.sidebar:
    st.subheader("Pipeline Actions")
    if st.button("1. Fetch Fresh Jobs", use_container_width=True, type="primary"):
        with st.spinner("Scanning live roles across target countries..."):
            res = subprocess.run(["python3", "job_fetcher.py"], capture_output=True, text=True)
            st.success("Job fetch complete.")
            with st.expander("Fetcher Log"):
                st.code(res.stdout or res.stderr)

    if st.button("2. Score & Tailor Resumes", use_container_width=True):
        with st.spinner("Scoring ATS fit and building application packets..."):
            res = subprocess.run(["python3", "auto_apply.py"], capture_output=True, text=True)
            st.success("Application packets ready.")
            with st.expander("Tailoring Log"):
                st.code(res.stdout or res.stderr)
            st.rerun()

    st.divider()
    if os.path.exists("my_resume.txt"):
        with st.expander("Master Resume (my_resume.txt)"):
            st.text(open("my_resume.txt").read())

if not os.path.exists("tracker.csv"):
    st.info("No opportunities in tracker.csv yet. Configure your Profile & API Key below, then run Pipeline Actions in the sidebar.")
    tab_settings = st.container()
else:
    df = pd.read_csv("tracker.csv")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Action Queue", len(df[df["Status"] == "Ready to Submit"]))
    c2.metric("Applied", len(df[df["Status"] == "Applied"]))
    c3.metric("Interviews", len(df[df["Status"] == "Interviewing"]))
    c4.metric("Avg ATS Score", f"{int(df['ATS_Score'].mean())}%")

    st.write("")
    regions = ["All Regions"] + sorted(df["Region"].dropna().unique().tolist()) if "Region" in df.columns else ["All Regions"]
    selected_region = st.selectbox("Region Filter", regions, label_visibility="collapsed")
    scoped_df = df[df["Region"] == selected_region].copy() if (selected_region != "All Regions" and "Region" in df.columns) else df.copy()

    tab_queue, tab_history, tab_settings = st.tabs(["Active Queue (Ready to Submit)", "Submitted & Archive", "Profile & API Settings"])

    with tab_queue:
        queue_df = scoped_df[scoped_df["Status"] == "Ready to Submit"].copy()
        if queue_df.empty:
            st.success("Queue clear! All matched roles in this region have been processed.")
        else:
            display_cols = [c for c in ["ATS_Score", "Region", "Location", "Company", "Role", "Sponsorship", "Salary_Info", "Status"] if c in queue_df.columns]
            edited_queue = st.data_editor(
                queue_df[display_cols],
                column_config={"ATS_Score": st.column_config.NumberColumn("ATS Match", format="%d%%"), "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True)},
                disabled=[c for c in display_cols if c != "Status"],
                use_container_width=True, hide_index=True, key="queue_editor",
            )
            if not edited_queue["Status"].equals(queue_df["Status"]):
                for idx in edited_queue.index: df.at[idx, "Status"] = edited_queue.at[idx, "Status"]
                df.to_csv("tracker.csv", index=False); st.rerun()

            st.divider()
            st.subheader("Packet Inspector & Outreach Assets")
            idx_list = queue_df.index.tolist()
            chosen_idx = st.selectbox(
                "Select active role:",
                idx_list,
                format_func=lambda i: f"[{df.at[i, 'ATS_Score']}%] {df.at[i, 'Company']} — {df.at[i, 'Role']} ({df.at[i, 'Location']})",
                key="active_role_selector"
            )
            job = df.loc[chosen_idx]
            pdf_path = str(job["Resume_PDF"])
            folder = os.path.dirname(pdf_path)

            left, right = st.columns([1, 1.35])
            with left:
                recruiter_path = os.path.join(folder, "recruiter_info.txt")
                recruiter_text = open(recruiter_path).read().strip() if os.path.exists(recruiter_path) else "NONE"
                has_contact = recruiter_text and recruiter_text.upper() != "NONE" and "talent acquisition" not in recruiter_text.lower()
                comp = str(job["Company"])
                li_people_url = "https://" + "://linkedin.com" + urllib.parse.quote(comp + " talent acquisition")
                contact_html = f'<p style="margin-bottom:0;"><strong>Recruiter Contact:</strong> {recruiter_text}</p>' if has_contact else ""

                st.markdown(f"""<div class="packet-card"><h4 style="margin-top:0;">{job['Role']}</h4><p style="color:#1f6feb; font-weight:600; margin-bottom:8px;">{job['Company']} &bull; {job.get('Location', '')}</p><p style="margin-bottom:4px;"><strong>Sponsorship:</strong> {job.get('Sponsorship', 'N/A')}</p><p style="margin-bottom:4px;"><strong>Compensation:</strong> {job.get('Salary_Info', 'Not listed')}</p>{contact_html}</div>""", unsafe_allow_html=True)

                if has_contact:
                    st.link_button("Open Application Portal", str(job["Apply_URL"]), type="primary", use_container_width=True)
                else:
                    b1, b2 = st.columns(2)
                    b1.link_button("Open Application Portal", str(job["Apply_URL"]), type="primary", use_container_width=True)
                    b2.link_button("Search Hiring Team", li_people_url, use_container_width=True)

                p1, p2 = st.columns(2)
                if os.path.exists(pdf_path):
                    p1.download_button("Download 1-Page PDF", open(pdf_path, "rb").read(), file_name=os.path.basename(pdf_path), mime="application/pdf", use_container_width=True)
                    if p2.button("Open PDF in Preview", use_container_width=True, key=f"prev_res_{chosen_idx}"): subprocess.run(["open", pdf_path])

                st.write("")
                if st.button("Mark as Applied & Archive", use_container_width=True, key=f"app_{chosen_idx}"):
                    df.at[chosen_idx, "Status"] = "Applied"; df.to_csv("tracker.csv", index=False); st.rerun()

            with right:
                t_li, t_email, t_cl = st.tabs(["LinkedIn Note (Free Limit)", "Recruiter Email", "Tailored Cover Letter"])
                with t_li:
                    li_path = os.path.join(folder, "linkedin_note.txt") if os.path.exists(os.path.join(folder, "linkedin_note.txt")) else os.path.join(folder, "cover_note.txt")
                    if os.path.exists(li_path):
                        note_txt = open(li_path).read().strip()
                        st.caption(f"Character count: {len(note_txt)} / 300 max")
                        st.text_area("LinkedIn Connection Note", value=note_txt, height=130, label_visibility="collapsed", key=f"li_{chosen_idx}")
                with t_email:
                    em_path = os.path.join(folder, "recruiter_email.txt")
                    st.text_area("Recruiter Email", value=open(em_path).read().strip(), height=260, label_visibility="collapsed", key=f"em_{chosen_idx}") if os.path.exists(em_path) else st.info("Run '2. Score & Tailor Resumes' to generate recruiter email.")
                with t_cl:
                    cl_path = os.path.join(folder, "cover_letter.txt")
                    cl_pdfs = [f for f in os.listdir(folder) if f.startswith("Cover_Letter_") and f.endswith(".pdf")] if os.path.exists(folder) else []
                    if cl_pdfs:
                        cl_pdf_full = os.path.join(folder, cl_pdfs[0])
                        c1_btn, c2_btn = st.columns(2)
                        c1_btn.download_button("Download Cover Letter PDF", open(cl_pdf_full, "rb").read(), file_name=cl_pdfs[0], mime="application/pdf", use_container_width=True)
                        if c2_btn.button("Open Cover Letter in Preview", use_container_width=True, key=f"prev_cl_{chosen_idx}"): subprocess.run(["open", cl_pdf_full])
                    st.text_area("Cover Letter", value=open(cl_path).read().strip(), height=280, label_visibility="collapsed", key=f"cl_{chosen_idx}") if os.path.exists(cl_path) else st.info("Run '2. Score & Tailor Resumes' to generate cover letter.")

    with tab_history:
        hist_df = scoped_df[scoped_df["Status"] != "Ready to Submit"].copy()
        if hist_df.empty:
            st.info("No submitted or archived applications yet.")
        else:
            display_cols = [c for c in ["ATS_Score", "Region", "Company", "Role", "Status", "Apply_URL"] if c in hist_df.columns]
            edited_hist = st.data_editor(
                hist_df[display_cols],
                column_config={"ATS_Score": st.column_config.NumberColumn("ATS Match", format="%d%%"), "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True), "Apply_URL": st.column_config.LinkColumn("Job Link")},
                disabled=[c for c in display_cols if c != "Status"],
                use_container_width=True, hide_index=True, key="history_editor",
            )
            if not edited_hist["Status"].equals(hist_df["Status"]):
                for idx in edited_hist.index: df.at[idx, "Status"] = edited_hist.at[idx, "Status"]
                df.to_csv("tracker.csv", index=False); st.rerun()

with tab_settings:
    st.subheader("Profile & API Configuration")
    st.caption("Upload your existing resume (PDF, DOCX, or TXT), add optional projects/experience, and save your API key locally.")

    env_vars = {}
    if os.path.exists(".env"):
        for line in open(".env"):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env_vars[k] = v.strip().strip('"').strip("'")

    uploaded_file = st.file_uploader("Upload Existing Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    extracted_text = ""
    if uploaded_file is not None:
        fname = uploaded_file.name.lower()
        try:
            if fname.endswith(".pdf"):
                from pypdf import PdfReader
                reader = PdfReader(uploaded_file)
                extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
            elif fname.endswith(".docx"):
                import docx
                doc = docx.Document(uploaded_file)
                extracted_text = "\n".join(para.text for para in doc.paragraphs).strip()
            else:
                extracted_text = uploaded_file.read().decode("utf-8", errors="ignore").strip()
            if extracted_text:
                with open("my_resume.txt", "w") as rf:
                    rf.write(extracted_text + "\n")
                st.success(f"Extracted text from {uploaded_file.name} and updated Master Resume!")
        except Exception as e:
            st.error(f"Could not read file: {e}")

    curr_resume = extracted_text if extracted_text else (open("my_resume.txt").read() if os.path.exists("my_resume.txt") else "")
    curr_extra = open("extra_experience.txt").read() if os.path.exists("extra_experience.txt") else ""

    with st.form("settings_form"):
        api_key_in = st.text_input("Gemini API Key (Free at ://google.com)", value=env_vars.get("GEMINI_API_KEY", ""), type="password")
        scol1, scol2 = st.columns(2)
        li_in = scol1.text_input("LinkedIn Profile URL", value=env_vars.get("LINKEDIN_URL", ""))
        gh_in = scol2.text_input("GitHub / Portfolio URL", value=env_vars.get("GITHUB_URL", ""))

        resume_in = st.text_area("Master Resume Text (Auto-filled from upload or edit directly)", value=curr_resume, height=260)
        extra_in = st.text_area(
            "Optional Extra Experience & Projects Bank (Included in tailored CV ONLY when relevant to the target job)",
            value=curr_extra,
            height=160,
            placeholder="Add extra home labs, freelance work, or certifications here. They will only be added to your tailored PDF when relevant to the specific job."
        )

        if st.form_submit_button("Save Settings", type="primary"):
            with open(".env", "w") as ef:
                ef.write(f'GEMINI_API_KEY="{api_key_in.strip()}"\n')
                ef.write(f'LINKEDIN_URL="{li_in.strip()}"\n')
                ef.write(f'GITHUB_URL="{gh_in.strip()}"\n')
            with open("my_resume.txt", "w") as rf:
                rf.write(resume_in.strip() + "\n")
            with open("extra_experience.txt", "w") as xf:
                xf.write(extra_in.strip() + "\n")
            st.success("Saved! Your resume, optional experience bank, and API settings are ready.")
