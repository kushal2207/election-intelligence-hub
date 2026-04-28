import uuid
from datetime import datetime
from neo4j import GraphDatabase

class Neo4jService:
    """
    CRUD Service for India Election Knowledge Graph Assistant in Neo4j.
    Handles dynamic entity creation with versioning (valid_from, valid_to) 
    and conflict resolution.
    """
    
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def _execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def _get_id_field_for_label(self, label):
        """Map generic node labels to their specific ID fields."""
        mapping = {
            'Jurisdiction': 'jurisdiction_id',
            'Constituency': 'constituency_id',
            'Election_Act': 'act_id',
            'Act_Section': 'section_id',
            'Voter': 'voter_id',
            'Candidate': 'candidate_id',
            'Political_Party': 'party_id',
            'Source_Authority': 'authority_id',
            'Event': 'event_id'
        }
        return mapping.get(label, f"{label.lower()}_id")

    def create_node(self, label: str, properties: dict) -> dict:
        """
        Create a new node. Generates a UUID and initializes versioning and conflict flags.
        """
        node_id = str(uuid.uuid4())
        id_field = self._get_id_field_for_label(label)
        
        properties[id_field] = node_id
        properties['valid_from'] = properties.get('valid_from', datetime.now().isoformat())
        properties['valid_to'] = properties.get('valid_to', None)
        properties['conflict'] = properties.get('conflict', False)
        
        set_clause = ", ".join([f"n.{k} = ${k}" for k in properties.keys()])
        query = f"CREATE (n:{label}) SET {set_clause} RETURN n"
        
        result = self._execute_query(query, properties)
        return result[0] if result else None

    def read_node(self, label: str, node_id: str) -> dict:
        """Read a node by its UUID."""
        id_field = self._get_id_field_for_label(label)
        query = f"MATCH (n:{label} {{{id_field}: $node_id}}) RETURN n"
        result = self._execute_query(query, {"node_id": node_id})
        return result[0]['n'] if result else None

    def update_node(self, label: str, node_id: str, updates: dict) -> dict:
        """
        Update a node's properties. Use to set conflict=True or valid_to dates for deprecation.
        """
        id_field = self._get_id_field_for_label(label)
        set_clause = ", ".join([f"n.{k} = ${k}" for k in updates.keys()])
        query = f"MATCH (n:{label} {{{id_field}: $node_id}}) SET {set_clause} RETURN n"
        
        # Merge node_id into parameters
        updates_with_id = updates.copy()
        updates_with_id['node_id'] = node_id
        
        result = self._execute_query(query, updates_with_id)
        return result[0]['n'] if result else None

    def delete_node(self, label: str, node_id: str):
        """Hard delete a node and its relationships. (Usually prefer soft delete via valid_to)."""
        id_field = self._get_id_field_for_label(label)
        query = f"MATCH (n:{label} {{{id_field}: $node_id}}) DETACH DELETE n"
        self._execute_query(query, {"node_id": node_id})
        return True

    def create_relationship(self, from_label: str, from_id: str, to_label: str, to_id: str, 
                            rel_type: str, source_auth_id: str, source_detail: str) -> dict:
        """
        Create a directed relationship with strict source tracking and versioning.
        Every edge MUST carry source_authority and source_detail.
        """
        from_id_field = self._get_id_field_for_label(from_label)
        to_id_field = self._get_id_field_for_label(to_label)
        
        query = f"""
        MATCH (a:{from_label} {{{from_id_field}: $from_id}})
        MATCH (b:{to_label} {{{to_id_field}: $to_id}})
        CREATE (a)-[r:{rel_type} {{
            source_authority: $source_auth_id,
            source_detail: $source_detail,
            valid_from: $valid_from,
            conflict: false
        }}]->(b)
        RETURN r
        """
        params = {
            "from_id": from_id,
            "to_id": to_id,
            "source_auth_id": source_auth_id,
            "source_detail": source_detail,
            "valid_from": datetime.now().isoformat()
        }
        
        result = self._execute_query(query, params)
        return result[0]['r'] if result else None

    def flag_conflict(self, label: str, node_id: str, conflict_details: str):
        """Flags a node where two sources disagree."""
        return self.update_node(label, node_id, {
            "conflict": True,
            "conflict_details": conflict_details
        })
