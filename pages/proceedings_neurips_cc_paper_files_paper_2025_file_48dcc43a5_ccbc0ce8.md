<!-- source: https://proceedings.neurips.cc/paper_files/paper/2025/file/48dcc43a534c5b582f9d0fdb778e9b84-Paper-Conference.pdf -->

Title: 48dcc43a534c5b582f9d0fdb778e9b84-Paper-Conference.pdf

URL Source: https://proceedings.neurips.cc/paper_files/paper/2025/file/48dcc43a534c5b582f9d0fdb778e9b84-Paper-Conference.pdf

Number of Pages: 48

Markdown Content:
# OWL: Optimized Workforce Learning 

# General Multi-Agent Assistance for Real-World Task Automation 

Mengkang Hu 1,4∗, Yuhang Zhou 1∗, Wendong Fan 2, Yuzhou Nie 3, Bowei Xia 1,Tao Sun 2, Ziyu Ye 5, Zhaoxuan Jin 6,2, Yingru Li 7, Qiguang Chen 1, Zeyu Zhang 8,2,

Yifeng Wang 4, Qianshuo Ye 9,2, Bernard Ghanem 10 , Ping Luo 1†, Guohao Li 2† 

> 1

The University of Hong Kong 2 Eigent.AI 3 UCSB 4 CAMEL-AI  

> 5

The University of Chicago 6 Northwestern University 7 CUHK  

> 8

ANU 9 University of Cambridge 10 KAUST 

## Abstract 

Large Language Model (LLM)-based multi-agent systems show promise for au-tomating real-world tasks but struggle to transfer across domains due to their domain-specific nature. Current approaches face two critical shortcomings: they require complete architectural redesign and full retraining of all components when applied to new domains. We introduce WORKFORCE , a hierarchical multi-agent framework that decouples strategic planning from specialized execution through a modular architecture comprising: (i) a domain-agnostic Planner for task de-composition, (ii) a Coordinator for subtask management, and (iii) specialized 

Workers with domain-specific tool-calling capabilities. This decoupling enables cross-domain transferability during both inference and training phases: During inference, W ORKFORCE seamlessly adapts to new domains by adding or modifying worker agents; For training, we introduce O PTIMIZED WORKFORCE LEARNING 

(OWL), which improves generalization across domains by optimizing a domain-agnostic planner with reinforcement learning from real-world feedback. To vali-date our approach, we evaluate W ORKFORCE on the GAIA benchmark, covering various realistic, multi-domain agentic tasks. Experimental results demonstrate WORKFORCE achieves open-source state-of-the-art performance ( 69.70% ), out-performing commercial systems like OpenAI’s Deep Research by 2.34% . More notably, our OWL-trained 32B model achieves 52.73% accuracy ( +16.37% ) and demonstrates performance comparable to GPT-4o on challenging tasks. To summa-rize, by enabling scalable generalization and modular domain transfer, our work establishes a foundation for the next generation of general-purpose AI assistants. 1

## 1 Introduction 

Large Language Models (LLMs) have undergone a period of rapid advancement, evolving from simple text predictors into powerful autonomous agents capable of planning, tool use, and multi-step reasoning [OpenAI, 2024, Anthropic, 2025]. Recently, multi-agent systems (MAS) have emerged as a promising approach for complex real-world tasks, demonstrating that dividing tasks among specialized agents can enhance performance [Li et al., 2023, Qian et al., 2023, Wang et al., 2024]. Although current MAS have yielded impressive results, their designs are typically domain-specific, severely restricting cross-domain transferability . This shortcoming appears in two forms: (i) 

39th Conference on Neural Information Processing Systems (NeurIPS 2025). 

> 1

Our code is available at https://github.com/camel-ai/owl. Coordinator                         

