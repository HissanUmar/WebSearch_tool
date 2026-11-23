<!-- source: https://aclanthology.org/2026.emnlp-main.2357.pdf -->

Title: 2026.emnlp-main.2357.pdf

URL Source: https://aclanthology.org/2026.emnlp-main.2357.pdf

Published Time: Wed, 21 Oct 2026 17:25:15 GMT

Number of Pages: 21

Markdown Content:
> Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing , pages 53526–53546 October 24-29, 2026 ©2026 Association for Computational Linguistics

# KnowGPO: Knowledge-Grouped Policy Optimization for Search Agents 

Siqi Chen 1,2 , Zhengxi Lu 1, Yuchen Yan 1, Xingyu Wu 1,2 , Qipeng Chen 1, Xin Zhang 2,Aiting Liu 2, Chao Deng 2, Jie Liu 2, Jin Ma 2, Weiming Lu 1,

Jun Xiao 1, Yongliang Shen 1*1Zhejiang University, 2Tencent. 

{siqichen,syl}@zju.edu.cn, daniellwang@tencent.com 

Abstract 

Deep search agents solve knowledge-intensive tasks through long-horizon, multi-turn inter-actions, where assigning credit to individ-ual search decisions is fundamentally diffi-cult. Outcome-based reinforcement learning provides only a single terminal reward shared across an entire trajectory. Recent process-supervision methods aim to assign credit at finer granularity, but they typically anchor credit to either surface-level trajectory states or model-internal signals, both of which be-come unreliable in deep search where observa-tions are heterogeneous and retrieved contexts are long and noisy. We propose KnowGPO , a reinforcement learning framework that aligns trajectories by the task-relevant knowledge they have acquired rather than by their surface ob-servations. For each query, KnowGPO de-composes the information required to derive the answer into atomic knowledge conditions, and represents the state of a trajectory at each step by the subset of conditions it has satis-fied. Trajectories sharing the same knowledge state are grouped for within-group comparison, and the incremental knowledge gain between consecutive steps serves as an environment-grounded process reward. Experiments on Xbench, BrowseComp-ZH, and GAIA show KnowGPO consistently outperforms outcome-only (GRPO) and process-supervision base-lines (GiGPO, IGPO) by 3.8 to 4.2 points, with our 8B model rivaling or exceeding most 32B open-source systems. Our code is available at 

https://github.com/ZJU-REAL/KnowGPO .

1 Introduction 

LLM-based deep search agents have become a pow-erful paradigm for knowledge-intensive problem solving, coordinating multi-turn search, evidence inspection, query reformulation, and termination decisions through language-model reasoning (Yao 

> *Corresponding author

et al., 2022; Zhang et al., 2026a). Unlike con-ventional retrieval-augmented generation (RAG), which typically follows a one-pass retrieve-then-read pipeline (Lewis et al., 2021; Gao et al., 2024; Zhao et al., 2024), deep search agents iteratively formulate queries, inspect evidence, update beliefs, and decide when to stop (Nakano et al., 2021; Li et al., 2025c). This makes deep search a long-horizon sequential decision problem, where suc-cess depends on adaptive decisions about what to search, what evidence to keep, and when to termi-nate . Because supervised fine-tuning mainly imi-tates surface behavior (Nakano et al., 2021; Schick et al., 2023) and cannot optimize such strategic de-cisions, reinforcement learning has become central to training competitive deep search agents (Guo et al., 2025; Jin et al., 2025; Song et al., 2025). However, applying reinforcement learning to deep search agents encounters three coupled diffi-culties in credit assignment (Figure 1). First, termi-nal outcome rewards used by group-relative meth-ods such as GRPO (Shao et al., 2024; Jin et al., 2025; Song et al., 2025; Lu et al., 2025; Li et al., 2025b; Liu et al., 2025) are uniformly broadcast to every action, so a single final reward cannot reveal which intermediate decisions were useful, redundant, or harmful. Second, recent process-supervision methods such as GiGPO (Feng et al., 2025) that align trajectories by their intermediate states require state recurrence across trajectories, yet deep search rollouts seldom revisit the same ob-servable state even when they acquire the same evi-dence. Third, dense process rewards derived from changes in the model’s predicted answer probabil-ity, as in IGPO (Wang et al., 2026), or from learned critics and rubric-based reward models (Shi et al., 2025; Lee et al., 2025; Zhang et al., 2025, 2026b; Lu et al., 2026), provide denser signals but are driven by model-internal beliefs or learned proxies rather than by externally verified knowledge. Deep search trajectories vary widely at the level 

