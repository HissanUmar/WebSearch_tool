<!-- source: https://wanghao.in/paper/ICML26_MASProVe.pdf -->

Title: MAS-ProVe: Understanding the Process Verification of Multi-Agent Systems

URL Source: https://wanghao.in/paper/ICML26_MASProVe.pdf

Published Time: Thu, 25 Jun 2026 04:14:08 GMT

Number of Pages: 32

Markdown Content:
# MAS-ProVe : Understanding the Process Verification of Multi-Agent Systems 

Vishal Venkataramani 1 Haizhou Shi * 1 2 Zixuan Ke † 2 Austin Xu 2 Xiaoxiao He 1 Yingbo Zhou 2

Semih Yavuz 2 Hao Wang ‡ 1 Shafiq Joty ‡ 2

## Abstract 

Multi-Agent Systems (MAS) built on Large Lan-guage Models (LLMs) often exhibit high variance in their reasoning trajectories. Process verifica-tion, which evaluates intermediate steps in trajec-tories, has shown promise in general reasoning settings, and has been suggested as a potential tool for guiding coordination of MAS; however, its ac-tual effectiveness in MAS remains unclear. To fill this gap, we present MAS-ProVe , a systematic empirical study of process verification for MAS. Our study spans three verification paradigms 

(LLM-as-a-Judge, reward models, and process reward models), evaluated across two levels of verification granularity (agent-level and iteration-level). We further examine five representative ver-ifiers and four context management strategies, and conduct experiments over six diverse MAS frame-works on multiple reasoning benchmarks. We find that process-level verification does not con-sistently improve performance and frequently ex-hibits high variance, highlighting the difficulty of reliably evaluating partial multi-agent trajectories. Among the methods studied, LLM-as-a-Judge generally outperforms reward-based approaches, with trained judges surpassing general-purpose LLMs. We further observe a small performance gap between LLMs acting as judges and as single agents, and identify a context-length-performance trade-off in verification. Overall, our results sug-gest that effective and robust process verifica-tion for MAS remains an open challenge, requir-ing further advances beyond current paradigms. Code is available at https://github.com/ Wang-ML-Lab/MAS-ProVe .       

> ∗Work done during an internship at Salesforce AI Re-search. †Project Lead. ‡Equal Advising. 1Rutgers University
> 2Salesforce AI Research. Correspondence to: Vishal Venkatara-mani <vishal.venkataramani@rutgers.edu>, Zixuan Ke <zix-uan.ke@salesforce.com>, Hao Wang <hw488@cs.rutgers.edu>, Shafiq Joty <sjoty@salesforce.com>.
> Proceedings of the 43 rd International Conference on Machine Learning , Seoul, South Korea. PMLR 306, 2026. Copyright 2026 by the author(s).

## 1. Introduction 

Recent advances in Large Language Models (LLMs) have enabled the solution of a wide range of tasks requiring care-ful high-level planning and scheduling (Ke et al., 2025a), complex logical and mathematical reasoning (Wang et al., 2025), and self-reflection for iterative outcome improve-ment (Shinn et al., 2023). As these intrinsic capabilities continue to mature, and as the scaling gains of single foun-dation models begin to plateau, there has been growing interest in constructing coordinated ensembles of LLMs that can collectively understand, decompose, execute, sum-marize, and reflect on complex tasks (Kim et al., 2025). This emerging paradigm of Multi-Agent Systems (MAS) offers several advantages over Single-Agent Systems (SAS), including reduced context interference and improved paral-lelism (LangChain, 2025; Ke et al., 2026). Any potential benefits of MAS are accompanied by in-creased complexity, increasing the number of potential failure points: final outcome correctness in MAS now de-pends inherently on the intermediate outputs of a variety of coordinated sub-agents. To weed out mistakes before they influence downstream correctness, many MAS frame-works (Shinn et al., 2023; Du et al., 2024; Liang et al., 2023) explicitly incorporate automatic verification sub-agents to check or refine intermediate outputs, while others work incorporate verifiers for further do test-time scaling of MAS (Brown et al., 2024; Jin et al., 2025). Despite the explicit inclusion of verification modules, subpar evaluation remains a bottleneck in the efficacy of MAS (Cemri et al., 2025). This work attempts to understand the fundamen-tal role of automatic evaluation in MAS by systematically studying evaluators, MAS frameworks, and domains, guided by a central research question: 

