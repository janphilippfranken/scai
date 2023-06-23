##  🕉️ SCAI: Social Contract AI

A Simulator for Learning AI Constitutions

### 🧐 What is this?

#### 🧘🏾‍♀️ A (Decentralized) Simulator for Learning AI Constitutions with Meta-Prompt
The details within the 'constitutions' employed in paradigms like [Constitutional AI](https://www.anthropic.com/index/claudes-constitution) are increasingly important for defining the values, behavioral bounds, and capabilities of LLMs. These have previously been developed top-down and in isolation. We offer a democratic alternative: Social Contract AI (SCAI), an open-ended platform enabling multiple (simulated) users to interact and collaboratively define a model's constitution via meta-prompt. We explain the construction of our simulator and demonstrate its potential for exploring trade-offs between users (with crowd-sourced personas), eliciting subtle constitutional aspects, and evaluating different utility metrics.


### 📂 Repro structure

```
├── src                  
│   └── scai      
│       ├── modules 
│           ├── assistant     
│           ├── episode
│           ├── memory
│           ├── meta_prompt
│           ├── task
│           └── user
├── docs                
│   ├── build            
│   └── source           
├── experiments    
│   ├── v1
│       ├── config  
│       ├── custom_chat_models
│       └── sim_res
│   └── v2
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