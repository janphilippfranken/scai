##  🕉️ SCAI: Social Contract AI

Useful, self-improving language agents. Written in [LangChain](https://github.com/hwchase17/langchain).

#### <span style="color: red;">@dev team</span>: Please read the [documentation](#documentation) below.
 
#### 📖 Background
Large Language Models (LLMs) are exciting 😍🚀. Transforming base models into useful instruction-following and chat models requires additional fine-tuning. This vertical momentum is primarily driven by data like human demonstrations or preference labels  [e.g. [1](https://proceedings.neurips.cc/paper_files/paper/2022/file/b1efde53be364a73914f58805a001731-Paper-Conference.pdf)]. However, as LLMs become more capable, the effectiveness of methods relying on human oversight is likely going to decrease [e.g. [2](https://arxiv.org/pdf/1606.06565.pdf), [3](https://arxiv.org/pdf/2211.03540.pdf), [4](https://arxiv.org/pdf/2212.08073.pdf)]. This opens up exciting possibilities for new data-generation methods based on self-improvement [e.g. [5](https://noahgoodman.substack.com/p/meta-prompt-a-simple-self-improving)].


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


### 📖 [Documentation] ‼️
<a name="documentation"></a>
Currently only available locally.

To build docs from source/open docs, run `sphinx-build -b html docs/source docs/build`.
Thereafter, run `open docs/build/index.html` to open docs. 

As we are working on this in a bigger team, its important to keep this up to date.

When you are adding a new class or make modifications to an important functionality, please document them in `docs/source`. 
E.g., if you changed smth to a model class such as the `assistant`, please document this in `docs/source/models/models.rst`.

Thereafter, run `sphinx-build -b html docs/source docs/build` to update the docs.






