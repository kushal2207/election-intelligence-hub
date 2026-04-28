// Neo4j Database Schema for India Election Knowledge Graph Assistant
// Contains UUID constraints, Indexes, and Sample MERGE scripts

// ==========================================
// 1. UNIQUE CONSTRAINTS (UUID enforcement)
// ==========================================
CREATE CONSTRAINT jurisdiction_id_unique IF NOT EXISTS FOR (n:Jurisdiction) REQUIRE n.jurisdiction_id IS UNIQUE;
CREATE CONSTRAINT constituency_id_unique IF NOT EXISTS FOR (n:Constituency) REQUIRE n.constituency_id IS UNIQUE;
CREATE CONSTRAINT act_id_unique IF NOT EXISTS FOR (n:Election_Act) REQUIRE n.act_id IS UNIQUE;
CREATE CONSTRAINT section_id_unique IF NOT EXISTS FOR (n:Act_Section) REQUIRE n.section_id IS UNIQUE;
CREATE CONSTRAINT voter_id_unique IF NOT EXISTS FOR (n:Voter) REQUIRE n.voter_id IS UNIQUE;
CREATE CONSTRAINT candidate_id_unique IF NOT EXISTS FOR (n:Candidate) REQUIRE n.candidate_id IS UNIQUE;
CREATE CONSTRAINT party_id_unique IF NOT EXISTS FOR (n:Political_Party) REQUIRE n.party_id IS UNIQUE;
CREATE CONSTRAINT authority_id_unique IF NOT EXISTS FOR (n:Source_Authority) REQUIRE n.authority_id IS UNIQUE;
CREATE CONSTRAINT event_id_unique IF NOT EXISTS FOR (n:Event) REQUIRE n.event_id IS UNIQUE;

// ==========================================
// 2. PERFORMANCE INDEXES
// ==========================================
CREATE INDEX jurisdiction_name_idx IF NOT EXISTS FOR (n:Jurisdiction) ON (n.name);
CREATE INDEX constituency_name_idx IF NOT EXISTS FOR (n:Constituency) ON (n.name);
CREATE INDEX act_title_idx IF NOT EXISTS FOR (n:Election_Act) ON (n.title);
CREATE INDEX candidate_name_idx IF NOT EXISTS FOR (n:Candidate) ON (n.full_name);
CREATE INDEX party_name_idx IF NOT EXISTS FOR (n:Political_Party) ON (n.name);
CREATE INDEX event_date_idx IF NOT EXISTS FOR (n:Event) ON (n.date_of_occurrence);

// ==========================================
// 3. SAMPLE MERGE STATEMENTS (UPSERTS)
// ==========================================

// --- Create a Source Authority ---
MERGE (auth:Source_Authority {authority_id: 'auth-eci-001'})
ON CREATE SET 
    auth.authority_name = 'Election Commission of India',
    auth.source_type = 'Constitutional Body',
    auth.valid_from = date('1950-01-25'),
    auth.valid_to = null,
    auth.conflict = false;

// --- Create a Jurisdiction ---
MERGE (j:Jurisdiction {jurisdiction_id: 'jur-ind-001'})
ON CREATE SET 
    j.name = 'India',
    j.level = 'National',
    j.parent_jurisdiction_id = null,
    j.valid_from = date('1947-08-15'),
    j.valid_to = null,
    j.conflict = false;

// Relationship: Jurisdiction HAS_SOURCE Authority
MATCH (j:Jurisdiction {jurisdiction_id: 'jur-ind-001'})
MATCH (auth:Source_Authority {authority_id: 'auth-eci-001'})
MERGE (j)-[r:HAS_SOURCE]->(auth)
ON CREATE SET 
    r.source_authority = 'auth-eci-001',
    r.source_detail = 'Article 324 of the Constitution of India establishes the ECI for national oversight',
    r.valid_from = date('1950-01-25'),
    r.conflict = false;

// --- Create a Constituency ---
MERGE (c:Constituency {constituency_id: 'const-up-001'})
ON CREATE SET 
    c.name = 'Varanasi',
    c.jurisdiction_id = 'jur-ind-001',
    c.electoral_type = 'Lok Sabha',
    c.valid_from = date('1952-01-01'),
    c.valid_to = null,
    c.conflict = false;

// Relationship: Constituency IS_GOVERNED_BY Jurisdiction
MATCH (c:Constituency {constituency_id: 'const-up-001'})
MATCH (j:Jurisdiction {jurisdiction_id: 'jur-ind-001'})
MERGE (c)-[r:IS_GOVERNED_BY]->(j)
ON CREATE SET 
    r.source_authority = 'auth-eci-001',
    r.source_detail = 'Delimitation Commission Order',
    r.valid_from = date('2008-02-19'),
    r.conflict = false;

// --- Create an Election Act ---
MERGE (act:Election_Act {act_id: 'act-rpa-1951'})
ON CREATE SET 
    act.title = 'Representation of the People Act, 1951',
    act.version_number = '1.0',
    act.effective_date = date('1951-07-17'),
    act.valid_from = date('1951-07-17'),
    act.valid_to = null,
    act.conflict = false;

// --- Create an Act Section ---
MERGE (sec:Act_Section {section_id: 'sec-rpa-33'})
ON CREATE SET 
    sec.section_number = '33',
    sec.text_content = 'Presentation of nomination paper and requirements for a valid nomination.',
    sec.source_text = 'Bare Act RPA 1951 Chapter 1',
    sec.vector_id = 'pinecone-vec-rpa-33',
    sec.valid_from = date('1951-07-17'),
    sec.valid_to = null,
    sec.conflict = false;

// Relationship: Election_Act CONTAINS_SECTION Act_Section
MATCH (act:Election_Act {act_id: 'act-rpa-1951'})
MATCH (sec:Act_Section {section_id: 'sec-rpa-33'})
MERGE (act)-[r:CONTAINS_SECTION]->(sec)
ON CREATE SET 
    r.source_authority = 'auth-eci-001',
    r.source_detail = 'Official Gazette Notification',
    r.valid_from = date('1951-07-17'),
    r.conflict = false;

// --- Create a Political Party ---
MERGE (p:Political_Party {party_id: 'party-bjp-001'})
ON CREATE SET 
    p.name = 'Bharatiya Janata Party',
    p.registration_date = date('1980-04-06'),
    p.valid_from = date('1980-04-06'),
    p.valid_to = null,
    p.conflict = false;

// --- Create a Candidate ---
MERGE (cand:Candidate {candidate_id: 'cand-nm-001'})
ON CREATE SET 
    cand.full_name = 'Narendra Modi',
    cand.party_affiliation = 'party-bjp-001',
    cand.bio = 'Incumbent Prime Minister of India, Member of Parliament from Varanasi.',
    cand.valid_from = date('2014-05-26'),
    // valid_to left null assuming current applicability
    cand.valid_to = null,
    cand.conflict = false;

// Relationship: Candidate CANDIDATE_AFFILIATION Political_Party
MATCH (cand:Candidate {candidate_id: 'cand-nm-001'})
MATCH (p:Political_Party {party_id: 'party-bjp-001'})
MERGE (cand)-[r:CANDIDATE_AFFILIATION]->(p)
ON CREATE SET 
    r.source_authority = 'auth-eci-001',
    r.source_detail = 'Form B submitted during nomination',
    r.valid_from = date('2014-04-24'),
    r.conflict = false;
