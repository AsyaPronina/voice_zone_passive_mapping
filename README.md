# voice_zone_passive_mapping_ui
Python GUI for Voice Zone Passive Mapping


>**NOTE: Tool is developed for Windows OS! Though, it can be launched on Linux, but can contain bugs and have not nice look.**  

## How to configure enviroment for development using Miniconda:
- Clone repository to your system:
  ```bash
  git clone git@github.com:AsyaPronina/voice_zone_passive_mapping_ui.git
  ```
- Install Miniconda on your system: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
- Go to Anaconda Prompt from your "Start Menu" on Windows or just open a new bash (to catch newly installed miniconda) on Linux.
- In the Anaconda Prompt:
  - Go to directory of repository:
    ```bash
    cd <path-to>/voice_zone_passive_mapping_ui/
    ```
  - Type:
    ```bash
    conda env create -f environment.yml
    ```
    ```bash
    conda activate voice-zone-passive-mapping-ui
    ```
  - Launch the tool!
    ```bash
    python tool.py
    ```
