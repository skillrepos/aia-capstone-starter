# Enterprise AI Accelerator - Day 3

## Building Out Your Capstone Project ##

These instructions will guide you through configuring a GitHub Codespaces environment that you can use to do the labs. 

<br><br>

**1. Click on the button below to start a new codespace from this repository.**

Click here ➡️  [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/skillrepos/aia-capstone-starter?quickstart=1)

<br><br>

**2. Then click on the option to create a new codespace. *While this is running, you can be creating your Hugging Face token in the next step!***

![Creating new codespace from button](./images/aia-3-24.png?raw=true "Creating new codespace from button")

This will run for a long time while it gets everything ready.

After the initial startup, it will run a script to setup the python environment and install needed python pieces. This will take several more minutes to run. It will look like this while this is running.

![Final prep](./images/aia-3-25.png?raw=true "Final prep")

The codespace is ready to use when you see output like the one shown below in its terminal.

![Ready to use](./images/aia-3-26.png?raw=true "Ready to use")

<br><br>

**3. Set up your HuggingFace API token.**

The RAG agent uses HuggingFace's Inference API to generate LLM responses. You'll need a free API token:

A. Go to (https://huggingface.co)[https://huggingface.co] and log in if you already have an account. If you need to create an account, click the *Sign Up* button or visit (https://huggingface.co/join)[https://huggingface.co/join]

![HF login](./images/aia-3-19.png?raw=true "HF login")

<br>
   
B. Navigate to (https://huggingface.co/settings/tokens)[https://huggingface.co/settings/tokens].  Click on *+ Create new token*.

![Get token](./images/aia-3-20.png?raw=true "Get token")


C. Select **Read** for the token type and provide a name.

![Read token](./images/aia-3-21.png?raw=true "Read token")
   
D. Click on the *Create token* button and copy the token (it starts with `hf_`). Save it somewhere.

![Save/copy token](./images/aia-3-22.png?raw=true "Save/copy token")

E. For all runs of agents in the labs, make sure the token is set in your terminal before running the agent:

```bash
export HF_TOKEN="hf_your_token_here"
```

F. Alternatively, to make this permanent for your codespace session, add it to your shell profile:

```bash
echo 'export HF_TOKEN="hf_your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

<br><br>

**4. Open the labs file.**

You can open the [labs.md](./labs.md) file either in your codespace or in a separate browswer tab/instance.**

![Labs](./images/aia-2-35.png?raw=true "Labs")

<br>

**Now, you are ready for the labs!**

<br><br>



---

## License and Use

These materials are provided as part of the **Enterprise AI Accelerator Workshop** conducted by **TechUpSkills (Brent Laster)**.

Use of this repository is permitted **only for registered workshop participants** for their own personal learning and
practice. Redistribution, republication, or reuse of any part of these materials for teaching, commercial, or derivative
purposes is not allowed without written permission.

© 2025 TechUpSkills / Brent Laster. All rights reserved.