Do multi-agent systems actually benefit from automatic process-level verification? 

In this paper, we address this question along four comple-mentary dimensions: (i) verification type ( generative versus 

scoring-based ), (ii) verification granularity in MAS (verify-ing each agentic call versus each full iteration ), (iii) context management strategies, and (iv) solvability. Our empirical study spans six representative MAS frameworks, two rea-1MAS-ProVe : Process Verification of Multi-Agent Systems 

soning domains (mathematical problem solving and agentic search), and five distinct evaluators, enabling a systematic and controlled examination of when, how, and to what ex-tent process-level verification benefits multi-agent systems. Through this analysis, we identify both consistent patterns and high-variance behaviors across settings, clarifying the practical limits and trade-offs of applying process verifica-tion to MAS. To facilitate reproducible research and establish a stan-dardized testbed for the community, we introduce a uni-versally applicable protocol, MAS -Pro cess Ve rification (MAS-ProVe ), for integrating process-level verification into MAS test-time scaling, as demonstrated in Fig. 1. 

MAS-ProVe is modular and extensible, operating as a plug-and-play wrapper for any off-the-shelf MAS framework and 

any verification method, and requiring only minimal code modifications. 

Main Observations. We present the first systematic study of the strengths and limitations of process verification in MAS, spanning multiple dimensions including verification types, granularity, context management, and problem solv-ability. • Verification type : Process verification in MAS does not consistently yield performance improvements across verification types and often exhibits high variance, with judge-based verifiers dominating the reward-based ver-ifiers. This highlights the intrinsic difficulty of reliably evaluating partial multi-agent trajectories. • Verification Granularity : While no single verification granularity universally dominates across MAS frame-works, individual MAS often exhibit a clear preference between agent-level and iteration-level verification. • Context Management Strategies : Comparable per-formance between only step responses vs context + step(raw) responses, with summarization of responses leading the performance gains in long-context MAS. • Solvability : A question-wise analysis on mathematical reasoning benchmarks shows that the process verifi-cation with optimized settings can improve stability, but rarely recovers instances that are fundamentally unsolvable by MAS. 

## 2. Background 

In this section, we establish the formal framework that gov-erns our experimental design. Rather than focusing on spe-cific models or datasets, we define the general abstractions for the two core components of our study: the taxonomy of Multi-Agent Systems (Sec. 2.1) and the classes of Auto-matic Verification (Sec. 2.2). Finally, in Sec. 2.3, we unify these components to define the specific design space of our analysis—granularity, context, and search strategy, which serves as the theoretical basis for the concrete instantiations detailed in the experimental setup. 

2.1. MAS Overview 

A Multi-Agent System (MAS) consists of multiple LLM-based agents, each equipped with its own context and (sub-)goals, coordinated as a system to perform a given task. We denote the resulting system-level behavior to an input query a reasoning trajectory , where the output of each sub-agent can be considered a “step” towards the final output. While a general concept, a variety of recent works (Liu et al., 2024; Chen et al., 2024; Zhang et al., 2025b) have proposed differ-ent instantiations of MAS. Broadly, we consider two classes of MAS: (i) fixed architecture systems, where the topol-ogy of agents and communication edges remains fixed for all problems, and (ii) adaptive architecture systems, where the MAS topology may change based on a per-query basis. MAS belonging to the former may either be human designed MAS topologies (e.g., LLM-debate) or instantiated by it-eratively searching for the best MAS structure on a small validation set (i.e., “training”). In the latter, MAS tend to self-evolve over multiple iterations at test-time, typically us-ing self-reflection to update agent roles and communication edges. 

