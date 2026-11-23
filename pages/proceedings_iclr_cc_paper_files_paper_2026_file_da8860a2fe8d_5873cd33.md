<!-- source: https://proceedings.iclr.cc/paper_files/paper/2026/file/da8860a2fe8ddb7589136853bcc313fc-Paper-Conference.pdf -->

Title: da8860a2fe8ddb7589136853bcc313fc-Paper-Conference.pdf

URL Source: https://proceedings.iclr.cc/paper_files/paper/2026/file/da8860a2fe8ddb7589136853bcc313fc-Paper-Conference.pdf

Number of Pages: 31

Markdown Content:
Published as a conference paper at ICLR 2026 

# TOWARDS SELF -E VOLVING AGENT BENCHMARKS :VALIDATABLE AGENT TRAJECTORY VIA TEST -T IME 

# EXPLORATION 

Dadi Guo 1,2∗, Tianyi Zhou 1,3∗, Dongrui Liu 1∗, Chen Qian 4, Qihan Ren 5, Shuai Shao 5,Zhiyuan Fan 2, Yi R. Fung 2, Kun Wang 6, Linfeng Zhang 5, Jing Shao 1†

> 1

Shanghai Artificial Intelligence Laboratory 2Hong Kong University of Science and Technology 

> 3

University of Michigan 4Renmin University of China 5Shanghai Jiao Tong University 

> 6

Nanyang Technological University  

> dguoae@connect.ust.hk zhtianyi@umich.edu {liudongrui,shaojing}@pjlab.org.cn

## ABSTRACT 

Recent advances in large language models (LLMs) and agent system designs have empowered agents with unprecedented levels of capability. However, existing agent benchmarks are showing a trend of rapid ceiling-hitting by newly developed agents, making it increasingly difficult to meet the demands of evaluating agent abilities. To address this problem, we propose the Trajectory-based Validated-by-Reproducing Agent-benchmark Complexity Evolution ( TRACE ) framework. This framework takes an original task from an existing benchmark and encour-ages agents to freely explore and evolve it into a new task with higher difficulty while recording the corresponding execution trajectories. The framework pro-ceeds in three stages: (1) evolutionary proposal mining , which generates task evolution proposals through preliminary exploration and divergent thinking; (2) 

problem construction via free exploration , where proposals are instantiated into concrete problem instances through agent exploration, with execution trajecto-ries recorded along the process; and (3) multi-level validation , which ensures that the evolved tasks are accompanied by reproducible and logically coherent tra-jectories. Experiments on the GAIA benchmark demonstrate that the TRACE 

framework consistently enhances task complexity while improving correctness reliability through trajectory-level validation. In addition, our framework can suc-cessfully adapt to and improve reasoning benchmarks such as AIME-2024. This work marks a paradigm shift from static, manually curated benchmarks to dy-namic, self-evolving evaluation systems, providing a sustainable and challeng-ing foundation for agent development. Code and data can be found at https: //github.com/titanwings/trace-benchmark-evolving .

## 1 INTRODUCTION 

The paradigm of artificial intelligence is rapidly shifting towards autonomous agents capable of complex reasoning (Comanici et al., 2025; Huang & Yang, 2025), planning (Huang et al., 2024), and tool utilization (Qu et al., 2025; Wang et al., 2024a). This progress is starkly evident in the performance on challenging agent benchmarks (Mialon et al., 2023; Jimenez et al., 2023), which were once considered formidable. For instance, on the GAIA benchmark which is designed to test real-world assistant capabilities, top-performing agents have achieved scores exceeding 90% (GAIA Benchmark Team, 2025), rapidly closing the gap with the human baseline. This rapid pace signals an urgent challenge: existing benchmarks are becoming saturated, diminishing their ability to differ- 

> ∗Equal contribution. Work done during an internship at Shanghai Artificial Intelligence Laboratory, supervised by Dongrui Liu
> †Corresponding author