> ...
> Training Data In Domain
> New Domain Adaptation
> Chain
> Centralized Decentralized
> 69
> GAIA Score
> Model
> 67
> 55
> Workforce
> Model
> 52
> GAIA Score
> 36
> Need Re -train!!
> ... Domain
> Agent 2
> Domain
> Agent 3
> Domain -Agnostic
> Planner
> Worker
> Nodes
> Task
> Channel
> Domain -
> Agnostic Planner
> ... Domain
> Agent 1
> Domain
> Agent 2
> Domain
> Agent 3
> Task
> Channel
> Coordinator
> Worker
> Nodes
> Optimized Workforce Learning
> Task 3
> Task 2
> Task 1Train
> Previous Inference
> Previous Training
> Train
> Domain
> Agent 1
> Task -
> Independent
> Context 1
> Task -
> Independent
> Context 2
> Task -
> Independent
> Context 3
> Agent 1Agent 2
> Multi -Agent System
> Agent …Agent N

Figure 1: Overview of W ORKFORCE and O PTIMIZED WORKFORCE LEARNING .First, on the inference side, deploying a system in a new domain often entails a full redesign; for instance, MetaGPT [Hong et al., 2023] depends on Standard Operating Procedures tailored to software engineering, hindering its extension to other fields. (ii) Second, on the training side, existing works often optimize every agent. MALT [Motwani et al., 2024], for example, follows a fixed generator-verifier-refiner pipeline, necessitating separate training for every component. Consequently, migrating such systems demands retraining the entire agent ensemble, sharply reducing flexibility. These drawbacks underscore the need for a generalized, modular multi-agent architecture that can be rapidly adapted to diverse domains with minimal retraining and redesign. Building upon these observations, firstly, we introduce W ORKFORCE , a hierarchical multi-agent inference framework that decouples strategic planning from domain-specific execution. As is shown in Figure 1, This modular design comprises three core components: (i) Domain-agnostic Planner :Generates abstract task decompositions based on high-level goals. (ii) Coordinator : Assigns subtasks to appropriate workers. (ii) Domain-specific Worker Nodes : A set of specialized agents that perform tool calls to accomplish each subtasks. The decoupling of these components enables plug-and-play extensibility, allowing W ORKFORCE to be seamlessly adapted to new domains by simply replacing or adding worker nodes. Furthermore, this modular architecture facilitates O PTIMIZED 

WORKFORCE LEARNING (OWL), a novel multi-agent training paradigm. OWL focuses on enhancing MAS’s cross-domain transferability by training a generalizable domain-agnostic planner. Specifically, we employ a two-stage training strategy: Supervised Fine-Tuning (SFT) for planner initialization, followed by Reinforcement Learning [Rafailov et al., 2023] to further enhance the model’s generalization capabilities. We evaluate our approach on the GAIA benchmark, a rigorous suite for generalist AI assistants that spans diverse domains and demands multimodal reasoning, code execution, and live web search [Mialon et al., 2023]. WORKFORCE attains an accuracy of 69.70% , surpassing strong commercial proprietary baselines like OpenAI’s Deep Research [OpenAI, 2024] (55.15%). To demonstrate the effectiveness of OWL, we further post-trained a strategic planner initialized by Qwen2.5-32B-Instruct [Yang et al., 2024] on a custom-curated training dataset without using any GAIA data. After training, the model reaches 52.73% score ( +16.37% ), outperforming models like GPT-4o-mini [OpenAI, 2024] (47.27%) and Qwen2.5-72B-Instruct (49.09%). These results confirm that our modular training strategy generalizes across domains while requiring minimal retraining. 

Our key contributions are fourfold: 1. A New Flexible and Modular Multi-Agent Architecture. We propose W ORKFORCE that is modular and scalable in both inference and training, enhancing cross-domain transferability. 

2. State-of-the-Art Performance. Our system achieves open-source state-of-the-art performance on the GAIA benchmark, even surpassing proprietary systems like OpenAI’s Deep Research. 23. Efficient and Effective Training Paradigm. OWL significantly enhances model capabilities with minimal overhead, enabling Qwen2.5-32B-Instruct to achieve a 16.37% performance gain and reach comparable performance to GPT-4o on challenging tasks. 

4. Fully Open-Source. We release all code, models, and data to support open research. 

## 2 Preliminary 

Large Language Model (LLM)-based Agents are autonomous systems that perceive, reason, and act in various environments [Xie et al., 2023]. These agents operate in a perception-reasoning-action loop, where they observe their environment, process information through the language model, determine appropriate actions, and execute them to achieve goals. 

