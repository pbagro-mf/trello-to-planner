import json
import requests
from time import sleep

# Define your schema value mapper algorithm
def schema_value_mapper(data):
    # Your mapping logic here
    # For example, let's just capitalize all string values
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, dict):
        return {key: schema_value_mapper(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [schema_value_mapper(item) for item in data]
    else:
        return data

# Load JSON file
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_active_columns(json_data):
    active_columns = []
    for table_dict in json_data['lists']:
    #   print(table_dict)
        if table_dict['closed'] == False and table_dict['name'] != 'Done' and table_dict['name'] != 'Closed not complete':
            active_columns.append(table_dict)
            # print(table_dict)
    return active_columns

def filter_active_cards(json_data, card_data):
    active_cards = []
    id_list = [d["id"] for d in json_data]
    # print(id_list)
    for card in card_data:
        if card['idList'] in id_list:
            # print(json.dumps(card))
            active_cards.append(card)
    return active_cards

def print_json_tree(data, path="", printed_structures=None):
    if printed_structures is None:
        printed_structures = set()

    if isinstance(data, dict):
        for key, value in data.items():
            sub_path = f"{path}.{key}" if path else key
            if id(value) not in printed_structures:
                print(sub_path)
                printed_structures.add(id(value))
                print_json_tree(value, sub_path, printed_structures)
            else:
                pass

    elif isinstance(data, list):
        for idx, item in enumerate(data):
            sub_path = f"{path}[{idx}]"
            if id(item) not in printed_structures:
                print_json_tree(item, sub_path, printed_structures)
            else:
                pass

# Transform JSON based on schema value mapper algorithm
def transform_json(json_data):
    return schema_value_mapper(json_data)

# Create planner plans
def create_planner_plans(group_token,planner_title, auth_token):
    planner_url = "https://graph.microsoft.com/beta/planner/plans"
    group_url = f"https://graph.microsoft.com/beta/groups/{group_token}"
    payload = {
        "container": {
            "url": group_url
        },
        "title": f"{planner_title}"
    }
    # Headers
    headers = {
    "Authorization": auth_token,
    "Content-Type": "application/json"
    }
    try:
        # Sending POST request to create planner
        response = requests.post(planner_url, headers=headers, json=payload)

        # Checking if request was successful (status code 201)
        if response.status_code == 201:
            print(f"Plan {payload['title']} created successfully.")
        else:
            print(f"Failed to create planner. Status code: {response.status_code}")
            print(response.text)  # Printing error message if any
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Get Planner Plans
def get_planner_plans(group_id, auth_token):
    planner_url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/planner/plans"
    headers = {
        "Authorization": auth_token
    }
    all_plans = []
    try:
        # Sending POST request to create planner
        response = requests.get(planner_url, headers=headers)

        # Checking if request was successful (status code 201)
        if response.status_code == 200:
            plans = response.json()
            for plan in plans['value']:
                # print(plan)
                all_plans.append({
                    "title": plan['title'],
                    "id": plan['id'],
                    "etag": plan['@odata.etag']
                })
                # print(f"title: {plan['title']}")
                # print(f"id: {plan['id']}")
                # print(f"etag: {plan['@odata.etag']}")            
        else:
            print(f"Failed to get planner. Status code: {response.status_code}")
            print(response.text)  # Printing error message if any
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return all_plans

# Delete Planner Plans
def delete_planner_plans(plans, auth_token, group_token):
    headers = {
            "Authorization": auth_token,
            "If-Match": ""
        }
    not_clean = True
    delete_plan_list = []
    while(not_clean):
        all_plans = get_planner_plans(group_id=group_token, auth_token=auth_token)
        for plan in all_plans:
            if plan["title"] in plans:
                print(f"title: {plan['title']}")
                # print(f"id: {plan['id']}")
                # print(f"url: https://graph.microsoft.com/beta/planner/plans/{plan['id']}")
                delete_plan_list.append(plan)
        if len(delete_plan_list) == 0:
            not_clean=False
        
        for plan in delete_plan_list:
            # get etag instance
            all_plans = get_planner_plans(group_id=group_token, auth_token=auth_token)
            plan_index = all_plans.index(plan)
            # print(all_plans[plan_index])

            try:
                planner_url = f"https://tasks.office.com/opentextcorporation.onmicrosoft.com/en-US/Home/Planner/#/plantaskboard?groupId=fe9029cd-804c-476a-b30e-21ecdff8143b&planId={plan['id']}"
                delete_url = f"https://graph.microsoft.com/beta/planner/plans/{plan['id']}"
                # print(planner_url)
                headers["If-Match"] = plan["etag"]
                # print(plan['title'])
                # print(planner_url)
                # print(plan['headers']['If-Match'])
                # Sending POST request to create planner
                response = requests.delete(delete_url, headers=headers)
                # Checking if request was successful (status code 201)
                if response.status_code == 204:
                    print("Planner deleted successfully.")
                else:
                    print(f"Failed to delete planner. Status code: {response.status_code}")
                    print(response.text)  # Printing error message if any
                pass
            except Exception as e:
                print(f"An error occurred: {str(e)}")

# Create planner buckets
def create_planner_buckets(plan_values, auth_token, group_token):
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }
    # Loop through planner and buckets
    for bucket in plan_values['json_data']:

        # get etag instance
        all_plans = get_planner_plans(group_id=group_token, auth_token=auth_token)
        # print(all_plans)
        for plan in all_plans:
            if plan_values['plan_name'] == plan["title"]:
                payload = {
                    "name": bucket['name'],
                    "planId": plan["id"],
                    "orderHint": " !"
                }

                try:                    
                    bucket_url = "https://graph.microsoft.com/v1.0/planner/buckets"
                    response = requests.post(bucket_url, headers=headers, json=payload)
                    # Checking if request was successful (status code 201)
                    if response.status_code == 201:
                        print(f"Planner {plan['title']} bucket {bucket['name']} created successfully.")
                    else:
                        print(f"Failed to create planner {plan['title']} bucket {bucket['name']}. Status code: {response.status_code}")
                        print(response.text)  # Printing error message if any
                    pass
                except Exception as e:
                    print(f"An error occurred: {str(e)}")

# Get planner buckets
def get_planner_buckets(plan_values, auth_token, group_token):
    headers = {
        "Authorization": auth_token
    }
    planner_buckets = {}
    # get etag instance
    all_plans = get_planner_plans(group_id=group_token, auth_token=auth_token)
    for plan in all_plans:
        if plan_values['plan_name'] == plan["title"]:

            try:
                planner_url = f"https://graph.microsoft.com/beta/planner/plans/{plan['id']}/buckets"                    
                # print(planner_url)
                # print(plan['title'])
                # print(planner_url)
                # print(plan['headers']['If-Match'])
                # Sending POST request to create planner
                response = requests.get(planner_url, headers=headers)
                # Checking if request was successful (status code 201)
                if response.status_code == 200:
                    planner_buckets = dict(response.json())
                else:
                    print(response.text)  # Printing error message if any
                pass
            except Exception as e:
                print(f"An error occurred: {str(e)}")
    return planner_buckets

# Create bucket tasks
def create_bucket_tasks(plan_values, auth_token, group_token):
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }
    all_buckets = get_planner_buckets(plan_values=plan_values,auth_token=auth_token,group_token=group_token)
    bucket_lists_names = [d["name"] for d in all_buckets['value']]
    
    # print(f"Creating tasks for planner: {plan_values['plan_name']}")
    # print(f"trello tasks:")
    trello_list_names = [d["name"] for d in plan_values['json_data']]
    trello_list_ids = [d["id"] for d in plan_values['json_data']]
    # print(bucket_lists_names)
    # print(trello_list_ids)

    # print(bucket_list)
    # active_cards - 
    # idList -> list name == bucket name -> bucket id
    
    # print(json.dumps(active_cards))
    active_cards = plan_values['active_cards']
    # Payload
    for card in active_cards:
        # print(json.dumps(card))
        # print(trello_list_ids)
        trello_list_name = trello_list_names[trello_list_ids.index(card['idList'])]
        # print(f"trello id list name: {trello_list_name}")
        # planner bucket name index
        # print(f"planner bucket index: {bucket_lists_names.index(trello_list_name)}")
        # planner bucket name id
        planner_bucket = all_buckets['value'][bucket_lists_names.index(trello_list_name)]
        # print(f"planner bucket name id: {planner_bucket['id']}")
        # planner plan id
        # print(f"planner plan id: {planner_bucket['planId']}")
        
        payload = {
            "planId": planner_bucket['planId'],
            "title": card["name"],
            "bucketId": planner_bucket['id'],
            "description": card['desc'],
            "assignments": {}
        }
    
        try:
            # Sending POST request to create planner task
            create_task_url = "https://graph.microsoft.com/beta/planner/tasks"
            response = requests.post(create_task_url, json=payload, headers=headers)
            # Checking if request was successful (status code 201)
            if response.status_code == 201:
                print(f"Planner {plan_values['plan_name']} task {payload['title']} successfully created.")
                # print(response.text)

                # Update task immediately after creation
                description = card['desc']
                etag = json.loads(response.text)["@odata.etag"]
                task_id = json.loads(response.text)["id"]
                update_planner_tasks(
                    plan_name=plan_values['plan_name'],
                    task_name=payload['title'],
                    auth_token=auth_token,
                    description=description,
                    task_id=task_id
                )
            else:
                print(f"Failed to get planner. Status code: {response.status_code}")
                print(response.text)  # Printing error message if any
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        
            