1Published as a conference paper at ICLR 2026 0.0 0.1 0.2 0.3 0.4 0.5 0.6                     

> Pass@1
> L1 L2 L3 Total L1 L2 L3 Total L1 L2 L3 Total L1 L2 L3 Total
> Deepseek-v3.1 Gemini-2.5-flash KIMI-K2 GPT-5-Mini
> Pass@1 Score Across Different Levels and Rounds
> Original Round 1 Round 2

Figure 1: Model performance comparison on the Pass@1 metric across four distinct difficulty levels and evolution rounds under the TRACE framework. As the number of evolution rounds increases, the performance of models shows a downward trend, demonstrating that our framework successfully evolves more challenging tasks. entiate state-of-the-art agents and risking progress being driven by overfitting to static test sets rather than generalizable intelligence. However, the cost of manually creating novel, complex, and reliable tasks is a labor-intensive, time-consuming, and expensive process, which highlights an urgent need for an automated and scalable approach to agent benchmark evolution. However, evolving agent tasks presents unique challenges not found in conventional domains like mathematical reasoning (Hendrycks et al., 2021; Guo et al., 2025) or knowledge-based question an-swering (Yang et al., 2018). Agent tasks are defined by two key characteristics: (1) their procedural nature, which emphasizes complex, multi-step interactions with dynamic, scalable real-world envi-ronments (e.g., websites, APIs) (Huang et al., 2025; Liu et al., 2025a; Gao et al., 2025a), and (2) their immense diversity, spanning from web navigation to software operation. These characteristics render traditional task evolution methods, such as rule-based parameter mutation or scaling largely ineffective. For instance, rule-based changes (Wu & Liu, 2025; Wang et al., 2024b) (e.g., altering a specific keyword in a search query) are often insufficiently robust. In a dynamic web environment, such a minor change could break the task’s solvability entirely rather than increasing its reasoning complexity. Similarly, merely scaling up a task (Liu et al., 2025b) (e.g., asking to book three flights instead of one) often increases repetition, rather than the core cognitive or planning challenges. Thus, a new paradigm is required that moves beyond superficial modifications to fundamentally enhance the procedural, logical and semantic complexity of agent tasks. To bridge this gap, we introduce TRACE (Trajectory-based Validated-by-Reproducing Agent-benchmark Complexity Evolution). Departing from rigid, rule-based heuristics, TRACE leverages the agentic capabilities of LLMs to drive task evolution through three specialized components. The 

