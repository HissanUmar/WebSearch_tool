<!-- source: https://users.cs.utah.edu/~tch/publications/pub341.pdf -->

Title: pub341.pdf

URL Source: https://users.cs.utah.edu/~tch/publications/pub341.pdf

Published Time: Mon, 04 May 2026 18:07:22 GMT

Number of Pages: 11

Markdown Content:
# A Self-Aware BDI Agent for LLM-Driven Reasoning: Architecture, Design, and Preliminary Evaluation 

## Christopher Lawton, David Sacharny and Thomas C. Henderson 

## UUCS-26-001 

Kahlert School of Computing University of Utah Salt Lake City, UT 84112 USA 15 May 2026 

# Abstract 

Large language models (LLMs) are capable of sophisticated reasoning over individual steps but exhibit irrationality across multi-step tasks: they contradict prior statements, forget commitments, and accumulate errors in proportion to task length. Classical Belief-Desire-Intention (BDI) agent theory offers a principled framework for structured, persistent, verifiable reasoning. This paper describes the first phase of an ongoing project to build a full BDI agent architecture powered by LLMs: the design and implementation of the core deliberation loop and its evaluation harness. We make three contributions. First, we introduce architectural self-awareness : a design principle in which each loop phase is structured so the LLM understands how its outputs will be mechanically consumed downstream, yielding schema beliefs tuned for NLI plan matching, machine-verifiable satisfaction conditions, and a three-tier independent verification system. Second, unlike prior BDI systems that rely on hand-authored plans, our agent generates parameterized natural language plans 

at runtime using role-based parameter slots, enabling each plan template to generalize across struc-turally equivalent questions without human authorship. Third, we introduce a simulation-seeding workflow : the agent refines its plan library across multiple rounds using environmental feedback (wrong answers as failure signals), and the resulting library seeds new independent agent instances, enabling structured cross-agent knowledge transfer without retraining. We evaluate the agent on 53 GAIA level-1 questions using Qwen3-8B via vLLM. Simulation mode achieves 13.2% (any round), while seeded and non-seeded single-pass runs each achieve 9.4%. Qualitative trace analysis shows that plan seeding improves reasoning structure even when raw accuracy is unchanged, and identifies web search reliability and effective tool use as the primary bottleneck. 1A Self-Aware BDI Agent for LLM-Driven Reasoning Lawton, 2026 

# A Self-Aware BDI Agent for LLM-Driven Reasoning: Architecture, Design, and Preliminary Evaluation 

## Christopher Lawton, David Sacharny and Tom Henderson 

University of Utah 

chris.ian.lawton@gmail.com 

Abstract 

Large language models (LLMs) are capable of sophisticated reasoning over individual steps but exhibit irrationality across multi-step tasks: they contradict prior statements, forget commitments, and accumulate errors in proportion to task length. Classical Belief-Desire-Intention (BDI) agent theory offers a principled framework for structured, persistent, verifiable reasoning. This paper describes the first phase of an ongoing project to build a full BDI agent architecture powered by LLMs: the design and implementation of the core deliberation loop and its evaluation harness. We make three contributions. First, we introduce 

architectural self-awareness : a design principle in which each loop phase is structured so the LLM understands how its outputs will be mechanically consumed downstream, yielding schema beliefs tuned for NLI plan matching, machine-verifiable satisfaction conditions, and a three-tier independent verification system. Second, unlike prior BDI systems that rely on hand-authored plans [5], our agent generates parameterized natural language plans at runtime using role-based parameter slots, enabling each plan template to generalize across structurally equivalent questions without human authorship. Third, we introduce a 

simulation-seeding workflow : the agent refines its plan library across multiple rounds using environmental feedback (wrong answers as failure signals), and the resulting library seeds new independent agent instances, enabling structured cross-agent knowledge transfer without retraining. We evaluate the agent on 53 GAIA level-1 questions using Qwen3-8B via vLLM. Simulation mode achieves 13.2% (any round), while seeded and non-seeded single-pass runs each achieve 9.4%. Qualitative trace analysis shows that plan seeding improves reasoning structure even when raw accuracy is unchanged, and identifies web search reliability and effective tool use as the primary bottleneck. 

## 1. Introduction 