2.2. Automatic Verification 

To meet demands for scalable verification, automatic veri-fiers have been deployed to provide feedback signals about output and intermediate state correctness in reasoning set-tings (Snell et al., 2025; Zhou et al., 2025b; Shao et al., 2025). There are three primary classes of verifiers: (i) 

reward model (RMs) , which produce a continuous score for an input and terminal output state, (ii) process reward models (PRMs) , which produce continuous scores for in-termediate states, measuring likelihood of reaching a cor-rect outcome from a given state, and (iii) generative veri-fiers (LLM-as-a-Judge) , which outputs feedback and evalua-tion in natural language. For LLM-as-a-Judge baselines, we analyze both general purpose LLMs as judges and special-ized, state-of-the-art finetuned verifier models. 

2.3. Marrying MAS and Verification 

Integrating verification into MAS settings gives rise to a search-based optimization problem that we seek to analyze, i.e., yielding multiple execution/trajectories in parallel and then letting the verifier to pick the most promising candidate. We choose three crucial facets for analysis: 

Verification Types. To broadly cover the dominant classes of automatic verifiers used in prior work, MAS-ProVe in-cludes all three verifier types in our analysis. To the best of our knowledge, existing verifiers are not explicitly trained on 2MAS-ProVe : Process Verification of Multi-Agent Systems MAS Workflow Multi-Agent Systems  (MAS)    

> AFlow Graph-Based MAS
> - Generate Node
> - Program Node
> - Review Node
> Iteration-Based MAS
> …
> Code-Based MAS
> cot_reasoning()
> web_search()
> self_refine()
> MaAS
> …
> ADAS
> MAS-Zero
> …
> Debate
> DyLAN
> …
> Iter+1
> Unfold
> MAS Process Verification Framework (MAS-ProVe)
> Agent -Level  Search Iteration -Level  Search
> Context Management Tools
> Raw Context
> No Context
> Summarizing Context
> …
> Summarizing Context & Step
> Context …
> Candidates
> Process Verification
> Context
> Context
> Context
> Process Verifier
> Return to Workflow
> Best
> Candidate

Figure 1. Overview of Multi-Agent System Process Verification Framework ( MAS-ProVe ). The execution of any multi-agent system (MAS) can be abstracted into a unified workflow, where stages are executed sequentially and atomic LLM calls within each stage may run in parallel. MAS-ProVe systematically evaluates the integration of MAS with process verification by performing parallel search at two complementary granularities: agent-level and iteration-level , while remaining agnostic to the choice of process verifier. Prior to verification, customizable context-management strategies can be applied to partial multi-agent trajectories, enabling flexible control over the information passed to the verifier and the selection of the best candidate to return to the workflow. 

multi-agent trajectories; as a result, their application to MAS constitutes a strictly out-of-distribution setting. Among these approaches, LLM-as-a-Judge is typically instantiated using general-purpose LLMs with strong generalization ca-pabilities. In contrast, reward models—particularly process reward models—are commonly trained on single-agent, ver-ifiable reasoning trajectories (e.g., mathematical problem solving). Consequently, we hypothesize that LLM-as-a-Judge is more naturally suited to MAS test-time scaling than reward-based alternatives. 

Verification Granularity. Verification-based interven-tions can occur at different levels of granularity. We study two concrete levels, as shown in Fig. 1 (middle): the Agent-Level , where the outputs of each sub-agent are explicitly verified, and the Iteration-Level , where the MAS itself is evaluated as a whole. The former enables catching fine-grained errors before they corrupt other sub-agent behavior, but introduces significant overhead. The latter takes a more global perspective potentially at the cost of finding step-level errors. 