Multi-Agent Systems extend this paradigm by enabling multiple LLM-based agents to collaborate on complex tasks. Frameworks such as CAMEL [Li et al., 2023] and MetaGPT [Hong et al., 2023] have demonstrated that collaborative approaches can outperform single-agent systems on tasks requiring diverse expertise. However, existing multi-agent frameworks are typically constrained by domain-specific designs that limit their broader applicability. This paper aims to develop scalable and generalizable multi-agent frameworks W ORKFORCE through strategic planning and task execution decoupling, enabling efficient coordination across diverse domains. (See complete formalization in Appendix C and more related works in Section 6.) 

Generalist AI Assistant was first introduced by GAIA [Mialon et al., 2023]. These systems are designed to handle a diverse range of complicated tasks across multiple domains and modalities. As the first question answering benchmark evaluating generalist AI assistants, GAIA proposes to enable LLM-based agents to gather information in real-world contexts, testing fundamental capabilities including multi-modal understanding, web browsing, reasoning, and complex problem-solving. Recently, numerous companies have released generalist AI assistant products (e.g., OpenAI’s Deep Research [OpenAI, 2024]). While open-source frameworks have made significant progress (e.g., Huggingface’s Open Deep Research [Roucher et al., 2025a]), they still lag behind commercial solutions. In this paper, we aim to close the gap between open-source and commercial proprietary agent frameworks. The proposed W ORKFORCE surpasses OpenAI’s Deep Research by 2.34%, while our training method OWL significantly improves Qwen2.5-32B-Instruct’s performance by 16.37%. 

## 3 Multi-Agent Inference: W ORKFORCE 

3.1 WORKFORCE 

Motivation. Contemporary multi-agent systems are critically limited by domain specificity and architectural rigidity, requiring complete redesign and retraining for each new application domain. We introduce W ORKFORCE , which addresses this fundamental challenge through modular architecture, particularly the separation of domain-agnostic planning from domain specific execution. More details about W ORKFORCE can be found in Appendix D. Task Channel        

> Task State :
> Assignee :<web_agent_id >
> Task State :
> Assignee :<web_agent_id >
> Task State :OPEN
> Assignee :<reasoning_agent_id >
> Planner

(1) Task Planning                            

> Apaper about AI regulation ... Which of these
> words is used to describe atype of society in a
> Physics and Society article submitted to arXiv .org
> on August 11 ,2016 ?

(2) Task Solving                                                                                                    

> Coordinator
> Subtask 2should be assigned to <web_agent_id>
> Worker Pool
> Document
> Agent
> Reasoning
> Agent
> Subtask 2:Search for the Physics and Society article
> and identify keywords used to describe atype of society .
> User
> Subtask 1:Search for the correct
> paper about AI regulation ...
> Subtask 2:Search for the Physics
> and Society article ...
> Subtask 3:Compare the label words
> from the AI regulation ...
> Subtask 4:Transform the original
> problem into aspecial format ...
> DONE
> RUNING
> OPEN
> Subtask 2:Search for the Physics
> and Society article submitted to ...
> Subtask 1:Search for the correct
> paper about AI regulation ...
> Subtask 3:Compare the label
> words from the AI regulation ...
> Task State :OPEN
> Assignee :None
> OPEN
> Subtask 4:Transform the origin -
> al problem into aspecial format ...
> Search Results:
> {
> "title" :"Phase transition from.." ,
> "description" :"... [Submitted on 11 Aug 2016]. Title:Phase
> transition from egalitarian to hierarchical societies..." ,
> "url ":"https:// arxiv.org /abs/1608.03637"
> },
> ...
> Web
> Agent

Figure 2: Overview of the W ORKFORCE framework. The system consists of a Planner Agent for task decomposition, a Coordinator Agent for orchestrating subtasks, and multiple specialized Worker Nodes equipped with domain-specific toolkits to execute assigned tasks. 3Architecture. As illustrated in Figure 2, W ORKFORCE comprises three core components: (i) Planner Agent analyzes incoming tasks and decomposes them into subtasks based on worker capability registry; (ii) Coordinator Agent serves as the central orchestration mechanism, managing worker assignments and task dependencies while integrating intermediate results; (iii) Worker Nodes consist of one or more specialized agents equipped with specific capabilities and toolkits that execute assigned subtasks and post results. This modular architecture provides inherent flexibility, allowing the framework to be deployed across diverse applications by simply modifying the worker nodes while maintaining its core planning and coordinating mechanism. 