Despite remarkable progress in language model capabil-ity, LLMs face a structural limitation when deployed as agents for long-horizon tasks: they fail to satisfy the ra-tionality criteria that motivate BDI agent design. The BDI tradition holds that rational agents must maintain consistent beliefs, honor commitments once made, and act in accordance with their stated goals [4]. LLMs routinely violate all three: they contradict statements made earlier in the same context, abandon commitments across turns without explanation, and accumulate errors at a rate that grows exponentially with task length. A model that exe-cutes each individual reasoning step with 90% reliability achieves only (0 .9) 30 ≈ 4% reliability over a 30-step task as errors compound without external structure to catch and correct them. This rationality problem is not an artifact of insufficient scale. It is a consequence of architecture: autoregres-sive models reason from context windows that function as bounded working memory, without persistent, addressable, verifiable state. As models grow larger, this structural limitation becomes more consequential as they are, in prac-tice, deployed on tasks with longer horizons and higher stakes. Structured agent architectures are therefore essen-tial as LLMs scale and are applied in highly regulated and high-consequence domains such as autonomous vehicles and clinical applications. Belief-Desire-Intention (BDI) agent theory, introduced by Rao and Georgeff [4] and implemented in systems such as PRS [2] and AgentSpeak [3], provides a formal account of how rational agents maintain consistent beliefs, commit to goals, and execute plans while remaining responsive to new information. The deliberation loop governing these states provides an explicit structure for multi-step reasoning that is absent from standard LLM inference. This paper covers the first phase of a larger project whose proposal [1] outlines a complete multi-module system in-cluding a versioned persistent knowledge base, a policy layer for consistency enforcement, an RL-based intention filter, and human-in-the-loop approval gates. Here we cover a prerequisite layer: the core deliberation loop and the evaluation harness needed to measure it. Future mod-ules are designed to slot into this foundation; none can be meaningfully evaluated without a working loop to run them on. 

Contributions. This paper makes three contributions to the design of LLM-powered BDI agents: 1. Architectural self-awareness : a design principle in which each loop phase explicitly instructs the LLM how its outputs will be consumed downstream, yielding structured beliefs, desires, and intentions, along with verifiable plan postconditions. 2. Parameterized, LLM-generated plans : unlike 1A Self-Aware BDI Agent for LLM-Driven Reasoning Lawton, 2026 

prior BDI systems that require human-authored, task-specific plan rules [5], our agent generates parameter-ized plan templates at runtime using abstract, role-based parameter slots, which in theory should enable plan reuse across structurally equivalent questions with-out human authorship. 3. Simulation-seeding for cross-agent plan transfer :a workflow in which the agent refines its plan library across multiple rounds using environmental feedback, and exports the resulting structured library to seed new independent agent instances, a form of experience transfer not achievable with bounded episodic memory systems such as Reflexion [7]. The remainder of this paper is organized as follows. Sec-tion 2 surveys related work. Section 3 describes the high-level architecture. Section 4, the core of the pa-per, describes each of the seven BDI loop phases in detail. Section 5 discusses self-awareness as a cross-cutting design principle. Section 6 describes the evaluation harness. Sec-tion 7 presents preliminary benchmark results. Section 8 discusses scope, lessons, and limitations. Sections 9 and 10 address future work and conclude. 

## 2. Background and Related Work 

2.1. The Rationality Problem in LLMs 

An autoregressive model generates each token conditioned only on a finite context window that functions as bounded working memory. The model has no privileged access to beliefs expressed earlier in the conversation; it must re-derive them from text, making consistency across turns fragile. The result is systematic failure of BDI rationality criteria: belief inconsistency, commitment failures, and error accumulation. 

2.2. BDI Agent Theory 

BDI agent theory [4] models rational agents in terms of three mental states: beliefs (the agent’s world representa-tion), desires (goals to achieve), and intentions (desires the agent has committed to pursue). The deliberation cy-cle governs how these states are updated: new perceptions revise beliefs, revised beliefs generate candidate desires, candidate desires are filtered into committed intentions, and intentions drive action selection. NatBDI [5] extends BDI to natural language environments using natural language inference (NLI) to match plans written in natural language against current beliefs, with a fallback RL policy when no applicable plan exists. Even 13 hand-crafted plans substantially improved performance over pure RL on ScienceWorld tasks (up to 98% on certain subtasks). Two limitations of NatBDI directly motivate this work. First, plans are human-authored : NatBDI requires a de-veloper to write plan rules in controlled natural language before deployment; the authors explicitly identify “learn-ing plan-rules from data” as future work. Second, plans are unparameterized : each plan is bound to the specific task description it was written for (e.g., IF your task is to get the metal pot... ), and cannot generalize to structurally equivalent tasks with different entities. Our system addresses both limitations: plans are generated at runtime by the LLM and use abstract, role-based parame-ter slots (e.g. numerator , denominator ) that generalize across task instances of the same structural type. 

