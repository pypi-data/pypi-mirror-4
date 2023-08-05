CREATE SEQUENCE key_generator
    START WITH 10100
    INCREMENT BY 10
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

CREATE TABLE address (
    address_id integer NOT NULL,
    object_version integer,
    company_id integer,
    name1 character varying(255),
    name2 character varying(255),
    name3 character varying(255),
    street character varying(255),
    zip character varying(50),
    zipcity character varying(255),
    country character varying(100),
    state character varying(100),
    type character varying(50) NOT NULL,
    db_status character varying(50),
    source_url character varying(255),
    district character varying(255)
);


CREATE TABLE appointment_resource (
    appointment_resource_id integer NOT NULL,
    object_version integer,
    name character varying(255) NOT NULL,
    email character varying(255),
    email_subject character varying(255),
    category character varying(255),
    notification_time integer,
    db_status character varying(50)
);


CREATE TABLE article (
    article_id integer NOT NULL,
    article_unit_id integer,
    article_category_id integer,
    object_version integer,
    article_name character varying(255) NOT NULL,
    article_nr character varying(255) NOT NULL,
    article_text text,
    status character varying(50),
    price numeric(19,4),
    vat numeric(19,4),
    vat_group character varying(50),
    db_status character varying(50)
);


CREATE TABLE article_category (
    article_category_id integer NOT NULL,
    category_name character varying(255) NOT NULL,
    category_abbrev character varying(255)
);


CREATE TABLE article_unit (
    article_unit_id integer NOT NULL,
    format character varying(50),
    singular_unit character varying(255),
    plural_unit character varying(255)
);

CREATE TABLE company (
    company_id integer NOT NULL,
    object_version integer,
    owner_id integer,
    contact_id integer,
    template_user_id integer,
    is_private smallint,
    is_person smallint,
    is_readonly smallint,
    is_enterprise smallint,
    is_account smallint,
    is_intra_account smallint,
    is_extra_account smallint,
    is_trust smallint,
    is_team smallint,
    is_location_team smallint,
    is_customer smallint,
    number character varying(100),
    description character varying(255),
    priority character varying(50),
    keywords character varying(255),
    url character varying(255),
    email character varying(100),
    type character varying(50),
    bank character varying(100),
    bank_code character varying(50),
    account character varying(50),
    payment character varying(50),
    is_locked smallint,
    is_template_user smallint,
    can_change_password smallint,
    login character varying(50),
    password character varying(255),
    pop3_account character varying(50),
    name character varying(50),
    middlename character varying(50),
    firstname character varying(50),
    salutation character varying(50),
    degree character varying(50),
    birthday timestamp with time zone,
    sex character varying(10),
    source_url character varying(255),
    db_status character varying(50),
    sensitivity smallint,
    boss_name character varying(255),
    partner_name character varying(255),
    assistant_name character varying(255),
    department character varying(255),
    office character varying(255),
    occupation character varying(255),
    anniversary timestamp with time zone,
    dir_server character varying(255),
    email_alias character varying(255),
    freebusy_url character varying(255),
    fileas character varying(255),
    name_title character varying(255),
    name_affix character varying(255),
    im_address character varying(255),
    associated_contacts character varying(255),
    associated_categories character varying(255),
    associated_company character varying(255),
    show_email_as character varying(255),
    show_email2_as character varying(255),
    show_email3_as character varying(255),
    birthplace character varying(255),
    birthname character varying(255),
    family_status character varying(255),
    citizenship character varying(255),
    dayofdeath timestamp with time zone
);


CREATE TABLE company_assignment (
    company_assignment_id integer NOT NULL,
    company_id integer,
    sub_company_id integer,
    is_headquarter smallint,
    is_chief smallint,
    function character varying(255),
    db_status character varying(50)
);


CREATE TABLE company_category (
    company_category_id integer NOT NULL,
    object_version integer,
    category character varying(255),
    db_status character varying(50)
);


CREATE TABLE company_info (
    company_info_id integer NOT NULL,
    company_id integer NOT NULL,
    comment text,
    db_status character varying(50)
);


CREATE TABLE company_value (
    company_value_id integer NOT NULL,
    company_id integer,
    attribute character varying(255),
    attribute_type character varying(50),
    value_string character varying(255),
    value_date timestamp with time zone,
    value_int integer,
    is_enum smallint,
    category character varying(255),
    uid integer,
    label character varying(255),
    type integer,
    is_label_localized smallint,
    db_status character varying(50)
);


CREATE TABLE ctags (
    entity character varying NOT NULL,
    ctag integer DEFAULT 0 NOT NULL
);



CREATE TABLE date_company_assignment (
    date_company_assignment_id integer NOT NULL,
    company_id integer,
    date_id integer,
    is_staff smallint,
    is_new smallint,
    partstatus character varying(50),
    role character varying(50),
    comment character varying(255),
    rsvp smallint,
    db_status character varying(50),
    outlook_key character varying(255)
);



CREATE TABLE date_info (
    date_info_id integer NOT NULL,
    date_id integer NOT NULL,
    comment text,
    db_status character varying(50)
);



CREATE TABLE date_x (
    date_id integer NOT NULL,
    object_version integer,
    owner_id integer,
    access_team_id integer,
    parent_date_id integer,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    cycle_end_date timestamp with time zone,
    type character varying(50),
    title character varying(255) NOT NULL,
    location character varying(255),
    absence character varying(255),
    resource_names character varying(255),
    write_access_list character varying(255),
    is_absence smallint,
    is_attendance smallint,
    is_conflict_disabled smallint,
    travel_duration_before integer,
    travel_duration_after integer,
    notification_time integer,
    db_status character varying(50),
    apt_type character varying(100),
    calendar_name character varying(255),
    source_url character varying(255),
    fbtype character varying(50),
    sensitivity smallint,
    busy_type smallint,
    importance smallint,
    last_modified integer,
    evo_reminder character varying(255),
    ol_reminder character varying(255),
    online_meeting character varying(255),
    associated_contacts character varying(255),
    keywords character varying(255)
);