Context Management. The reliability of process verifica-tion critically depends on how the reasoning state is repre-sented to the verifier. In MAS, trajectories may span many interaction turns; naively providing the full raw history can introduce bias due to context saturation, while condition-ing only on the current step ignores the state dependencies required to assess reasoning continuity. To empirically iden-tify a “sweet spot” in contextual conditioning, we evaluate four context specifications with increasing information den-sity: (i) current-step only , (ii) summarize(context) + current step , (iii) summarize(context + current step) , and (iv) full context + current step .

Solvability. To disentangle the effect of process verifica-tion from the intrinsic reasoning capability of the underlying agents, we analyze MAS performance through the lens of 

problem solvability . A verification signal can guide the sys-tem toward a correct solution only if such an outcome lies within the agent’s generation horizon. Consequently, it is es-sential to first characterize the difficulty of the benchmarks on which the MAS operates. We partition each benchmark into three difficulty levels, Easy , Medium , and Hard based on the empirical pass rate of the unguided CoT(Chain-of-Thought) baseline, and introduce task-specific metrics to quantify how process verification interacts with solvabil-ity. Specifically, we consider: (i) Performance Gain , (ii) Evaluator Stability , and (iii) Intra-MAS Resurrection .

## 3. Experimental Setup 

Benchmarks. Our analysis focuses on four represen-tative reasoning domains: mathematics ( AIME24 and 

AIME25 , (AIME, 2025)), agentic assistance ( GAIA (Mi-alon et al., 2023)), coding ( HumanEval (Chen et al., 2021)), and scientific reasoning ( GPQA (Rein et al., 2023)). To support MAS baselines that require training or tuning, we partition each benchmark into a validation set (20%) and a test set (80%), and reuse the same splits across all methods for fair comparison. 3MAS-ProVe : Process Verification of Multi-Agent Systems 

MAS Baselines and Implementation Details. We con-duct a comprehensive evaluation on six state-of-the-art MAS frameworks with both fixed architectures , including LLM-Debate ( Debate ) (Du et al., 2024), Agentic Work-flow ( AFlow ) (Zhang et al., 2025b), and Automated De-sign of Agentic Systems ( ADAS ) (Hu et al., 2025), and 

adaptive architectures , including Dynamic LLM-Powered Agent Network ( DyLAN ) (Liu et al., 2024), Multi-agent Ar-chitecture Search ( MaAS ) (Zhang et al., 2025a), and MAS with Zero Supervision ( MAS-Zero ) (Ke et al., 2025b). To balance cost efficiency and reasoning capability, we adopt GPT-5-Mini as the primary backbone model across all baselines. Only for HumanEval, we use the GPT-4.1-nano model; this prevents the performance ceiling that stronger models would hit on this simpler task, allowing us to accurately observe the delta introduced by process verifi-cation. For the agentic benchmark GAIA, all MAS frame-works are further equipped with a DuckDuckGo search tool via OpenAI’s tool-calling interface. This enables dynamic external information retrieval and facilitates a systematic evaluation of process verification granularity in tool-assisted reasoning settings. Detailed configurations of the MAS base-lines can be found in Appendix A.2. 

Verifiers. We consider three main verifiers, one for each category: Skywork-Reward-V2-Llama-3.1-8B (Liu et al., 2025a) as an RM, Qwen2.5-Math-PRM-7B (Zhang et al., 2025d) as a PRM, and GPT-5-Mini as an LLM-as-Judge. In extended analysis, we also consider the weaker GPT-4o-Mini and the finetuned verifier FARE-20B (Xu et al., 2025), which is trained from GPT-OSS-20B (Agarwal et al., 2025). 

Integrating Verifiers into MAS via Search. Given verifi-cation scores produced by the chosen evaluators, the system must determine how to advance the reasoning process. We adopt a greedy best-first search strategy at the specified ver-ification granularity for every MAS framework to ensure a scalable, effective, and fair comparison. At each state, the MAS generates N =3 candidate continuations and se-lects the highest-scoring/ranking candidate according to the verifier to define the next state. This procedure effectively transforms the MAS from a purely stochastic generator into a verifier-guided search process. To further enrich the search heuristics and provide a more comprehensive explo-ration of this bounded space, we additionally implement Beam Search (beam width =3) on top of the Debate frame-work using our optimal Generative Judge, as detailed in Appendix B.4. 