53526 Step 0 Step 1 Step 2 Step 3                 

> Group Comp Q
> …
> …
> …
> R1
> R2
> R3
> Trajectory
> Group Comp
> R1‘
> Group Comp
> R1‘R2‘R3‘
> Step 0 Step 1 Step 2 Step 3 Group Comp
> …
> …
> …
> Q
> R1
> R2
> R3
> R2‘
> R3‘
> Trajectory
> ………
> Q
> R1
> R2
> R3
> Trajectory
> Step 0 Step 1 Step 2 Step 3 Group Comp
> R1‘s1,2
> 𝜏 1
> 𝜏 2
> 𝜏 3
> 𝜏 1
> 𝜏 2
> 𝜏 3
> 𝜏 1
> 𝜏 2
> 𝜏 3
> s2,3
> s3,2 ̃𝑠 :s1,2 s2,3 s3,2
> s1,2
> s2,3
> s3,2
> s1,2 s2,3 s3,2 ̃𝑠 :
> r1,2
> r2,3
> r3,2
> r2,3 r1,2 r3,2
> Outcome-only Reward

Figure 1: Comparison of credit assignment in deep search agents. Left: GRPO uses episode-level advantages from terminal rewards ( R1, R2, R3) without intermediate feedback. Middle: GiGPO matches environment states ( ˜s)but suffers from severe fragmentation under heterogeneous observations. Right: KnowGPO abstracts heterogeneous states into knowledge states ( si,t ) and computes step-level advantages from incremental knowledge gains ( ri,t ). 

of queries, pages, and reasoning traces, but con-verge on the same underlying quantity: the task-relevant knowledge they have accumulated toward the correct answer. This knowledge, not obser-vations or model confidence, provides the natural signal for credit assignment in long-horizon search. We propose Knowledge-Grouped Policy Op-timization (KnowGPO) , a RL framework that aligns trajectories by the task-relevant knowledge they have acquired rather than by their surface ob-servations. For each query, we decompose the in-formation required to derive the correct answer into a set of atomic knowledge conditions. At ev-ery step of a trajectory, we represent its state by the subset of conditions it has satisfied, called its 

knowledge state . We further define incremental knowledge gain , the increase in satisfied condi-tions between consecutive steps, as a process re-ward that scores each action’s immediate contri-bution. While knowledge-state grouping ensures only semantically comparable steps are contrasted, incremental gain provides the dense signal within each group, enabling fine-grained credit assign-ment without a learned critic. Trajectories sharing the same knowledge state are grouped for within-group comparison, yielding step-level advantages that combine with episode-level outcome advan-tages through a single mixing coefficient. The result is fine-grained credit assignment for long-horizon deep search without observation match-ing, without dependence on the model’s own confi-dence, and without a learned reward model. We train Qwen3-8B with KnowGPO on three challenging deep search benchmarks: Xbench, BrowseComp-ZH, and GAIA. KnowGPO im-proves over outcome-only GRPO by 2.0% to 5.9% and consistently outperforms recent process-supervision baselines including GiGPO and IGPO, with the resulting 8B agent matching or surpassing open-source systems of up to 32B parameters. In summary, our contributions are threefold: • We propose KnowGPO, a reinforcement learn-ing framework that performs credit assign-ment in a query-specific knowledge state space rather than over surface observations, enabling within-group comparison across se-mantically equivalent trajectories. • We introduce incremental knowledge gain as a process reward grounded in the environment, providing dense step-level supervision with-out observation matching, learned critics, or reliance on model-internal probabilities. • We demonstrate that KnowGPO outper-forms outcome-based and recent process-supervision baselines by 3.8% to 4.2% across three deep search benchmarks, with an 8B agent matching or surpassing open-source sys-tems of up to 32B parameters. 

2 Related Work 

2.1 Reinforcement Learning for Search Agent 