CREATE TABLE document (
    document_id integer NOT NULL,
    object_version integer,
    project_id integer,
    parent_document_id integer,
    date_id integer,
    first_owner_id integer,
    current_owner_id integer,
    version_count integer,
    file_size integer,
    is_note smallint,
    is_folder smallint,
    is_object_link smallint,
    is_index_doc smallint,
    title character varying(255),
    abstract character varying(255),
    file_type character varying(255),
    object_link character varying(255),
    creation_date timestamp with time zone,
    lastmodified_date timestamp with time zone,
    status character varying(50),
    db_status character varying(50),
    contact character varying(255),
    company_id integer
);



CREATE TABLE doc (
)
INHERITS (document);


CREATE TABLE document_editing (
    document_editing_id integer NOT NULL,
    object_version integer,
    document_id integer,
    current_owner_id integer,
    title character varying(255),
    abstract character varying(255),
    file_type character varying(255),
    file_size integer,
    version integer,
    is_attach_changed smallint,
    checkout_date timestamp with time zone,
    status character varying(50),
    db_status character varying(50),
    contact character varying(255)
);



CREATE TABLE document_version (
    document_version_id integer NOT NULL,
    object_version integer,
    document_id integer,
    last_owner_id integer,
    title character varying(255),
    abstract character varying(255),
    file_type character varying(255),
    version integer,
    file_size integer,
    creation_date timestamp with time zone,
    archive_date timestamp with time zone,
    is_packed smallint,
    change_text text,
    db_status character varying(50),
    contact character varying(255)
);



CREATE TABLE enterprise (
)
INHERITS (company);



CREATE TABLE invoice (
    invoice_id integer NOT NULL,
    debitor_id integer NOT NULL,
    parent_invoice_id integer,
    invoice_nr character varying(255) NOT NULL,
    invoice_date timestamp with time zone,
    kind character varying(100),
    status character varying(100) NOT NULL,
    net_amount numeric(19,4),
    gross_amount numeric(19,4),
    paid numeric(19,4),
    comment text,
    object_version integer,
    db_status character varying(50)
);



CREATE TABLE invoice_account (
    invoice_account_id integer NOT NULL,
    enterprise_id integer NOT NULL,
    account_nr character varying(50) NOT NULL,
    balance numeric(19,4),
    object_version integer,
    db_status character varying(50)
);



CREATE TABLE invoice_accounting (
    invoice_accounting_id integer NOT NULL,
    action_id integer NOT NULL,
    debit numeric(19,4),
    balance numeric(19,4),
    object_version integer,
    db_status character varying(50)
);



CREATE TABLE invoice_action (
    invoice_action_id integer NOT NULL,
    account_id integer NOT NULL,
    invoice_id integer,
    document_id integer,
    action_date timestamp with time zone,
    action_kind character varying(100) NOT NULL,
    log_text text,
    object_version integer,
    db_status character varying(50)
);



CREATE TABLE invoice_article_assignment (
    invoice_article_assignment_id integer NOT NULL,
    invoice_id integer NOT NULL,
    article_id integer NOT NULL,
    article_count numeric(19,4) NOT NULL,
    object_version integer,
    net_amount numeric(19,4),
    vat numeric(19,8),
    comment text,
    db_status character varying(50)
);



CREATE TABLE job (
    job_id integer NOT NULL,
    object_version integer,
    parent_job_id integer,
    project_id integer,
    creator_id integer,
    executant_id integer,
    name character varying(255) NOT NULL,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    notify_x integer,
    is_control_job smallint,
    is_team_job smallint,
    is_new smallint,
    job_status character varying(255),
    category character varying(255),
    priority integer,
    db_status character varying(50),
    kind character varying(50),
    keywords character varying(255),
    source_url character varying(255),
    sensitivity smallint,
    job_comment text,
    completion_date timestamp with time zone,
    percent_complete smallint,
    actual_work smallint,
    total_work smallint,
    last_modified integer,
    accounting_info character varying(255),
    kilometers character varying(255),
    associated_companies character varying(255),
    associated_contacts character varying(255),
    timer_date timestamp with time zone,
    owner_id integer
);



CREATE TABLE job_assignment (
    job_assignment_id integer NOT NULL,
    parent_job_id integer NOT NULL,
    child_job_id integer NOT NULL,
    position_x integer,
    assignment_kind character varying(50),
    db_status character varying(50)
);



CREATE TABLE job_history (
    job_history_id integer NOT NULL,
    object_version integer,
    job_id integer NOT NULL,
    actor_id integer,
    action character varying(50),
    action_date timestamp with time zone,
    job_status character varying(50),
    db_status character varying(50)
);



CREATE TABLE job_history_info (
    job_history_info_id integer NOT NULL,
    job_history_id integer NOT NULL,
    comment text,
    db_status character varying(50)
);



CREATE TABLE job_resource_assignment (
    job_resource_assignment_id integer NOT NULL,
    resource_id integer,
    job_id integer,
    operative_part integer,
    db_status character varying(50)
);

CREATE TABLE log (
    log_id integer NOT NULL,
    creation_date timestamp with time zone NOT NULL,
    object_id integer NOT NULL,
    log_text text NOT NULL,
    action character varying(100) NOT NULL,
    account_id integer
);