MAS-ProVe Framework. A broad overview of our framework is illustrated in Fig. 1. Conceptually, the ex-ecution of any multi-agent system can be abstracted into a unified workflow, where stages are executed sequentially and atomic LLM calls within each stage may run in paral-lel. MAS-ProVe systematically evaluates the integration of MAS with process verification by performing parallel search at two complementary granularities: agent-level and 

iteration-level , while remaining agnostic to the choice of process verifier. Prior to verification, customizable context-management strategies can be applied to partial multi-agent trajectories, enabling flexible control over the information passed to the verifier and the selection of the best candidate to return to the workflow. 

Practically, the MAS-ProVe framework is implemented as an isolated client-middleware-server architecture: • Client side. The client executes the original MAS agentic logic without modification, as at each reason-ing step, the wrapper function automatically executes the original LLM call for N times and interfaces with the middleware to obtain the selected continuation and resumes execution along the chosen path. • Middleware side. A context-management tool inter-cepts the agent’s execution, retrieves the accumulated context from the MAS, and re-organizes the context. Then these partial trajectories are forwarded to the server for evaluation. • Server side. The server hosts a pool of verifiers that score and rank the received partial trajectories. The resulting rankings are returned to the client via the mid-dleware, which selects the highest-ranked continuation and enables the MAS to proceed. 

Remark on Computational Overhead. MAS-ProVe ’s systematic study inherently incurs additional computational overhead and is not intended to reflect the practical integra-tion of process verification into MAS. A detailed breakdown of the wall-clock time is provided in Appendix B.1. 

## 4. Main Results 

This section expands on the empirical insights derived from experiments conducted along the four dimensions intro-duced in Sec. 2. Sec. 4.1 examines different verification types , comparing generative and scoring-based verifiers and analyzing the impact of judge specialization. Sec. 4.2 studies verification granularity , characterizing each MAS’s preference between agent-level and iteration-level process verification for maximizing performance gains. Sec. 4.3 investigates context management strategies , quantifying the trade-off between information retention and verification re-liability. Finally, Sec. 4.4 decomposes performance by prob-lem solvability , isolating the role of process verification in recovering previously unsolvable queries versus improving stability across varying difficulty levels. 

4.1. Verification Paradigms 

We analyze the extent of judge verification through different choices of verifiers. The experiments on Table 1 and 2 4MAS-ProVe : Process Verification of Multi-Agent Systems 

Table 1. Main Study of MAS-ProVe on Verification Types and Granularity. We investigate two core dimensions of process verification for multi-agent systems: (i) the choice of process verifier (LLM-as-a-Judge, Reward Model, or Process Reward Model), and (ii) the granularity at which verification is applied. All experiments are repeated three times, and we report the mean and standard deviation. Values reported under the No ProVe row for each MAS correspond to the baseline performance. Higher values indicate better performance throughout. Boldface denotes the best result in each setting. Green cells indicate improvements over the baseline, while red cells indicate degradations relative to the baseline. 

Method MAS-Arch ProVe Level AIME24 AIME25 GAIA 

Judge RM PRM Judge RM PRM Judge RM PRM Debate Fixed No ProVe 74.13 ±3.44 61.87 ±3.21 31.07 ±2.07 

Agent 81.11 ±1.92 71.67 ±1.44 68.10 ±4.50 62.97 ±3.38 54.45 ±3.85 57.12 ±8.85 30.28 ±1.51 25.05 ±2.33 26.20 ±0.14 

