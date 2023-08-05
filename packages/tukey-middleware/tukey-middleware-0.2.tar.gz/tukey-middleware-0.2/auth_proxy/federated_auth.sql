--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: cloud_cloud_id_sequence; Type: SEQUENCE; Schema: public; Owner: cloudgui
--

CREATE SEQUENCE cloud_cloud_id_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cloud_cloud_id_sequence OWNER TO cloudgui;

--
-- Name: cloud_cloud_id_sequence; Type: SEQUENCE SET; Schema: public; Owner: cloudgui
--

SELECT pg_catalog.setval('cloud_cloud_id_sequence', 4, true);


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: cloud; Type: TABLE; Schema: public; Owner: cloudgui; Tablespace: 
--

CREATE TABLE cloud (
    cloud_id integer DEFAULT nextval('cloud_cloud_id_sequence'::regclass) NOT NULL,
    cloud_name character varying
);


ALTER TABLE public.cloud OWNER TO cloudgui;

--
-- Name: keypair; Type: TABLE; Schema: public; Owner: cloudgui; Tablespace: 
--

CREATE TABLE keypair (
    id integer NOT NULL,
    userid integer,
    pubkey text,
    cloud_id integer,
    fingerprint character varying(48),
    name character varying(16)
);


ALTER TABLE public.keypair OWNER TO cloudgui;

--
-- Name: keypair_id_seq; Type: SEQUENCE; Schema: public; Owner: cloudgui
--

CREATE SEQUENCE keypair_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.keypair_id_seq OWNER TO cloudgui;

--
-- Name: keypair_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloudgui
--

ALTER SEQUENCE keypair_id_seq OWNED BY keypair.id;


--
-- Name: keypair_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cloudgui
--

SELECT pg_catalog.setval('keypair_id_seq', 50, true);


--
-- Name: login_userid_sequence; Type: SEQUENCE; Schema: public; Owner: cloudgui
--

CREATE SEQUENCE login_userid_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.login_userid_sequence OWNER TO cloudgui;

--
-- Name: login_userid_sequence; Type: SEQUENCE SET; Schema: public; Owner: cloudgui
--

SELECT pg_catalog.setval('login_userid_sequence', 23, true);


--
-- Name: login; Type: TABLE; Schema: public; Owner: cloudgui; Tablespace: 
--

CREATE TABLE login (
    id integer DEFAULT nextval('login_userid_sequence'::regclass) NOT NULL,
    userid integer NOT NULL,
    cloud_id integer NOT NULL,
    username character varying,
    password character varying
);


ALTER TABLE public.login OWNER TO cloudgui;

--
-- Name: login_enabled; Type: TABLE; Schema: public; Owner: cloudgui; Tablespace: 
--

CREATE TABLE login_enabled (
    login_id integer NOT NULL
);


ALTER TABLE public.login_enabled OWNER TO cloudgui;

--
-- Name: login_identifier_id_sequence; Type: SEQUENCE; Schema: public; Owner: cloudgui
--

CREATE SEQUENCE login_identifier_id_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.login_identifier_id_sequence OWNER TO cloudgui;

--
-- Name: login_identifier_id_sequence; Type: SEQUENCE SET; Schema: public; Owner: cloudgui
--

SELECT pg_catalog.setval('login_identifier_id_sequence', 26, true);


--
-- Name: login_identifier; Type: TABLE; Schema: public; Owner: cloudgui; Tablespace: 
--

CREATE TABLE login_identifier (
    id integer DEFAULT nextval('login_identifier_id_sequence'::regclass) NOT NULL,
    userid integer NOT NULL,
    method_id integer NOT NULL,
    identifier character varying NOT NULL
);


ALTER TABLE public.login_identifier OWNER TO cloudgui;

--
-- Name: login_identifier_enabled; Type: TABLE; Schema: public; Owner: cloudgui; Tablespace: 
--

CREATE TABLE login_identifier_enabled (
    login_identifier_id integer NOT NULL
);


ALTER TABLE public.login_identifier_enabled OWNER TO cloudgui;

--
-- Name: login_method_method_id_sequence; Type: SEQUENCE; Schema: public; Owner: cloudgui
--

CREATE SEQUENCE login_method_method_id_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.login_method_method_id_sequence OWNER TO cloudgui;

--
-- Name: login_method_method_id_sequence; Type: SEQUENCE SET; Schema: public; Owner: cloudgui
--

SELECT pg_catalog.setval('login_method_method_id_sequence', 3, true);


--
-- Name: login_method; Type: TABLE; Schema: public; Owner: cloudgui; Tablespace: 
--

CREATE TABLE login_method (
    method_id integer DEFAULT nextval('login_method_method_id_sequence'::regclass) NOT NULL,
    method_name character varying
);


ALTER TABLE public.login_method OWNER TO cloudgui;

--
-- Name: userid_userid_sequence; Type: SEQUENCE; Schema: public; Owner: cloudgui
--

CREATE SEQUENCE userid_userid_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.userid_userid_sequence OWNER TO cloudgui;

--
-- Name: userid_userid_sequence; Type: SEQUENCE SET; Schema: public; Owner: cloudgui
--

SELECT pg_catalog.setval('userid_userid_sequence', 18, true);


--
-- Name: userid; Type: TABLE; Schema: public; Owner: cloudgui; Tablespace: 
--