CREATE TABLE login_token (
    token character varying(4096) NOT NULL,
    account_id integer NOT NULL,
    environment text,
    info text,
    creation_date timestamp with time zone DEFAULT now() NOT NULL,
    touch_date timestamp with time zone DEFAULT now() NOT NULL,
    timeout integer DEFAULT 3600 NOT NULL,
    expiration_date timestamp with time zone
);

CREATE TABLE news_article (
    news_article_id integer NOT NULL,
    object_version integer,
    name character varying(255),
    caption character varying(255),
    is_index_article smallint,
    creation_date timestamp with time zone,
    db_status character varying(50)
);

CREATE TABLE news_article_link (
    news_article_link_id integer NOT NULL,
    object_version integer,
    news_article_id integer,
    sub_news_article_id integer
);


CREATE TABLE note (
)
INHERITS (document);



CREATE TABLE obj_info (
    obj_id integer NOT NULL,
    obj_type character varying(255) NOT NULL
);



CREATE TABLE obj_link (
    obj_link_id integer NOT NULL,
    source_id integer NOT NULL,
    source_type character varying(50),
    target character varying(255) NOT NULL,
    target_id integer,
    target_type character varying(50),
    link_type character varying(50),
    label character varying(255)
);



CREATE TABLE obj_property (
    obj_property_id integer NOT NULL,
    obj_id integer NOT NULL,
    obj_type character varying(255),
    access_key integer,
    value_key character varying(255) NOT NULL,
    namespace_prefix character varying(255),
    preferred_type character varying(255) NOT NULL,
    value_string character varying(255),
    value_int integer,
    value_float numeric(19,8),
    value_date timestamp with time zone,
    value_oid character varying(255),
    blob_size integer,
    value_blob text
);



CREATE TABLE object_acl (
    object_acl_id integer NOT NULL,
    sort_key integer NOT NULL,
    action character varying(10) NOT NULL,
    object_id integer NOT NULL,
    auth_id integer,
    permissions character varying(50)
);



CREATE TABLE object_model (
    db_version integer NOT NULL,
    model_name character varying(255) NOT NULL
);



CREATE TABLE person (
)
INHERITS (company);



CREATE TABLE project (
    project_id integer NOT NULL,
    object_version integer,
    owner_id integer NOT NULL,
    team_id integer,
    number character varying(100),
    name character varying(255),
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    status character varying(255),
    is_fake smallint,
    db_status character varying(50),
    kind character varying(50),
    url character varying(100),
    parent_project_id integer
);


CREATE TABLE project_company_assignment (
    project_company_assignment_id integer NOT NULL,
    company_id integer,
    project_id integer,
    info character varying(255),
    has_access smallint,
    access_right character varying(50),
    db_status character varying(50)
);



CREATE TABLE project_info (
    project_info_id integer NOT NULL,
    project_id integer NOT NULL,
    comment text,
    db_status character varying(50)
);



CREATE TABLE resource (
    resource_id integer NOT NULL,
    resource_name character varying(255) NOT NULL,
    token character varying(255),
    object_id integer,
    quantity integer,
    comment text,
    standard_costs numeric(19,2),
    type integer NOT NULL,
    db_status character varying(50),
    object_version integer
);


CREATE TABLE session_log (
    session_log_id integer NOT NULL,
    account_id integer NOT NULL,
    log_date timestamp with time zone NOT NULL,
    action character varying(255) NOT NULL
);



CREATE TABLE staff (
    staff_id integer NOT NULL,
    company_id integer NOT NULL,
    description character varying(255),
    login character varying(255),
    is_team smallint,
    is_account smallint,
    db_status character varying(50)
);



CREATE TABLE table_version (
    table_name character varying(255) NOT NULL,
    table_version integer NOT NULL
);



CREATE TABLE team (
)
INHERITS (company);



CREATE TABLE telephone (
    telephone_id integer NOT NULL,
    object_version integer,
    company_id integer,
    number character varying(255),
    real_number character varying(255),
    type character varying(50) NOT NULL,
    info character varying(255),
    url character varying(255),
    db_status character varying(50)
);



CREATE TABLE trust (
)
INHERITS (company);


ALTER TABLE ONLY address
    ADD CONSTRAINT company_unique_adrtype UNIQUE (company_id, type);


ALTER TABLE ONLY ctags
    ADD CONSTRAINT ctag_unique_entity UNIQUE (entity);


ALTER TABLE ONLY login_token
    ADD CONSTRAINT login_token_pkey PRIMARY KEY (token);

ALTER TABLE ONLY address
    ADD CONSTRAINT pk_address PRIMARY KEY (address_id);


ALTER TABLE ONLY article
    ADD CONSTRAINT pk_article PRIMARY KEY (article_id);


ALTER TABLE ONLY article_category
    ADD CONSTRAINT pk_article_category PRIMARY KEY (article_category_id);


ALTER TABLE ONLY news_article_link
    ADD CONSTRAINT pk_article_link PRIMARY KEY (news_article_link_id);


ALTER TABLE ONLY company
    ADD CONSTRAINT pk_company PRIMARY KEY (company_id);


ALTER TABLE ONLY company_assignment
    ADD CONSTRAINT pk_company_assignment PRIMARY KEY (company_assignment_id);


ALTER TABLE ONLY company_category
    ADD CONSTRAINT pk_company_category PRIMARY KEY (company_category_id);


ALTER TABLE ONLY company_info
    ADD CONSTRAINT pk_company_info PRIMARY KEY (company_info_id);


ALTER TABLE ONLY company_value
    ADD CONSTRAINT pk_company_value PRIMARY KEY (company_value_id);


ALTER TABLE ONLY date_x
    ADD CONSTRAINT pk_date PRIMARY KEY (date_id);


