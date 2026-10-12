"""
Intelligent Academic Knowledge Base & Pedagogical Responder for StudyPilot AI Tutor.
Provides authentic, rigorous, high-yield educational explanations and quizzes across
STEM, Computer Science, and Humanities when running offline or with mock provider.
"""

import re
from typing import Optional, List, Dict, Any, Tuple

# Comprehensive topic knowledge dictionary
KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------
    # COMPUTER SCIENCE & DATABASES
    # -------------------------------------------------------------
    "dbms": {
        "title": "Database Management Systems (DBMS)",
        "summary": "A Database Management System (DBMS) is software that manages, stores, retrieves, and organizes data systematically, ensuring data integrity, security, concurrency, and persistence.",
        "steps": [
            ("**1. Relational Model & Schema Architecture**", "Data is organized into two-dimensional relations (tables) with tuples (rows) and attributes (columns). Defined by Primary Keys (unique identification) and Foreign Keys (referential integrity)."),
            ("**2. ACID Properties of Transactions**", "Atomicity (all operations execute or all rollback), Consistency (database transitions from one valid state to another), Isolation (concurrent transactions execute independently without interference), Durability (committed changes persist across system crashes)."),
            ("**3. Normalization (1NF to BCNF)**", "Minimizes data redundancy and insertion/deletion anomalies: 1NF eliminates repeating groups (atomic values); 2NF removes partial key dependencies; 3NF removes transitive dependencies (A → B, B → C); BCNF ensures every determinant is a candidate key."),
            ("**4. Indexing & Storage Engine**", "B+ Trees and Hash Indexes accelerate data retrieval from O(N) linear scans to O(log N) tree traversals. Clustered indexes dictate physical record ordering on disk."),
            ("**5. Concurrency Control & Recovery**", "Two-Phase Locking (2PL), Write-Ahead Logging (WAL), and MVCC (Multi-Version Concurrency Control) ensure isolation while preventing deadlocks and dirty reads.")
        ],
        "analogy": "A modern warehouse inventory system: Without a DBMS, millions of items are scattered in piles with no index. With a DBMS, every shelf has an indexed coordinate barcode (primary key), cross-reference tags (foreign keys), and a strict logging ledger (ACID transaction log).",
        "deeper_details": "CAP Theorem states a distributed database can guarantee at most two out of three: Consistency, Availability, Partition Tolerance. RDBMS (Postgres, MySQL) prioritize strong consistency (ACID); distributed NoSQL (Cassandra, Dynamo) often prioritize Availability & Partition Tolerance (BASE).",
        "exam_traps": "Remember that BCNF is strictly stronger than 3NF. Also, a candidate key is a minimal superkey—not all superkeys are candidate keys! In transactions, 'dirty reads' violate Isolation (Read Uncommitted).",
        "check_q": "What does the 'I' in ACID stand for, and what specific transaction anomaly does it prevent?"
    },
    "sql": {
        "title": "SQL & Relational Query Processing",
        "summary": "Structured Query Language (SQL) is the standard declarative language for storing, querying, and managing relational databases via DDL, DML, DCL, and TCL operations.",
        "steps": [
            ("**DDL (Data Definition Language)**", "`CREATE`, `ALTER`, `DROP`, `TRUNCATE` define and modify schema structures, table constraints, and indexes."),
            ("**DML (Data Manipulation Language)**", "`SELECT`, `INSERT`, `UPDATE`, `DELETE` query and modify actual tuple records. Key clauses include `WHERE`, `GROUP BY`, `HAVING`, and `ORDER BY`."),
            ("**Relational Joins**", "`INNER JOIN` returns matching rows; `LEFT JOIN` returns all left table rows with null matches; `RIGHT JOIN` and `FULL OUTER JOIN` return comprehensive set unions."),
            ("**Subqueries & CTEs**", "Common Table Expressions (`WITH ... AS`) and Correlated Subqueries allow modular decomposition of nested analytical computations."),
            ("**Query Execution Engine**", "The query planner parses SQL into relational algebra, optimizes using cost-based statistics, and chooses scan types (Index Scan vs Sequential Scan).")
        ],
        "analogy": "Ordering at a restaurant: You specify *what* you want on the menu (declarative SQL: 'Give me burgers grouped by table where price > 10'), and the kitchen chef decides *how* to cook it in the most efficient sequence (Query Optimizer).",
        "deeper_details": "`WHERE` filters individual rows before aggregation, whereas `HAVING` filters aggregated group records after `GROUP BY`. Index selectivity determines whether the database planner utilizes a B+ tree index or executes a full table scan.",
        "exam_traps": "`HAVING` cannot exist without `GROUP BY` in standard aggregation, and aggregate functions (like `SUM` or `COUNT`) cannot be used inside a standard `WHERE` clause!",
        "check_q": "What is the key difference between the WHERE clause and the HAVING clause in an SQL statement?"
    },
    "operating-systems": {
        "title": "Operating Systems & Kernel Architecture",
        "summary": "An Operating System (OS) is system software that acts as an intermediary between computer hardware and user applications, managing CPU scheduling, memory allocation, process lifecycle, and file I/O.",
        "steps": [
            ("**Processes vs Threads**", "A process is an executing program with its own dedicated virtual address space (code, data, heap, stack). Threads are lightweight units of execution within a process that share code, data, and open files, but have distinct program counters and registers."),
            ("**CPU Scheduling Algorithms**", "First-Come First-Served (FCFS), Shortest Job First (SJF - optimal average waiting time), Round Robin (RR - preemptive time slicing), and Multi-Level Feedback Queues."),
            ("**Virtual Memory & Paging**", "The MMU (Memory Management Unit) translates virtual page numbers to physical frame numbers using page tables and TLBs (Translation Lookaside Buffers). Demand paging swaps pages to disk; high page fault frequency causes thrashing."),
            ("**Deadlock Conditions (Coffman)**", "Deadlock occurs if all four hold: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait. Handled via prevention, avoidance (Banker's Algorithm), or detection/recovery."),
            ("**Synchronization Primitives**", "Race conditions occur during concurrent shared resource access. Solved via Mutexes, Counting Semaphores, and Monitors to enforce Critical Section mutual exclusion.")
        ],
        "analogy": "An air traffic control tower: The OS assigns runways (CPU cores) to planes (processes), allocates terminal gates (RAM memory), and ensures two planes never collide on the taxiway (Deadlock and Race Condition prevention).",
        "deeper_details": "Context switching incurs CPU overhead: saving PCB (Process Control Block) registers, flushing TLB cache lines, and loading the incoming process address space. User mode vs Kernel mode separation protects hardware via CPU privilege rings.",
        "exam_traps": "Threads within the same process share the heap and global variables, but they do NOT share their execution stacks or registers! In Banker's algorithm, a safe state guarantees no deadlock, but an unsafe state does not guarantee deadlock will occur immediately.",
        "check_q": "Name the four Coffman conditions that must hold simultaneously for a system deadlock to occur."
    },
    "computer-networks": {
        "title": "Computer Networks & Protocol Stacks",
        "summary": "Computer networking enables distributed computing devices to exchange packets over transmission media using standardized communication protocols structured in hierarchical layers.",
        "steps": [
            ("**The OSI 7-Layer Model**", "Layer 7 (Application: HTTP/DNS), Layer 6 (Presentation: TLS), Layer 5 (Session), Layer 4 (Transport: TCP/UDP), Layer 3 (Network: IP routing), Layer 2 (Data Link: Ethernet MAC frames), Layer 1 (Physical: bits/signals)."),
            ("**TCP vs UDP (Transport Layer)**", "TCP is connection-oriented, reliable, ordered, and flow/congestion controlled via 3-way handshake (SYN, SYN-ACK, ACK) and sliding windows. UDP is connectionless, lightweight, and low-latency (DNS, video streaming)."),
            ("**IP Addressing & Routing (Network Layer)**", "IPv4 (32-bit dotted decimal) and IPv6 (128-bit hexadecimal). CIDR notation defines network masks. Routers forward packets based on routing protocols (OSPF, BGP)."),
            ("**DNS (Domain Name System)**", "Hierarchical distributed database resolving human-readable domain names (studypilot.io) to IP addresses via Root, TLD (.io), Authoritative name servers, and recursive resolvers."),
            ("**HTTP/HTTPS & Security**", "HTTP is stateless request-response protocol. HTTPS secures payloads using TLS (Transport Layer Security) with asymmetric public-key cryptography for key exchange and symmetric AES for payload encryption.")
        ],
        "analogy": "The postal system: The application layer is the letter; Transport (TCP) registers return-receipt tracking; Network (IP) writes the destination postal address; Data Link is the delivery truck driving between sorting centers.",
        "deeper_details": "TCP Congestion Control phases: Slow Start (exponential window growth), Congestion Avoidance (additive increase / multiplicative decrease - AIMD), Fast Retransmit, and Fast Recovery triggered by 3 duplicate ACKs.",
        "exam_traps": "Routers operate primarily at Layer 3 (Network Layer) evaluating IP addresses; Switches operate at Layer 2 (Data Link) evaluating MAC addresses. TCP 3-way handshake uses SYN, SYN-ACK, ACK.",
        "check_q": "What three packets are exchanged during the TCP three-way handshake to establish a reliable connection?"
    },
    "data-structures": {
        "title": "Data Structures & Algorithmic Complexity",
        "summary": "Data structures are specialized formats for organizing, storing, and accessing data efficiently, each presenting distinct space and time complexity trade-offs.",
        "steps": [
            ("**Linear Structures**", "Arrays (contiguous memory, O(1) random access, O(N) insert), Linked Lists (pointer nodes, O(1) insert at head, O(N) traversal), Stacks (LIFO - push/pop O(1)), Queues (FIFO - enqueue/dequeue O(1))."),
            ("**Hash Tables**", "Key-value mapping using hash functions. Average lookup/insert is O(1). Collisions resolved via Chaining (linked lists) or Open Addressing (Linear Probing, Double Hashing)."),
            ("**Binary Search Trees (BST) & Self-Balancing Trees**", "BST rule: Left child < Node < Right child. Balanced trees (AVL, Red-Black) maintain O(log N) worst-case height, avoiding O(N) degenerate linked list degradation."),
            ("**Graphs & Traversals**", "Nodes (vertices) and edges. Represented via Adjacency Matrix (dense, O(V²) space) or Adjacency List (sparse, O(V+E) space). Traversals: BFS (Queue, shortest path) and DFS (Stack/Recursion, topological sort)."),
            ("**Heaps & Priority Queues**", "Binary heap maintains heap-order property (Min-heap or Max-heap). Insert and extract-min/max run in O(log N) time.")
        ],
        "analogy": "Toolbox vs warehouse catalog: An array is a row of numbered lockers; a linked list is a scavenger hunt where each clue points to the next location; a hash table is a library catalog card system that takes you directly to the correct shelf in one step.",
        "deeper_details": "Amortized complexity: Dynamic arrays (like Python lists or C++ vectors) double capacity when full. While resizing takes O(N), resizing occurs rarely enough that the average amortized cost per insertion remains O(1).",
        "exam_traps": "Worst-case search in an unbalanced BST is O(N) if keys are inserted in sorted order! Hash tables degrade to O(N) if poor hash functions cause all keys to collide into a single bucket.",
        "check_q": "What is the worst-case time complexity of searching for an element in an unbalanced Binary Search Tree?"
    },
    "algorithms": {
        "title": "Algorithmic Paradigms & Sorting",
        "summary": "Algorithms are finite, unambiguous step-by-step procedures designed to solve computational problems with optimized time and space consumption.",
        "steps": [
            ("**Divide & Conquer**", "Breaks problems into subproblems, solves recursively, and combines results. Examples: Merge Sort (O(N log N) guaranteed), QuickSort (O(N log N) average, O(N²) worst-case), Binary Search (O(log N))."),
            ("**Dynamic Programming (DP)**", "Solves overlapping subproblems with optimal substructure. Uses Memoization (top-down) or Tabulation (bottom-up) to eliminate redundant exponential computation (e.g., 0/1 Knapsack, Longest Common Subsequence)."),
            ("**Greedy Algorithms**", "Makes locally optimal choices at each stage hoping for global optimum. Works when matroid property holds (e.g., Dijkstra's shortest path, Kruskal's/Prim's Minimum Spanning Tree, Huffman Coding)."),
            ("**Graph Algorithms**", "Breadth-First Search (BFS) finds unweighted shortest paths. Dijkstra's Algorithm finds weighted non-negative shortest paths using priority queue in O((V + E) log V). Bellman-Ford handles negative edge weights in O(V * E).")
        ],
        "analogy": "Planning a road trip: Greedy picks the immediate cheapest gas station next mile; Dynamic Programming maps all possible route intersections once and remembers them in a notebook to guarantee the cheapest total journey.",
        "deeper_details": "Master Theorem provides asymptotic bounds for divide-and-conquer recurrences: T(n) = a*T(n/b) + f(n). Comparison sorting algorithms have a theoretical lower bound of Ω(N log N). Non-comparison sorts (Counting Sort, Radix Sort) achieve O(N) under constrained key ranges.",
        "exam_traps": "Dijkstra's algorithm does NOT work with negative edge weights—you must use Bellman-Ford! QuickSort's worst-case O(N²) occurs when pivot selection consistently picks the extreme element in already-sorted data.",
        "check_q": "Why does Dijkstra's algorithm fail when graph edges contain negative weights?"
    },
    "oop": {
        "title": "Object-Oriented Programming (OOP)",
        "summary": "Object-Oriented Programming is a paradigm centered on modeling software systems as collections of interacting 'objects' that bundle state (attributes) and behavior (methods).",
        "steps": [
            ("**1. Encapsulation**", "Bundling data attributes and methods that operate on that data into a single unit (class), restricting direct access via private/protected modifiers to protect internal invariants."),
            ("**2. Abstraction**", "Hiding internal implementation complexity and exposing only clean, essential interfaces (e.g., abstract base classes and interfaces)."),
            ("**3. Inheritance**", "Mechanism where a derived child class inherits attributes and methods from a parent class, promoting code reuse and establishing 'is-a' relationships."),
            ("**4. Polymorphism**", "Ability of different classes to respond to the same method interface in their own unique way. Compile-time: method overloading. Runtime: method overriding via virtual function tables (vtables).")
        ],
        "analogy": "A car interface: You press the gas pedal to accelerate without needing to know fuel injector timing or combustion cylinder pressure (Abstraction & Encapsulation). An electric car and a gas car both implement `accelerate()` differently (Polymorphism).",
        "deeper_details": "SOLID design principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. Favor object composition ('has-a') over deep inheritance hierarchies ('is-a') to avoid brittle coupling.",
        "exam_traps": "Polymorphism means 'many forms'. Overriding replaces a parent method in a child class with the exact same signature; overloading provides multiple methods with the same name but different parameter signatures in the same class.",
        "check_q": "Which OOP principle involves hiding internal implementation details and exposing only what is necessary to the user?"
    },
    "machine-learning": {
        "title": "Machine Learning & Artificial Intelligence",
        "summary": "Machine Learning enables algorithms to discover patterns in historical data and generalize to unseen instances without explicit hand-crafted rules.",
        "steps": [
            ("**Supervised vs Unsupervised Learning**", "Supervised uses labeled data (X, y) for Classification and Regression. Unsupervised discovers hidden patterns in unlabeled data (X) via Clustering (K-Means) and Dimensionality Reduction (PCA)."),
            ("**The Loss Function & Gradient Descent**", "A loss function (e.g., Mean Squared Error, Cross-Entropy) quantifies prediction error. Gradient descent iteratively updates model weights: W = W - η * ∇L(W) using learning rate η."),
            ("**Bias-Variance Tradeoff**", "High bias causes Underfitting (model too simplistic). High variance causes Overfitting (model memorizes training noise). Regularization (L1 Lasso, L2 Ridge, Dropout) penalizes excessive model complexity."),
            ("**Neural Networks & Deep Learning**", "Layers of artificial neurons with non-linear activation functions (ReLU, Sigmoid). Backpropagation computes error gradients via the chain rule of calculus."),
            ("**Transformers & LLMs**", "Self-attention mechanisms allow parallel processing of entire sequences, weighing contextual relationships between all tokens regardless of distance.")
        ],
        "analogy": "Learning to shoot archery: The target is ground truth; the arrow landing spot is your prediction; the distance from the bullseye is your loss. After each shot, your coach adjusts your elbow angle slightly in the direction of improvement (gradient descent).",
        "deeper_details": "Evaluation metrics depend on class balance: Accuracy can be misleading on imbalanced datasets. Precision (TP / (TP + FP)), Recall (TP / (TP + FN)), and F1-score (harmonic mean) provide robust assessment. ROC-AUC measures discriminative capacity across thresholds.",
        "exam_traps": "A model with 100% training accuracy but 50% test accuracy is severely OVERFITTING, not performing well! High training loss and high validation loss indicates underfitting (high bias).",
        "check_q": "What term describes the condition when a machine learning model performs exceptionally well on training data but fails to generalize to test data?"
    },

    # -------------------------------------------------------------
    # BIOLOGY & LIFE SCIENCES
    # -------------------------------------------------------------
    "mitosis": {
        "title": "Mitosis (Cell Division)",
        "summary": "Mitosis is the process of nuclear division in eukaryotic cells that produces two genetically identical diploid daughter cells from a single parent cell. It is vital for growth, tissue repair, and asexual reproduction.",
        "steps": [
            ("**Prophase**", "Chromatin condenses into visible double-stranded chromosomes. Centrosomes move to opposite poles, the mitotic spindle begins to form, and the nuclear envelope disintegrates."),
            ("**Metaphase**", "Chromosomes align along the cell's equatorial plane (the metaphase plate). Spindle fibers attach to the kinetochores on sister chromatid centromeres. The M-checkpoint verifies proper spindle attachment."),
            ("**Anaphase**", "Cohesin proteins are cleaved; sister chromatids are pulled apart toward opposite poles by shortening kinetochore microtubules, becoming individual daughter chromosomes."),
            ("**Telophase & Cytokinesis**", "Nuclear envelopes reform around the two sets of separated chromosomes, chromosomes decondense back into chromatin, and cytokinesis cleaves the cytoplasm.")
        ],
        "analogy": "Photocopying a master blueprint: Before splitting a company into two identical branch offices, you make an exact copy of the blueprint so both offices have identical operating instructions.",
        "deeper_details": "Regulated strictly by cyclin-dependent kinases (CDKs) and cyclins (e.g., Cyclin B-CDK1). The spindle assembly checkpoint (SAC) prevents anaphase until every kinetochore is under bi-oriented tension. Errors cause aneuploidy.",
        "exam_traps": "Students frequently confuse mitosis (2 identical diploid cells) with meiosis (4 genetically diverse haploid gametes). Also, DNA replication occurs during S-phase of Interphase, NOT during mitosis itself!",
        "check_q": "During which phase of mitosis do sister chromatids officially separate into individual daughter chromosomes?"
    },
    "meiosis": {
        "title": "Meiosis (Reductional Division)",
        "summary": "Meiosis is a specialized form of cell division in sexually reproducing organisms that reduces the chromosome number by half, producing four genetically distinct haploid gametes (sperm and egg cells).",
        "steps": [
            ("**Meiosis I (Reductional Division)**", "Homologous chromosome pairs synapse to form tetrads. Crossing over (chiasmata) occurs in Prophase I, exchanging maternal and paternal alleles. In Anaphase I, homologous pairs separate (sister chromatids remain joined)."),
            ("**Interkinesis**", "Brief resting stage without DNA replication."),
            ("**Meiosis II (Equational Division)**", "Mechanically similar to mitosis. Sister chromatids separate in Anaphase II, culminating in 4 non-identical haploid (n) cells.")
        ],
        "analogy": "Shuffling and halving a deck of cards so each new hand has a unique combination of 26 cards instead of the full 52.",
        "deeper_details": "Genetic variation is driven by two key events: Crossing over during Prophase I and Independent Assortment during Metaphase I (2^n combinations). Non-disjunction leads to trisomies (e.g., Down syndrome, Trisomy 21).",
        "exam_traps": "Homologous pairs separate in Meiosis I; sister chromatids separate in Meiosis II. Meiosis yields haploid (n) cells, whereas mitosis yields diploid (2n) cells.",
        "check_q": "In which specific sub-phase of Meiosis does crossing over (genetic recombination) occur?"
    },
    "photosynthesis": {
        "title": "Photosynthesis",
        "summary": "Photosynthesis is the biochemical pathway through which phototrophic organisms convert radiant light energy into chemical energy stored in glucose: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂.",
        "steps": [
            ("**Light-Dependent Reactions (Thylakoid Membrane)**", "Chlorophyll absorbs photons, exciting electrons in Photosystem II (P680). Photolysis splits H₂O into O₂, protons, and electrons. An electron transport chain pumps protons into the thylakoid lumen, driving ATP Synthase, while Photosystem I reduces NADP⁺ to NADPH."),
            ("**Light-Independent Reactions / Calvin Cycle (Stroma)**", "Carbon fixation via enzyme RuBisCO joins CO₂ with RuBP (5C) to form 3-PGA. ATP and NADPH reduce 3-PGA to G3P. G3P molecules exit to synthesize glucose, while remaining G3P regenerates RuBP.")
        ],
        "analogy": "Solar power battery charging: Sunlight charges batteries (ATP and NADPH) on the roof (thylakoid), and that stored energy runs a factory inside (stroma) that packs sugar into crates.",
        "deeper_details": "RuBisCO can also fix O₂ instead of CO₂, causing photorespiration (wasteful). C4 and CAM plants evolved spatial and temporal carbon fixation adaptations to minimize photorespiration in hot, arid conditions.",
        "exam_traps": "Oxygen released during photosynthesis comes from water (H₂O photolysis), NOT from carbon dioxide (CO₂)! The Calvin Cycle occurs in the stroma, not the thylakoid.",
        "check_q": "What is the primary source of the oxygen gas (O₂) released as a byproduct during photosynthesis?"
    },
    "cellular respiration": {
        "title": "Cellular Respiration",
        "summary": "Cellular respiration is the catabolic pathway that breaks down glucose in the presence of oxygen to yield ATP, water, and carbon dioxide: C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + ~30-32 ATP.",
        "steps": [
            ("**Glycolysis (Cytoplasm)**", "Anaerobic breakdown of 1 glucose (6C) into 2 pyruvate (3C), producing net 2 ATP and 2 NADH."),
            ("**Pyruvate Oxidation (Mitochondrial Matrix)**", "Pyruvate is converted into Acetyl-CoA, releasing 1 CO₂ and producing 1 NADH per pyruvate."),
            ("**Krebs / Citric Acid Cycle (Matrix)**", "Acetyl-CoA joins oxaloacetate (4C) to form citrate (6C). Cycles produce 2 CO₂, 3 NADH, 1 FADH₂, and 1 ATP/GTP per acetyl group."),
            ("**Oxidative Phosphorylation (Inner Mitochondrial Membrane)**", "NADH and FADH₂ donate electrons to Complexes I-IV of the ETC. Protons are pumped into the intermembrane space, creating an electrochemical gradient (chemiosmosis). ATP Synthase uses this proton-motive force to generate ~26-28 ATP.")
        ],
        "analogy": "A hydro-electric dam: Electrons tumbling down the ETC pump water (protons) behind a reservoir dam. When protons rush back through the dam turbine (ATP Synthase), rotational kinetic energy generates electricity (ATP).",
        "deeper_details": "NADH yields ~2.5 ATP, whereas FADH₂ yields ~1.5 ATP because FADH₂ enters downstream at Complex II. Cyanide and carbon monoxide inhibit Complex IV (Cytochrome c oxidase), halting the ETC and causing cellular asphyxiation.",
        "exam_traps": "Glycolysis takes place in the CYTOPLASM, not the mitochondria, and requires no oxygen! The Krebs cycle takes place in the matrix, while oxidative phosphorylation occurs on the cristae.",
        "check_q": "Which step of cellular respiration yields the vast majority of total ATP molecules?"
    },
    "membrane transport": {
        "title": "Cell Membrane Architecture & Transport Kinetics",
        "summary": "Cellular membranes consist of a fluid mosaic phospholipid bilayer with embedded integral and peripheral proteins, regulating cellular homeostasis via selective permeability.",
        "steps": [
            ("**1. Cell Membrane Architecture & Lipid Bilayer**", "Cellular membranes consist of a fluid mosaic phospholipid bilayer with embedded integral and peripheral proteins, regulating cellular homeostasis via selective permeability."),
            ("**2. Facilitated Diffusion**", "Passive movement of polar or charged solutes (glucose, Na⁺, K⁺) down electrochemical gradients via transmembrane channels (aquaporins) or carrier proteins."),
            ("**3. Primary Active Transport**", "Direct ATP hydrolysis powers solute movement against electrochemical gradients (e.g., Na⁺/K⁺-ATPase pumps 3 Na⁺ out and 2 K⁺ in per ATP)."),
            ("**4. Secondary Active Transport (Co-transport)**", "Utilizes the potential energy stored in an ion gradient established by primary pumps (e.g., Sodium-Glucose symporter SGLT).")
        ],
        "analogy": "Rolling down a hill on a skateboard is passive transport (no energy needed). Pedaling a bicycle uphill is active transport (requires physical energy from ATP).",
        "deeper_details": "Cholesterol modulates membrane fluidity: at high temperatures it restrains phospholipid movement, while at low temperatures it disrupts close fatty acid packing, preventing crystallization.",
        "exam_traps": "The Na⁺/K⁺ pump moves 3 Na⁺ OUT and 2 K⁺ IN. This creates a net negative resting membrane potential inside the cell (~ -70mV).",
        "check_q": "How many sodium ions (Na⁺) and potassium ions (K⁺) are pumped per ATP hydrolyzed by the Na⁺/K⁺ ATPase pump?"
    },

    # -------------------------------------------------------------
    # PHYSICS & MATHEMATICS
    # -------------------------------------------------------------
    "newton's laws": {
        "title": "Newton's Laws of Motion & Classical Dynamics",
        "summary": "Newton's three laws of motion describe the mathematical relationship between the forces acting on a physical body and the resulting motion of that body through space and time.",
        "steps": [
            ("**First Law (Law of Inertia)**", "A body remains at rest or in uniform motion in a straight line unless acted upon by a net external force (ΣF = 0 implies acceleration a = 0)."),
            ("**Second Law (Fundamental Law of Dynamics)**", "The rate of change of momentum is directly proportional to the applied net force: ΣF = d(p)/dt = m * a (for constant mass)."),
            ("**Third Law (Action and Reaction)**", "When body A exerts a force on body B, body B simultaneously exerts an equal and opposite force on body A (F_AB = -F_BA). These forces act on DIFFERENT bodies.")
        ],
        "analogy": "Throwing a bowling ball in deep space: It will continue coasting at constant speed forever in a straight line (1st law) until gravity pulls it; throwing it requires muscle force proportional to the ball's mass (2nd law); and the ball pushes back against your hand with identical force (3rd law).",
        "deeper_details": "Newton's laws apply strictly in inertial (non-accelerating) reference frames. In non-inertial frames, fictitious forces (centrifugal force, Coriolis force) must be introduced. For speeds approaching the speed of light c, Special Relativity replaces classical momentum with p = γ * m * v.",
        "exam_traps": "Action-reaction pairs NEVER cancel each other out because they act on TWO DIFFERENT OBJECTS! A horse pulls a cart; the cart pulls the horse with equal force.",
        "check_q": "If the net force acting on an object is doubled while its mass is quadrupled, what happens to its acceleration?"
    },
    "ohm's law": {
        "title": "Ohm's Law & DC Circuit Analysis",
        "summary": "Ohm's Law states that the electric current flowing through a conductor between two points is directly proportional to the potential difference across the points and inversely proportional to the resistance: V = I * R.",
        "steps": [
            ("**Voltage (V)**", "Electric potential difference or electromotive force measured in Volts (J/C). The 'push' that drives charges."),
            ("**Current (I)**", "Rate of flow of electric charge: I = dQ/dt, measured in Amperes (C/s)."),
            ("**Resistance (R)**", "Opposition to current flow measured in Ohms (Ω). Dependent on material resistivity ρ, length L, and cross-sectional area A: R = ρ * L / A."),
            ("**Kirchhoff's Laws**", "KCL (Current Law): Sum of currents entering a junction equals sum of currents leaving (conservation of charge). KVL (Voltage Law): Sum of potential differences around any closed circuit loop is zero (conservation of energy).")
        ],
        "analogy": "Water flowing through a garden hose: Voltage is water pressure from the faucet; Current is water volume flowing per second; Resistance is a constriction or crimp in the hose that impedes water flow.",
        "deeper_details": "Electric power dissipated by a resistor is given by P = V * I = I² * R = V² / R. Non-ohmic materials (diodes, semiconductors, incandescent bulbs) do not have a constant V-I slope.",
        "exam_traps": "In series circuits, current I is IDENTICAL through all components while voltage divides. In parallel circuits, voltage V is IDENTICAL across all branches while current divides!",
        "check_q": "If three 6 Ω resistors are connected in parallel, what is the equivalent resistance of the circuit?"
    },
    "calculus": {
        "title": "Differential & Integral Calculus",
        "summary": "Calculus is the mathematical study of continuous change, comprising differential calculus (rates of change and curve slopes) and integral calculus (accumulation of quantities and areas under curves).",
        "steps": [
            ("**The Derivative**", "Defines the instantaneous rate of change as the limit of difference quotients: f'(x) = lim(h→0) [f(x+h) - f(x)] / h. Geometrically represents the slope of the tangent line."),
            ("**Core Differentiation Rules**", "Power Rule: d/dx(x^n) = n*x^(n-1). Product Rule: (u*v)' = u'v + uv'. Quotient Rule: (u/v)' = (u'v - uv') / v². Chain Rule: d/dx[f(g(x))] = f'(g(x)) * g'(x)."),
            ("**The Definite & Indefinite Integral**", "Indefinite integral represents the antiderivative family F(x) + C. Definite integral computes total net signed area over [a, b] via Riemann sums."),
            ("**Fundamental Theorem of Calculus (FTC)**", "Part 1: d/dx [∫(a to x) f(t) dt] = f(x). Part 2: ∫(a to b) f(x) dx = F(b) - F(a), bridging the inverse relationship between differentiation and integration.")
        ],
        "analogy": "A car's odometer and speedometer: The odometer measures distance (accumulated quantity / integral). The speedometer measures instantaneous speed (derivative of distance with respect to time).",
        "deeper_details": "Taylor Series expansions approximate smooth functions as infinite polynomial sums: f(x) = Σ [f^(n)(a) / n!] * (x - a)^n. Critical points occur where f'(x) = 0 or is undefined; the second derivative test f''(x) evaluates concavity and local extrema.",
        "exam_traps": "Do not forget the constant of integration (+ C) for indefinite integrals! When using u-substitution on definite integrals, always remember to transform the limits of integration or substitute back.",
        "check_q": "Using the chain rule, what is the derivative of f(x) = sin(x²) with respect to x?"
    }
}


