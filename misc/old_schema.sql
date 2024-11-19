--
-- PostgreSQL database dump
--

-- Dumped from database version 14.1 (Debian 14.1-1.pgdg110+1)
-- Dumped by pg_dump version 16.4 (Ubuntu 16.4-0ubuntu0.24.04.2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accession; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.accession (
    code character varying(20) NOT NULL,
    prov_type character varying(16),
    wild_prov_status character varying(16),
    date_accd date,
    date_recvd date,
    quantity_recvd integer,
    recvd_type character varying(4),
    id_qual_rank character varying(10),
    id_qual character varying(9) NOT NULL,
    private boolean,
    species_id integer NOT NULL,
    intended_location_id integer,
    intended2_location_id integer,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.accession OWNER TO ghini;

--
-- Name: accession_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.accession_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.accession_id_seq OWNER TO ghini;

--
-- Name: accession_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.accession_id_seq OWNED BY public.accession.id;


--
-- Name: accession_note; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.accession_note (
    date date,
    "user" character varying(64),
    category character varying(32),
    type character varying(32),
    note text NOT NULL,
    accession_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.accession_note OWNER TO ghini;

--
-- Name: accession_note_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.accession_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.accession_note_id_seq OWNER TO ghini;

--
-- Name: accession_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.accession_note_id_seq OWNED BY public.accession_note.id;


--
-- Name: bauble; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.bauble (
    name character varying(64),
    value text,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.bauble OWNER TO ghini;

--
-- Name: bauble_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.bauble_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bauble_id_seq OWNER TO ghini;

--
-- Name: bauble_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.bauble_id_seq OWNED BY public.bauble.id;


--
-- Name: collection; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.collection (
    collector character varying(64),
    collectors_code character varying(50),
    date date,
    locale text NOT NULL,
    latitude character varying(15),
    longitude character varying(15),
    gps_datum character varying(32),
    geo_accy double precision,
    elevation double precision,
    elevation_accy double precision,
    habitat text,
    notes text,
    geographic_area_id integer,
    source_id integer,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.collection OWNER TO ghini;

--
-- Name: collection_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.collection_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.collection_id_seq OWNER TO ghini;

--
-- Name: collection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.collection_id_seq OWNED BY public.collection.id;


--
-- Name: color; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.color (
    name character varying(32),
    code character varying(8),
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.color OWNER TO ghini;

--
-- Name: color_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.color_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.color_id_seq OWNER TO ghini;

--
-- Name: color_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.color_id_seq OWNED BY public.color.id;


--
-- Name: contact; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.contact (
    name character varying(75),
    description text,
    source_type character varying(21),
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.contact OWNER TO ghini;

--
-- Name: contact_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.contact_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contact_id_seq OWNER TO ghini;

--
-- Name: contact_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.contact_id_seq OWNED BY public.contact.id;


--
-- Name: contact_note; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.contact_note (
    date date,
    "user" character varying(64),
    category character varying(32),
    type character varying(32),
    note text NOT NULL,
    contact_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.contact_note OWNER TO ghini;

--
-- Name: contact_note_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.contact_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contact_note_id_seq OWNER TO ghini;

--
-- Name: contact_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.contact_note_id_seq OWNED BY public.contact_note.id;


--
-- Name: default_vernacular_name; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.default_vernacular_name (
    species_id integer NOT NULL,
    vernacular_name_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.default_vernacular_name OWNER TO ghini;

--
-- Name: default_vernacular_name_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.default_vernacular_name_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.default_vernacular_name_id_seq OWNER TO ghini;

--
-- Name: default_vernacular_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.default_vernacular_name_id_seq OWNED BY public.default_vernacular_name.id;


--
-- Name: family; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.family (
    epithet character varying(45) NOT NULL,
    author character varying(255),
    qualifier character varying(7),
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.family OWNER TO ghini;

--
-- Name: family_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.family_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.family_id_seq OWNER TO ghini;

--
-- Name: family_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.family_id_seq OWNED BY public.family.id;


--
-- Name: family_note; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.family_note (
    date date,
    "user" character varying(64),
    category character varying(32),
    type character varying(32),
    note text NOT NULL,
    family_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.family_note OWNER TO ghini;

--
-- Name: family_note_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.family_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.family_note_id_seq OWNER TO ghini;

--
-- Name: family_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.family_note_id_seq OWNED BY public.family_note.id;


--
-- Name: family_synonym; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.family_synonym (
    family_id integer NOT NULL,
    synonym_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.family_synonym OWNER TO ghini;

--
-- Name: family_synonym_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.family_synonym_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.family_synonym_id_seq OWNER TO ghini;

--
-- Name: family_synonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.family_synonym_id_seq OWNED BY public.family_synonym.id;


--
-- Name: genus; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.genus (
    epithet character varying(64) NOT NULL,
    author character varying(255),
    qualifier character varying(7),
    family_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.genus OWNER TO ghini;

--
-- Name: genus_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.genus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.genus_id_seq OWNER TO ghini;

--
-- Name: genus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.genus_id_seq OWNED BY public.genus.id;


--
-- Name: genus_note; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.genus_note (
    date date,
    "user" character varying(64),
    category character varying(32),
    type character varying(32),
    note text NOT NULL,
    genus_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.genus_note OWNER TO ghini;

--
-- Name: genus_note_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.genus_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.genus_note_id_seq OWNER TO ghini;

--
-- Name: genus_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.genus_note_id_seq OWNED BY public.genus_note.id;


--
-- Name: genus_synonym; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.genus_synonym (
    genus_id integer NOT NULL,
    synonym_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.genus_synonym OWNER TO ghini;

--
-- Name: genus_synonym_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.genus_synonym_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.genus_synonym_id_seq OWNER TO ghini;

--
-- Name: genus_synonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.genus_synonym_id_seq OWNED BY public.genus_synonym.id;


--
-- Name: geographic_area; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.geographic_area (
    name character varying(255) NOT NULL,
    tdwg_code character varying(6),
    iso_code character varying(7),
    parent_id integer,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.geographic_area OWNER TO ghini;

--
-- Name: geographic_area_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.geographic_area_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.geographic_area_id_seq OWNER TO ghini;

--
-- Name: geographic_area_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.geographic_area_id_seq OWNED BY public.geographic_area.id;


--
-- Name: habit; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.habit (
    name character varying(64),
    code character varying(8),
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.habit OWNER TO ghini;

--
-- Name: habit_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.habit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.habit_id_seq OWNER TO ghini;

--
-- Name: habit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.habit_id_seq OWNED BY public.habit.id;


--
-- Name: history; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.history (
    id integer NOT NULL,
    table_name text NOT NULL,
    table_id integer NOT NULL,
    "values" text NOT NULL,
    operation text NOT NULL,
    "user" text,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.history OWNER TO ghini;

--
-- Name: history_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.history_id_seq OWNER TO ghini;

--
-- Name: history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.history_id_seq OWNED BY public.history.id;


--
-- Name: location; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.location (
    code character varying(12) NOT NULL,
    name character varying(64),
    description text,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.location OWNER TO ghini;

--
-- Name: location_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.location_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.location_id_seq OWNER TO ghini;

--
-- Name: location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.location_id_seq OWNED BY public.location.id;


--
-- Name: location_note; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.location_note (
    date date,
    "user" character varying(64),
    category character varying(32),
    type character varying(32),
    note text NOT NULL,
    location_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.location_note OWNER TO ghini;

--
-- Name: location_note_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.location_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.location_note_id_seq OWNER TO ghini;

--
-- Name: location_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.location_note_id_seq OWNED BY public.location_note.id;


--
-- Name: plant; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.plant (
    code character varying(6) NOT NULL,
    acc_type character varying(10),
    memorial boolean,
    quantity integer NOT NULL,
    accession_id integer NOT NULL,
    location_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.plant OWNER TO ghini;

--
-- Name: plant_change; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.plant_change (
    plant_id integer NOT NULL,
    parent_plant_id integer,
    from_location_id integer,
    to_location_id integer,
    person character varying(64),
    quantity integer NOT NULL,
    note_id integer,
    reason character varying(4),
    date timestamp without time zone,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.plant_change OWNER TO ghini;

--
-- Name: plant_change_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.plant_change_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plant_change_id_seq OWNER TO ghini;

--
-- Name: plant_change_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.plant_change_id_seq OWNED BY public.plant_change.id;


--
-- Name: plant_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.plant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plant_id_seq OWNER TO ghini;

--
-- Name: plant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.plant_id_seq OWNED BY public.plant.id;


--
-- Name: plant_note; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.plant_note (
    date date,
    "user" character varying(64),
    category character varying(32),
    type character varying(32),
    note text NOT NULL,
    plant_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.plant_note OWNER TO ghini;

--
-- Name: plant_note_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.plant_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plant_note_id_seq OWNER TO ghini;

--
-- Name: plant_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.plant_note_id_seq OWNED BY public.plant_note.id;


--
-- Name: plant_prop; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.plant_prop (
    plant_id integer NOT NULL,
    propagation_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.plant_prop OWNER TO ghini;

--
-- Name: plant_prop_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.plant_prop_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plant_prop_id_seq OWNER TO ghini;

--
-- Name: plant_prop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.plant_prop_id_seq OWNED BY public.plant_prop.id;


--
-- Name: plugin; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.plugin (
    name character varying(64),
    version character varying(12),
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.plugin OWNER TO ghini;

--
-- Name: plugin_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.plugin_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.plugin_id_seq OWNER TO ghini;

--
-- Name: plugin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.plugin_id_seq OWNED BY public.plugin.id;


--
-- Name: prop_cutting; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.prop_cutting (
    cutting_type character varying(10),
    tip character varying(7),
    leaves character varying(7),
    leaves_reduced_pct integer,
    length integer,
    length_unit character varying(2),
    wound character varying(6),
    flower_buds character varying(7),
    fungicide text,
    hormone text,
    media text,
    container text,
    location text,
    cover text,
    bottom_heat_temp integer,
    bottom_heat_unit character varying(1),
    rooted_pct integer,
    propagation_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.prop_cutting OWNER TO ghini;

--
-- Name: prop_cutting_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.prop_cutting_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prop_cutting_id_seq OWNER TO ghini;

--
-- Name: prop_cutting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.prop_cutting_id_seq OWNED BY public.prop_cutting.id;


--
-- Name: prop_cutting_rooted; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.prop_cutting_rooted (
    date date,
    quantity integer NOT NULL,
    cutting_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.prop_cutting_rooted OWNER TO ghini;

--
-- Name: prop_cutting_rooted_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.prop_cutting_rooted_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prop_cutting_rooted_id_seq OWNER TO ghini;

--
-- Name: prop_cutting_rooted_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.prop_cutting_rooted_id_seq OWNED BY public.prop_cutting_rooted.id;


--
-- Name: prop_seed; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.prop_seed (
    pretreatment text,
    nseeds integer NOT NULL,
    date_sown date NOT NULL,
    container text,
    media text,
    covered text,
    location text,
    moved_from text,
    moved_to text,
    moved_date date,
    germ_date date,
    nseedlings integer,
    germ_pct integer,
    date_planted date,
    propagation_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.prop_seed OWNER TO ghini;

--
-- Name: prop_seed_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.prop_seed_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prop_seed_id_seq OWNER TO ghini;

--
-- Name: prop_seed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.prop_seed_id_seq OWNED BY public.prop_seed.id;


--
-- Name: propagation; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.propagation (
    prop_type character varying(15) NOT NULL,
    date date,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.propagation OWNER TO ghini;

--
-- Name: propagation_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.propagation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.propagation_id_seq OWNER TO ghini;

--
-- Name: propagation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.propagation_id_seq OWNED BY public.propagation.id;


--
-- Name: propagation_note; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.propagation_note (
    date date,
    "user" character varying(64),
    category character varying(32),
    type character varying(32),
    note text NOT NULL,
    propagation_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.propagation_note OWNER TO ghini;

--
-- Name: propagation_note_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.propagation_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.propagation_note_id_seq OWNER TO ghini;

--
-- Name: propagation_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.propagation_note_id_seq OWNED BY public.propagation_note.id;


--
-- Name: source; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.source (
    sources_code character varying(32),
    accession_id integer,
    source_detail_id integer,
    propagation_id integer,
    plant_propagation_id integer,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.source OWNER TO ghini;

--
-- Name: source_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.source_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.source_id_seq OWNER TO ghini;

--
-- Name: source_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.source_id_seq OWNED BY public.source.id;


--
-- Name: species; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.species (
    epithet character varying(64),
    sp2 character varying(64),
    author character varying(128),
    hybrid boolean,
    sp_qual character varying(7),
    cv_group character varying(50),
    trade_name character varying(64),
    infrasp1 character varying(64),
    infrasp1_rank character varying(7),
    infrasp1_author character varying(64),
    infrasp2 character varying(64),
    infrasp2_rank character varying(7),
    infrasp2_author character varying(64),
    infrasp3 character varying(64),
    infrasp3_rank character varying(7),
    infrasp3_author character varying(64),
    infrasp4 character varying(64),
    infrasp4_rank character varying(7),
    infrasp4_author character varying(64),
    genus_id integer NOT NULL,
    label_distribution text,
    bc_distribution text,
    habit_id integer,
    flower_color_id integer,
    awards text,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.species OWNER TO ghini;

--
-- Name: species_distribution; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.species_distribution (
    geographic_area_id integer NOT NULL,
    species_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.species_distribution OWNER TO ghini;

--
-- Name: species_distribution_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.species_distribution_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.species_distribution_id_seq OWNER TO ghini;

--
-- Name: species_distribution_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.species_distribution_id_seq OWNED BY public.species_distribution.id;


--
-- Name: species_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.species_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.species_id_seq OWNER TO ghini;

--
-- Name: species_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.species_id_seq OWNED BY public.species.id;


--
-- Name: species_note; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.species_note (
    date date,
    "user" character varying(64),
    category character varying(32),
    type character varying(32),
    note text NOT NULL,
    species_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.species_note OWNER TO ghini;

--
-- Name: species_note_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.species_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.species_note_id_seq OWNER TO ghini;

--
-- Name: species_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.species_note_id_seq OWNED BY public.species_note.id;


--
-- Name: species_synonym; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.species_synonym (
    species_id integer NOT NULL,
    synonym_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.species_synonym OWNER TO ghini;

--
-- Name: species_synonym_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.species_synonym_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.species_synonym_id_seq OWNER TO ghini;

--
-- Name: species_synonym_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.species_synonym_id_seq OWNED BY public.species_synonym.id;


--
-- Name: tag; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.tag (
    tag character varying(64) NOT NULL,
    description text,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.tag OWNER TO ghini;

--
-- Name: tag_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tag_id_seq OWNER TO ghini;

--
-- Name: tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.tag_id_seq OWNED BY public.tag.id;


--
-- Name: tag_note; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.tag_note (
    date date,
    "user" character varying(64),
    category character varying(32),
    type character varying(32),
    note text NOT NULL,
    tag_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.tag_note OWNER TO ghini;

--
-- Name: tag_note_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.tag_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tag_note_id_seq OWNER TO ghini;

--
-- Name: tag_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.tag_note_id_seq OWNED BY public.tag_note.id;


--
-- Name: tagged_obj; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.tagged_obj (
    obj_id integer,
    obj_class character varying(128),
    tag_id integer,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.tagged_obj OWNER TO ghini;

--
-- Name: tagged_obj_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.tagged_obj_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tagged_obj_id_seq OWNER TO ghini;

--
-- Name: tagged_obj_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.tagged_obj_id_seq OWNED BY public.tagged_obj.id;


--
-- Name: verification; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.verification (
    verifier character varying(64) NOT NULL,
    date date NOT NULL,
    reference text,
    accession_id integer NOT NULL,
    level integer NOT NULL,
    species_id integer NOT NULL,
    prev_species_id integer NOT NULL,
    notes text,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.verification OWNER TO ghini;

--
-- Name: verification_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.verification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.verification_id_seq OWNER TO ghini;

--
-- Name: verification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.verification_id_seq OWNED BY public.verification.id;


--
-- Name: vernacular_name; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.vernacular_name (
    name character varying(128) NOT NULL,
    language character varying(128),
    species_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.vernacular_name OWNER TO ghini;

--
-- Name: vernacular_name_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.vernacular_name_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vernacular_name_id_seq OWNER TO ghini;

--
-- Name: vernacular_name_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.vernacular_name_id_seq OWNED BY public.vernacular_name.id;


--
-- Name: voucher; Type: TABLE; Schema: public; Owner: ghini
--

CREATE TABLE public.voucher (
    herbarium character varying(5) NOT NULL,
    code character varying(32) NOT NULL,
    parent_material boolean,
    accession_id integer NOT NULL,
    id integer NOT NULL,
    _created timestamp with time zone,
    _last_updated timestamp with time zone
);


ALTER TABLE public.voucher OWNER TO ghini;

--
-- Name: voucher_id_seq; Type: SEQUENCE; Schema: public; Owner: ghini
--

CREATE SEQUENCE public.voucher_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.voucher_id_seq OWNER TO ghini;

--
-- Name: voucher_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ghini
--

ALTER SEQUENCE public.voucher_id_seq OWNED BY public.voucher.id;


--
-- Name: accession id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.accession ALTER COLUMN id SET DEFAULT nextval('public.accession_id_seq'::regclass);


--
-- Name: accession_note id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.accession_note ALTER COLUMN id SET DEFAULT nextval('public.accession_note_id_seq'::regclass);


--
-- Name: bauble id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.bauble ALTER COLUMN id SET DEFAULT nextval('public.bauble_id_seq'::regclass);


--
-- Name: collection id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.collection ALTER COLUMN id SET DEFAULT nextval('public.collection_id_seq'::regclass);


--
-- Name: color id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.color ALTER COLUMN id SET DEFAULT nextval('public.color_id_seq'::regclass);


--
-- Name: contact id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.contact ALTER COLUMN id SET DEFAULT nextval('public.contact_id_seq'::regclass);


--
-- Name: contact_note id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.contact_note ALTER COLUMN id SET DEFAULT nextval('public.contact_note_id_seq'::regclass);


--
-- Name: default_vernacular_name id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.default_vernacular_name ALTER COLUMN id SET DEFAULT nextval('public.default_vernacular_name_id_seq'::regclass);


--
-- Name: family id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family ALTER COLUMN id SET DEFAULT nextval('public.family_id_seq'::regclass);


--
-- Name: family_note id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family_note ALTER COLUMN id SET DEFAULT nextval('public.family_note_id_seq'::regclass);


--
-- Name: family_synonym id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family_synonym ALTER COLUMN id SET DEFAULT nextval('public.family_synonym_id_seq'::regclass);


--
-- Name: genus id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus ALTER COLUMN id SET DEFAULT nextval('public.genus_id_seq'::regclass);


--
-- Name: genus_note id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus_note ALTER COLUMN id SET DEFAULT nextval('public.genus_note_id_seq'::regclass);


--
-- Name: genus_synonym id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus_synonym ALTER COLUMN id SET DEFAULT nextval('public.genus_synonym_id_seq'::regclass);


--
-- Name: geographic_area id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.geographic_area ALTER COLUMN id SET DEFAULT nextval('public.geographic_area_id_seq'::regclass);


--
-- Name: habit id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.habit ALTER COLUMN id SET DEFAULT nextval('public.habit_id_seq'::regclass);


--
-- Name: history id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.history ALTER COLUMN id SET DEFAULT nextval('public.history_id_seq'::regclass);


--
-- Name: location id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.location ALTER COLUMN id SET DEFAULT nextval('public.location_id_seq'::regclass);


--
-- Name: location_note id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.location_note ALTER COLUMN id SET DEFAULT nextval('public.location_note_id_seq'::regclass);


--
-- Name: plant id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant ALTER COLUMN id SET DEFAULT nextval('public.plant_id_seq'::regclass);


--
-- Name: plant_change id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_change ALTER COLUMN id SET DEFAULT nextval('public.plant_change_id_seq'::regclass);


--
-- Name: plant_note id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_note ALTER COLUMN id SET DEFAULT nextval('public.plant_note_id_seq'::regclass);


--
-- Name: plant_prop id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_prop ALTER COLUMN id SET DEFAULT nextval('public.plant_prop_id_seq'::regclass);


--
-- Name: plugin id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plugin ALTER COLUMN id SET DEFAULT nextval('public.plugin_id_seq'::regclass);


--
-- Name: prop_cutting id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.prop_cutting ALTER COLUMN id SET DEFAULT nextval('public.prop_cutting_id_seq'::regclass);


--
-- Name: prop_cutting_rooted id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.prop_cutting_rooted ALTER COLUMN id SET DEFAULT nextval('public.prop_cutting_rooted_id_seq'::regclass);


--
-- Name: prop_seed id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.prop_seed ALTER COLUMN id SET DEFAULT nextval('public.prop_seed_id_seq'::regclass);


--
-- Name: propagation id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.propagation ALTER COLUMN id SET DEFAULT nextval('public.propagation_id_seq'::regclass);


--
-- Name: propagation_note id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.propagation_note ALTER COLUMN id SET DEFAULT nextval('public.propagation_note_id_seq'::regclass);


--
-- Name: source id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.source ALTER COLUMN id SET DEFAULT nextval('public.source_id_seq'::regclass);


--
-- Name: species id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species ALTER COLUMN id SET DEFAULT nextval('public.species_id_seq'::regclass);


--
-- Name: species_distribution id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_distribution ALTER COLUMN id SET DEFAULT nextval('public.species_distribution_id_seq'::regclass);


--
-- Name: species_note id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_note ALTER COLUMN id SET DEFAULT nextval('public.species_note_id_seq'::regclass);


--
-- Name: species_synonym id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_synonym ALTER COLUMN id SET DEFAULT nextval('public.species_synonym_id_seq'::regclass);


--
-- Name: tag id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.tag ALTER COLUMN id SET DEFAULT nextval('public.tag_id_seq'::regclass);


--
-- Name: tag_note id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.tag_note ALTER COLUMN id SET DEFAULT nextval('public.tag_note_id_seq'::regclass);


--
-- Name: tagged_obj id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.tagged_obj ALTER COLUMN id SET DEFAULT nextval('public.tagged_obj_id_seq'::regclass);


--
-- Name: verification id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.verification ALTER COLUMN id SET DEFAULT nextval('public.verification_id_seq'::regclass);


--
-- Name: vernacular_name id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.vernacular_name ALTER COLUMN id SET DEFAULT nextval('public.vernacular_name_id_seq'::regclass);


--
-- Name: voucher id; Type: DEFAULT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.voucher ALTER COLUMN id SET DEFAULT nextval('public.voucher_id_seq'::regclass);


--
-- Name: accession accession_code_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.accession
    ADD CONSTRAINT accession_code_key UNIQUE (code);


--
-- Name: accession_note accession_note_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.accession_note
    ADD CONSTRAINT accession_note_pkey PRIMARY KEY (id);


--
-- Name: accession accession_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.accession
    ADD CONSTRAINT accession_pkey PRIMARY KEY (id);


--
-- Name: bauble bauble_name_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.bauble
    ADD CONSTRAINT bauble_name_key UNIQUE (name);


--
-- Name: bauble bauble_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.bauble
    ADD CONSTRAINT bauble_pkey PRIMARY KEY (id);


--
-- Name: collection collection_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.collection
    ADD CONSTRAINT collection_pkey PRIMARY KEY (id);


--
-- Name: collection collection_source_id_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.collection
    ADD CONSTRAINT collection_source_id_key UNIQUE (source_id);


--
-- Name: color color_code_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.color
    ADD CONSTRAINT color_code_key UNIQUE (code);


--
-- Name: color color_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.color
    ADD CONSTRAINT color_pkey PRIMARY KEY (id);


--
-- Name: contact contact_name_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.contact
    ADD CONSTRAINT contact_name_key UNIQUE (name);


--
-- Name: contact_note contact_note_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.contact_note
    ADD CONSTRAINT contact_note_pkey PRIMARY KEY (id);


--
-- Name: contact contact_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.contact
    ADD CONSTRAINT contact_pkey PRIMARY KEY (id);


--
-- Name: default_vernacular_name default_vernacular_name_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.default_vernacular_name
    ADD CONSTRAINT default_vernacular_name_pkey PRIMARY KEY (id);


--
-- Name: default_vernacular_name default_vn_index; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.default_vernacular_name
    ADD CONSTRAINT default_vn_index UNIQUE (species_id, vernacular_name_id);


--
-- Name: family family_epithet_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family
    ADD CONSTRAINT family_epithet_key UNIQUE (epithet);


--
-- Name: family_note family_note_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family_note
    ADD CONSTRAINT family_note_pkey PRIMARY KEY (id);


--
-- Name: family family_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family
    ADD CONSTRAINT family_pkey PRIMARY KEY (id);


--
-- Name: family_synonym family_synonym_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family_synonym
    ADD CONSTRAINT family_synonym_pkey PRIMARY KEY (id);


--
-- Name: family_synonym family_synonym_synonym_id_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family_synonym
    ADD CONSTRAINT family_synonym_synonym_id_key UNIQUE (synonym_id);


--
-- Name: genus genus_epithet_author_qualifier_family_id_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus
    ADD CONSTRAINT genus_epithet_author_qualifier_family_id_key UNIQUE (epithet, author, qualifier, family_id);


--
-- Name: genus_note genus_note_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus_note
    ADD CONSTRAINT genus_note_pkey PRIMARY KEY (id);


--
-- Name: genus genus_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus
    ADD CONSTRAINT genus_pkey PRIMARY KEY (id);


--
-- Name: genus_synonym genus_synonym_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus_synonym
    ADD CONSTRAINT genus_synonym_pkey PRIMARY KEY (id);


--
-- Name: genus_synonym genus_synonym_synonym_id_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus_synonym
    ADD CONSTRAINT genus_synonym_synonym_id_key UNIQUE (synonym_id);


--
-- Name: geographic_area geographic_area_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.geographic_area
    ADD CONSTRAINT geographic_area_pkey PRIMARY KEY (id);


--
-- Name: habit habit_code_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.habit
    ADD CONSTRAINT habit_code_key UNIQUE (code);


--
-- Name: habit habit_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.habit
    ADD CONSTRAINT habit_pkey PRIMARY KEY (id);


--
-- Name: history history_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.history
    ADD CONSTRAINT history_pkey PRIMARY KEY (id);


--
-- Name: location location_code_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_code_key UNIQUE (code);


--
-- Name: location_note location_note_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.location_note
    ADD CONSTRAINT location_note_pkey PRIMARY KEY (id);


--
-- Name: location location_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);


--
-- Name: plant_change plant_change_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_change
    ADD CONSTRAINT plant_change_pkey PRIMARY KEY (id);


--
-- Name: plant plant_code_accession_id_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant
    ADD CONSTRAINT plant_code_accession_id_key UNIQUE (code, accession_id);


--
-- Name: plant_note plant_note_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_note
    ADD CONSTRAINT plant_note_pkey PRIMARY KEY (id);


--
-- Name: plant plant_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant
    ADD CONSTRAINT plant_pkey PRIMARY KEY (id);


--
-- Name: plant_prop plant_prop_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_prop
    ADD CONSTRAINT plant_prop_pkey PRIMARY KEY (id);


--
-- Name: plugin plugin_name_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plugin
    ADD CONSTRAINT plugin_name_key UNIQUE (name);


--
-- Name: plugin plugin_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plugin
    ADD CONSTRAINT plugin_pkey PRIMARY KEY (id);


--
-- Name: prop_cutting prop_cutting_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.prop_cutting
    ADD CONSTRAINT prop_cutting_pkey PRIMARY KEY (id);


--
-- Name: prop_cutting_rooted prop_cutting_rooted_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.prop_cutting_rooted
    ADD CONSTRAINT prop_cutting_rooted_pkey PRIMARY KEY (id);


--
-- Name: prop_seed prop_seed_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.prop_seed
    ADD CONSTRAINT prop_seed_pkey PRIMARY KEY (id);


--
-- Name: propagation_note propagation_note_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.propagation_note
    ADD CONSTRAINT propagation_note_pkey PRIMARY KEY (id);


--
-- Name: propagation propagation_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.propagation
    ADD CONSTRAINT propagation_pkey PRIMARY KEY (id);


--
-- Name: source source_accession_id_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.source
    ADD CONSTRAINT source_accession_id_key UNIQUE (accession_id);


--
-- Name: source source_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.source
    ADD CONSTRAINT source_pkey PRIMARY KEY (id);


--
-- Name: species_distribution species_distribution_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_distribution
    ADD CONSTRAINT species_distribution_pkey PRIMARY KEY (id);


--
-- Name: species_note species_note_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_note
    ADD CONSTRAINT species_note_pkey PRIMARY KEY (id);


--
-- Name: species species_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species
    ADD CONSTRAINT species_pkey PRIMARY KEY (id);


--
-- Name: species_synonym species_synonym_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_synonym
    ADD CONSTRAINT species_synonym_pkey PRIMARY KEY (id);


--
-- Name: species_synonym species_synonym_synonym_id_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_synonym
    ADD CONSTRAINT species_synonym_synonym_id_key UNIQUE (synonym_id);


--
-- Name: tag_note tag_note_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.tag_note
    ADD CONSTRAINT tag_note_pkey PRIMARY KEY (id);


--
-- Name: tag tag_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_pkey PRIMARY KEY (id);


--
-- Name: tag tag_tag_key; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_tag_key UNIQUE (tag);


--
-- Name: tagged_obj tagged_obj_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.tagged_obj
    ADD CONSTRAINT tagged_obj_pkey PRIMARY KEY (id);


--
-- Name: verification verification_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.verification
    ADD CONSTRAINT verification_pkey PRIMARY KEY (id);


--
-- Name: vernacular_name vernacular_name_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.vernacular_name
    ADD CONSTRAINT vernacular_name_pkey PRIMARY KEY (id);


--
-- Name: vernacular_name vn_index; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.vernacular_name
    ADD CONSTRAINT vn_index UNIQUE (name, language, species_id);


--
-- Name: voucher voucher_pkey; Type: CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.voucher
    ADD CONSTRAINT voucher_pkey PRIMARY KEY (id);


--
-- Name: ix_family_epithet; Type: INDEX; Schema: public; Owner: ghini
--

CREATE INDEX ix_family_epithet ON public.family USING btree (epithet);


--
-- Name: ix_genus_epithet; Type: INDEX; Schema: public; Owner: ghini
--

CREATE INDEX ix_genus_epithet ON public.genus USING btree (epithet);


--
-- Name: ix_species_epithet; Type: INDEX; Schema: public; Owner: ghini
--

CREATE INDEX ix_species_epithet ON public.species USING btree (epithet);


--
-- Name: ix_species_sp2; Type: INDEX; Schema: public; Owner: ghini
--

CREATE INDEX ix_species_sp2 ON public.species USING btree (sp2);


--
-- Name: accession accession_intended2_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.accession
    ADD CONSTRAINT accession_intended2_location_id_fkey FOREIGN KEY (intended2_location_id) REFERENCES public.location(id);


--
-- Name: accession accession_intended_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.accession
    ADD CONSTRAINT accession_intended_location_id_fkey FOREIGN KEY (intended_location_id) REFERENCES public.location(id);


--
-- Name: accession_note accession_note_accession_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.accession_note
    ADD CONSTRAINT accession_note_accession_id_fkey FOREIGN KEY (accession_id) REFERENCES public.accession(id);


--
-- Name: accession accession_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.accession
    ADD CONSTRAINT accession_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(id);


--
-- Name: collection collection_geographic_area_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.collection
    ADD CONSTRAINT collection_geographic_area_id_fkey FOREIGN KEY (geographic_area_id) REFERENCES public.geographic_area(id);


--
-- Name: collection collection_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.collection
    ADD CONSTRAINT collection_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.source(id);


--
-- Name: contact_note contact_note_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.contact_note
    ADD CONSTRAINT contact_note_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contact(id);


--
-- Name: default_vernacular_name default_vernacular_name_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.default_vernacular_name
    ADD CONSTRAINT default_vernacular_name_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(id);


--
-- Name: default_vernacular_name default_vernacular_name_vernacular_name_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.default_vernacular_name
    ADD CONSTRAINT default_vernacular_name_vernacular_name_id_fkey FOREIGN KEY (vernacular_name_id) REFERENCES public.vernacular_name(id);


--
-- Name: family_note family_note_family_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family_note
    ADD CONSTRAINT family_note_family_id_fkey FOREIGN KEY (family_id) REFERENCES public.family(id);


--
-- Name: family_synonym family_synonym_family_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family_synonym
    ADD CONSTRAINT family_synonym_family_id_fkey FOREIGN KEY (family_id) REFERENCES public.family(id);


--
-- Name: family_synonym family_synonym_synonym_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.family_synonym
    ADD CONSTRAINT family_synonym_synonym_id_fkey FOREIGN KEY (synonym_id) REFERENCES public.family(id);


--
-- Name: genus genus_family_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus
    ADD CONSTRAINT genus_family_id_fkey FOREIGN KEY (family_id) REFERENCES public.family(id);


--
-- Name: genus_note genus_note_genus_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus_note
    ADD CONSTRAINT genus_note_genus_id_fkey FOREIGN KEY (genus_id) REFERENCES public.genus(id);


--
-- Name: genus_synonym genus_synonym_genus_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus_synonym
    ADD CONSTRAINT genus_synonym_genus_id_fkey FOREIGN KEY (genus_id) REFERENCES public.genus(id);


--
-- Name: genus_synonym genus_synonym_synonym_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.genus_synonym
    ADD CONSTRAINT genus_synonym_synonym_id_fkey FOREIGN KEY (synonym_id) REFERENCES public.genus(id);


--
-- Name: geographic_area geographic_area_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.geographic_area
    ADD CONSTRAINT geographic_area_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.geographic_area(id);


--
-- Name: location_note location_note_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.location_note
    ADD CONSTRAINT location_note_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.location(id);


--
-- Name: plant plant_accession_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant
    ADD CONSTRAINT plant_accession_id_fkey FOREIGN KEY (accession_id) REFERENCES public.accession(id);


--
-- Name: plant_change plant_change_from_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_change
    ADD CONSTRAINT plant_change_from_location_id_fkey FOREIGN KEY (from_location_id) REFERENCES public.location(id);


--
-- Name: plant_change plant_change_note_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_change
    ADD CONSTRAINT plant_change_note_id_fkey FOREIGN KEY (note_id) REFERENCES public.plant_note(id);


--
-- Name: plant_change plant_change_parent_plant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_change
    ADD CONSTRAINT plant_change_parent_plant_id_fkey FOREIGN KEY (parent_plant_id) REFERENCES public.plant(id);


--
-- Name: plant_change plant_change_plant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_change
    ADD CONSTRAINT plant_change_plant_id_fkey FOREIGN KEY (plant_id) REFERENCES public.plant(id);


--
-- Name: plant_change plant_change_to_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_change
    ADD CONSTRAINT plant_change_to_location_id_fkey FOREIGN KEY (to_location_id) REFERENCES public.location(id);


--
-- Name: plant plant_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant
    ADD CONSTRAINT plant_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.location(id);


--
-- Name: plant_note plant_note_plant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_note
    ADD CONSTRAINT plant_note_plant_id_fkey FOREIGN KEY (plant_id) REFERENCES public.plant(id);


--
-- Name: plant_prop plant_prop_plant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_prop
    ADD CONSTRAINT plant_prop_plant_id_fkey FOREIGN KEY (plant_id) REFERENCES public.plant(id);


--
-- Name: plant_prop plant_prop_propagation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.plant_prop
    ADD CONSTRAINT plant_prop_propagation_id_fkey FOREIGN KEY (propagation_id) REFERENCES public.propagation(id);


--
-- Name: prop_cutting prop_cutting_propagation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.prop_cutting
    ADD CONSTRAINT prop_cutting_propagation_id_fkey FOREIGN KEY (propagation_id) REFERENCES public.propagation(id);


--
-- Name: prop_cutting_rooted prop_cutting_rooted_cutting_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.prop_cutting_rooted
    ADD CONSTRAINT prop_cutting_rooted_cutting_id_fkey FOREIGN KEY (cutting_id) REFERENCES public.prop_cutting(id);


--
-- Name: prop_seed prop_seed_propagation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.prop_seed
    ADD CONSTRAINT prop_seed_propagation_id_fkey FOREIGN KEY (propagation_id) REFERENCES public.propagation(id);


--
-- Name: propagation_note propagation_note_propagation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.propagation_note
    ADD CONSTRAINT propagation_note_propagation_id_fkey FOREIGN KEY (propagation_id) REFERENCES public.propagation(id);


--
-- Name: source source_accession_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.source
    ADD CONSTRAINT source_accession_id_fkey FOREIGN KEY (accession_id) REFERENCES public.accession(id);


--
-- Name: source source_plant_propagation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.source
    ADD CONSTRAINT source_plant_propagation_id_fkey FOREIGN KEY (plant_propagation_id) REFERENCES public.propagation(id);


--
-- Name: source source_propagation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.source
    ADD CONSTRAINT source_propagation_id_fkey FOREIGN KEY (propagation_id) REFERENCES public.propagation(id);


--
-- Name: source source_source_detail_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.source
    ADD CONSTRAINT source_source_detail_id_fkey FOREIGN KEY (source_detail_id) REFERENCES public.contact(id);


--
-- Name: species_distribution species_distribution_geographic_area_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_distribution
    ADD CONSTRAINT species_distribution_geographic_area_id_fkey FOREIGN KEY (geographic_area_id) REFERENCES public.geographic_area(id);


--
-- Name: species_distribution species_distribution_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_distribution
    ADD CONSTRAINT species_distribution_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(id);


--
-- Name: species species_flower_color_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species
    ADD CONSTRAINT species_flower_color_id_fkey FOREIGN KEY (flower_color_id) REFERENCES public.color(id);


--
-- Name: species species_genus_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species
    ADD CONSTRAINT species_genus_id_fkey FOREIGN KEY (genus_id) REFERENCES public.genus(id);


--
-- Name: species species_habit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species
    ADD CONSTRAINT species_habit_id_fkey FOREIGN KEY (habit_id) REFERENCES public.habit(id);


--
-- Name: species_note species_note_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_note
    ADD CONSTRAINT species_note_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(id);


--
-- Name: species_synonym species_synonym_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_synonym
    ADD CONSTRAINT species_synonym_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(id);


--
-- Name: species_synonym species_synonym_synonym_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.species_synonym
    ADD CONSTRAINT species_synonym_synonym_id_fkey FOREIGN KEY (synonym_id) REFERENCES public.species(id);


--
-- Name: tag_note tag_note_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.tag_note
    ADD CONSTRAINT tag_note_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id);


--
-- Name: tagged_obj tagged_obj_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.tagged_obj
    ADD CONSTRAINT tagged_obj_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id);


--
-- Name: verification verification_accession_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.verification
    ADD CONSTRAINT verification_accession_id_fkey FOREIGN KEY (accession_id) REFERENCES public.accession(id);


--
-- Name: verification verification_prev_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.verification
    ADD CONSTRAINT verification_prev_species_id_fkey FOREIGN KEY (prev_species_id) REFERENCES public.species(id);


--
-- Name: verification verification_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.verification
    ADD CONSTRAINT verification_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(id);


--
-- Name: vernacular_name vernacular_name_species_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.vernacular_name
    ADD CONSTRAINT vernacular_name_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(id);


--
-- Name: voucher voucher_accession_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ghini
--

ALTER TABLE ONLY public.voucher
    ADD CONSTRAINT voucher_accession_id_fkey FOREIGN KEY (accession_id) REFERENCES public.accession(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO xwiki;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

