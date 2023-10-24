##  🕉️ Social Contract AI: Aligning AI Assistants with Implicit Group Norms


### 🧐 What is this?
SCAI is a simulator for studying practical alignment questions with language feedback/verbal reinforcement [[1](https://github.com/ngoodman/metaprompt), [2](https://arxiv.org/abs/2303.11366), [3](https://arxiv.org/abs/2310.02304)].

We are currently exploring a few different directions (work in progress):

1. Learning unknown user preferences from observed game interactions in the ultimatum game [[3](https://en.wikipedia.org/wiki/Ultimatum_game)].
![Illustration of Ultimatum Game Setup](./assets/ultimatum_fig.png)

2. Red-teaming with language models [[5](https://arxiv.org/abs/2202.03286)].

3. Exploring theory-of-mind and planning in the buyer-seller game [[4](https://openreview.net/pdf?id=yd8VOEpw8h)].


### 📂 Repro structure
```
├── src                  
│   └── scai      
│       ├── chat_models
│       ├── games
│       └── memory       
├── experiments    
│   ├── ultimatum_simulation
│   ├── buyer_seller
│   └── red_teaming
├── LICENSE              
├── requirements.txt    
├── pyproject.toml    
├── setup.py    
└── .gitignore           
```

#### 🚀 Getting started 
##### Using miniforge
1. install miniforge from `https://github.com/conda-forge/miniforge` (eg `Miniforge3-MacOSX-arm64`)
2. `bash Miniforge3-MacOSX-arm64.sh`
3. close terminal
4. `conda create --name scai python==3.10`
5. `conda activate scai`
6. `pip install -e .` 