ALTER TABLE ONLY date_company_assignment
    ADD CONSTRAINT pk_date_company_assignment PRIMARY KEY (date_company_assignment_id);


ALTER TABLE ONLY date_info
    ADD CONSTRAINT pk_date_info PRIMARY KEY (date_info_id);


ALTER TABLE ONLY document
    ADD CONSTRAINT pk_document PRIMARY KEY (document_id);


ALTER TABLE ONLY document_editing
    ADD CONSTRAINT pk_document_editing PRIMARY KEY (document_editing_id);


ALTER TABLE ONLY document_version
    ADD CONSTRAINT pk_document_version PRIMARY KEY (document_version_id);


ALTER TABLE ONLY invoice
    ADD CONSTRAINT pk_invoice PRIMARY KEY (invoice_id);


ALTER TABLE ONLY invoice_account
    ADD CONSTRAINT pk_invoice_account PRIMARY KEY (invoice_account_id);


ALTER TABLE ONLY invoice_accounting
    ADD CONSTRAINT pk_invoice_accounting PRIMARY KEY (invoice_accounting_id);


ALTER TABLE ONLY invoice_action
    ADD CONSTRAINT pk_invoice_action PRIMARY KEY (invoice_action_id);


ALTER TABLE ONLY invoice_article_assignment
    ADD CONSTRAINT pk_invoice_article_assignment PRIMARY KEY (invoice_article_assignment_id);


ALTER TABLE ONLY job
    ADD CONSTRAINT pk_job PRIMARY KEY (job_id);


ALTER TABLE ONLY job_assignment
    ADD CONSTRAINT pk_job_assignment PRIMARY KEY (job_assignment_id);


ALTER TABLE ONLY job_history
    ADD CONSTRAINT pk_job_history PRIMARY KEY (job_history_id);


ALTER TABLE ONLY job_history_info
    ADD CONSTRAINT pk_job_history_info PRIMARY KEY (job_history_info_id);


--
-- Name: pk_job_resource_id; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY job_resource_assignment
    ADD CONSTRAINT pk_job_resource_id PRIMARY KEY (job_resource_assignment_id);


--
-- Name: pk_log; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY log
    ADD CONSTRAINT pk_log PRIMARY KEY (log_id);


--
-- Name: pk_news_article; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY news_article
    ADD CONSTRAINT pk_news_article PRIMARY KEY (news_article_id);


--
-- Name: pk_obj_info; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY obj_info
    ADD CONSTRAINT pk_obj_info PRIMARY KEY (obj_id);


--
-- Name: pk_obj_property; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY obj_property
    ADD CONSTRAINT pk_obj_property PRIMARY KEY (obj_property_id);



--
-- Name: pk_project; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace:
--

ALTER TABLE ONLY project
    ADD CONSTRAINT pk_project PRIMARY KEY (project_id);


--
-- Name: pk_project_company_assignment; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY project_company_assignment
    ADD CONSTRAINT pk_project_company_assignment PRIMARY KEY (project_company_assignment_id);


--
-- Name: pk_project_info; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace:
--

ALTER TABLE ONLY project_info
    ADD CONSTRAINT pk_project_info PRIMARY KEY (project_info_id);


--
-- Name: pk_resource_id; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY resource
    ADD CONSTRAINT pk_resource_id PRIMARY KEY (resource_id);


--
-- Name: pk_session_log; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace:
--

ALTER TABLE ONLY session_log
    ADD CONSTRAINT pk_session_log PRIMARY KEY (session_log_id);


--
-- Name: pk_staff; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY staff
    ADD CONSTRAINT pk_staff PRIMARY KEY (staff_id);


--
-- Name: pk_table_version; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY table_version
    ADD CONSTRAINT pk_table_version PRIMARY KEY (table_name);


--
-- Name: pk_telephone; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY telephone
    ADD CONSTRAINT pk_telephone PRIMARY KEY (telephone_id);


--
-- Name: pk_url_x; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY article_unit
    ADD CONSTRAINT pk_url_x PRIMARY KEY (article_unit_id);


--
-- Name: pkx_company_category; Type: CONSTRAINT; Schema: public; Owner: OGo; Tablespace: 
--

ALTER TABLE ONLY appointment_resource
    ADD CONSTRAINT pkx_company_category PRIMARY KEY (appointment_resource_id);


--
-- Name: access_right_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX access_right_idx ON project_company_assignment USING btree (access_right);


--
-- Name: account_id_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX account_id_idx ON session_log USING btree (account_id);


--
-- Name: address_company_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX address_company_idx ON address USING btree (company_id);


--
-- Name: address_type_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX address_type_idx ON address USING btree (type);


--
-- Name: address_zip_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX address_zip_idx ON address USING btree (zip);


--
-- Name: assigned_task_links; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX assigned_task_links ON obj_link USING btree (target) WHERE (((link_type)::text = 'Preferred Job Executant'::text) AND ((source_type)::text = 'Job'::text));


--
-- Name: assignment_kind_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX assignment_kind_idx ON job_assignment USING btree (assignment_kind);


--
-- Name: cassignment_company_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX cassignment_company_idx ON company_assignment USING btree (company_id);


--
-- Name: cassignment_subcompany_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX cassignment_subcompany_idx ON company_assignment USING btree (sub_company_id);


--
-- Name: cinfo_company_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX cinfo_company_idx ON company_info USING btree (company_id);


--
-- Name: company_contact_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_contact_idx ON company USING btree (contact_id);


--
-- Name: company_is_enterprise_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_is_enterprise_idx ON company USING btree (is_enterprise);


--
-- Name: company_is_person_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_is_person_idx ON company USING btree (is_person);