Reinforcement learning with verifiable outcome rewards has become the dominant paradigm for post-training deep search agents. Early systems train models to interleave search and reasoning through outcome-based optimization on multi-hop QA (Jin et al., 2025; Chen et al., 2025; Wang et al., 2025; Zheng et al., 2025; Wu et al., 2025), showing that group-relative methods such as GRPO scale to multi-turn tool use without learned value func-tions. Subsequent work scales this paradigm along two axes: harder data through knowledge graphs, web exploration, and synthetic multi-hop genera-tion (Lu et al., 2025; Li et al., 2025b; Liu et al., 2025; Li et al., 2025a; Du et al., 2026; Gao et al., 2025; Chu et al., 2026; Team et al., 2026e,d), and 53527 refined reward shaping and policy gradient stability for long-horizon rollouts (Wu et al., 2026; Dong et al., 2025; Luo et al., 2025; Tang et al., 2025). Despite these advances, the supervisory signal in most systems remains a binary reward at the end of each trajectory, leaving the contribution of search decisions inside long rollouts unidentified. 

2.2 Credit Assignment for Search Agents 

A growing line of work aims to address long-horizon credit assignment through process-level supervision. GiGPO (Feng et al., 2025) extends GRPO with anchor-state grouping, computing step-level advantages by matching trajectories that re-visit the same environment state; this mechanism requires reliable state recurrence, which is rare in deep search where retrieved contents and reason-ing histories are open-ended. IGPO (Wang et al., 2026) instead derives dense step rewards from the model’s own probability of producing the correct answer, sidestepping state matching but anchor-ing the signal to internal confidence that can be biased by long, noisy retrieved contexts. A par-allel direction introduces externally grounded su-pervision through learned reward models or rubric decompositions (Zhang et al., 2026b, 2025; Lee et al., 2025; Shi et al., 2025), providing denser feed-back than outcome rewards but relying on learned proxies whose calibration is itself a research ques-tion, and without producing step groupings that make semantically equivalent decisions directly comparable across trajectories. KnowGPO instead anchors credit assignment to an externally verifi-able representation of progress, the set of satisfied atomic knowledge conditions, and uses this repre-sentation as both the grouping criterion for within-group comparison and the basis of a process reward grounded in the environment. 

3 Method 

3.1 Problem Formulation 

We formulate deep search as a multi-turn sequen-tial decision process. Given a query Q and a refer-ence answer y∗, an agent interacts with a retrieval environment over time steps t ∈ { 1, . . . , T }. At each step the agent produces a reasoning trace and an action at ∈ { search , answer } from its policy 

πθ(· | ht, Q ), where ht = ( a1, o 1, . . . , a t−1, o t−1)

is the interaction history and ot is the observa-tion returned by the environment (e.g., retrieved documents for search , or a terminal signal for 

answer ). A complete trajectory is denoted τ =(a1, o 1, . . . , a T , o T ) and terminates with a binary outcome reward R(τ ) = I(ans (τ ) = y∗). We build on group-relative policy optimization, which estimates advantages from a group of N trajecto-ries sampled for the same Q and avoids learning a separate value network. The challenge addressed throughout this section is that R(τ ) alone provides no signal for distinguishing useful, redundant, or harmful steps inside a long-horizon trajectory. 

3.2 Knowledge State 

A central design choice in KnowGPO is to ab-stract the progress of a search trajectory through the task-relevant knowledge it has acquired, rather than through its surface observations. We realize this abstraction in two steps: constructing a query-specific set of atomic knowledge conditions, and representing each trajectory step by the subset of conditions it has satisfied. 

Knowledge conditions. For each query Q with reference answer y∗, we construct a finite set of atomic knowledge conditions 

K(Q) = {k1, . . . , k K }, (1) where each kj is a single-hop factual constraint needed to derive y∗. Intuitively, K(Q) encodes the answer’s logical skeleton: a trajectory cannot reli-ably produce y∗ without acquiring every kj . We construct K(Q) through a two-stage pipeline that first identifies the reasoning skeleton implied by Q

(with placeholders for unknown entities) and then grounds each placeholder using y∗ and a successful reference trajectory. This decoupling produces a trajectory-agnostic knowledge space and ensures three properties: each condition encodes a single fact (atomicity), the conditions jointly support the full reasoning chain to y∗ (completeness), and en-tity references remain consistent across the query, the answer, and the search trajectories (grounding consistency). Construction details and the prompts used at each stage are deferred to Appendix B. 

Knowledge state. Given K(Q), we represent the state of a trajectory τi at step t by the subset of conditions it has satisfied so far. At each step, an LLM-based verifier inspects the new observation 

oi,t and outputs a binary vector ∆si,t ∈ { 0, 1}K

indicating the set of conditions newly verifiable from oi,t :

[∆ si,t ]j = I(hi,t |= kj ) . (2) 53528 Knowledge Construction 