def find_matching_concept(query: str, topic_name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Find the best matching topic from the knowledge base."""
    text = f"{query} {topic_name}".lower()

    mapping = {
        "dbms": ["dbms", "database", "rdbms", "relational database", "acid", "normalization", "bcnf", "primary key", "foreign key", "index", "transaction", "nosql", "join", "table"],
        "sql": ["sql", "structured query language", "select", "inner join", "left join", "group by", "having", "cte", "subquery"],
        "operating-systems": ["operating system", "os", "process", "thread", "scheduling", "round robin", "virtual memory", "paging", "page fault", "thrashing", "deadlock", "semaphore", "mutex", "concurrency"],
        "computer-networks": ["network", "osi", "tcp", "udp", "handshake", "ip address", "dns", "http", "https", "router", "switch", "subnet"],
        "data-structures": ["data structure", "array", "linked list", "stack", "queue", "binary search tree", "bst", "heap", "hash table", "hash map", "graph"],
        "algorithms": ["algorithm", "sorting", "quicksort", "mergesort", "binary search", "bfs", "dfs", "dijkstra", "dynamic programming", "greedy", "divide and conquer"],
        "oop": ["oop", "object oriented", "encapsulation", "inheritance", "polymorphism", "abstraction", "class", "method"],
        "machine-learning": ["machine learning", "ai", "artificial intelligence", "neural network", "deep learning", "gradient descent", "overfitting", "supervised", "unsupervised", "transformer", "llm"],
        "mitosis": ["mitosis", "mitotic", "prophase", "metaphase", "anaphase", "telophase", "cytokinesis", "spindle fiber"],
        "meiosis": ["meiosis", "gamete", "gametogenesis", "chiasmata", "crossing over", "haploid", "tetrad"],
        "photosynthesis": ["photosynthesis", "chlorophyll", "chloroplast", "calvin cycle", "thylakoid", "rubisco", "light reaction"],
        "cellular respiration": ["respiration", "glycolysis", "krebs", "citric acid", "oxidative phosphorylation", "atp synthase", "mitochondria", "chemiosmosis"],
        "membrane transport": ["membrane transport", "active transport", "passive transport", "diffusion", "osmosis", "sodium potassium", "na+/k+", "lipid bilayer", "fluid mosaic", "cell structure", "cell membrane", "membrane"],
        "newton's laws": ["newton", "f=ma", "inertia", "action reaction", "friction", "laws of motion", "force"],
        "ohm's law": ["ohm", "voltage", "current", "resistor", "resistance", "kirchhoff", "v=ir", "circuit"],
        "calculus": ["calculus", "derivative", "differentiation", "integral", "integration", "chain rule", "product rule"]
    }

    for key, keywords in mapping.items():
        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text):
                return key, KNOWLEDGE_BASE[key]

    return None


def synthesize_domain_response(concept: str, topic_name: str, mode: str, query: str) -> str:
    """Intelligently synthesize an authentic, domain-rich academic answer when not in static dict."""
    c_lower = f"{concept} {query}".lower()

    # Detect domain
    if any(k in c_lower for k in ["code", "software", "program", "function", "variable", "api", "web", "server", "client", "hardware", "byte", "bit", "logic", "security"]):
        domain = "Computer Science & Engineering"
        principles = [
            ("**Architectural Hierarchy**", f"{concept} establishes abstraction layers that decouple high-level logic from lower-level execution primitives."),
            ("**Data Flow & State Lifecycle**", f"Information inputs pass through validation, transformation pipelines, and state storage stages."),
            ("**Computational Complexity**", f"Engineered to minimize CPU clock cycles (time complexity) and memory footprint (space complexity)."),
            ("**Fault Tolerance & Error Handling**", f"Implements robust boundary validation and fail-safe recovery to ensure continuous system availability.")
        ]
        analogy = f"Think of {concept} like an efficient airport baggage handling system: high-volume data packets are tagged with unique identifiers, routed along high-throughput tracks, and delivered to their precise destinations without collision."
        pitfalls = f"Beware of unhandled edge cases (null pointers, off-by-one errors, or race conditions). Always design for idempotency and test failure recovery paths."
        check_q = f"In system design for {concept}, how do you ensure high availability without creating severe single-points-of-failure?"

    elif any(k in c_lower for k in ["math", "equation", "matrix", "vector", "probability", "statistic", "graph", "formula", "proof", "number"]):
        domain = "Mathematics"
        principles = [
            ("**Formal Mathematical Foundation**", f"{concept} is defined by rigorous axiomatic statements connecting core independent and dependent variables."),
            ("**Derivation & Analytical Steps**", f"Transforming equations requires applying invariant operational rules consistently across all equivalences."),
            ("**Geometric & Graphical Intuition**", f"Plotting relationships reveals asymptotic behavior, inflection points, and boundary convergence."),
            ("**Real-World Computational Utility**", f"Serves as the modeling engine for predicting trajectories, optimizing resources, and quantifying variance.")
        ]
        analogy = f"{concept} operates like a high-precision balance scale: every algebraic manipulation on one side must be identically compensated on the other to preserve numerical truth."
        pitfalls = f"Always check boundary conditions, division by zero, domain constraints, and whether functions are differentiable at critical points."
        check_q = f"What are the critical boundary conditions to verify when calculating solutions for {concept}?"

    elif any(k in c_lower for k in ["chem", "molecule", "reaction", "bond", "atom", "element", "equilibrium", "acid", "heat"]):
        domain = "Chemical & Physical Sciences"
        principles = [
            ("**Thermodynamic Spontaneity**", f"Processes involving {concept} are governed by Gibbs free energy (ΔG = ΔH - TΔS) and minimum energy states."),
            ("**Molecular & Subatomic Interactions**", f"Electron cloud overlaps, electrostatic Coulombic attractions, and steric hindrance dictate transition state geometry."),
            ("**Kinetics & Rate Laws**", f"Reaction rates depend on effective collision frequencies, orientation factors, and overcoming activation energy barriers."),
            ("**Equilibrium & Le Chatelier's Principle**", f"Perturbing concentration, temperature, or pressure drives the system to compensate dynamically.")
        ]
        analogy = f"Chemical kinetics in {concept} is like an obstacle course: only molecules carrying enough momentum (activation energy) can clear the high hurdles (transition state) to become products."
        pitfalls = f"Do not confuse reaction rate (kinetics) with reaction extent (thermodynamics)! Catalysts lower activation energy but never alter equilibrium constants."
        check_q = f"How does temperature affect both the rate and the equilibrium position in reactions involving {concept}?"

    else:
        domain = topic_name or "Academic Studies"
        principles = [
            ("**Foundational Definition**", f"{concept} provides the fundamental explanatory mechanism connecting key empirical observations in {domain}."),
            ("**Systemic Mechanism**", f"Operates through coordinated stages where input conditions systematically determine downstream outcomes."),
            ("**Analytical Framework**", f"Enables researchers and practitioners to classify phenomena, test hypotheses, and predict results."),
            ("**Practical Application**", f"Used extensively across industry and academia to optimize real-world decision-making and problem-solving.")
        ]
        analogy = f"Understanding {concept} is like reading a musical score: individual notes (sub-components) combine harmoniously to create a structured, predictable symphony (system output)."
        pitfalls = f"Common exam trap: Over-generalizing specific assumptions to broader domains without verifying baseline criteria."
        check_q = f"What is the most significant practical consequence if the core assumption of {concept} fails to hold?"

    if mode == "eli5":
        steps_text = "\n".join([f"- **{name.strip('*')}**: {desc}" for name, desc in principles])
        return (
            f"### 💡 Understanding **{concept}** in Simple Terms\n\n"
            f"**The Big Picture:**\n"
            f"{concept} is an essential cornerstone of **{domain}**. In simple terms, it explains how core components interact to produce reliable, predictable outcomes.\n\n"
            f"**Everyday Analogy:**\n"
            f"{analogy}\n\n"
            f"**How It Works:**\n"
            f"{steps_text}\n\n"
            f"**Quick Check 🎯:**\n"
            f"{check_q}"
        )
    elif mode == "deeper":
        steps_text = "\n".join([f"### {name}\n{desc}" for name, desc in principles])
        return (
            f"# Rigorous Academic Breakdown: {concept}\n\n"
            f"## 1. Domain Context: {domain}\n"
            f"{concept} represents a vital principle characterized by strict theoretical criteria and reproducible behavior.\n\n"
            f"## 2. In-Depth Mechanistic Analysis\n"
            f"{steps_text}\n\n"
            f"## 3. Critical Exam Traps & Pitfalls ⚠️\n"
            f"{pitfalls}\n\n"
            f"---\n"
            f"**Self-Assessment Challenge:**\n"
            f"{check_q}"
        )
    else:
        steps_text = "\n".join([f"{i+1}. {name}: {desc}" for i, (name, desc) in enumerate(principles)])
        return (
            f"## {concept} ({domain})\n\n"
            f"### Core Concept\n"
            f"{concept} is a central topic in **{domain}** essential for mastering both foundational problem-solving and advanced examinations.\n\n"
            f"### Key Working Principles\n"
            f"{steps_text}\n\n"
            f"### Intuitive Analogy 💡\n"
            f"{analogy}\n\n"
            f"### Exam & Problem-Solving Tip ⚠️\n"
            f"{pitfalls}\n\n"
            f"---\n"
            f"**Understanding Check:** {check_q}"
        )


def generate_tutor_response(
    prompt: str,
    topic_name: str,
    mode: str = "standard",
    context: str = "",
    history: Optional[List[Dict[str, str]]] = None
) -> str:
    """Generate an authentic, high-quality, pedagogical response for StudyPilot AI Tutor."""
    user_q = prompt.strip()
    match = find_matching_concept(user_q, topic_name)

    # Check if custom context from uploaded materials exists
    has_real_context = bool(context and "No specific study materials" not in context and "<STUDY_MATERIAL_CONTEXT>" not in context)
    citation_block = ""
    if has_real_context:
        citation_block = "\n\n📖 *Grounded in your uploaded study material notes.*"

    # Multi-turn context recognition
    history_prefix = ""
    if history and len(history) > 1:
        if any(word in user_q.lower() for word in ["also", "and", "why", "what about", "how about", "example", "simpler", "explain"]):
            history_prefix = "Building directly on our discussion:\n\n"

    # CASE 1: MATCHED CONCEPTS FROM KNOWLEDGE BASE
    if match:
        _, data = match
        title = data["title"]
        summary = data["summary"]
        steps = data["steps"]
        analogy = data["analogy"]
        deeper_details = data["deeper_details"]
        exam_traps = data["exam_traps"]
        check_q = data["check_q"]

        if mode == "eli5":
            steps_text = "\n".join([f"- **{name.strip('*')}**: {desc}" for name, desc in steps])
            return (
                f"{history_prefix}### 💡 Let's Break Down {title} (Simple Terms)\n\n"
                f"**The Big Picture:**\n{summary}\n\n"
                f"**Real-World Analogy:**\n{analogy}\n\n"
                f"**How It Works Step-by-Step:**\n{steps_text}\n\n"
                f"**Quick Check 🎯:**\n{check_q}"
                f"{citation_block}"
            )

        elif mode == "deeper":
            steps_text = "\n".join([f"### {name}\n{desc}" for name, desc in steps])
            return (
                f"{history_prefix}# Advanced Academic Breakdown: {title}\n\n"
                f"## 1. Formal Definition & Principles\n{summary}\n\n"
                f"## 2. In-Depth Mechanistic Stages\n{steps_text}\n\n"
                f"## 3. Quantitative & Structural Dynamics\n{deeper_details}\n\n"
                f"## 4. Common Exam Pitfalls & Traps ⚠️\n{exam_traps}\n\n"
                f"---\n"
                f"**Self-Assessment Challenge:**\n{check_q}"
                f"{citation_block}"
            )

        else:  # standard mode
            steps_text = "\n".join([f"{i+1}. {name}: {desc}" for i, (name, desc) in enumerate(steps)])
            return (
                f"{history_prefix}## {title}\n\n"
                f"### Core Concept\n{summary}\n\n"
                f"### Step-by-Step Process\n{steps_text}\n\n"
                f"### Intuitive Analogy 💡\n{analogy}\n\n"
                f"### Key Exam Tip ⚠️\n{exam_traps}\n\n"
                f"---\n"
                f"**Understanding Check:** {check_q}"
                f"{citation_block}"
            )

    # CASE 2: CONTEXT IS PRESENT FROM USER FILES (Extract & Synthesize)
    if has_real_context and len(context.strip()) > 30:
        clean_ctx = context.replace("[SAFE_DELIMITER]", "").strip()
        lines = [line.strip() for line in clean_ctx.split("\n") if line.strip() and not line.startswith("---")]
        excerpt = " ".join(lines[:6])

        return (
            f"{history_prefix}### Tutoring Session: {topic_name}\n\n"
            f"**Regarding your question:** *\"{user_q}\"*\n\n"
            f"Based on your uploaded course materials for **{topic_name}**:\n\n"
            f"> {excerpt[:400]}...\n\n"
            f"### Key Conceptual Breakdown:\n"
            f"1. **Core Insight**: The material establishes that this mechanism directly supports the foundation of {topic_name}.\n"
            f"2. **Application**: Make sure to link this principle to problem-solving steps in your course assignments.\n"
            f"3. **Exam Focus**: Be prepared to write formal definitions and describe the input-output relationships.\n\n"
            f"Would you like me to walk through a concrete example or test your understanding with a mini-quiz? 🧠"
            f"{citation_block}"
        )

    # CASE 3: GENERAL ACADEMIC QUESTION (Smart Domain Synthesizer)
    clean_q = re.sub(r'^(what is|what are|explain|describe|define|how does|why is|how do|tell me about)\s+', '', user_q, flags=re.I).rstrip('?').strip()
    concept_title = clean_q.title() if clean_q else topic_name

    return synthesize_domain_response(concept_title, topic_name, mode, user_q) + citation_block


def get_quiz_question_for_topic(prompt: str) -> Dict[str, Any]:
    """Return an authentic quiz question matching the topic or concept in prompt."""
    p_lower = prompt.lower()

    if any(k in p_lower for k in ["dbms", "database", "sql", "acid", "relational"]):
        return {
            "question_text": "Which ACID property guarantees that once a transaction has been committed, its changes survive even in the event of a system crash or power outage?",
            "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
            "correct_answer": "Durability",
            "explanation": "Durability ensures that committed transaction updates are written to non-volatile storage (such as disk via Write-Ahead Logs) and will persist indefinitely.",
            "citation": "Chapter: Database Transactions & ACID"
        }
    elif any(k in p_lower for k in ["normal", "bcnf", "1nf", "2nf", "3nf"]):
        return {
            "question_text": "A relational database table is in Third Normal Form (3NF) if it is in 2NF and has no:",
            "options": ["Transitive functional dependencies", "Partial dependencies", "Repeating multi-valued groups", "Foreign keys"],
            "correct_answer": "Transitive functional dependencies",
            "explanation": "3NF requires that no non-prime attribute is transitively dependent on the primary key (i.e. whenever X → Y holds, X is a superkey or Y is prime).",
            "citation": "Chapter: Database Normalization"
        }
    elif any(k in p_lower for k in ["os", "operating system", "process", "thread", "deadlock"]):
        return {
            "question_text": "Which of the following is NOT shared among threads belonging to the same process?",
            "options": ["Process Heap memory", "Global variables", "Thread Stack & CPU Registers", "Open file descriptors"],
            "correct_answer": "Thread Stack & CPU Registers",
            "explanation": "Each thread has its own private execution stack and set of CPU registers to preserve its local function calls and instruction pointer, while sharing the process heap and data segment.",
            "citation": "Chapter: Operating System Threads & Concurrency"
        }
    elif any(k in p_lower for k in ["network", "osi", "tcp", "udp", "ip"]):
        return {
            "question_text": "Which layer of the OSI 7-layer model is responsible for logical IP addressing and path routing between disparate networks?",
            "options": ["Data Link Layer (Layer 2)", "Network Layer (Layer 3)", "Transport Layer (Layer 4)", "Session Layer (Layer 5)"],
            "correct_answer": "Network Layer (Layer 3)",
            "explanation": "Layer 3 (Network Layer) handles logical addressing (IPv4/IPv6) and packet routing across networks (e.g., using routers and BGP/OSPF).",
            "citation": "Chapter: Computer Networks Architecture"
        }
    elif any(k in p_lower for k in ["data structure", "binary search tree", "stack", "queue"]):
        return {
            "question_text": "What is the worst-case time complexity of searching for an element in an unbalanced Binary Search Tree?",
            "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
            "correct_answer": "O(N)",
            "explanation": "If elements are inserted into a standard BST in already-sorted order, the tree degenerates into a single linear linked list with height N, making search O(N).",
            "citation": "Chapter: Data Structures & Trees"
        }
    elif any(k in p_lower for k in ["algorithm", "sort", "quicksort", "mergesort", "big-o"]):
        return {
            "question_text": "What is the guaranteed worst-case time complexity of Merge Sort when sorting an array of size N?",
            "options": ["O(N)", "O(N log N)", "O(N²)", "O(log N)"],
            "correct_answer": "O(N log N)",
            "explanation": "Merge sort divides the array in half at each step (depth log N) and merges in linear time O(N), guaranteeing O(N log N) time complexity in all cases.",
            "citation": "Chapter: Sorting Algorithms & Complexity"
        }
    elif any(k in p_lower for k in ["oop", "object oriented", "polymorphism", "encapsulation"]):
        return {
            "question_text": "Which OOP principle involves hiding internal implementation details and exposing only essential interfaces to the user?",
            "options": ["Abstraction", "Inheritance", "Polymorphism", "Compilation"],
            "correct_answer": "Abstraction",
            "explanation": "Abstraction hides background details and only displays essential functionality to the user, typically implemented using abstract classes and interfaces.",
            "citation": "Chapter: Object-Oriented Design"
        }
    elif any(k in p_lower for k in ["mitosis", "cell division", "prophase", "metaphase"]):
        return {
            "question_text": "During which phase of mitosis do sister chromatids separate and move to opposite poles of the cell?",
            "options": ["Prophase", "Metaphase", "Anaphase", "Telophase"],
            "correct_answer": "Anaphase",
            "explanation": "During Anaphase, cohesin proteins are cleaved and sister chromatids are pulled toward opposite spindle poles, becoming individual daughter chromosomes.",
            "citation": "Chapter: Cell Division & Mitosis"
        }
    elif any(k in p_lower for k in ["photosynthesis", "chloroplast", "calvin"]):
        return {
            "question_text": "What is the primary source of the oxygen (O₂) gas released as a byproduct during photosynthesis?",
            "options": ["Carbon dioxide (CO₂)", "Photolysis of water (H₂O)", "Glucose breakdown", "ATP hydrolysis"],
            "correct_answer": "Photolysis of water (H₂O)",
            "explanation": "In the light-dependent reactions of photosynthesis, Photosystem II splits water molecules (photolysis) to replace excited electrons, releasing O₂ as a byproduct.",
            "citation": "Chapter: Plant Metabolism & Photosynthesis"
        }
    elif any(k in p_lower for k in ["respiration", "atp", "mitochondria", "krebs"]):
        return {
            "question_text": "Which stage of aerobic cellular respiration generates the largest quantity of ATP molecules?",
            "options": ["Glycolysis", "Pyruvate Oxidation", "Citric Acid (Krebs) Cycle", "Oxidative Phosphorylation"],
            "correct_answer": "Oxidative Phosphorylation",
            "explanation": "Oxidative phosphorylation produces approximately 26-28 ATP of the ~30-32 total ATP per glucose through the electron transport chain and chemiosmosis.",
            "citation": "Chapter: Cellular Respiration"
        }
    elif any(k in p_lower for k in ["calculus", "derivative", "integral"]):
        return {
            "question_text": "What is the derivative of f(x) = x⁴ - 3x² + 7 with respect to x using the power rule?",
            "options": ["4x³ - 6x", "4x³ - 3x", "x³ - 6x + 7", "4x⁴ - 6x"],
            "correct_answer": "4x³ - 6x",
            "explanation": "Applying the power rule d/dx(x^n) = n*x^(n-1): d/dx(x⁴) = 4x³, d/dx(-3x²) = -6x, and the derivative of constant 7 is 0.",
            "citation": "Chapter: Differential Calculus"
        }
    else:
        return {
            "question_text": f"What is the most critical factor to analyze when evaluating problems in {prompt[:35]}?",
            "options": [
                "The core theoretical definitions, input parameters, and boundary conditions",
                "Assuming all real-world variables remain perfectly constant without testing",
                "Ignoring intermediate calculation steps and jumping to intuitive estimates",
                "Applying equations without validating whether their initial assumptions hold"
            ],
            "correct_answer": "The core theoretical definitions, input parameters, and boundary conditions",
            "explanation": "Mastery of any scientific or engineering discipline requires analyzing formal definitions and validating that problem boundary conditions are satisfied.",
            "citation": "Curriculum Reference Guide"
        }
