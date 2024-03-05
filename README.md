# trello-to-planner

## Assumptions
- You already have vscode installed
- Python installed with virtual environment
- You can MS graph at https://developer.microsoft.com/en-us/graph/graph-explorer
- Ensure you have the necessary permissions to get, patch and post in MS graph 

## Pre-requisite 
1. Export data from Trello 
    
    1.1 Go to Trello board

    1.2 On the upper right corner next to Share button, click on the `...` then click `print, export and share` then `export as json` 

    1.3 New tab will appear with sample URL https://trello.com/b/tOIeItvM.json right click then click `save as` json with file name of Trello board eg. site-reliability-engineer.json

    1.4 Copy the json file under `data ` file path that comes with the repository

2. Go to MS graph to get the `Access Token`
    
    2.1 Navigate to URL https://developer.microsoft.com/en-us/graph/graph-explorer to get the  `Access Token`. 
    
    2.2 Save it in a notepad, you will use that later in the python code. 

3. Go Planner to get the `groupID`
    
    3.1 Navigate to planner URL of your Teams channel where the Trello cards will be migration eg. https://tasks.office.com/opentextcorporation.onmicrosoft.com/en-US/Home/Planner/#/plantaskboard?groupId=afcd4a12-cc7b-4bcb-84ad-2ac80d6b6185&planId=LlQlQkEFc0qn_enuDyBdBGQAD6Mu to get the `groupID` eg. afcd4a12-cc7b-4bcb-84ad-2ac80d6b6185 
    
    3.2 Save it in a notepad, you will use that later in the python code. 

4. Prepare python environment
    4.1 Initialize python virtual env
        ```bash
        # initialise virtualenv directory
        python -m virtualenv .venv
        ```
    4.2 Install dependencies
        ```bash
        # load python paths
        source .venv/Scripts/activate # windows
        source .venv/bin/activate # linux
    
        # upgrade pip python package manager
        pip install --upgrade pip

        # install python dependencies
        pip install -r requirements.txt
        ```

## How to run the migrate.py code

1. Activate virtual environment by the below command: 
    source .venv/Scripts/activate
  

    