Communication Mechanism. Communication in W ORKFORCE operates through a shared task channel that serves as a central hub. The coordinator posts tasks and assignments to this channel. Upon completion, workers post only their final results back to the channel, while the detailed execution context of tool calls remains isolated within each subtask’s scope. This maintains a clean context for each worker, who only has access to the current subtask details and concise previous subtask results. This centralized approach simplifies system management and enhances scalability by eliminating direct agent-to-agent messaging. 

Task Flow. The task processing workflow within W ORKFORCE follows a structured pipeline: (i) The Planner analyzes incoming overall tasks and then decomposes them into a set of subtasks according to the capabilities of available worker nodes and the overall task’s complexity; (ii) The Coordinator assesses the capabilities of available worker nodes and dispatches subtasks accordingly; (iii) The Worker Nodes perform the assigned subtasks using their specialized tools; (iv) Results from worker nodes are posted to the shared task channel ; (v) The Coordinator manages task dependencies and integrates results, ultimately forwarding them to the Planner; (vi) The Planner analyzes the results of each subtask and synthesizes the final output. 

Replanning Mechanism. During task execution, workers self-assess whether the assigned subtask is failed. When a worker determines that a subtask has failed, it posts failure information to the task channel. The task channel then detects this failure, and the planner will be prompted to generate new subtasks based on the feedback information. This replanning mechanism enables test-time scaling by dynamically adjust its approach to increasingly complex tasks, which is validated in Section 5. 

3.2 Generalist Multi-Agent Assistance 

To construct a generalist multi-agent assistant capable of processing diverse real-world tasks, we instantiated W ORKFORCE with three worker agents, each equipped with domain-specific toolkits: 

(i) A Web Agent , capable of performing web searches, extracting webpage content, and simulating browser actions; (ii) A Document Processing Agent , designed to process documents and multimodal data, including text, images, audio, video, spreadsheets, and various file formats; and (iii) A Rea-soning/Coding Agent , which handles analytical reasoning and code execution tasks. The details of worker agents and corresponding toolkits could be found in Appendix D.3. 

3.3 Experiments 

Baselines. We selected a comprehensive set of baseline systems, categorized into four main groups: 

(i) Proprietary frameworks establish upper-bound commercial performance, including commercial agentic systems like OpenAI’s Deep Research [OpenAI, 2024], h2oGPTe Agent [H2O.ai, 2024], etc. (ii) Open-source frameworks reveal the community progress, including strong baselines like HuggingFace’s Open Deep Research [Roucher et al., 2025a], Trase Agent [Trase, 2024], etc. (iii) A

Single Agent baseline utilizing multi-step tool calling. (iv) Role Playing Li et al. [2023] comprising two agents (user agent and assistant agent) that collaborate through structured dialogue to accomplish tasks. Note that to control experimental variables, both the Single Agent and Role Playing baselines utilize identical tool sets to W ORKFORCE .

Implementation Details. For our implementation, we access all models via APIs, eliminating the need for GPUs. To ensure reproducibility, we configure API inference with greedy decoding. The default replanning threshold is set to 2. For evaluation methodology, we employ pass@3 sampling for W ORKFORCE with GPT-4o [OpenAI, 2024] and pass@1 for W ORKFORCE with Claude-3.7-sonnet [Anthropic, 2025]. Since some gold answers from GAIA had been leaked online, we blocked several websites to ensure fair comparison [OpenAI, 2024]. 4Table 1: Performance comparison of agent frameworks on GAIA [Mialon et al., 2023] validation set with accuracy score (%) as the evaluation metric. Scores of open-source and proprietary frameworks were obtained from the official leaderboard. The best-performing proprietary and open-source frameworks are highlighted in bold .Agent Name Base Model Level 1 Level 2 Level 3 Average 

Proprietary Frameworks 

