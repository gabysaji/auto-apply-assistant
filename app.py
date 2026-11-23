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