Evolutionary Proposer identifies diverse evolution directions via preliminary exploration; the Ex-ploration Executor navigates real-world environments to materialize these proposals into recorded execution trajectories; and the Trajectory Validator enforces logical coherence and reproducibility. This ensures that evolved tasks are grounded in verifiable solution paths rather than relying solely on final-answer correctness. The coordination between these agents enables a structured workflow for task evolution. This pro-cess begins with the Evolutionary Proposer , which analyzes task bottlenecks and explores its se-mantic space to identify evolutionary forks. Consider the question: “What is the name of Taylor Swift’s debut album?” Rather than stopping at the direct answer, it examines related artifacts, such as the music video for the single Teardrops on My Guitar , and generates multiple evolution pro-posals. These proposals introduce additional reasoning dependencies, such as linking the video’s actor to their filmography or tracing their cross-domain career trajectory. Subsequently, the Explo-ration Executor materializes these proposals through proposal-guided trajectory construction . It traverses the original solution path and integrates compatible proposals at appropriate intermediate states. For example, it may first inject a proposal to identify the actor in the video ( Tyler Hilton ) and the TV series he starred in ( One Tree Hill ), then introduce a second proposal that pivots to his music career. This process transforms a single-hop lookup into a multi-step reasoning task with cross-domain dependencies, culminating in a more complex final question (Trinh et al., 2024; Fang et al., 2Published as a conference paper at ICLR 2026 2025; Sun et al., 2024; Gao et al., 2025b), such as: “The male lead in the music video for a song from Taylor Swift’s debut album is a multi-talented individual who also starred in a long-running TV series that premiered in 2003. What is the title of this individual’s own debut studio album?” More broadly, this bottleneck-aware proposal and injection process extends beyond information-seeking tasks to reasoning-intensive, mathematical, and coding problems, demonstrating the generality of the workflow. Importantly, each exploration step is recorded as an execution trajectory that serves as the basis for validation, ensuring that the introduced complexity remains transparent and verifiable. This architecture balances flexibility and rigor in task evolution. Flexibility arises from the separa-tion of the Evolutionary Proposer and the Exploration Executor , enabling evolution along multiple dimensions, such as deeper tool integration, increased logical dependency, or combinatorial compo-sition, without reliance on hard-coded templates. To maintain rigor, the Executor outputs the evolved task together with its execution trajectory, including reasoning steps, tool invocations, and observed results. The Trajectory Validator then audits logical coherence and re-executes each step to confirm reproducibility. This validation loop ensures that generated benchmarks are complex, solvable, and grounded in executable evidence. In essence, TRACE models the workflow of a human benchmark designer while replacing manual curation with an autonomous evolution process. Unlike static rule-based approaches, it enables agents to explore real-world environments ( e.g. , the live internet) as structured task substrates. This exploration is guided by bottleneck analysis: by diagnosing limitations of a seed task such as shallow tool usage or limited reasoning depth, the framework steers evolution toward targeted structural augmentation. As a result, TRACE evolves tasks into tool-integrated, multi-step challenges that better reflect real-world problem-solving dynamics, repositioning the agent from a passive solver to an active benchmark constructor. Our contributions are threefold: • We propose TRACE (Trajectory-based Validated-by-Reproducing Agent-benchmark 

Complexity Evolution), a benchmark self-evolving framework that encourages agent ex-ploration and records execution trajectories as first-class artifacts, ensuring transparency and reproducibility in task evolution. • We empirically validate TRACE on general-purpose agent benchmarks such as GAIA as well as reasoning benchmarks such as AIME-2024, demonstrating that it consistently produces tasks of higher difficulty, on which prominent agent systems exhibit significant performance degradation shown in Figure 1, thereby validating the effectiveness of our approach. • Beyond “one-more-hop” edits, our experiments reveal a From Seed to Spark pattern: under our TRACE framework, the model autonomously explores and evolves problems that can shift into entirely different capability domains ( e.g. , from retrieval to math and coding), thereby substantially increasing the diversity of evolved tasks. The evolved tasks exhibit greater task diversity and require deeper reasoning depth , providing a robust methodology for rigorously evaluating and advancing future agents. 

## 2 RELATED WORK 

Agent Benchmark A range of agent benchmarks have been proposed to evaluate LLM-based agents under realistic problem-solving settings. GAIA (Mialon et al., 2023) focuses on human-centric questions that require reasoning, multimodal understanding, web browsing, and tool use. USACO (Shi et al., 2024) adapts competitive programming problems with unit tests and reference solutions to assess algorithmic reasoning. MLE-bench (Chan et al., 2024) evaluates end-to-end ML engineering by grounding tasks in Kaggle-style competitions spanning data preparation, model training, and experiment management. SWE-bench (Jimenez et al., 2023) measures software engi-neering ability through real GitHub issues that require generating patches under authentic repository contexts. Beyond answer-verified benchmarks, several works emphasize process-level evaluation by analyz-ing agent trajectories. WebArena (Zhou et al., 2023) provides self-hosted websites with executable scoring and trajectory replay for reproducible step- and task-level analyses. Mind2Web (Deng et al., 2023) contributes human demonstrations on real websites with fine-grained metrics (e.g., element 3Published as a conference paper at ICLR 2026 accuracy and step success), and its multimodal extension (Pahuja et al., 2025) augments trajectories with multimodal signals and step-wise evaluation. Despite their breadth, these benchmarks are largely static : tasks and environments are pre-defined and updated infrequently. As agent capability improves, static benchmarks can saturate and be-come costly to refresh at a cadence aligned with model iteration, motivating scalable approaches to benchmark evolution. 