DRP-val-v.1.0 - 56.60 48.84 15.38 46.06 omne O1-Preview † 60.38 44.19 23.08 46.06 Barcelona v0.1 Claude-3.5-Sonnet † 62.26 50.00 26.92 50.30 Ormind v0.1 Claude † 69.81 54.65 26.92 55.15 desearch GPT-4o 71.70 58.14 23.08 56.97 Anges Claude † 66.04 65.12 30.77 60.00 h2oGPTe Agent v1.6.8 [H2O.ai, 2024] Claude-3.5-Sonnet 67.92 67.44 42.31 63.64 Deep Research [OpenAI, 2024] O3 78.66 73.21 58.03 67.36 Trase Agent v0.3 [Trase, 2024] Claude † 83.02 69.77 46.15 70.30 Langfun Agent v2.1 ∗ [Google, 2023] Claude-3.7-Sonnet † 83.02 68.60 57.69 71.52 

Open-Source Frameworks 

FRIDAY [Wu et al., 2024] GPT-4-Turbo 45.28 34.88 11.54 34.55 Multi-Agent Exp v0.1 [Microsoft, 2024] GPT-4-Turbo 54.72 38.37 11.54 39.39 HuggingFace Agents [Roucher et al., 2025b] GPT-4o 58.49 43.02 19.23 44.24 Magnetic-One [Fourney et al., 2024a] O1 † 56.60 46.51 23.08 46.06 AutoAgent [Tang et al., 2025] Claude-3.5-Sonnet 71.70 53.49 26.92 55.15 Open Deep Research [Roucher et al., 2025a] O1 67.92 53.49 34.62 55.15 TapeAgents [Bahdanau et al., 2024] Claude-3.7-Sonnet 71.70 53.49 30.77 55.76 Single Agent GPT-4o 52.83 34.88 15.38 37.58 Role Playing [Li et al., 2023] GPT-4o 75.47 52.33 19.23 54.55 Role Playing ‡ [Li et al., 2023] GPT-4o † 81.14 54.65 23.08 58.18 

Ours 

WORKFORCE GPT-4o 81.14 58.14 26.92 60.61 WORKFORCE Claude-3.7-Sonnet 84.91 68.60 42.31 69.70 

Main Results. Several conclusions could be drawn from Table 1: 

(i) Workforce achieves state-of-the-art performance among open-source frameworks. Our WORKFORCE achieves 69.70% , consistently outperforming previous open-source frameworks across all difficulty levels. Under strictly controlled settings with the same model and toolkits, our GPT-4o-based W ORKFORCE achieves 60.61% accuracy - 23.03% higher than the Single Agent and 6.06% 

higher than the multi-agent baseline Role Playing. 

(ii) Workforce demonstrates comparable or even superior performance relative to commercial proprietary frameworks. While previous open-source frameworks have exhibited a substantial performance gap compared to closed-source alternatives, W ORKFORCE considerably narrows this divide. To our knowledge, W ORKFORCE is the first open-source system to exceed OpenAI’s Deep Research, achieving a 2.34% improvement, and also establishes a new Level 1 best by outperforming Langfun Agent v2.1 by 1.89% .

## 4 Multi-Agent Training: O PTIMIZED WORKFORCE LEARNING 

4.1 Training Strategy 

Motivation. The W ORKFORCE architecture separates domain-agnostic planning from domain-specific execution, allowing us to adapt to new domains by simply adding or replacing Worker Nodes while preserving the core planning mechanism. We introduce OPTIMIZED WORKFORCE LEARNING 

(OWL) , which focuses on enhancing a generalizable Planner Agent capable of handling diverse  

> 1†

Indicates systems that use multiple models, and only the primary model is listed.  

> ∗

Indicates frameworks that have released an early version but have not provided the latest version that can replicate these results.  

> ‡

Indicates an optimized version of role-playing where we introduced an LLM-based classifier that switches to O3-mini when tasks require more reasoning and coding, and uses GPT-4o otherwise. 

5Table 2: The statistics of the dataset. We use icons to repre-sent different agent capabilities: Web Browsing; Reasoning; 

Document Processing; Coding; Multimodal Handling. More details of training data can be found in Appendix D.4.                      

> Dataset # Total # SFT Filtering # DPO Filtering Agent Capabilities
> HotpotQA 998 495 354
> WikiTableQuestions 869 577 311
> Math-related 1100 487 297
> Infinity-MM 499 40 47
> Total/Average 3466 1599 1009 30 40 50
> Average Score (%)
> With Filtering (OWL) Without Filtering
> Base Model SFT SFT+DPO
> 36.36 41.21
> Base Model (Qwen2.5-32B-Instruct)
> 52.73 35.15 46.06

