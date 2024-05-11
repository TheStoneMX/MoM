# MoM
Mixture of Models (MoM) for Problem Solving

The Mixture of Models (MoM) approach to solve various problems like logic reasoning, coding, and sentence generation. Three architectures are investigated:

Master: Multiple LLMs ("workers") gather information, and a Master LLM (GPT-4) analyzes it to provide a final answer.
Duo Poly: Two co-founders (CLAW 3 Opus and GPT-4 Turbo) discuss and debate the problem to find a solution.
Democracy: All available LLMs vote on the best solution out of those proposed.
These architectures are tested on four problems:

Logic reasoning: Marble placement in an inverted cup.
Age reasoning: Calculating age based on relative ages.
Coding: Python code solution.
Sentence generation: Sentences ending with "apples".
Results: The King architecture achieved the highest accuracy, solving all problems except sentence generation. Duo Poly performed well but was less accurate than the King. Democracy had the lowest accuracy.

Conclusion: The MoM approach is a promising strategy for solving complex problems, with the King architecture being the most successful in this demonstration. However, other architectures may be better suited for different types of problems.

Setup
  - git clone https://github.com/TheStoneMX/MoM.git
  - cd dir
  - pip install -r requirements.txt
  - SET your API KEYS in .env
  - Download ollama (https://ollama.com/download)
  - ollama pull "modelname" (pick the models you wanna use)
  - adjust ollama model list in code
  - set your problem in problem.txt
  - python theking2.py (The King Arch)
  - python duop.py (The Duopoly Arch)
  - python democracy.py (The Democracy Arch)