2.3. LLM-Based Agents 

ReAct [6] interleaves reasoning traces with external actions in a single LLM output stream, making the agent’s rea-soning inspectable and allowing corrections to propagate. ReAct achieves substantial improvements on AlfWorld (34%) and WebShop (10%) compared to existing imitation and RL methods. Our step execution phase is in the spirit of ReAct: the LLM drives its own inner tool-use loop. Reflexion [7] introduces verbal reinforcement learning: agents generate self-reflections on task outcomes stored in a bounded episodic memory (typically 1–3 recent experi-ences), improving future attempts without weight updates. Reflexion achieves 91% pass@1 accuracy on HumanEval through iterative self-reflection. Our plan review phase (Phase 7) shares Reflexion’s core intuition of learning from failure without gradient descent, but differs structurally in three ways. First, our memory is a structured plan library with quantitative statistics (useCount , successCount , failureCount ) rather than free-form textual summaries; this enables aggregate evalu-ation across many task instances, not just recent episodes. Second, the library is unbounded : plans accumulate indef-initely and are pruned by the review phase rather than truncated by a context window. Third, the library is 

transferable : the structured plan representation can be exported and used to seed entirely new, independent agent instances; a form of cross-agent knowledge transfer that Reflexion’s per-agent episodic memory cannot support. 

2.4. Neuro-Symbolic Verification 

Logic-LM [8] proposes a three-stage hybrid approach: LLMs translate natural language problems into symbolic form, a deterministic solver reasons over the symbolic representation, and the LLM maps results back to natural language, achieving a 39.2% improvement over pure LLM on logical reasoning benchmarks. Explanation-Refiner [9] integrates theorem provers with LLMs to verify and iteratively refine natural language ex-planations. GPT-4 improves from 36% to 84% valid expla-nations on e-SNLI through iterative refinement. Our tiered verification system is an instance of this LLM-verifier pat-2A Self-Aware BDI Agent for LLM-Driven Reasoning Lawton, 2026 

tern: the LLM generates step outputs, an independent verifier checks them, and failures trigger replanning. 

2.5. Structured LLM Output and Harness Archi-tectures 

Kambhampati et al. [10] argue that LLMs should not plan autonomously but instead operate inside a LLM-Modulo 

loop: the LLM proposes candidates and an external critic verifies them before they are accepted. Our three-tier verification system is an instance of this pattern applied per-step within a BDI deliberation loop, the harness never trusts a step’s self-reported completion and always applies an independent check. DSPy [11] treats LLM calls as typed modules with explicit input/output signatures, and compiles pipelines of such modules into optimized prompt-structure pairs. Our sys-tem applies the same principle at the prompt level: each phase specifies the schema its LLM call must produce, and that schema is the input contract for the next phase. The key distinction is mechanism, DSPy enforces struc-ture by optimizing prompts automatically; our system enforces it by explicitly telling the LLM why its output must take a particular form (e.g., that schema beliefs will be used as NLI queries, so they must be abstract and domain-agnostic). 

## 3. Architecture Overview 

The system is built around a plugin interface that sepa-rates the agent’s environment (terminal UI, tool execution, benchmark runner) from the agent backend (the BDI de-liberation loop). All agents implement the same interface:       

> in terf ace AgentPlugin {initialize ( env : Environment ) : Promise < void >; handle ( perception : Perception ) : AsyncGenerator < Action >; reset () : Promise < void >; }

This interface enables swappable agent implementations, clean benchmarking, and simulation (routing the same question to the same agent multiple times with an accu-mulating plan library). 

BDI State. The agent maintains: schemaBeliefs 

(abstract, for plan matching); groundBeliefs (con-crete key-value facts); desires (natural language goals); 

currentIntention (the typed commitment being pur-sued); planLibrary (accumulated plans with statistics); and intentionHistory (records used for plan review). 

LLM Providers The loop is backend-agnostic. Three providers are implemented: Anthropic (via SDK), Ollama (local), and vLLM. All expose:         

