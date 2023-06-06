##  🕉️ SCAI: Social Contract AI

Supporting effective human—AI collaboration through democratically aligned language agents.


### 🧐 What is this?


#### 🔀 Background: Steering AI Systems
As Large Language Models (LLMs) advance, human-dependent fine-tuning techniques like RLHF [e.g. [1](https://proceedings.neurips.cc/paper_files/paper/2017/file/d5e2c0adad503c91f91df240d0cd4e49-Paper.pdf), [2](https://proceedings.neurips.cc/paper_files/paper/2022/file/b1efde53be364a73914f58805a001731-Paper-Conference.pdf)] are becoming less effective [e.g. [3](https://arxiv.org/pdf/1606.06565.pdf), [4](https://arxiv.org/pdf/2304.00612.pdf)]. This necessitates the adoption of self-improvement methods such as Constitutional AI [[5](https://arxiv.org/pdf/2212.08073.pdf)], which combine AI-supervised fine-tuning with RLAIF for the development of helpful, harmless, and honest language agents like Claude.


#### 🧘🏾‍♀️ Our Proposal: A bottom-up alternative to Constitutional AI 
The details within the "constitutions" employed in paradigms like CAI are increasingly important for defining the values, behavioral boundaries, and capabilities of LLMs. These are typically developed top-down and in isolation by corporations. We offer a democratic alternative: social contract AI (scai), an open-ended platform enabling multiple (simulated) users with crowd-sourced personas to interact and collaboratively define a model's constitution via [meta-prompt](https://noahgoodman.substack.com/p/meta-prompt-a-simple-self-improving). We explain the construction of our simulator and demonstrate its potential for exploring trade-offs between users (with crowd-sourced personas), eliciting subtle constitutional aspects, and evaluating different utility metrics.

#### ✅ Expected outcome
Our simulation is expected to generate practical "system message" prompts for chatbots like Claude or GPT-4, as well as provide a large-scale, diverse dataset for fine-tuning language models (which can then tested on benchmarks similar to those in the CAI paper).


### 📂 Repro structure

```
├── src                  
│   └── scai      
│       ├── modules           
│       ├── data  
│       ├── custom_chat_models   
│       └── hugging_face_models
├── docs                
│   ├── build            
│   └── source           
├── experiments         
├── LICENSE              
├── requirements.txt      
└── .gitignore           
```


### 📖 Documentation
<a name="documentation"></a>

#### 🚀 Getting started 
##### Using miniconda
1. `curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh`
2. `bash Miniconda3-latest-MacOSX-x86_64.sh`
3. close and reopen terminal
4. `source ~/.bashrc`
5. `conda create --name name-of-my-env python==3.10`
6. `conda activate name-of-my-env`
7. `pip install -e .` 

##### Using poetry (will update this later)
1. `curl -sSL https://install.python-poetry.org | python -`
2. `export PATH="/Users/YOUR_NAM/.local/bin:$PATH`
3. `poetry install`

#### 📖 Updating Docs (will update this later)
1. `sphinx-build -b html docs/source docs/build` (build docs)
2. `open docs/build/index.html` to open docs locally.  

When you are adding a new class or make modifications to an important functionality, please document them in `docs/source`. Run `sphinx-build -b html docs/source docs/build` to update the docs.