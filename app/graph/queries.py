# Create index for Elder isolation
CREATE_ELDER_INDEX = """
CREATE INDEX elder_id_idx IF NOT EXISTS FOR (n:Elder) ON (n.elder_id)
"""

CREATE_GENERIC_NODE_ELDER_INDEX = """
CREATE INDEX base_elder_id_idx IF NOT EXISTS FOR (n:BaseNode) ON (n.elder_id)
"""

# Constraints
CREATE_ELDER_CONSTRAINT = """
CREATE CONSTRAINT elder_id_unique IF NOT EXISTS FOR (n:Elder) REQUIRE n.id IS UNIQUE
"""

CREATE_NODE_CONSTRAINT = """
CREATE CONSTRAINT node_id_unique IF NOT EXISTS FOR (n:BaseNode) REQUIRE n.id IS UNIQUE
"""

# Create or Update a generic memory node
MERGE_MEMORY_NODE = """
MERGE (e:Elder {id: $elder_id})
MERGE (m:EmotionalMemory {id: $memory_id})
ON CREATE SET 
    m.elder_id = $elder_id,
    m.description = $description,
    m.emotion_tag = $emotion_tag,
    m.created_at = $created_at,
    m.confidence_score = $confidence_score,
    m.source_type = $source_type,
    m.last_reinforced_at = $last_reinforced_at
ON MATCH SET 
    m.last_reinforced_at = $last_reinforced_at,
    m.confidence_score = CASE WHEN m.confidence_score < 1.0 THEN m.confidence_score + 0.1 ELSE 1.0 END
MERGE (e)-[r:HAS_MEMORY]->(m)
RETURN m.id as node_id, m.confidence_score as confidence, m.description as description
"""

MERGE_MEDICINE_NODE = """
MERGE (e:Elder {id: $elder_id})
MERGE (m:Medicine {elder_id: $elder_id, name: $name})
ON CREATE SET m.id = $node_id, m.dosage = coalesce($dosage, ""), m.created_at = $created_at, m.confidence_score = $confidence_score, m.source_type = $source_type, m.last_reinforced_at = $last_reinforced_at
ON MATCH SET m.dosage = coalesce($dosage, m.dosage), m.last_reinforced_at = $last_reinforced_at
MERGE (e)-[r:TAKES_MEDICINE]->(m)
RETURN m.id as node_id
"""

MERGE_APPOINTMENT_NODE = """
MERGE (e:Elder {id: $elder_id})
MERGE (a:Appointment {id: $node_id})
ON CREATE SET a.elder_id = $elder_id, a.title = $title, a.datetime = coalesce($datetime, ""), a.created_at = $created_at, a.confidence_score = $confidence_score, a.source_type = $source_type, a.last_reinforced_at = $last_reinforced_at
ON MATCH SET a.datetime = coalesce($datetime, a.datetime), a.last_reinforced_at = $last_reinforced_at
MERGE (e)-[r:HAS_APPOINTMENT]->(a)
RETURN a.id as node_id
"""

MERGE_SYMPTOM_NODE = """
MERGE (e:Elder {id: $elder_id})
MERGE (s:Symptom {id: $node_id})
ON CREATE SET s.elder_id = $elder_id, s.name = $name, s.severity = coalesce($severity, 1), s.created_at = $created_at, s.confidence_score = $confidence_score, s.source_type = $source_type, s.last_reinforced_at = $last_reinforced_at
ON MATCH SET s.last_reinforced_at = $last_reinforced_at
MERGE (e)-[r:FEELS_SYMPTOM]->(s)
RETURN s.id as node_id
"""

# Generalized merge node query with dynamic labels using APOC, but since we may not have APOC:
# We parameterize the label carefully or inject it securely.
# Note: Neo4j python driver does not allow parameterizing labels.

# Full mindmap query (k-hop traversal, usually k=3 for mindmaps to prevent explosion)
# optimized with MATCH paths
GET_MINDMAP_QUERY = """
MATCH path = (e:Elder {id: $elder_id})-[*1..3]-(connected)
WHERE all(node in nodes(path) WHERE (node.elder_id = $elder_id OR node:Elder))
UNWIND nodes(path) AS n
UNWIND relationships(path) AS r
RETURN COLLECT(DISTINCT {
    node_id: coalesce(n.id, n.memory_id, toString(id(n))),
    elder_id: n.elder_id,
    name: coalesce(n.name, n.description, n.title, ""),
    label: coalesce(n.emotion_tag, ""),
    labels: labels(n),
    confidence_score: n.confidence_score,
    source_type: n.source_type,
    created_at: n.created_at
}) AS path_nodes,
COLLECT(DISTINCT {
    id: toString(id(r)),
    type: type(r),
    source: coalesce(startNode(r).id, toString(id(startNode(r)))),
    target: coalesce(endNode(r).id, toString(id(endNode(r))))
}) AS path_rels
"""

# Conflict detection query (Example: CONTRADICTS)
DETECT_CONFLICTS_QUERY = """
MATCH (n1 {elder_id: $elder_id})-[r:CONTRADICTS]->(n2 {elder_id: $elder_id})
RETURN n1.id AS source_id, n2.id AS target_id, type(r) AS rel_type, r.reason AS reason
"""

GET_APPOINTMENTS_QUERY = """
MATCH (e:Elder {id: $elder_id})-[r:HAS_APPOINTMENT]->(a:Appointment)
RETURN a.id as id, a.title as title, a.datetime as datetime, a.confidence_score as confidence_score, a.source_type as source_type, a.created_at as created_at
ORDER BY a.created_at DESC
"""

GET_SYMPTOMS_QUERY = """
MATCH (e:Elder {id: $elder_id})-[r:FEELS_SYMPTOM]->(s:Symptom)
RETURN s.id as id, s.name as name, s.severity as severity, s.confidence_score as confidence_score, s.source_type as source_type, s.created_at as created_at
ORDER BY s.created_at DESC
"""

GET_MEDICINES_QUERY = """
MATCH (e:Elder {id: $elder_id})-[r:TAKES_MEDICINE]->(m:Medicine)
RETURN m.id as id, m.name as name, m.dosage as dosage, m.confidence_score as confidence_score, m.source_type as source_type, m.created_at as created_at
ORDER BY m.created_at DESC
"""

REINFORCE_NODE_QUERY = """
MATCH (n {id: $node_id})
SET n.confidence_score = CASE WHEN coalesce(n.confidence_score, 0.0) + 0.15 >= 1.0 THEN 1.0 ELSE coalesce(n.confidence_score, 0.0) + 0.15 END,
    n.last_reinforced_at = $now
RETURN n.id as node_id, n.confidence_score as confidence
"""

GET_USER_BY_USERNAME = """MATCH (u:User {username: $username}) RETURN u"""

GET_USER_BY_EMAIL = """MATCH (u:User {email: $email}) RETURN u"""

CREATE_USER = """
CREATE (u:User {
    id: randomUUID(),
    username: $username,
    email: $email,
    password_hash: $password_hash,
    role: $role,
    elder_id: $elder_id,
    full_name: $full_name,
    created_at: $created_at,
    is_active: $is_active
}) RETURN u.id as user_id, u.username as username, u.role as role
"""

ENSURE_ELDER_NODE = """
MERGE (e:Elder {id: $elder_id})
ON CREATE SET e.full_name = $full_name, e.created_at = $created_at
"""

CREATE_USER_USERNAME_CONSTRAINT = """
CREATE CONSTRAINT user_username_unique IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE
"""

CREATE_USER_EMAIL_CONSTRAINT = """
CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE
"""