> in terf ace LLMProvider {complete ( messages : LLMMessage []) : Promise < string >; runAgentic ( messages , tools , executor , channel , signal ) : Promise < string >; }

complete is used for single-turn phases; runAgentic for step execution where the LLM drives its own inner tool-use loop. 

Plan Persistence and Seeding. The plan library is persisted to a plans.json file which can be loaded on initialization. Plans generated in one session survive across sessions and can seed a new agent run, enabling a cross-agent knowledge transfer approach. 

Run Modes: 

• Standard : one pass per query using an initially unpop-ulated plan library. • Simulation : multiple rounds per query; plan library accumulates across rounds. If query is answered incor-rectly an LLM is used as judge to refine executed plan for next round. • Seeded : standard mode but starting with a pre-populated plan library generated from another agent’s run which used either Standard or Simulation mode. 

## 4. The BDI Loop: Design and Rationale 

The deliberation loop consists of seven phases. Algorithm 1 presents the high-level structure; each phase is described below with design rationale, an example for the running Kipchoge question 1, and influence on adjacent phases. 

Algorithm 1: BDI Deliberation Loop 

Input : user message m, plan library L, max cycles C

beliefs , desire ← Perceive( m)

intention ← Formalize( desire , beliefs )

repeat 

plan ← SearchLibrary( intention , beliefs , L)

if plan = ∅ then plan ←

GeneratePlan( intention , beliefs )

foreach step ∈ TopoSort( plan .dag ) do 

result ← Execute( step , Snapshot( beliefs )) 

ok ← Verify( step .postcondition , result , beliefs )

if not ok then log failure; break to replan 

beliefs ← Merge( beliefs , result .newBeliefs )

sat ← CheckSat( intention , beliefs )

if sat then emit answer; break until C cycles exceeded 

every N intentions: Review( L, intention_history )

4.1. Phase 1: Perceive - Belief and Desire Extrac-tion 

The LLM receives the raw user message and produces three outputs simultaneously: 

> 1“If Eliud Kipchoge could maintain his record-making marathon pace indefinitely, how many thousand hours would it take him to run the distance between the Earth and the Moon at its closest approach?”

3A Self-Aware BDI Agent for LLM-Driven Reasoning Lawton, 2026 

1. Schema beliefs: abstract, structural facts about the 

type of problem. No concrete values or domain-specific names. Examples: “task requires computing a ratio” ,

“task requires retrieving a value from a specified external source” .2. Ground beliefs: concrete key-value pairs ex-tracted from the message. Names are role-based and domain-agnostic: numerator not distance_km ;

target_entity not moon .3. Desire: a natural language statement of the goal that becomes the input to Phase 2. 

Example output for the Kipchoge question:                                               

> schemaBeliefs : -" task requires computing aratio " -" task requires retrieving avalue from aspecified external source " -" task requires rounding to nearest 1000" groundBeliefs : -name : target_entity value : earth_moon_distance unit : km source : user -name : target_entity value : e liud_ki pchoge _speed unit : km / h source : user -name : rounding_unit value : "1000" unit : hours source : user desire : " calculate the time required to run the Earth - Moon distance at Kipchoge ’ s pace "

Why abstract schema beliefs? A question about how long Kipchoge takes to run to the Moon and a question about how many days a snail takes to cross the Sahara share the same abstract structure: retrieve two values, compute a ratio, round the result. If schema beliefs are query-specific, they cannot match across task instances. If abstract, a plan built for the Kipchoge question can match the snail question at library search time. Abstraction is the mechanism by which plans generalize. Schema beliefs are the NLI query for plan library search in Phase 3. 

Why role-based ground belief names? Plans are parameterized, a plan’s step can reference beliefs by name to use the value of an existing belief or to create a new belief as the output from said step. For example, a step can state “fetch the value of numerator ” rather than “fetch Kipchoge’s marathon pace.” Role-based names make the plan library reusable; concrete names make it question-specific. Ground beliefs populate plan parameter slots in Phase 4. 

4.2. Phase 2: Formalize - Intention creation and satisfiability conditions 

The desire and schema beliefs are converted into a typed 

Intention :        

> type : " c o m p u t e _ r a t i o _ r e t r i e v a l _ r o u n d i n g " goal : " calculate the time required ..." sa ti sfa cti on Con di tio n : " ground_belief ( final_answer ) is known " openParameters : [ earth_moon_distance , kipchoge_pace , rounded_result ]

