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
- In the Anaconda Prompt/Bash shell:
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
    You are ready to edit it!

## This tool is implemented through MVVM pattern:
![image](https://user-images.githubusercontent.com/15359579/143722373-25d2296d-6346-4c61-bb89-d8b253df1dde.png)
https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel

## Map of UI and Python classes:
![image](https://user-images.githubusercontent.com/15359579/143721501-e13522cc-73c7-45b7-a640-50eb60271f44.png)

![image](https://user-images.githubusercontent.com/15359579/143722211-7172d4b2-e819-486e-a9cd-b710f1ad728a.png)


## Integration of mapping algorithm is WIP on the branch: _integrate_mapping_algorithm_wip_

## Known issues:
* Objects pictures are not yet handled in any view of the tool