> Query. During a certain pe-riod, a music producer organ-ized a concert at a venue in a certain city…..Who is the fo-under of this cultural com -pany? Answer. Landy Chang Trajectory. <Think>xxx</Th-ink>......<Answer>The answer is xxx</Ansert> K1: The "Rock China Power" concert was hosted by Magic Stone Culture.

…

> K5: Landy Chang subseque-ntly founded "Magic Stone Culture."
> Two Stage Pipeline

R1

R2

R3

Episode-Level 

A1E

A2E

A3Ẽ𝑠 :

s1,2   

> Step 1 Step 2 Step 3

Q

…

…

…

s1,2 

s2,3 

s3,2 

r1,2 

Rollout Data     

> Step 0
> K1; k 2; K 4
> K3; k 5
> S1,2 = [1, 1, 0, 1, 0]
> =

s3,2 - s3,1  

> =

s3,2 ∥ ∥1 - ∥ ∥1

State Definition Knowledge Gain Step- Level  

> Group Comp
> K1K5

…

s3,1 

> 𝜏 1
> 𝜏 2
> 𝜏 3

r2,3 

r3,2 

s1,2 r3,2 

s3,1 

r1,2 r2,3 r3,2 

Two-stage Construction Pipeline    

> Inputs
> Query Q Answer y *Ref. Tra

𝜏 

Stage 2 

> Q
> (Grounding Placeholder)
> Y*

𝜏     

> <E0> Landy Chang <E1> Rock China Power <E2> Magic Stone Culture
> Placeholder Grounded Knowledge

…

Stage 1   

