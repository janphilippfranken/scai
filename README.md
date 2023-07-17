##  🕉️ SCAI: Social Contract AI

A Simulator for Learning AI Social Contracts with Meta-Prompt
<!-- 
### 🧐 What is this?


#### 🔀 Background



#### Our Proposal: A (Decentralized) Simulator for Learning AI Constitutions with Verbal Reinforcement -->


### 📂 Repro structure

```
├── src                  
│   └── scai      
│       ├── agents
│       ├── prompts
│       ├── context
│       └── memory
├── docs                
│   ├── build            
│   └── source           
├── experiments    
│   ├── simulator
│       ├── config  
│       ├── custom_chat_models
│       └── sim_res
├── LICENSE              
├── requirements.txt      
└── .gitignore           
```


### 📖 Documentation
<a name="documentation"></a>

#### 🚀 Getting started 
##### Using miniforge
1. install miniforge from `https://github.com/conda-forge/miniforge` (eg `Miniforge3-MacOSX-arm64`)
2. `bash Miniforge3-MacOSX-arm64.sh`
3. close terminal
4. `conda create --name name-of-my-env python==3.10`
5. `conda activate name-of-my-env`
6. `pip install -e .` 

<!-- ##### Using poetry (will update this later)
1. `curl -sSL https://install.python-poetry.org | python -`
2. `export PATH="/Users/YOUR_NAM/.local/bin:$PATH`
3. `poetry install` -->

#### 📖 Updating Docs
1. `sphinx-build -b html docs/source docs/build` (build)
2. `open docs/build/index.html` (open)