--
-- Name: company_is_team_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_is_team_idx ON company USING btree (is_team);


--
-- Name: company_is_trust_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_is_trust_idx ON company USING btree (is_trust);


--
-- Name: company_owner_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_owner_idx ON company USING btree (owner_id);


--
-- Name: company_value_i1; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_value_i1 ON company_value USING btree (company_id);


--
-- Name: company_value_i2; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_value_i2 ON company_value USING btree (company_id, attribute);


--
-- Name: company_value_i3; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_value_i3 ON company_value USING btree (attribute);


--
-- Name: company_value_i4; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_value_i4 ON company_value USING btree (value_string) WHERE ((attribute)::text = 'email1'::text);


--
-- Name: company_value_i5; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_value_i5 ON company_value USING btree (value_string) WHERE ((attribute)::text = 'email2'::text);


--
-- Name: company_value_i6; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_value_i6 ON company_value USING btree (value_string) WHERE ((attribute)::text = 'email3'::text);


--
-- Name: company_value_i7; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX company_value_i7 ON company_value USING btree (value_string) WHERE ((attribute)::text = 'job_title'::text);


--
-- Name: date_assign_apt_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX date_assign_apt_idx ON date_company_assignment USING btree (date_id);


--
-- Name: date_assign_company_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX date_assign_company_idx ON date_company_assignment USING btree (company_id);


--
-- Name: date_info_apt_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX date_info_apt_idx ON date_info USING btree (date_id);


--
-- Name: date_x_aux000_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX date_x_aux000_idx ON date_x USING btree (end_date, start_date);


--
-- Name: date_x_i1; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX date_x_i1 ON date_x USING btree (owner_id);


--
-- Name: date_x_i2; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX date_x_i2 ON date_x USING btree (parent_date_id);


--
-- Name: date_x_i3; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX date_x_i3 ON date_x USING btree (access_team_id);


--
-- Name: date_x_i4; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX date_x_i4 ON date_x USING btree (end_date);


--
-- Name: date_x_i5; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX date_x_i5 ON date_x USING btree (start_date);


--
-- Name: dediting_current_owner_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX dediting_current_owner_idx ON document_editing USING btree (current_owner_id);


--
-- Name: dediting_doc_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX dediting_doc_idx ON document_editing USING btree (document_id);


--
-- Name: doc_current_owner_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX doc_current_owner_idx ON doc USING btree (current_owner_id);


--
-- Name: doc_first_owner_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX doc_first_owner_idx ON doc USING btree (first_owner_id);


--
-- Name: doc_is_note_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX doc_is_note_idx ON document USING btree (is_note);


--
-- Name: doc_parent_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX doc_parent_idx ON doc USING btree (parent_document_id);


--
-- Name: doc_project_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX doc_project_idx ON doc USING btree (project_id);


--
-- Name: doc_title_id_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX doc_title_id_idx ON doc USING btree (title varchar_pattern_ops);


--
-- Name: doc_v_obj_version_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX doc_v_obj_version_idx ON document_version USING btree (object_version);


--
-- Name: document_editing_status_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX document_editing_status_idx ON document_editing USING btree (status);


--
-- Name: document_status_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX document_status_idx ON doc USING btree (status);


--
-- Name: dversion_doc_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX dversion_doc_idx ON document_version USING btree (document_id);


--
-- Name: dversion_last_owner_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX dversion_last_owner_idx ON document_version USING btree (last_owner_id);


--
-- Name: enterprise_aux000; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX enterprise_aux000 ON enterprise USING btree (company_id);


--
-- Name: enterprise_description_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX enterprise_description_idx ON enterprise USING btree (description varchar_pattern_ops);


--
-- Name: enterprise_email_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX enterprise_email_idx ON enterprise USING btree (email);


--
-- Name: enterprise_keywords_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX enterprise_keywords_idx ON enterprise USING btree (keywords varchar_pattern_ops);


--
-- Name: enterprise_test; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX enterprise_test ON enterprise USING btree (is_person) WHERE (((is_account = 0) OR (is_account IS NULL)) AND ((is_private = 0) OR (is_private IS NULL)));


--
-- Name: has_access_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX has_access_idx ON project_company_assignment USING btree (has_access);


--
-- Name: is_control_job_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX is_control_job_idx ON job USING btree (is_control_job);


--
-- Name: is_fake_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX is_fake_idx ON project USING btree (is_fake);


--
-- Name: is_folder_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX is_folder_idx ON doc USING btree (is_folder);


--
-- Name: is_index_article_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX is_index_article_idx ON news_article USING btree (is_index_article);


--
-- Name: is_index_doc_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX is_index_doc_idx ON doc USING btree (is_index_doc);


--
-- Name: is_new_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX is_new_idx ON job USING btree (is_new);


--
-- Name: is_object_link_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX is_object_link_idx ON doc USING btree (is_object_link);


--
-- Name: is_team_job_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX is_team_job_idx ON job USING btree (is_team_job);


--
-- Name: job__keywords; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX job__keywords ON job USING btree (keywords varchar_pattern_ops);


--
-- Name: job_aux000_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX job_aux000_idx ON job USING btree (project_id) WHERE (((is_control_job IS NULL) OR (is_control_job = 0)) AND (kind IS NULL));


--
-- Name: job_aux001_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX job_aux001_idx ON job USING btree (job_status) WHERE (((is_control_job IS NULL) OR (is_control_job = 0)) AND (kind IS NULL));


--
-- Name: job_creator_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX job_creator_idx ON job USING btree (creator_id);


--
-- Name: job_db_status_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX job_db_status_idx ON job USING btree (db_status);


--
-- Name: job_executant_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX job_executant_idx ON job USING btree (executant_id);