Iteration 72.67 ±5.97 81.11 ±3.85 70.34 ±3.07 53.33 ±8.82 57.78 ±7.70 54.59 ±2.18 32.68 ±3.11 20.60 ±1.21 23.20 ±4.50 

AFlow Fixed No ProVe 65.67 ±5.09 59.72 ±6.37 11.50 ±3.25 

Agent 76.39 ±6.36 76.22 ±6.59 74.17 ±3.01 58.33 ±4.17 58.32 ±11.04 56.94 ±8.68 21.68 ±2.08 18.08 ±5.52 14.62 ±2.03 

Iteration 69.44 ±8.67 52.73 ±10.52 61.11 ±2.41 60.39 ±6.26 54.16 ±5.89 49.99 ±4.18 18.62 ±0.78 21.64 ±1.64 13.85 ±2.55 

ADAS Fixed No ProVe 62.49 ±4.19 54.17 ±4.15 19.30 ±0.92 

Agent 73.33 ±12.83 73.93 ±8.26 68.07 ±9.64 58.33 ±0.00 61.10 ±2.42 48.90 ±2.42 20.90 ±2.50 22.10 ±2.50 19.70 ±4.33 

Iteration 70.83 ±15.03 66.67 ±11.06 63.87 ±6.36 61.10 ±4.85 59.73 ±4.79 54.23 ±0.00 22.90 ±2.08 19.70 ±1.83 18.53 ±3.01 

MaAS Adaptive No ProVe 76.39 ±6.36 58.33 ±7.22 20.97 ±4.90 

Agent 80.55 ±8.67 84.03 ±6.73 83.33 ±4.17 61.09 ±4.83 52.08 ±2.94 59.70 ±2.42 26.89 ±5.11 25.36 ±6.41 24.70 ±0.86 

Iteration 77.22 ±10.48 86.11 ±6.37 81.94 ±6.36 68.06 ±6.36 63.89 ±2.41 63.88 ±8.68 31.21 ±3.60 27.29 ±2.55 24.26 ±0.97 

DyLAN Adaptive No ProVe 81.11 ±5.09 65.55 ±5.09 19.37 ±0.95 

Agent 85.56 ±1.93 76.67 ±0.00 77.78 ±3.85 70.00 ±3.85 72.22 ±5.09 67.78 ±3.85 18.12 ±2.02 19.41 ±1.68 16.50 ±1.37 

Iteration 84.44 ±1.93 78.89 ±1.92 82.22 ±10.71 71.11 ±3.85 73.33 ±5.78 67.77 ±8.39 15.50 ±1.41 14.83 ±1.53 9.70 ±1.37 

MAS-Zero Adaptive No ProVe 37.78 ±1.92 35.56 ±1.93 10.47 ±0.68 

Agent 47.78 ±1.92 38.89 ±1.92 33.34 ±5.77 42.22 ±3.85 28.87 ±5.10 20.00 ±3.85 17.36 ±0.97 19.14 ±1.06 10.14 ±0.62 

Iteration 50.00 ±3.33 45.00 ±2.36 37.78 ±1.92 27.78 ±1.92 25.56 ±5.09 25.56 ±8.39 17.95 ±1.11 14.94 ±0.62 8.20 ±0.71 

are conducted by fixing the context to Raw/Full History to establish a baseline. 

Intrinsic Difficulty of Partial Trajectory Verification. 

As evidenced by the high variance in the Debate , AFlow ,and MAS-Zero rows of Table 1 and 2, process verification does not consistently yield monotonic performance improve-ments. Although other methods show a natural sign of performance gains compared to the baseline, the pattern is noisy which highlights the challenge of evaluating the partial trajectories of MAS. 