Benchmark Evolving Benchmark evolution has been explored to mitigate saturation of static datasets. Benchmark Self-Evolving (Wang et al., 2024b) and AutoEvoEval (Wu & Liu, 2025) apply predefined atomic operations to reformulate reasoning and close-ended QA tasks via struc-tural or semantic perturbations, primarily targeting robustness rather than increasing procedural task complexity. AdamMeme (Chen et al., 2025b) adopts multi-agent refinement to iteratively up-date meme datasets for probing harmfulness-related reasoning, but is specialized to this domain. EvoCodeBench (Li et al., 2024) updates code benchmarks by periodically ingesting new reposito-ries to reduce leakage, relying on curated data streams and fixed schedules rather than model-driven exploration. In contrast, TRACE evolves agent tasks via test-time exploration in real-world environments. In-stead of predefined edits or scheduled refreshes, agents autonomously construct harder tasks and output their execution trajectories, which are subsequently validated for logical coherence and repro-ducibility. This trajectory-aware evolution supports scalable benchmark updating while preserving solvability and verifiability. 

## 3 PRELIMINARY 

3.1 AGENTIC WORKFLOW AS A DAG In this section, we represent an agentic workflow W as a directed acyclic graph (DAG) G = ( S, E),where the node set S = {S1, S 2, . . . , S N } corresponds to an ordered sequence of discrete LLM-invoking steps, and the edge set E ⊆ S × S encodes data dependencies and control-flow constraints. Specifically, an edge (Si, S j ) ∈ E signifies that the output of step Si is required as input for step Sj .Each node can be abstracted as the quadruple below: 

Si =  ci−1, r i, a i, o i

,

where • Context ci−1: the interaction history up to step i−1 (previous actions and observations together with fixed task/context). • Reasoning in test-time ri: the agent’s latent reasoning state at step i (internal scratchpad/-planning variables and intermediate choices that are not executed by the environment). • Action ai: the external action/message emitted at step i conditioned on ci−1 and ri (e.g., a tool/API call with arguments, code to run, a retrieval query, or a user-visible response), which is the only component actually executed outside the agent. This state-transit process could be modeled as p(ai | ci−1, r i) = πa

 ai | ci−1, r i

.• Observation oi: the feedback returned by the environment after executing ai (e.g., tool outputs, retrieved documents, execution logs, state deltas, optionally a numeric score). After execution, the context is updated as ci = ci−1 ⊕(ai, o i), and edges (Si, S j ) arise when artifacts from Si, typically oi or the updated context ci, are consumed by Sj ; tool-free steps are a special case where ai is a user-facing message and oi may be empty. 3.2 EXPLORATION TRAJECTORIES FOR BENCHMARK EVOLUTION 

Given the DAG formulation of an agentic workflow, we next define how exploration trajectories 

serve as the foundation for benchmark evolution. An execution trajectory τ is a path through the workflow DAG, 

τ = S1, S 2, . . . , S T ,

4Published as a conference paper at ICLR 2026 where each Si is realized by the tuple (ci−1, r i, a i, o i). Unlike static benchmarks that only verify the final output oT , we treat the entire trajectory τ as a first-class artifact: it captures the agent’s reasoning, tool-use decisions, and environment feedback across all intermediate steps. Formally, we denote the trajectory distribution under an agent policy π as 

pπ (τ ) = 

> T

Y

> i=1

πa(ai | ci−1, r i) p(oi | ai, c i−1),

where πa governs the action selection and the environment dynamics determine p(oi | ai, c i−1).

Trajectory as Evolutionary Material. Benchmark evolution proceeds by exploring alternative trajectories τ ′ that diverge from the original trajectory τ . A proposal identifies a modification point 