--
-- Name: job_kind_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX job_kind_idx ON job USING btree (kind);


--
-- Name: job_project_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX job_project_idx ON job USING btree (project_id);


--
-- Name: job_status_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX job_status_idx ON job USING btree (job_status);


--
-- Name: jobh_actor_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX jobh_actor_idx ON job_history USING btree (actor_id);


--
-- Name: jobh_job_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX jobh_job_idx ON job_history USING btree (job_id);


--
-- Name: jobhi_jobh_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX jobhi_jobh_idx ON job_history_info USING btree (job_history_id);


--
-- Name: log_date_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace:
--

CREATE INDEX log_date_idx ON session_log USING btree (log_date);


--
-- Name: log_object_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX log_object_idx ON log USING btree (object_id);


--
-- Name: newsa_news_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX newsa_news_idx ON news_article_link USING btree (news_article_id);


--
-- Name: newsa_subnews_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX newsa_subnews_idx ON news_article_link USING btree (sub_news_article_id);


--
-- Name: note_date_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX note_date_idx ON note USING btree (date_id);


--
-- Name: note_project_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX note_project_idx ON note USING btree (project_id);


--
-- Name: obj_acl_action_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_acl_action_idx ON object_acl USING btree (action);


--
-- Name: obj_acl_auth_id_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_acl_auth_id_idx ON object_acl USING btree (auth_id);


--
-- Name: obj_acl_object_id_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_acl_object_id_idx ON object_acl USING btree (object_id);


--
-- Name: obj_acl_permissions_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_acl_permissions_idx ON object_acl USING btree (permissions);


--
-- Name: obj_acl_sort_key_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_acl_sort_key_idx ON object_acl USING btree (sort_key);


--
-- Name: obj_l_label_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_l_label_idx ON obj_link USING btree (label);


--
-- Name: obj_l_obj_id_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_l_obj_id_idx ON obj_link USING btree (obj_link_id);


--
-- Name: obj_l_source_id_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_l_source_id_idx ON obj_link USING btree (source_id);


--
-- Name: obj_l_source_type_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_l_source_type_idx ON obj_link USING btree (source_type);


--
-- Name: obj_l_target_id_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_l_target_id_idx ON obj_link USING btree (target);


--
-- Name: obj_l_target_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_l_target_idx ON obj_link USING btree (target_id);


--
-- Name: obj_l_target_type_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_l_target_type_idx ON obj_link USING btree (target_type);


--
-- Name: obj_l_type_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_l_type_idx ON obj_link USING btree (link_type);


--
-- Name: obj_link_1m; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_link_1m ON obj_link USING btree (target_id) WHERE (target_id < 1000000);


--
-- Name: obj_link_2m; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_link_2m ON obj_link USING btree (target_id) WHERE ((target_id > 1000000) AND (target_id < 2000000));


--
-- Name: obj_p_access_key_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_p_access_key_idx ON obj_property USING btree (access_key);


--
-- Name: obj_p_namespace_prefix_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_p_namespace_prefix_idx ON obj_property USING btree (namespace_prefix varchar_pattern_ops);


--
-- Name: obj_p_obj_id_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_p_obj_id_idx ON obj_property USING btree (obj_id);


--
-- Name: obj_p_obj_type_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_p_obj_type_idx ON obj_property USING btree (obj_type);


--
-- Name: obj_p_value_key_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_p_value_key_idx ON obj_property USING btree (value_key);


--
-- Name: obj_p_value_string_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX obj_p_value_string_idx ON obj_property USING btree (value_string varchar_pattern_ops);


--
-- Name: object_link_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX object_link_idx ON doc USING btree (object_link);


--
-- Name: person_aux000; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_aux000 ON person USING btree (company_id);


--
-- Name: person_aux000_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_aux000_idx ON person USING btree (company_id) WHERE (((db_status)::text <> 'archived'::text) AND ((is_template_user IS NULL) OR (is_template_user = 0)));


--
-- Name: person_aux001_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_aux001_idx ON person USING btree (company_id) WHERE ((db_status)::text <> 'archived'::text);


--
-- Name: person_company_db_status_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_company_db_status_idx ON person USING btree (db_status);


--
-- Name: person_firstname_idx001; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_firstname_idx001 ON person USING btree (firstname);


--
-- Name: person_firstname_idx002; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_firstname_idx002 ON person USING btree (firstname varchar_pattern_ops);


--
-- Name: person_is_account_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_is_account_idx ON person USING btree (is_account);


--
-- Name: person_is_extra_account_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_is_extra_account_idx ON person USING btree (is_extra_account);


--
-- Name: person_is_intra_account_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_is_intra_account_idx ON person USING btree (is_intra_account);


--
-- Name: person_is_template_user_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_is_template_user_idx ON person USING btree (is_template_user);


--
-- Name: person_keywords_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_keywords_idx ON person USING btree (keywords varchar_pattern_ops);


--
-- Name: person_login_idx003; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_login_idx003 ON person USING btree (lower((login)::text) varchar_pattern_ops) WHERE (((db_status)::text <> 'archived'::text) AND ((is_template_user IS NULL) OR (is_template_user = 0)));


--
-- Name: person_name_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_name_idx ON person USING btree (name varchar_pattern_ops);


--
-- Name: person_private_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_private_idx ON person USING btree (is_private);


--
-- Name: person_test; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX person_test ON person USING btree (is_person) WHERE (((is_account = 0) OR (is_account IS NULL)) AND ((is_private = 0) OR (is_private IS NULL)));


--
-- Name: priority_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX priority_idx ON job USING btree (priority);


--
-- Name: project_assign_company_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX project_assign_company_idx ON project_company_assignment USING btree (company_id);