Generative Judges Outperform Scoring-based Reward Models. Despite the high variance, a clear hierarchy is no-ticed when comparing the LLM-as-a-Judge column against the Reward Model (Skywork-Reward-V2) and Process Re-ward Model (Qwen2.5-Math-PRM) columns. Generative judges achieved higher accuracy in 24 out of 36 experimen-tal configurations across Agent-Call and Iteration levels. We attribute this performance gap to the nature of the training data for the reward model baselines. While the scalar base-lines are highly specialized for specific domains (e.g., math steps or final outcomes), general-purpose generative judges appear better equipped to interpret the heterogeneous, out-of-distribution dynamics of MAS trajectories. This supports our hypothesis that the flexible, natural language reasoning of general LLMs offers a stronger steering signal for multi-agent systems than the rigid scalar values of specialized reward models. 

Diminishing Returns on Judge Scaling. In Table 3, here, we fix the process verification level to Agent Call (for gran-ular viewing) and isolate the impact of the verifier’s model architecture. The performance gap between using a smaller generalist judge (GPT-4o-mini) and a reasoning judge (GPT-5-mini) is significantly smaller than the gap observed when these models act as solvers. This indicates that the reason-ing threshold required to verify a multi-agent trajectory is lower than the threshold required to generate it, suggesting that cost-effective, smaller models can serve as effective supervisors for larger systems. 

Understanding Specialized Verification Models. Notably, the task-specific evaluator FARE-20B generally outper-forms both general-purpose models (GPT-5-mini and GPT-4o-mini). For example, FARE-20B leads to the highest performance for MAS-Zero on AIME24 (51.11 ±1.92) and GAIA (21.15 ±2.72), ADAS on AIME25 (66.66 ±4.15) and GAIA (22.50 ±4.85) across all our experiments. These re-sults suggest that evaluation-specific finetuning can yield additional gains over general-purpose LLMs-as-Judges. 

4.2. Verification Granularity 

Table 1 shows that no single verification granularity uni-versally dominates across multi-agent systems . Neither agent-level nor iteration-level verification consistently out-performs the other across MAS architectures, benchmarks, and verifier types, indicating that granularity choice is highly architecture-dependent rather than a global heuristic. Nevertheless, individual MAS often exhibit clear pref-

5MAS-ProVe : Process Verification of Multi-Agent Systems 

Table 2. Main Study of MAS-ProVe on Verification Types and Granularity (on Coding and Scientific Reasoning). Higher values indicate better performance throughout. Boldface denotes the best result in each setting. Green cells indicate improvements over the baseline, while red cells indicate degradations relative to the baseline. 

Method MAS-Arch ProVe Level HumanEval GPQA 

Judge RM PRM Judge RM PRM Debate Fixed No ProVe 76.40 ±1.56 59.13 ±3.50 

Agent 78.35 ±0.49 76.10 ±0.17 78.04 ±0.00 66.82 ±3.36 52.48 ±2.79 55.25 ±0.28 

Iteration 77.72 ±0.45 76.20 ±0.85 77.02 ±0.71 70.95 ±0.35 69.19 ±0.71 58.53 ±5.78 

AFlow Fixed No ProVe 88.78 ±1.17 46.33 ±0.96 

Agent 89.80 ±1.19 88.14 ±0.51 73.66 ±4.86 54.93 ±2.65 44.24 ±1.32 39.72 ±1.78 

Iteration 92.58 ±0.48 92.75 ±0.54 89.28 ±1.11 52.20 ±3.55 40.56 ±2.22 37.73 ±1.78 

ADAS Fixed No ProVe 95.42 ±3.12 66.54 ±1.83 

Agent 94.82 ±2.41 95.03 ±3.83 94.08 ±4.37 68.94 ±3.64 69.16 ±4.31 60.79 ±4.82 

Iteration 96.38 ±2.63 95.20 ±2.88 96.20 ±1.65 69.54 ±2.90 55.23 ±3.76 51.65 ±2.31 

MaAS Adaptive No ProVe 96.18 ±1.08 66.23 ±1.44 

Agent 95.93 ±0.44 95.80 ±2.70 96.18 ±0.00 67.90 ±0.86 66.66 ±0.89 65.09 ±1.33 