CREATE TABLE userid (
    userid integer DEFAULT nextval('userid_userid_sequence'::regclass) NOT NULL
);


ALTER TABLE public.userid OWNER TO cloudgui;

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: cloudgui
--

ALTER TABLE ONLY keypair ALTER COLUMN id SET DEFAULT nextval('keypair_id_seq'::regclass);


--
-- Data for Name: cloud; Type: TABLE DATA; Schema: public; Owner: cloudgui
--

COPY cloud (cloud_id, cloud_name) FROM stdin;
2	adler
3	sullivan
\.


--
-- Data for Name: login_method; Type: TABLE DATA; Schema: public; Owner: cloudgui
--

COPY login_method (method_id, method_name) FROM stdin;
2	openid
3	shibboleth
\.


--
-- Data for Name: userid; Type: TABLE DATA; Schema: public; Owner: cloudgui
--

COPY userid (userid) FROM stdin;
2
3
\.


--
-- Name: cloud_id; Type: CONSTRAINT; Schema: public; Owner: cloudgui; Tablespace: 
--

ALTER TABLE ONLY cloud
    ADD CONSTRAINT cloud_id PRIMARY KEY (cloud_id);


--
-- Name: cloud_user_name; Type: CONSTRAINT; Schema: public; Owner: cloudgui; Tablespace: 
--

ALTER TABLE ONLY keypair
    ADD CONSTRAINT cloud_user_name UNIQUE (cloud_id, userid, name);


--
-- Name: keypair_id; Type: CONSTRAINT; Schema: public; Owner: cloudgui; Tablespace: 
--

ALTER TABLE ONLY keypair
    ADD CONSTRAINT keypair_id PRIMARY KEY (id);


--
-- Name: login_enabled_userid; Type: CONSTRAINT; Schema: public; Owner: cloudgui; Tablespace: 
--

ALTER TABLE ONLY login_enabled
    ADD CONSTRAINT login_enabled_userid PRIMARY KEY (login_id);


--
-- Name: login_id; Type: CONSTRAINT; Schema: public; Owner: cloudgui; Tablespace: 
--

ALTER TABLE ONLY login
    ADD CONSTRAINT login_id PRIMARY KEY (id);


--
-- Name: login_identifier_enabled_login_identifier_id; Type: CONSTRAINT; Schema: public; Owner: cloudgui; Tablespace: 
--

ALTER TABLE ONLY login_identifier_enabled
    ADD CONSTRAINT login_identifier_enabled_login_identifier_id PRIMARY KEY (login_identifier_id);


--
-- Name: login_identifier_id; Type: CONSTRAINT; Schema: public; Owner: cloudgui; Tablespace: 
--

ALTER TABLE ONLY login_identifier
    ADD CONSTRAINT login_identifier_id PRIMARY KEY (id);


--
-- Name: login_method_id; Type: CONSTRAINT; Schema: public; Owner: cloudgui; Tablespace: 
--

ALTER TABLE ONLY login_method
    ADD CONSTRAINT login_method_id PRIMARY KEY (method_id);


--
-- Name: userid_userid; Type: CONSTRAINT; Schema: public; Owner: cloudgui; Tablespace: 
--

ALTER TABLE ONLY userid
    ADD CONSTRAINT userid_userid PRIMARY KEY (userid);


--
-- Name: username; Type: CONSTRAINT; Schema: public; Owner: cloudgui; Tablespace: 
--

ALTER TABLE ONLY login
    ADD CONSTRAINT username UNIQUE (cloud_id, username);


--
-- Name: fki_userid; Type: INDEX; Schema: public; Owner: cloudgui; Tablespace: 
--

CREATE INDEX fki_userid ON login_enabled USING btree (login_id);


--
-- Name: cloud_id_cloud; Type: FK CONSTRAINT; Schema: public; Owner: cloudgui
--

ALTER TABLE ONLY keypair
    ADD CONSTRAINT cloud_id_cloud FOREIGN KEY (cloud_id) REFERENCES cloud(cloud_id);


--
-- Name: login_enabled_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cloudgui
--

ALTER TABLE ONLY login_enabled
    ADD CONSTRAINT login_enabled_userid_fkey FOREIGN KEY (login_id) REFERENCES login(id);


--
-- Name: login_identifier_enabled_login_identifier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cloudgui
--

ALTER TABLE ONLY login_identifier_enabled
    ADD CONSTRAINT login_identifier_enabled_login_identifier_id_fkey FOREIGN KEY (login_identifier_id) REFERENCES login_identifier(id);


--
-- Name: login_identifier_method_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cloudgui
--

ALTER TABLE ONLY login_identifier
    ADD CONSTRAINT login_identifier_method_id_fkey FOREIGN KEY (method_id) REFERENCES login_method(method_id);


--
-- Name: login_identifier_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cloudgui
--

ALTER TABLE ONLY login_identifier
    ADD CONSTRAINT login_identifier_userid_fkey FOREIGN KEY (userid) REFERENCES userid(userid);


--
-- Name: login_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cloudgui
--

ALTER TABLE ONLY login
    ADD CONSTRAINT login_userid_fkey FOREIGN KEY (userid) REFERENCES userid(userid);


--
-- Name: userid_userid; Type: FK CONSTRAINT; Schema: public; Owner: cloudgui
--

ALTER TABLE ONLY keypair
    ADD CONSTRAINT userid_userid FOREIGN KEY (userid) REFERENCES userid(userid);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