--
-- Name: project_assign_project_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX project_assign_project_idx ON project_company_assignment USING btree (project_id);


--
-- Name: project_db_status_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX project_db_status_idx ON project USING btree (db_status);


--
-- Name: project_kind_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX project_kind_idx ON project USING btree (kind);


--
-- Name: project_owner_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX project_owner_idx ON project USING btree (owner_id);


--
-- Name: project_status_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX project_status_idx ON project USING btree (status);


--
-- Name: project_team_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX project_team_idx ON project USING btree (team_id);


--
-- Name: session_log_action_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX session_log_action_idx ON session_log USING btree (action);


--
-- Name: staff__is_account; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX staff__is_account ON staff USING btree (is_account);


--
-- Name: staff__is_team; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX staff__is_team ON staff USING btree (is_team);


--
-- Name: team_description_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX team_description_idx ON team USING btree (description varchar_pattern_ops);


--
-- Name: team_is_location_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX team_is_location_idx ON team USING btree (is_location_team);


--
-- Name: tel_company_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX tel_company_idx ON telephone USING btree (company_id);


--
-- Name: telephone__fnumber; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX telephone__fnumber ON telephone USING btree (number);


--
-- Name: telephone__ftype; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX telephone__ftype ON telephone USING btree (type);


--
-- Name: telephone__real_number; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE INDEX telephone__real_number ON telephone USING btree (real_number);


--
-- Name: unique_aptresname_idx; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE UNIQUE INDEX unique_aptresname_idx ON appointment_resource USING btree (name);


--
-- Name: unique_company_id; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE UNIQUE INDEX unique_company_id ON staff USING btree (company_id);


--
-- Name: unique_company_login; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE UNIQUE INDEX unique_company_login ON company USING btree (login);


--
-- Name: unique_company_number; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE UNIQUE INDEX unique_company_number ON company USING btree (number);


--
-- Name: unique_enterprise_login; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE UNIQUE INDEX unique_enterprise_login ON enterprise USING btree (login);


--
-- Name: unique_enterprise_number; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE UNIQUE INDEX unique_enterprise_number ON enterprise USING btree (number);


--
-- Name: unique_person_login; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE UNIQUE INDEX unique_person_login ON person USING btree (login);


--
-- Name: unique_person_number; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE UNIQUE INDEX unique_person_number ON person USING btree (number);


--
-- Name: unique_project_number; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE UNIQUE INDEX unique_project_number ON project USING btree (number);


--
-- Name: unique_team_login; Type: INDEX; Schema: public; Owner: OGo; Tablespace: 
--

CREATE UNIQUE INDEX unique_team_login ON team USING btree (login);


--
-- Name: unique_team_number; Type: INDEX; Schema: public; Owner: OGo; Tablespace:
--

CREATE UNIQUE INDEX unique_team_number ON team USING btree (number);


--
-- Name: watched_object_links; Type: INDEX; Schema: public; Owner: OGo; Tablespace:
--

CREATE INDEX watched_object_links ON obj_link USING btree (source_id) WHERE ((link_type)::text = 'Watch'::text);


INSERT INTO person (company_id, login, name, description, is_account,
                    is_intra_account, is_extra_account, is_person, number,
                    is_private, is_readonly, db_status, object_version)
  VALUES (10000, 'ogo', 'ogo', 'Administrator', 1, 1, 0, 1, 'LS10000', 0, 1,
          'inserted', 1);

INSERT INTO person (company_id, owner_id, login, name, description,
                    is_account, is_intra_account, is_extra_account,
                    is_person, number, is_private, is_readonly, is_locked,
                    is_template_user, db_status, object_version)
  VALUES (9999, 10000, 'template', 'template', 'Template', 1, 1, 0, 1,
          'LS9999', 1, 1, 1, 1, 'inserted', 1);

INSERT INTO team (company_id, description, is_team, number, login, db_status,
                  object_version, owner_id, is_readonly, is_private)
  VALUES (10003, 'all intranet', 1, 'LS10003', 'all intranet', 'inserted', 1,
          10000, 1, 0);

INSERT INTO team (company_id, description, is_team, number, login, db_status,
                  object_version, owner_id, is_readonly, is_private)
  VALUES (9991, 'news editors', 1, 'LS9991', 'newseditors', 'inserted', 1,
          10000, 1, 0);

INSERT INTO team (company_id, description, is_team, number, login, db_status,
                  object_version, owner_id, is_readonly, is_private)
  VALUES (9981, 'team creators', 1, 'LS9981', 'teamcreators', 'inserted', 1,
          10000, 1, 0);


INSERT INTO ctags (entity) VALUES ('Person');
INSERT INTO ctags (entity) VALUES ('Enterprise');
INSERT INTO ctags (entity) VALUES ('Date');
INSERT INTO ctags (entity) VALUES ('Job');
INSERT INTO ctags (entity) VALUES ('Team');

UPDATE job SET owner_id = creator_id WHERE owner_id IS NULL;

CREATE TABLE message (
    uuid character varying(128) NOT NULL,
    scope character varying(128),
    process_id integer NOT NULL,
    db_status character(15),
    object_version integer DEFAULT 0,
    creation_timestamp timestamp with time zone,
    label character varying(128),
    mimetype character varying(50) DEFAULT 'application/octet-stream'::character varying,
    size integer DEFAULT 0
);

CREATE TABLE process (
    process_id integer NOT NULL,
    guid character varying(128),
    route_id integer NOT NULL,
    owner_id integer NOT NULL,
    object_version integer DEFAULT 0,
    input_message character varying(128) NOT NULL,
    db_status character(15),
    output_message character varying(128),
    started timestamp with time zone,
    completed timestamp with time zone,
    parked timestamp with time zone,
    state character(1) DEFAULT 'I'::bpchar,
    priority integer DEFAULT 0,
    task_id integer
);