(a) Ablation study on trajectory filtering 

real-world scenarios. This design significantly reduces training overhead since only the Planner Agent requires intensive optimization, while Worker Nodes can leverage existing domain-specific tools with minimal adaptation. This “stable core, variable periphery” approach enables efficient knowledge transfer across domains and eliminates the need to retrain entire systems for new applications, substantially reducing computational costs while maintaining consistent performance. 

Implementation. More specifically, we adopt a two-phase training paradigm: (i) In the first phase, we employ supervised fine-tuning (SFT) to initialize the Planner Agent with fundamental task decompo-sition skills derived from expert demonstrations. (ii) Subsequently, we utilize reinforcement learning to further optimize the SFT-initialized Planner Agent. We select Direct Preference Optimization (DPO) [Rafailov et al., 2023] as our optimization algorithm of choice, as this phase enhances the quality of decomposition strategies beyond mere imitation of demonstrations, enabling the Planner to develop more sophisticated decision-making capabilities. 

4.2 Task Curriculum 

Motivation. The core innovation of W ORKFORCE is its architectural separation of domain-agnostic planning from domain-specific execution. For this design to be effective, the Planner Agent must possess robust generalization capabilities across diverse problem domains. This creates a fundamental tension: the Planner must simultaneously maintain a deep understanding across disparate domains while avoiding overfitting to specific task patterns or domains. To address this challenge, we developed a strategically balanced task curriculum that deliberately spans multiple capability dimensions required for general intelligence. Our curriculum design is guided by two key principles: (i) 

Capability Coverage : Exposing the Planner to diverse reasoning patterns and problem structures. 

(ii) Transfer Learning : Prioritizing tasks that develop complementary cognitive skills which can transfer across domains, rather than domain-specific knowledge. 

Implementation. More specifically, as is shown in Table 2, we carefully selected four datasets, each targeting distinct agent cognitive capabilities dimensions: (i) HotpotQA [Yang et al., 2018]: This dataset requires multi-hop reasoning based on online information, challenging the Planner to orchestrate complex information-seeking behaviors. (ii) WikiTableQuestions [Pasupat and Liang, 2015]: This dataset requires the Planner to formulate strategies for navigating, filtering, and operating over tabular information. (iii) Math-related Problems : This is a custom-curated collection of mathematical problems that require reasoning or coding to solve, covering various mathematical domains. They help the Planner develop skills in logical reasoning and computational problem-solving. (iv) Infinity-MM [Gu et al., 2024]: As a multimodal dataset, Infinity-MM challenges the Planner to orchestrate multimodal information processing., including vision, text, and structured data. 

4.3 Trajectory Synthesis 

Supervised Fine-tuning. We employed our W ORKFORCE approach (§3.1) with GPT-4o-mini to synthesize expert trajectories, which consist of planner-generated subtasks and worker-generated execution traces. To filter out low-quality data, we applied different evaluation metrics across datasets: For HotpotQA and WikiTableQuestions, we used accuracy metrics; For Infinity-MM, we used text cosine similarity with a 0.7 threshold between ground truth and generated answers; For math-related problems, we implemented LLM-as-a-judge to compare ground truth answers with workforce-generated solutions. Ultimately, as shown in Table 2 and 6, we obtained 1,599 filtered trajectories for supervised fine-tuning, with each trajectory containing an average of 3.41 subtasks. 6Table 3: Performance comparison between different planners. Each result is based on the Workforce framework with GPT-4o as the worker foundation model.                                           

> Planner Level 1 Level 2 Level 3 Average
> GPT-4o-mini [OpenAI, 2024] 64.15 45.34 19.23 47.27 Qwen2.5-72B-Instruct [Yang et al., 2024] 60.30 51.16 19.23 49.09 Claude-3.7-Sonnet [Anthropic, 2025] 81.13 53.49 34.61 59.39 GPT-4o [OpenAI, 2024] 81.14 58.14 26.92 60.61 Qwen2.5-32B-Instruct [Yang et al., 2024] 49.05 33.72 19.23 36.36
> w. OWL (SFT) 56.60 +7.55 39.53 +5.81 15.38 -3.85 41.21 +4.85
> w. OWL (SFT + DPO) 67.92 +18.87 51.16 +17.44 26.92 +7.69 52.73 +16.37