Iteration 97.33 ±0.54 96.56 ±0.54 96.18 ±2.16 71.06 ±2.67 68.33 ±1.46 61.62 ±0.87 

DyLAN Adaptive No ProVe 90.23 ±0.00 68.18 ±1.43 

Agent 93.65 ±0.35 91.16 ±1.29 89.72 ±0.74 78.76 ±2.91 76.46 ±0.29 67.92 ±2.50 

Iteration 94.20 ±0.42 92.38 ±0.43 93.62 ±0.40 72.20 ±1.41 69.44 ±1.77 68.68 ±1.43 

MAS-Zero Adaptive No ProVe 53.63 ±3.00 60.72 ±3.50 

Agent 55.75 ±0.00 53.63 ±1.62 50.91 ±2.57 68.00 ±1.24 61.41 ±1.13 55.99 ±0.41 

Iteration 54.23 ±2.14 51.81 ±1.29 52.72 ±0.00 61.31 ±2.86 64.06 ±0.36 53.77 ±1.48 

Table 3. Study of MAS-ProVe on LLM-as-a-Judge as Verifiers. Boldface denotes the best performance. 

Method AIME24 AIME25 GAIA 

GPT-4o-mini GPT-5-mini FARE-20B GPT-4o-mini GPT-5-mini FARE-20B GPT-4o-mini GPT-5-mini FARE-20B Debate 72.23 ±3.87 81.11 ±1.92 76.67 ±1.65 54.47 ±6.32 62.97 ±3.38 64.43 ±5.38 26.85 ±4.42 30.28 ±1.51 27.87 ±2.66 

AFlow 76.39 ±8.67 76.39 ±6.36 81.94 ±4.82 58.33 ±4.17 58.33 ±4.17 61.10 ±2.42 19.27 ±4.17 21.68 ±2.08 16.55 ±0.85 

ADAS 69.45 ±4.81 73.33 ±12.83 68.07 ±9.64 63.87 ±6.36 58.33 ±0.00 66.66 ±4.15 20.50 ±2.08 20.90 ±2.50 22.50 ±4.85 

MAAS 83.31 ±8.30 80.55 ±8.67 84.73 ±6.36 62.50 ±4.17 61.09 ±4.83 58.33 ±4.17 26.50 ±3.19 26.89 ±5.11 28.31 ±0.85 

DyLAN 83.33 ±3.34 85.56 ±1.93 86.67 ±3.34 73.33 ±5.78 70.00 ±3.85 73.33 ±3.34 19.37 ±0.95 18.12 ±2.02 18.37 ±0.98 

MAS-Zero 42.22 ±5.09 47.78 ±1.92 51.11 ±1.92 30.00 ±3.33 42.22 ±3.85 38.89 ±1.92 16.62 ±1.48 17.36 ±0.97 21.15 ±2.72 

erences . Debate and MAS-Zero benefit more consistently from iteration-level verification—especially with LLM-as-a-Judge—while AFlow and ADAS show stronger gains under 

agent-level verification, suggesting better alignment with finer-grained control. MaAS improves under both granu-larities but with benchmark-specific differences, whereas adaptive architectures such as DyLAN display mixed behav-ior, favoring iteration-level verification for mathematical reasoning and agent-level verification for GAIA. Overall, these results highlight that verification granular-ity interacts closely with MAS coordination dynamics: al-though no granularity is universally optimal, aligning gran-ularity with the MAS architecture is crucial for realizing the benefits of process-level verification. 4.3. Context Management Strategies 

In Table 4, we investigate the impact of information fidelity on the judge decision-making process. The process verifica-tion level is again fixed to Agent Call .

Context-Length vs Performance Trade-Off. Results in Table 4 demonstrate that process verification with minimal context (Step-Only) performs comparably to, and occasion-ally better than, evaluation with Full Context. This suggests a strong need to understand the sweet-spot of context length that provides the right amount of context alongside not being vague. While full histor