Here type is a string filter when selecting plans, each plan will contain an intentionType which must match type .If a plan does not exist with the generated type , a new plan will be created with the provided intentionType .This matching accompanies the matching of Schema be-liefs to context conditions which is further described in Phase 3. goal is the promoted desire from the from previous phase which describes the intention in natural language. satisfactionCondition defines the success criteria of the intention once executed. The satisfaction condition determines which verification tier is invoked in Phase 6. openParameters declares upfront what ground beliefs the plan needs to populate before the synthesize step is reached in the plan. 

Why a machine-checkable satisfaction condition? 

If the agent expresses “done” as natural language, decid-ing whether the task is complete requires an LLM judg-ment call which is expensive and hallucination-prone. The predicate ground_belief(X) is known is a determinis-tic check: is X a ground belief? This costs zero tokens and cannot be hallucinated. The formalization prompt presents the three-tier verification hierarchy and asks the LLM to prefer Tier 1-checkable forms. This is the first instance of architectural self-awareness, the LLM produces output shaped by knowledge of how it will be consumed. 

4.3. Phase 3: Deliberate - Plan Search and Gen-eration 

3a: Plan Library Search 

Plan matching is completed via a single prompt to the LLM. The prompt includes the generated intention, schema beliefs, ground belief names, and entire plan li-brary. The prompt requests the LLM to match the plan based off matching plan intention type to the provided intention, the plan’s context conditions to the schema beliefs, and the plan’s parameters to the ground beliefs. A match increments the plan’s useCount , feeding the review phase’s statistics. 

3b: Plan Generation 

When no match exists, the LLM generates a new plan. This stands in direct contrast to NatBDI, where plans must be authored by a developer before deployment. Here the LLM generates top-level meta information about that plan that is used for BDI state matching and a parame-terized DAG at runtime. Each step in the DAG references abstract parameter slots rather than concrete values, so the same plan template applies to any question of the same structural type. For example, a full plan follows: 4A Self-Aware BDI Agent for LLM-Driven Reasoning Lawton, 2026                                                                  

> id : " plan -1776450034091 -3 vor7s " intentionType : " c o m p u t e _ r a t i o _ r e t r i e v a l _ r o u n d i n g " contextConditions : " task requires computing aratio " " task requires retrieving avalue from aspecified external source " " task requires rounding to nearest 1000" Steps S1 [ fetch , deps ={}] " Retrieve Kipchoge marathon pace in km / h " post : ground_belief ( denominator ) is known S2 [ fetch , deps ={}] " Retrieve Earth - Moon min perigee ( Wikipedia ) " post : ground_belief ( numerator ) is known S3 [ compute , deps ={ S1 , S2 }] " Compute time : numerator /denominator " post : ground_belief ( raw_result ) is known S4 [ compute , deps ={ S3 }] " Round raw_result to nearest 1000 hours " post : ground_belief ( rounded_result ) is known S5 [ synthesize , deps ={ S4 }] " Emit FINAL ANSWER : < rounded_result >" post : ground_belief ( final_answer ) is known

S1 and S2 have no dependencies and execute in parallel; S3 waits for both. The DAG structure makes dependencies explicit and enables concurrent execution. Each step re-quires a post condition to be generated so the system can verify the work done during DAG execution. Currently, plan generation prefers the simpler Tier 1 verification method for a given step, but all tiers are available for step verification. Plan generation is another instance of architectural self-awareness as the plan must be generaliz-able, matchable to the current BDI state, and processable by downstream verification mechanisms. Plan quality de-termines what beliefs get accumulated and whether the intention can be satisfied. A bad plan (e.g., in this case fetching speed of light instead of marathon pace) propa-gates failure through the system. 

4.4. Phase 4: Execute - Running the DAG 

All steps with satisfied dependencies are dispatched con-currently. Each step receives: schema beliefs, a snapshot 

of the ground beliefs at dispatch time (preventing race conditions between parallel steps), the current intention, and the step’s description and postcondition. The LLM drives its own inner agentic loop with three tools: web_search (DuckDuckGo/Brave snippets), bash 

(shell arithmetic and data manipulation), and read_file 

(local files, PDFs, spreadsheets). The loop runs until the LLM signals completion or a turn limit is reached. An example output for S1 above follows:              