Sk and suggests a new branch (e.g., adding a constraint, substituting a tool, transferring to another capability domain). The exploration process then unfolds as the agent executes along this modified branch, yielding an evolved trajectory τ ′. The final benchmark task is reconstructed from τ ′, and its complexity grows with the depth, diversity, and interdependence of such exploratory branches. 3.3 PROBLEM STATEMENT 

We now formalize the benchmark evolution problem. Given a seed benchmark B0 = {(q, τ ) | q ∈Q0} comprising tasks paired with their original trajectories τ , the objective is to construct an evolved benchmark B such that 

Difficulty( B′) > Difficulty( B0), and ∀(q′, τ ′) ∈ B ′ : τ ′ ∈ T validatable .

Here, Tvalidatable denotes the set of trajectories satisfying the validity conditions defined above. In practice, we operationalize Difficulty( ·) via a trajectory-informed bottleneck assessment inspired by theory-of-mind (Chen et al., 2025a): given the solution trajectories of the seed and evolved tasks, the difficulty judge estimates which task would impose a larger intrinsic bottleneck for a solver with comparable planning, reasoning, and tool-use capabilities (including access to a similar tool set), potentially requiring additional attempts or a non-trivial conceptual insight to resolve. The TRACE framework addresses this objective through a three-stage pipeline: proposal mining, proposal-guided exploration, and multi-level validation. 

## 4 THE DESIGN DETAIL OF TRACE 

TRACE is a multi-agent framework that not only generates tasks but also encourages free explo-ration and records a complete, validatable trajectory . The system comprises complementary roles that collaborate end-to-end: Evolution Proposer suggests evolutions from a seed task; Exploration Executor does not solve a problem but defines one by turning a proposal into an actionable explo-ration setup and conducting test-time exploration to produce an execution trajectory; and Trajectory Validator verifies and replays the trace to ensure determinism, safety, and correctness. Crucially, the product of evolution is not the problem alone , but the pair (evolved problem , validatable trajectory ).This pairing both grants the model an automatic route to discover harder variants and preserves an auditable record of its own decision process, enabling reproducible, process-aware evaluation. For the core concept of this section, we provide an example explanation in Figure 2. 4.1 STAGE 1: E VOLUTIONARY PROPOSAL MINING 

The Evolution Proposer takes the description of an original task from an existing dataset, optionally along with potential solution paths and answers, as input. Rather than directly generating modifi-cations, it first performs a bottleneck-aware pre-exploration stage . In this stage, the agent analyzes the original task and its solution trajectory to identify which agent capabilities the task primarily evaluates ( e.g. , planning, reasoning, or tool use) and where a solver is most likely to encounter in-trinsic difficulty. Based on this bottleneck analysis, the agent then probes the task’s semantic space to uncover dimensions that can be further strengthened such as extending evidence chains, increas-ing tool interaction complexity, or deepening reasoning requirements, thereby formulating targeted evolution proposals. 5Published as a conference paper at ICLR 2026 Original Task:  

> ---------------------------------------------------
> What was the volume in m^3 of the
> fish bag that was calculated in the
> University of Leicester paper "Can
> Hiccup Supply Enough Fish to
> Maintain a Dragon 2019 ’s Diet?

Solution Steps:   

> ---------------------------------------------------
> 1. Searched '"Can Hiccup Supply
> Enough Fish to Maintain a Dragon’s
> Diet?"' on Google.
> 2. Open paper at
> https:// journals.le.ac.uk /ojs1/ index.p
> hp /jist /article/view/733.
> 3. Clicked "PDF".
> 4. Found the calculations for the
> volume of the fish bag.

Answer :

> ---------------------------------------------------
> “0.1777 ”

Bottleneck Analysis: 

> ---------------------------------------------------------------
> The bottleneck of this task should be web
> search and document understanding. ..

