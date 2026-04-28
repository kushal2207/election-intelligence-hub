# India Election Knowledge Graph Assistant - Architecture & Schema

This document defines the schema for a hybrid Knowledge Graph (Neo4j) + Vector Search (Pinecone) database designed to assist with queries relating to Indian elections at all government levels.

## Neo4j Nodes
Each node leverages UUIDs as primary keys, along with `valid_from`, `valid_to`, and `conflict` flags for temporal and dispute resolution.

- **Jurisdiction**: `jurisdiction_id`, `level`, `name`, `parent_jurisdiction_id`
- **Constituency**: `constituency_id`, `name`, `jurisdiction_id`, `electoral_type`
- **Election_Act**: `act_id`, `title`, `version_number`, `effective_date`
- **Act_Section**: `section_id`, `section_number`, `text_content`, `source_text`, `vector_id` (maps to Pinecone UUID)
- **Voter**: `voter_id`, `date_of_birth`, `citizenship`, `jurisdiction_of_residence_id`
- **Candidate**: `candidate_id`, `full_name`, `party_affiliation`, `bio`
- **Political_Party**: `party_id`, `name`, `registration_date`
- **Source_Authority**: `authority_id`, `authority_name`, `source_type`
- **Event**: `event_id`, `event_type`, `date_of_occurrence`

## Neo4j Relationships
All relationships natively embed provenance data (`source_authority` UUID and `source_detail` context string).

- `(Constituency)-[:IS_GOVERNED_BY]->(Jurisdiction)`
- `(Constituency)-[:IS_LEGAL_COVERED_BY]->(Election_Act)`
- `(Election_Act)-[:CONTAINS_SECTION]->(Act_Section)`
- `(Act_Section)-[:AFFECTS]->(Constituency)`
- `(Voter)-[:REQUIRES_VALIDATION]->(Jurisdiction)`
- `(Candidate)-[:CANDIDATE_AFFILIATION]->(Political_Party)`
- `(Act_Section)-[:PRECEDES]->(Act_Section)`
- `(*)-[:HAS_SOURCE]->(Source_Authority)` *(Generic link connecting any node to its provenance)*

## Vector Schema (Pinecone)
Pinecone acts as the semantic engine. `sentence-transformers` ('all-MiniLM-L6-v2') handles embeddings.

- **Storage Target**: Act sections, local lore, and jurisdiction descriptions.
- **Record Format**: 
  ```json
  {
      "id": "uuid-v4", // Matches vector_id in Neo4j Act_Section node
      "values": [...384 dimension array...],
      "metadata": {
          "type": "Act_Section", // Or 'Local_Lore'
          "jurisdiction_id": "jur-ind-001",
          "act_id": "act-rpa-1951",
          "language": "en", // Multilingual tracking field
          "text": "Presentation of nomination paper..."
      }
  }
  ```

## Service Implementations
The Python service files are located in the `/services` directory:
- `neo4j_service.py`: Generalized CRUD utility with dynamic ID mappings, temporal versioning auto-injection (`valid_from`/`valid_to`), and relationship instantiation bound with source data constraints. Includes a dedicated `flag_conflict` method.
- `pinecone_service.py`: Automated indexing and document upsert workflows binding to `sentence-transformers`. Pre-builds semantic queries mapped to namespace filters (e.g., retrieving acts exclusively in `hi` (Hindi) for a specified jurisdiction).

## Operational Rules
1. **Versioning**: Nodes dynamically inject `valid_from` upon creation. Changes generate new nodes or relationships whilst terminating the old ones by setting `valid_to`.
2. **Conflict Resolution**: Any data dispute flips `conflict=True` via `neo4j_service.flag_conflict()`, enabling downstream UI handlers to visually warn users of contested data.
3. **Immutability**: Always reference the source authority ID with context for every connection established in the graph.