> postconditionMet : true newGroundBeliefs : -name : denominator value : "20.9" unit : km / h source : web_search summary : " Retrieved Kipchoge world record pace of 20.9 km / h "

New beliefs are merged into the ground belief store (upsert by name); subsequent steps see the updated store. These accumulated beliefs are the inputs to Phases 5 and 6 with a final_answer belief triggering Phase 6. 

4.5. Phase 5: Verify - Independent Postcondition Checking 

After each step, the harness independently verifies the step’s postcondition. It does not trust the step’s self-reported postconditionMet flag. Verification proceeds through three tiers, stopping at the first applicable: 

Tier 1 - Pattern matching Regex matching against known patterns: ground_belief(X) is known checks whether belief X exists in the store. Approximately 90% of postconditions match Tier 1 because the plan generation and formalization prompts explicitly elicit this form. 

Tier 2 - Symbolic reasoning via tau-prolog The LLM translates the postcondition and ground beliefs into a Prolog [15] program (facts, rules, query). A fresh tau-prolog session evaluates the query. 

Tier 3 - LLM fallback For qualitative or semantic predicates that neither pattern-match nor translate to Prolog, we prompt an LLM that takes in the existing BDI state and the postcondition and ask it to return True or False depending on if the condition is satisfied. A failed verification logs the failure mode such as 

bad_retrieval , incorrect_computation , etc., and trig-gers a replan attempt starting back at the top of Phase 3 with the partially-populated belief store. 

4.6. Phase 6: Satisfy - Goal Satisfaction Check 

After all DAG steps complete, the harness applies the same three-tier system to the intention-level 

satisfactionCondition . If any step output contains 

FINAL ANSWER: <value> , the harness extracts the value and exits the loop. If the condition is not met and maxCycles has not been exceeded, control returns to Phase 3 with the richer, partially-populated belief store. The agent replans with more information than it started with. 

4.7. Phase 7: Review - Plan Refinement 

Every N completed intentions (configurable; default N =3), the agent reviews its plan library. The LLM receives the N recent IntentionRecord objects which contain informa-tion that happened during the previous deliberation loops: what happened, which beliefs were accumulated, whether the intention was satisfied, which plan was used, and the current plan library with useCount , successCount ,

failureCount per plan. The LLM outputs per-plan decisions: keep , refine (up-date context conditions, step descriptions, or parameters), or remove . Refined plans are persisted to a configurable 

plans.json file and survive across sessions. 5A Self-Aware BDI Agent for LLM-Driven Reasoning Lawton, 2026 

Like Reflexion, the agent learns from failure without gra-dient descent. But the mechanism differs in a way that en-ables contribution 3: rather than maintaining a bounded, unstructured episodic memory within a single agent’s life-time, our review phase maintains a structured, persistent, transferable plan library . This library can be exported and used to initialize an entirely new agent instance so that experience accumulated in one run directly benefits future independent runs. 

Long-horizon influence. Plans that succeed frequently are retained and refined; failing plans are removed. Over sessions, the library converges toward plans that reliably handle the task distribution. The seeding mechanism is what makes this accumulated knowledge portable: struc-tured parameterized plans (contribution 2) are the unit of transfer, and architectural self-awareness (contribution 1) is what makes them reliably executable when reused. 

4.8. Cross-Phase Influences 

Table 1 summarizes the I/O for each phase. Three feed-back loops influence behavior: 1. Verify → Replan : failed step verification returns control to Phase 3 with a richer belief store. 2. Satisfy → Loop control : an unsatisfied intention re-enters Phase 3 up to maxCycles times. 3. Review → Plan Library : long-horizon refinement; plans from one run seed the next. Table 1: I/O of BDI loop phases               

> Phase Reads from Writes to
> Perceive user message schema/ground beliefs, desires Formalize desire, schemaBeliefs currentIntention Deliberate beliefs, intention, plan lib currentPlans Execute beliefs, intention groundBeliefs (new) Verify postcondition, beliefs step pass/fail Satisfy satisfactionCond loop control Review intentionHistory, plan lib planLibrary, plans.json

## 5. Self-Awareness as a Design Principle 

Architectural self-awareness refers to a design principle applied across several phases in the BDI loop. These phases are structured so that the LLM receives explicit information about how and why its output will be con-sumed downstream, and produces a response shaped by that knowledge. This section focuses on contribution 1, but the t