> Query Placeholder Knowledge
> Q
> {{<E0> organized concert <E1>} {{<E1> was hosted by company <E2>}} {{<E0> founded <E2>}}
> {{<E3> is a music producer (Identifying Reasoning Skeleton) <E3> Cindy Wang

…

s2,3 s3,2 

𝐴 !,#̃ % 𝐴 #,&̃ % 𝐴 &,#̃ %

s1,2 s2,3 s3,2 Figure 2: Overview of the KnowGPO framework. Left: Knowledge condition construction via a two-stage pipeline, illustrated with an example. Right: Rollout trajectories are grouped by matched knowledge states; step-level advantages are computed from incremental knowledge gains via group-relative comparisons. 

We then monotonically accumulate these incre-ments to obtain the cumulative knowledge state: 

si,t = si,t −1 ∨ ∆si,t , si, 0 = 0K , (3) where ∨ denotes element-wise OR. Monotonic ac-cumulation reflects the fact that acquired knowl-edge cannot be unacquired, and absorbs transient verifier noise across nearby steps. The knowl-edge state si,t defines a shared semantic space across episodes: two steps with the same s have, by construction, acquired the same set of task-relevant facts, regardless of which queries were issued, which pages were visited, or how reason-ing was phrased in between. This is the property that surface observations fail to provide and that KnowGPO exploits in the next subsection. 

3.3 Knowledge-Grouped Policy Optimization 

Given the knowledge state representation, Know-GPO assigns credit at two levels. Episode-level advantages align the policy with the final task ob-jective, and step-level advantages, computed by grouping steps under matched knowledge states, attribute credit to individual search decisions. 

Episode-level advantage. For each query Q, we sample N episodes {τi}Ni=1 from the current policy and compute the group-normalized advantage of episode i as 

AEi = R(τi) − μσ + ε , (4) where μ and σ are the empirical mean and stan-dard deviation of {R(τi)}Ni=1 , and ε is a small con-stant for numerical stability. This is the standard outcome-based group advantage of GRPO. 

Step-level advantage via knowledge-grouped comparison. To attribute credit at the step-level, we exploit the fact that the knowledge state ˜s par-titions the space of intermediate steps into seman-tically equivalent classes. Let U denote the set of distinct knowledge states observed across all N

episodes for query Q. For each ˜s ∈ U , we form a knowledge group 

G(˜ s) = {(i, t ) | si,t = ˜ s, a i,t ̸ = answer } (5) containing every non-terminal step that starts from state ˜s. We then define the step-level reward as the 

incremental knowledge gain ,

ri,t = ∥si,t ∥1 − ∥ si,t −1∥1, (6) which counts the number of new knowledge con-ditions satisfied by step (i, t ). The step-level ad-vantage is the group-normalized incremental gain within G(˜ s):

ASi,t = ri,t − μ˜s

σ˜s + ε , (7) where μ˜s and σ˜s are computed over G(˜ s). Two fea-tures of this construction are important. First, all steps compared within a group share the same prior knowledge state, so ASi,t measures how much more (or less) a step contributes to knowledge acquisi-tion than alternative actions taken from the same 53529 epistemic position. Second, the step-level signal is anchored to the environment through the verifier’s checks against K(Q), rather than to surface obser-vations or the policy’s own answer probabilities. 

Combined objective. For each step (i, t ), we combine the two advantages with a single mixing coefficient ω ∈ [0 , 1] :

Ai,t = (1 − ω) AEi + ω A Si,t . (8) The episode-level term keeps optimization aligned with the final outcome and prevents the policy from collapsing onto local information-gathering behav-iors. The step-level term provides dense, semanti-cally grounded supervision that distinguishes be-tween informative and redundant decisions sharing the same starting knowledge. We optimize the policy with a PPO-style clipped objective (Schulman et al., 2017): 

LKnowGPO (θ) = E

∑

> i,t

min 

(

ρi,t Ai,t ,

clip( ρi,t , 1 − ϵ, 1 + ϵ) Ai,t 

)] 

− β D KL (πθ ∥ πref ) ,

(9) The full procedure, including knowledge state veri-fication and group construction, is summarized in Algorithm 1 (Appendix A). 

4 Experiments 

We evaluate KnowGPO on four research ques-tions. First, does knowledge-grouped credit as-signment yield consistent gains over outcome-only and process-supervision baselines (Section 4.2)? Second, are knowledge-state grouping and incre-mental knowledge gain each individually necessary (Section 4.3)? Third, does the knowledge state genuinely provide a better grouping anchor than surface observations (Section 4.4)? Fourth, how does KnowGPO change search behavior, and at what training cost (Section 4.5)? 

4.1 Experimental Setup Benchmarks. We evaluate KnowGPO on three challenging deep search benchmarks that cover di-verse question distributions and difficulty levels: Xbench (Xbench-Team, 2025) (covering the 2505 and 2510 splits), BrowseComp-ZH (Zhou et al., 2025), and the text-only subset of GAIA (Mialon et al., 2023). Following standard LLM-as-judge protocols, GPT-4o (OpenAI et al., 2024) judges whether the agent’s final response matches the ground truth. All evaluations follow each bench-mark’s official protocol; we report the mean accu-racy over 3 independent runs. 

Baselines. We compare KnowGPO against three representative reinforcement learning approaches, all trained from the same SFT checkpoint with identical data and tool environments. GRPO (Shao et al., 2024) uses only the binary outcome reward and is the dominant baseline in current open-source systems. GiGPO (Feng et al., 2025) introduces step-level credit assignment by grouping steps that revisit the same intermediate state and computing within-group advantages from discounted future returns. IGPO (Wang et al., 2026) assigns each step a dense reward equal to the increase in the model’s predicted probability of the correct answer. In addition, we report numbers from several state-of-the-art open-source and proprietary deep search agents for context; differences in training data, con-text length, and tool stacks limit direct comparison, and we mark such systems separately. 

Implementation details. All trained models use Qwen3-8B (Yang et al., 2025) as the base model, with context extended to 128K tokens via YaRN (Peng et al., 2026). SFT is conducted with LlamaFactory (Zheng et al., 2024); RL training uses verl (Sheng et al., 2025). All baselines share the same SFT initialization, training data, learn-ing rate, batch size, and rollout configuration as KnowGPO; only the advantage estimator and re-ward design differ. Knowledge state verification uses DeepSeek-v3.2 as the LLM verifier; the choice and its quality analysis are reported in Appendix C. Full hyperparameters are in Appendix E. 

4.2 Main Results 

Tables 1 and 2 report performance on all three benchmarks. We make two observations. 

KnowGPO consistently outperforms both outcome-only and step-level baselines. All RL approaches improve over SFT, confirming that ex-plicit policy optimization is necessary for deep search agents. However, existing step-level meth-ods show considerable cross-dataset variability: GiGPO degrades by 2.0% on Xbench-2505 relative to GRPO despite winning on BrowseComp-ZH, and IGPO matches GRPO on Xbench-2505 but barely improves on BrowseComp-ZH. KnowGPO 53530 Model BrowseComp-ZH GAIA                                      

> Advanced Agents with Proprietary Data
> MiniMax-M2.1 47.8 64.3 DeepSeek-V3.1 49.2 63.1 DeepSeek-R1 26.3 16.5 GLM-4.5 37.5 66.0 Kimi-K2.5 62.3 –Claude-4-Sonnet 29.1 68.3
> Agents with Open-source Data
> WebExplorer-8B 32.0 50.0 WebSailor-7B 14.2 37.9 WebSailor-32B 25.5 51.5 ASearcher-Web-32B 15.6 52.8 DeepMiner-32B-RL 40.1 58.7 DeepDive-9B 15.1 –DeepDive-32B 29.7 –
> Our Agents
> Qwen3-8B-SFT 30.1 31.1 + GRPO 32.9 35.0 + GiGPO 37.3 35.0 + IGPO 32.2 37.9 +KnowGPO 38.8 40.2

Table 1: Performance comparison on BrowseComp-ZH and GAIA. Among RL-based methods, best results are in bold , and second-best are underlined. 

is the only method that improves on every split, gaining 5.9% on BrowseComp-ZH and 5.2% on GAIA over GRPO, and exceeding the strongest step-level baseline by 1.5% and 2.3% on these two benchmarks. The averaged gain over the SFT ini-tialization is 8.5%. We attribute this consistency to the fact that knowledge-grouped credit signals do not depend on either surface state recurrence or stable model confidence, both of which are particu-larly fragile on noisier benchmarks. 

KnowGPO closes the gap to 32B open-sour-ce deep search agents at 8B scale. On BrowseComp-ZH, KnowGPO reaches 38.8%, sur-passing the same-scale WebExplorer-8B by 6.8% and the 32B WebSailor-32B and DeepDive-32B by 13.3% and 9.1% respectively, and trailing the strongest open-source system DeepMiner-32B-RL by only 1.3%. On Xbench-2505 it reaches 48.0%, outperforming the 8B MiroThinker-v1.0 by 12.6%. These results show that knowledge-grouped credit assignment narrows the gap to substantially larger open-source systems without proprietary data or larger backbones. A gap to proprietary systems remains, for example 23.5% to Kimi-K2.5 on BrowseComp-ZH and 28.1% to Claude-4-Sonnet on GAIA, which we attribute to training data scale, model capacity, and inference-time optimization beyond our scope.                                        

> Model Xbench-2505 Xbench-2510
> Advanced Agents with Proprietary Data
> MiniMax-M2.1 68.7 43.0 DeepSeek-V3.2 78.0 55.7 GLM-4.7 72.0 52.3 Kimi-K2.5 –46.0 Claude-4-Sonnet 64.6 –OpenAI-o3 67.0 –OpenAI GPT-5-High 77.8 75.0 Gemini-3.0-Pro –53.0
> Agents with Open-source Data
> WebExplorer-8B 53.7 23.0 MiroThinker-v1.0-8b 60.6 34.0 MiroThinker-v1.0-30B 70.6 –MiroThinker-v1.5-30B 73.1 –MiroThinker-v1.7-mini –57.2
> Our Agents
> Qwen3-8B-SFT 39.0 29.0 + GRPO 46.0 34.0 + GiGPO 44.0 35.0 + IGPO 46.0 34.0 +KnowGPO 48.0 36.0

Table 2: Performance comparison on Xbench-2505 and Xbench-2510. Among RL-based methods, best results are in bold , and second-best are underlined.                     

> Model Xben05 Xben10 BC-ZH GAIA
> Qwen3-8b-SFT 39.0 29.0 30.1 31.1 +KnowGPO ( ω=0 )45.0 28.0 34.0 34.0 +KnowGPO ( ω=0 .3)48.0 36.0 38.8 40.2
> +KnowGPO ( ω=0 .5)47.0 35.0 36.3 37.9

Table 3: Performance of KnowGPO with different ω.

Training dynamics across baselines. Figure 3 tracks validation accuracy on Xbench-2505 in RL training. All four methods start from the same SFT checkpoint and follow comparable trajectories during the first 16 steps, after which they diverge. KnowGPO opens a clear gap by around step 20 and plateaus near step 32 at roughly 50%, while GRPO, GiGPO, and IGPO settle below 46%. The gap is consistent across the second half of training, sug-gesting that knowledge-grouped credit assignment provides a denser signal throughout rather than a small final-stage advantage. 

4.3 Ablation Study 

We next ablate the components of KnowGPO. The first ablation studies the mixing coefficient ω; the second isolates the contributions of incremental knowledge gain and knowledge-state grouping; the third compares incremental gain against discounted future returns as a process reward. All ablations use the same SFT initialization and training setup as the main experiments. 53531 1 8 16 24 32 40 48 

> Training Steps
> 30 35 40 45 50 55
> Accuracy (%)
> Training Curves on BrowseComp-ZH (Qwen3-8B)
> GRPO GiGPO IGPO
> KnowGPO

Figure 3: Training curves comparing GRPO, GiGPO, IGPO, and KnowGPO on our Qwen3-8B-SFT.                        

> Method Xben05 Xben10 BC-ZH GAIA
> GRPO (Base) 46.0 34.0 32.9 35.0 +∆KG 47.0 34.0 34.6 37.8 KnowGPO (w/ Gt)45.0 35.0 32.8 36.8
> KnowGPO 48.0 36.0 38.8 40.2

Table 4: Ablation study on reward design and group-ing mechanisms. (1) GRPO with outcome rewards, (2) GRPO with incremental knowledge gain, (3) KnowGPO with discounted future returns, and (4) KnowGPO. 

The mixing coefficient ω balances outcome and process supervision. Table 3 sweeps ω ∈{0, 0.3, 0.5}. Performance peaks at ω = 0.3

across all four splits. Setting ω = 0 disables step-level supervision yet still outperforms GRPO on BrowseComp-ZH and GAIA, suggesting that grouping by knowledge state implicitly regularizes learning even before any step reward is applied. Setting ω = 0 .5 overweights process supervision and degrades on three of four splits, reflecting that excessive local optimization can pull the policy away from the terminal objective. We use ω = 0 .3

throughout the rest of the paper. 

Both incremental gain and knowledge-state grouping are individually necessary. Table 4 decomposes KnowGPO against GRPO. Adding incremental knowledge gain to GRPO ( +∆KG , ap-plied without knowledge-state grouping) improves over GRPO by 1.0% to 2.8% across benchmarks, confirming that knowledge-grounded step rewards are useful even without proper grouping. Further introducing knowledge-state grouping (KnowGPO, full) yields an additional 1.0% to 4.2%, with the largest gain (+4.2%) on BrowseComp-ZH. The role of grouping is to restrict normalization to steps that share the same prior knowledge state, so that within-group comparison contrasts decisions made from the same epistemic position rather than across mixed positions; the ablation isolates this effect from the choice of process reward. 

Incremental knowledge gain outperforms dis-counted future returns as a process reward. 

Within the same knowledge-grouped framework, replacing incremental gain with the discounted future return Gt used by GiGPO drops accu-racy by 3.0%, 6.0%, and 3.4% on Xbench-2505, BrowseComp-ZH, and GAIA respectively (Table 4, row "KnowGPO w/ Gt"). The two rewards differ in how much downstream stochasticity they absorb: 

Gt couples a step’s credit to all subsequent deci-sions and is sensitive to long-horizon noise, while incremental knowledge gain is a local, immediate signal that does not require waiting for the trajec-tory to end. The gap shows that, even when group-ing is fixed, the choice of step reward materially matters for long-horizon credit assignment. 

4.4 Why Knowledge-Based Grouping Works 

The ablation shows that knowledge-state group-ing matters in aggregate. We now examine why it works by directly measuring the grouping behavior of three candidate anchors on real rollouts. 

Setup. We sample 500 queries from Xbench and BrowseComp (Wei et al., 2025) and rollout the SFT checkpoint up to 16 times per query, pro-ducing 5,922 valid trajectories with 55,571 steps after filtering. We compare three grouping an-chors: observation-anchored , matching steps by BGE-large cosine similarity over retrieved contents at threshold 0.9 (the protocol used by GiGPO); 

action-anchored , matching steps by similarity of generated queries; and knowledge-anchored (ours), matching steps by exact equality of accumulated knowledge state. Grouping quality is measured by the effective step ratio (ESR, fraction of steps in non-singleton groups), the singleton ratio, the mean non-singleton group size, and the cross-rollout cov-erage (average number of distinct rollouts per non-singleton group). Formal definitions are in Ap-pendix D. 

Knowledge state aligns far more steps than ob-servation or action. Table 5 reports the five met-rics. Observation-based grouping, the anchor used by GiGPO, leaves only 51.8% of steps inside non-singleton groups and produces 79.4% singletons, which me