CREATE TABLE route (
    route_id integer NOT NULL,
    name character varying(50) NOT NULL,
    comment text,
    object_version integer DEFAULT 0,
    owner_id integer NOT NULL,
    input_format character varying(128),
    db_status character varying(15)
);

CREATE TABLE collection (
    collection_id integer NOT NULL,
    version integer DEFAULT 0,
    owner_id integer NOT NULL,
    kind character varying(50),
    title character varying(255) NOT NULL,
    project_id integer,
    comment text,
    object_version integer,
    auth_token VARCHAR(12) DEFAULT 'unpublished',
    dav_enabled INTEGER DEFAULT 0
);

CREATE TABLE collection_assignment (
    collection_assignment_id integer NOT NULL,
    collection_id integer,
    assigned_id integer NOT NULL,
    sort_key integer,
    entity_name VARCHAR(42)
);


ALTER TABLE ONLY route
    ADD CONSTRAINT route_pkey PRIMARY KEY (route_id);
        
ALTER TABLE ONLY collection_assignment
    ADD CONSTRAINT collection_assignment_pkey PRIMARY KEY (collection_assignment_id);

ALTER TABLE ONLY collection
    ADD CONSTRAINT collection_pkey PRIMARY KEY (collection_id);    

ALTER TABLE date_x ADD COLUMN caldav_uid VARCHAR(100);
ALTER TABLE company ADD COLUMN carddav_uid VARCHAR(100);
ALTER TABLE job ADD COLUMN caldav_uid VARCHAR(100);
ALTER TABLE process ADD created TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE process ADD lastmodified TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE route ADD created TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE route  ADD lastmodified TIMESTAMP(6) WITH TIME ZONE;
ALTER TABLE message ADD lastmodified TIMESTAMP(6) WITH TIME ZONE;

CREATE SEQUENCE process_log_entry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

CREATE TABLE process_log
    (
        entry_id INTEGER DEFAULT nextval('process_log_entry_id_seq') NOT NULL,
        process_id INTEGER NOT NULL,
        source CHARACTER VARYING(64),
        time_stamp NUMERIC,
        stanza CHARACTER(32),
        MESSAGE TEXT,
        uuid CHARACTER VARYING(64),
        PRIMARY KEY(entry_id)
    );

CREATE INDEX process_log_i0 ON process_log(process_id);

ALTER TABLE process_log ADD category CHAR(15);

ALTER TABLE document ADD categories VARCHAR(255);
ALTER TABLE note  ADD caldav_uid VARCHAR(128);

ALTER TABLE ONLY message
    ADD CONSTRAINT message_pkey PRIMARY KEY (uuid);

ALTER TABLE ONLY process
    ADD CONSTRAINT process_pkey PRIMARY KEY (process_id);

ALTER TABLE message ALTER COLUMN size TYPE BIGINT;

--- Create a network-service context
INSERT INTO person
 ( company_id, object_version, owner_id, is_person, is_readonly,
   is_account, is_intra_account, number, description, is_locked,
   login, name, db_status)
 VALUES
 ( 8999, 1, 10000, 0, 1, 1, 1, 'OGo8999', 'Network Service Context',
   1, 'network', 'network-service', 'inserted' );

--- Add check
ALTER TABLE document_version ADD checksum CHAR(128);

CREATE TABLE LOCK (
   token CHARACTER(255) PRIMARY KEY,
   object_id INTEGER NOT NULL,
   owner_id INTEGER NOT NULL,
   expires BIGINT,
   granted BIGINT,
   exclusive CHARACTER(1) DEFAULT 'Y',
   kind CHARACTER(1) DEFAULT 'W',
   data BYTEA,
   operations VARCHAR(10) DEFAULT ''
);

ALTER TABLE obj_info ADD display_name VARCHAR(128);
ALTER TABLE obj_info ADD file_name VARCHAR(128);
ALTER TABLE obj_info ADD owner_id int;
ALTER TABLE obj_info ADD version int;
ALTER TABLE obj_info ADD file_size int;
ALTER TABLE obj_info ADD file_type VARCHAR(128);
ALTER TABLE obj_info ADD ics_size int;
ALTER TABLE obj_info ADD ics_type VARCHAR(128);
ALTER TABLE obj_info ADD created TIMESTAMP WITH TIME ZONE;
ALTER TABLE obj_info ADD modified TIMESTAMP WITH TIME ZONE;
ALTER TABLE obj_info ADD info_level SMALLINT DEFAULT 0;

CREATE TABLE attachment (
    attachment_id     VARCHAR(255) PRIMARY KEY,
    related_id        INTEGER,
    kind              VARCHAR(45),
    mimetype          VARCHAR(128),
    created           TIMESTAMP WITH TIME ZONE NOT NULL,
    expiration        INTEGER,
    context_id        INTEGER,
    size              BIGINT,
    webdav_uid        VARCHAR(128)
);

ALTER TABLE attachment ADD checksum VARCHAR(128);

CREATE TABLE vista_vector (
  object_id  INT PRIMARY KEY,
  version    INT DEFAULT 0, 
  edition    INT, 
  entity     VARCHAR(25) NOT NULL,
  event_date DATE DEFAULT 'TODAY',  
  archived   BOOL DEFAULT FALSE,
  keywords   VARCHAR(128)[], 
  vector     tsvector);
CREATE INDEX vista_idx_i0 ON vista_vector (entity);
CREATE INDEX vista_idx_i1 ON vista_vector (event_date);
CREATE INDEX vista_idx_i2 ON vista_vector USING gin(vector);