Pre -E xploration :

> ---------------------------------------------------------------
> I should actually read this article to see if there
> is any detailed information in it that can be
> used. ..
> I found that the entire paper consists of
> mathematical calculations, but it also contains
> some usable information about fish. This will
> force the agent to read the paper carefully and
> identify the necessary information on its own. ..

Proposal s:

> ----------------------------------------------------------
> This idea attempts to transform the simple
> problem mentioned in the paper into a complex
> mathematical modeling problem. We might as
> well use the fish data in the paper to create a
> scenario...
> …

New Task Design :

> ----------------------------------------------------
> The proposal intends to create a new
> mathematical modeling task...I need to
> read the paper to get the weight of the
> fish...

Evolved Task : 

> ----------------------json -------------------
> {
> “new_task ”: What is the total
> weight in kilograms of fish...
> “solution_steps ”:
> [
> {
> “thought ”: search the paper...
> “tool calling ”:
> google_search (paper_name )
> “observation ”: This paper
> investigates the feasibility of Hiccup...
> }
> ...
> ]
> “answer ”:“770.0 ”
> }

Lightweight check :  

> -----------------------------------------------
> Answer format check passed. Not
> open -ended answer...
> Attached file check passed. No file
> needed in this task...

Reproducibility Check:  

> ----------------------------------------------
> Step 1 passed. Actual tool calling result
> is consistent with the observation.
> Step 2 passed...

Solvability & Logicality 

Check  

> ----------------------------------------------
> I have checked the entire process, and
> the whole logical chain is correct,
> which indicates that this problem is
> solvable ...
> What is the total weight in
> kilograms of fish that Hiccup can
> transport in a single operation,
> utilizing a full set of identical, open -
> topped cylindrical containers
> optimally designed and
> manufactured from a total of 5.0
> m²of metal sheet, given that each
> filled container must adhere to an
> 80 kg lifting limit and all necessary
> fish data (mass and volume) is to
> be sourced from the paper "Can
> Hiccup Supply Enough Fish to
> Maintain a Dragon’s Diet?"

Original Task  Evolution Proposer  Exploration  Executor  Trajectory Validator  Task Evolved 

Figure 2: TRACE evolution pipeline. Starting from a GAIA Original Task , the Evolution Proposer 

conducts bottleneck analysis and pre-exploration, drafting a concrete proposal to increase difficulty. Crucially, the Evolution Executor constructs the evolved problem from its own trajectory : as it runs ReAct (Thought →Action →Observation), it collects evidence (numbers, constraints, citations, etc.) and uses this trajectory to parameterize and scaffold the new task , while simultaneously pro-ducing a complete solution trace. A Multi-Level Validator then applies lightweight schema checks, dynamic replay for reproducibility, and solvability/logic audits to ensure trace validity. The result is an Evolved Task that preserves origina benchmark’s interface yet requires deeper reasoning (math + coding), achieving a systematic benchmark-level difficulty increase. Based on this preliminary diagnosis, the proposer then synthesizes multiple evolutionary proposals. It is prompted with a comprehensive set of evolutionary strategies that serve as directional guidance rather than rigid transformation rules. These strategies encourage the agent to lengthen evidence chains, complicate tool interactions, target specialized domains, or escalate reasoning demands, while preserving high degrees of creative freedom. To ensure that exploration remains principled rather than arbitrary, the proposer is governed by a set of core guiding principles. These principles grant the autonomy to think divergently and even pivoting to new but semantically grounded scenarios when appropriate, while enforcing that all proposed modifications must yield deterministic and validatable solutions. Ultimately, the proposer consolidates its reasoning into a diverse set of actionable evolutionary proposals, each formulated as a clear and imperative instruction for how the seed task should be transformed. 4.2 STAGE 2: E XPLORATION AND TRAJECTORY RECORDING 