# Get Planner Task Details
def get_planner_tasks_details(task_id, auth_token):
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }
    try:
        # Sending GET request to get planner tasks
        get_task_url = f"https://graph.microsoft.com/v1.0/planner/tasks/{task_id}/details"
        response = requests.get(get_task_url, headers=headers)
        # Checking if request was successful (status code 201)
        if response.status_code == 200:
            return json.loads(response.text)

        else:
            print(f"Failed to get planner tasks. Status code: {response.status_code}")
            print(response.text)  # Printing error message if any
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Update Planner Tasks
def update_planner_tasks(plan_name, task_name, auth_token, description, task_id):
    headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json",
            "If-Match": ""
        }
    
    payload = {
        "description": description
    }
    try:
        etag = get_planner_tasks_details(task_id=task_id,auth_token=auth_token)["@odata.etag"]
        print(f"etag: {etag}")
        headers["If-Match"] = etag
        # Sending POST request to create planner task
        update_task_url = f"https://graph.microsoft.com/v1.0/planner/tasks/{task_id}/details"
        response = requests.patch(update_task_url, json=payload, headers=headers)
        # Checking if request was successful (status code 201)
        if response.status_code == 200 or response.status_code == 204:
            print(f"Planner {plan_name} task {task_name} successfully updated.")
        else:
            print(f"Failed to update planner task {task_id}. Status code: {response.status_code}")
            print(headers['If-Match'])
            print(response.text)  # Printing error message if any
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Main function
def main():
    # initialise Global Vars
    group_token = "afcd4a12-cc7b-4bcb-84ad-2ac80d6b6185"
    
    # CSD General token "fe9029cd-804c-476a-b30e-21ecdff8143b"
    # FOD token "f08ba8e6-8102-4bbe-96a7-0fc1c07fbc5d"
    # OT Support "afcd4a12-cc7b-4bcb-84ad-2ac80d6b6185"

    # Load JSON file
    data_path = "data"
    # Access Token
    auth_token = "Bearer eyJ0eXAiOiJKV1QiLCJub25jZSI6IldWdkhNakhmMllXR3NvSXRjemVSY1dsTkFTZ0NyMnFFSG00ZzFwSVVaV28iLCJhbGciOiJSUzI1NiIsIng1dCI6IlhSdmtvOFA3QTNVYVdTblU3Yk05blQwTWpoQSIsImtpZCI6IlhSdmtvOFA3QTNVYVdTblU3Yk05blQwTWpoQSJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8xMGExODQ3Ny1kNTMzLTRlY2QtYTc4ZC05MTZkYmQ4NDlkN2MvIiwiaWF0IjoxNzA5NjcwNTM0LCJuYmYiOjE3MDk2NzA1MzQsImV4cCI6MTcwOTY3NTQ5MCwiYWNjdCI6MCwiYWNyIjoiMSIsImFpbyI6IkFUUUF5LzhXQUFBQWJKdWFOR2VjM0h4RjJUbFhnSjFzeGFuWnlNZ242bkZOdTNNaVFZRTZMMVV5QUlPSUtJNnVEKy9yY3E1dWtEUGIiLCJhbXIiOlsicHdkIl0sImFwcF9kaXNwbGF5bmFtZSI6IkdyYXBoIEV4cGxvcmVyIiwiYXBwaWQiOiJkZThiYzhiNS1kOWY5LTQ4YjEtYThhZC1iNzQ4ZGE3MjUwNjQiLCJhcHBpZGFjciI6IjAiLCJmYW1pbHlfbmFtZSI6Ik0gQmFncm8iLCJnaXZlbl9uYW1lIjoiUHJpbmNlc3MgSm95IiwiaWR0eXAiOiJ1c2VyIiwiaXBhZGRyIjoiMjAwMTo4MDA0OjE1MjA6MjY2OTo3ZGE0OmRkYjo5N2M0OjZhODgiLCJuYW1lIjoiUHJpbmNlc3MgSm95IE0gQmFncm8iLCJvaWQiOiIwMzJmOGEyZC02MDUwLTQ2MTItYmJkYy0xNmNhOGRjNzgxYzQiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTQyMDQyMDAwLTc4MTk3NjAyMS0xMzE4NzI1ODg1LTM5ODczNyIsInBsYXRmIjoiMyIsInB1aWQiOiIxMDAzMjAwMjYwQTIzMjMwIiwicmgiOiIwLkFSY0FkNFNoRURQVnpVNm5qWkZ0dllTZGZBTUFBQUFBQUFBQXdBQUFBQUFBQUFBWEFMOC4iLCJzY3AiOiJBY2Nlc3NSZXZpZXcuUmVhZC5BbGwgQWNjZXNzUmV2aWV3LlJlYWRXcml0ZS5BbGwgQWNjZXNzUmV2aWV3LlJlYWRXcml0ZS5NZW1iZXJzaGlwIEFQSUNvbm5lY3RvcnMuUmVhZC5BbGwgQ2xvdWRQQy5SZWFkV3JpdGUuQWxsIERldmljZU1hbmFnZW1lbnRBcHBzLlJlYWQuQWxsIERldmljZU1hbmFnZW1lbnRNYW5hZ2VkRGV2aWNlcy5SZWFkLkFsbCBEaXJlY3RvcnkuQWNjZXNzQXNVc2VyLkFsbCBEaXJlY3RvcnkuUmVhZC5BbGwgRGlyZWN0b3J5LlJlYWRXcml0ZS5BbGwgR3JvdXAuUmVhZC5BbGwgR3JvdXAuUmVhZFdyaXRlLkFsbCBvcGVuaWQgcHJvZmlsZSBSZXBvcnRzLlJlYWQuQWxsIFVzZXIuUmVhZCBlbWFpbCIsInNpZ25pbl9zdGF0ZSI6WyJrbXNpIl0sInN1YiI6IkhUajNfMGMxblFiOGNLd0VzSmlLZEV0RWc1ekRNcHpFUjJiSUNKR0R6V2MiLCJ0ZW5hbnRfcmVnaW9uX3Njb3BlIjoiTkEiLCJ0aWQiOiIxMGExODQ3Ny1kNTMzLTRlY2QtYTc4ZC05MTZkYmQ4NDlkN2MiLCJ1bmlxdWVfbmFtZSI6InBtYmFncm9Ab3BlbnRleHQuY29tIiwidXBuIjoicG1iYWdyb0BvcGVudGV4dC5jb20iLCJ1dGkiOiJkQVZ1NXNyNXMwYWpqV3QyRm5lSkFRIiwidmVyIjoiMS4wIiwid2lkcyI6WyJiNzlmYmY0ZC0zZWY5LTQ2ODktODE0My03NmIxOTRlODU1MDkiXSwieG1zX2NjIjpbIkNQMSJdLCJ4bXNfc3NtIjoiMSIsInhtc19zdCI6eyJzdWIiOiJmN0J0dU16OEppTjNQNWtSQU80Rl9xc01IVTloNTUyY25qMmc4SUVTSTJJIn0sInhtc190Y2R0IjoxNDQ0MDU3MDIzfQ.PhnwIpKgX5SdwQHFp_PtQGKB5quClta2OL4eO_HrKLTz1nXjo47s9Am8vnYcEFDlYFhVQC2JDkvCRFjPvGDQLhybKaHondi3Yg1sV5bt0re52P5poC5Xgyl361iU8iY5gwSDRIySbhcgF3PyJ7Dv7ghssfp_Mugc31pn_ij4EQeBE7Ns7LBIkUIiU4DHhpQzms7IHsqri-GAufB0D957I9C0-kBbTaYwSJ4zKh_JnDMRDPNOwAb8tW7ZHb9Dxq2t3Gx8DS-LuEI_ggH6j0ZaKusgsw3mYNsZBIViHGEUW-dzeOKFyoLojhQjPbP9SMDOopvOGuYTT4XGBsfhhwC5wA"
    # test(auth_token)
    # "saas-compliance"
    plans = [
        "security-remediation",
        #"saas-compliance",
        #"saas-operations"
    ]
    plan_dict = {}
    for plan_name in plans:
        json_data = load_json(f"{data_path}/{plan_name}.json")
        active_columns = filter_active_columns(json_data)
        active_cards = filter_active_cards(active_columns, json_data['cards'])
        plan_dict[f"{plan_name}"] = {
            "plan_name": plan_name,
            "file_path": f"{data_path}/{plan_name}.json",
            "json_data": active_columns,
            "active_cards": active_cards
        }
    
    ## delete_planner_plans(plans=plans, auth_token=auth_token, group_token=group_token)
    
    for plan_name, plan_values in plan_dict.items():
        print(f"name: {plan_name}") # API CALL: CREATE PLANNER        
        create_planner_plans(group_token=group_token,planner_title=plan_name,auth_token=auth_token)        
        create_planner_buckets(plan_values, auth_token=auth_token, group_token=group_token)
        create_bucket_tasks(plan_values=plan_values,auth_token=auth_token,group_token=group_token)
        
    # """
        
        
if __name__ == "__main__":
    main()
