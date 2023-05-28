##  🕉️ SCAI: Social Contract AI

Useful, self-improving language agents. Insipred by [meta-prompt](https://noahgoodman.substack.com/p/meta-prompt-a-simple-self-improving). Written in [LangChain](https://github.com/hwchase17/langchain).

### 🧐 What is this?
#### 📖 Background
Large Language Models (LLMs) are exciting 🚀😍. However, as these models continue to advance, current fine-tuning methods that depend on human oversight [e.g. [1](https://proceedings.neurips.cc/paper_files/paper/2022/file/b1efde53be364a73914f58805a001731-Paper-Conference.pdf)] might become less effective [e.g. [2](https://arxiv.org/pdf/1606.06565.pdf), [3](https://arxiv.org/pdf/2211.03540.pdf), [4](https://arxiv.org/pdf/2212.08073.pdf)]. This opens up exciting new possibilities for self-improvement methods [e.g. [5](https://noahgoodman.substack.com/p/meta-prompt-a-simple-self-improving)].

<p align="left">
    <img src="assets/stack.jpg" alt="contract" width="20%">
</p>




#### The SCAI Approach

##### The Contract
<p align="left">
    <img src="assets/contract.jpg" alt="contract" width="20%">
</p>



##### Stage 1: Self-improvement with meta-prompting

###### System

###### Assistant
<p align="left">
    <img src="assets/assistant.jpg" alt="contract" width="20%">
</p>

###### User(s)

##### Stage 2: Fine-tuning on self-generated data
tbd


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

##### Using poetry (currently not supported)
1. `curl -sSL https://install.python-poetry.org | python -`
2. `export PATH="/Users/YOUR_NAM/.local/bin:$PATH`
3. `poetry install`

#### 📖 Updating Docs
1. `sphinx-build -b html docs/source docs/build` (build docs)
2. `open docs/build/index.html` to open docs locally.  

When you are adding a new class or make modifications to an important functionality, please document them in `docs/source`. Run `sphinx-build -b html docs/source docs/build` to update the docs.