The Exploration Executor operationalizes the proposer’s ideas by turning a high-level proposal into a feasible problem and by conducting test-time exploration that yields a validatable execution trace. Starting from the seed task, the Executor follows the current solution path and performs step-wise proposal injection : at an opportune step, it concretizes one evolutionary idea ( e.g. , adding a con-straint, substituting a tool, transferring to another capability domain), creating a controlled “fork in the road” that increases difficulty. The agent then explores along this branch with full tool access, producing a trajectory that records reasoning , action , and observation . This process serves a dual role: it provides the model with a validatable trace to discover harder variants of the seed problem and captures the model’s own execution path for subsequent auditing and analysis. Following the principle of inverse problem creation, the Executor’s primary creative act is not solving a problem, but defining one . With the new, complex solution trace in hand, its final task is to formulate a new problem description that fits this solution. Finally, the executor ensures the evolved task adheres to strict principles of authenticity, logical integrity, and solvability. It meticulously crafts the problem to guarantee the final answer is a single, deterministic, and validatable value, free from ambiguity, thereby producing a high-quality and challenging new task. 6Published as a conference paper at ICLR 2026 

Algorithm 1 TRACE Pseudo-code 

Require: Proposer P, Executor E, Validators V, Tools T , Seeds Q0, retries R

Ensure: Evolved set Q∗ = {(q′, τ ′)} 

> 1:

Q∗ ← ∅ ; C ← Q 0 

> 2:

while C̸ = ∅ do  

> 3:

q ← Select( C) 

> 4:

for r ← 1 to R do  

> 5:

∆ ← ProposeMining( P, q ) 

> 6:

τ ′ ← TaskEvolve( E, q, ∆, T ) ▷ test-time exploration yields trajectory  

> 7:

q′ ← QuestionFormulation( τ ′) ▷ define the problem post hoc from τ ′ 

> 8:

if Validate( V, q ′, τ ′) then  

> 9:

Q∗ ← { (q′, τ ′)} ∪ Q ∗; C ← C \ { q}; break  

> 10:

return Q∗

4.3 STAGE 3: M ULTI -L EVEL VALIDATION OF TRAJECTORIES 

The final stage of our framework is the Trajectory Validator , an autonomous agent that audits evolved tasks through multi-level validation. At the first level, it performs step-by-step replay to ensure reproducibility: for each step in the trajectory, the validator re-executes the tool call and ver-ifies that the resulting output aligns with the recorded observation. At the second level, it conducts a global trace audit to assess the overall logical coherence of the solution. Under the assumption that all intermediate observations are reproducible and the reasoning chain is internally consistent, the task is deemed solvable and well-posed. Beyond trace validation, the framework evaluates whether the evolved task reflects a genuine in-crease in difficulty, using the theory-of-mind–inspired bottleneck assessment described earlier. Ad-ditional integrity checks are also applied, including answer determinism (to ensure reliable eval-uation) and accessibility of referenced resources ( e.g. , URLs). Only tasks satisfying all criteria including reproducibility, logical validity, increased intrinsic difficulty, and evaluation integrity are accepted into the final dataset. To further guard against superficially modified but still easy items, we introduce a trajectory-agnostic solver as an auxiliary validator. This solver does not see the generation trajectory and operates purely under a ReAct (Yao et al., 2023) paradigm and enjoys tool-use parity with the main executor (same multi-modal access, web browsing, and coding). We run the solver under budgeted attempts; if it reliably solves the evolved task within resource limits, the item is flagged as insufficiently challenging and is rejected or sent back for re-evolution. Only tasks that resist this blind, tool-equipped solver proceed, providing an empirical difficulty floor independent of the authored trace. 4.4 TEST -T IME EXPLORATION 

Given the inherent stochasticity of large language model sampling and the open-ended nature of trajectory-level evolution, the generation of evolved tasks is not a single-shot procedure, but a struc-tured form of test-time exploration. Within each run, the model engages in multi-turn interactions with real tools and code execution in an open environment, wh