Reinforcement Learning. We use the SFT-initialized model to generate pair-wise trajectories for DPO [Rafailov et al., 2023]. Specifically, for each question in our collected dataset, we roll out n = 4 

distinct trajectories. The evaluation of these generated trajectories is the same as in the SFT stage. Then, we construct preference pairs from the n trajectories generated for each question based on their evaluation outcomes. For Math, HotpotQA, and WikiTableQuestions tasks, trajectories that are correct are labeled as “chosen”, while incorrect answers are labeled as “rejected”. For Infinity-MM dataset, trajectories whose final text cosine similarity scores exceeded the same threshold as in the SFT stage (0.7) are labeled as “chosen”, while those below the threshold are labeled as “rejected”. As shown in Table 2, we collect 1009 filtered trajectories pairs. 

4.4 Experiments 

Baselines. We compare our approach against multiple proprietary and open-source models as baselines, including the GPT-4o series [OpenAI, 2024], Claude-3.7-Sonnet [Anthropic, 2025], and the Qwen2.5 series [Yang et al., 2024]. These models represent the current state-of-the-art in language model capabilities across different scales and architectures. 

Implementation Details. Our model training is conducted on a computing cluster equipped with 8 NVIDIA H100 GPUs. We use the LlamaFactory [Zheng et al., 2024] framework for managing and executing our training procedures. Specifically, for all the models we trained, the input sequences are truncated to a maximum length of 32,768 tokens and the learning rate is set to 10 −5. All models are trained for a total of two epochs. To optimize memory usage and training efficiency, we use bfloat16 mixed-precision training. The effective batch size is 12, achieved through 1 per-device batch size combined with 12 gradient accumulation steps. 

Main Results. Table 3 reveals multiple important findings: 

(i) OWL significantly enhances planner capabilities, enabling open-source models to outperform proprietary alternatives. The OWL-trained Qwen2.5-32B-Instruct model demonstrates remarkable improvements with a substantial 16.37% gain. OWL enables open-source model reaches 52.73% 

performance, surpassing both the proprietary GPT-4o-mini (47.27%) and the larger Qwen2.5-72B-Instruct (49.09%). While GPT-4o (60.61%) still maintains an advantage, our OWL-trained model achieves comparable performance to GPT-4o (26.92%) on the more challenging Level 3 tasks. 

(ii) Reinforcement learning significantly boosts planner generalization. While supervised fine-tuning (SFT) alone improves performance on simpler tasks (Level 1 and 2), it shows a regression on the most complex tasks (Level 3), with performance dropping by 3.85%. However, when combined with DPO, our approach not only recovers this performance but significantly exceeds the base model across all difficulty levels, with a 7.69% improvement on Level 3 tasks. 

Ablation Study. We evaluated the impact of trajectory filtering on model performance. As shown in Figure 2a, models trained on filtered trajectories consistently outperform those trained on unfiltered data, which underscores that data quality is more critical than quantity for effective planner training. 

## 5 Analysis 

Performance Across Capability Types. Each evaluation case may require one or more types of agent capabilities (e.g., Web Browsing, Coding, Multimodal Processing). As shown in Figure 3(a), our experimental results demonstrate that: (i) The W ORKFORCE approach consistently outperforms both 700.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1Single Agent - GPT-4o Role Playing - GPT-4o Workforce - Qwen2.5-32B-Instruct - w. OWL 

> Average Score (%)
> Web Browsing Multi-Modality Diverse Filetype Reading Reasoning Coding
> Workforce - GPT-4o Workforce - Qwen2.5-32B-Instruct

0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.75 

> Average Score (%)
> Claude-3.7-Sonnet GPT-4o

Replanning Count   

> 012

(b) Test-time scaling (a) Performance by Capability 

> 0.43 0.54 0.60 0.51 0.60 0.69

Figure 3: Left : Average scores on GAIA validation categorized by different agent capabilities. Blue compares different agent frameworks, while brown compares different planner models. Right :Changes in Workforce performance as the 