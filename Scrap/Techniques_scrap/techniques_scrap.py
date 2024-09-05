import json
import re

import requests
def extract_techniques_base_data (data='data/STIX_enterprise_attack.json'):
    techniques_base_data = []
    # Load the JSON data from the file
    with open(data, 'r') as file:
        data = json.load(file)

    # Extract the objects field
    objects = data['objects']

    # Define important attributes and their new names for each object type
    important_attributes = {
        'x-mitre-data-component': {
            'name': 'Component Name',
            'description': 'Description',
            'created': 'Creation Date',
            'x_mitre_data_source_ref': 'Data Source Reference',
            'x_mitre_version': 'MITRE Version'
        },
        'course-of-action': {
            'name': 'Course of Action Name',
            'description': 'Description',
            'created': 'Creation Date',
            'x_mitre_deprecated': 'Deprecated'
        },
        'campaign': {
            'name': 'Campaign Name',
            'description': 'Description',
            'first_seen': 'First Seen Date',
            'last_seen': 'Last Seen Date'
        },
        'malware': {
            'name': 'Malware Name',
            'description': 'Description',
            'x_mitre_platforms': 'Platforms',
            'is_family': 'Is Family'
        },
        'marking-definition': {
            'definition': 'Definition Statement',
            'definition_type': 'Marking Definition Type'
        },
        'tool': {
            'name': 'Tool Name',
            'description': 'Description',
            'x_mitre_platforms': 'Platforms'
        },
        'x-mitre-data-source': {
            'name': 'Data Source Name',
            'description': 'Description',
            'x_mitre_platforms': 'Platforms'
        },
        'intrusion-set': {
            'name': 'Intrusion Set Name',
            'description': 'Description'
        },
        'x-mitre-tactic': {
            'name': 'Tactic Name',
            'description': 'Description'
        },
        'relationship': {
            'relationship_type': 'Relationship Type',
            'source_ref': 'Source Reference',
            'target_ref': 'Target Reference'
        },
        'x-mitre-matrix': {
            'name': 'Matrix Name',
            'description': 'Description'
        },
        'identity': {
            'name': 'Identity Name',
            'identity_class': 'Identity Class'
        },
        'attack-pattern': {
            'name': 'Technique Name',
            'description': 'Description',
            'x_mitre_platforms': 'Platforms',
            'x_mitre_detection': 'Detection',
            'x_mitre_is_subtechnique': 'Is Subtechnique',
            'x_mitre_defense_bypassed': 'Defense Bypassed',
            'kill_chain_phases': 'Kill Chain Phases'
        },
        'x-mitre-collection': {
            'name': 'Collection Name',
            'description': 'Description'
        }
    }

    # Function to extract and rename attributes, including CAPEC IDs from external_references
    def extract_attributes(obj, attributes_dict):
        result = {new_name: obj.get(old_name) for old_name, new_name in attributes_dict.items()}
        
        # Extract `external_id` from `external_references` if it exists
        if 'external_references' in obj:
            for ref in obj['external_references']:
            
                if 'external_id' in ref:
                    if ref.get('source_name') == 'capec':
                        result.setdefault('CAPEC IDs', []).append(ref['external_id'])
                    elif ref.get('source_name') in ['cwe', 'cve']:
                        result.setdefault(ref['source_name'].upper() + ' IDs', []).append(ref['external_id'])
                    else : result['External ID'] = ref['external_id']
        return result

    # Extract and save each object type in a separate JSON file
    object_types = set(obj.get('type') for obj in objects)
    for obj_type in object_types:
        # Filter objects by type
        filtered_objects = [obj for obj in objects if obj['type'] == obj_type]
        
        # Filter and rename attributes if the type is in the important attributes dictionary
        attribute_dict = important_attributes.get(obj_type, {})
        filtered_and_renamed_objects = [extract_attributes(obj, attribute_dict) for obj in filtered_objects]
        
        # Save to a separate JSON file
        filename = f"{obj_type.replace('-', '_')}"
        techniques_base_data.append((filename,filtered_and_renamed_objects))
    return techniques_base_data

def clean_attack_pattern(data):
    try:
        
        # Define the URL pattern to remove
        url_pattern = r'\(https://attack\.mitre\.org/.*?\)'

        # Iterate over each object in the JSON file
        for obj in data:
            if 'Detection' in obj and obj['Detection']:
                # Remove URLs matching the pattern from the detection
                obj['Detection'] = re.sub(url_pattern, '', obj['Detection'])

        return data
        
    except Exception as e:
        print(f"An error occurred: {e}")


def add_techniques_to_intrusion_sets(intrusion_sets):
    base_url = "https://attack.mitre.org/groups/{id}/{id}-enterprise-layer.json"

   
    for intrusion_set in intrusion_sets:
        external_id = intrusion_set.get('External ID')
        if not external_id:
            continue

        # Construct the URL and fetch the techniques used by the group
        url = base_url.format(id=external_id)
        try:
            response = requests.get(url)
            response.raise_for_status()
            techniques_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for {external_id}: {e}")
            continue

        # Extract the techniques and comments
        techniques_used = [
            {"techniqueID": tech.get("techniqueID"), "comment": tech.get("comment")}
            for tech in techniques_data.get("techniques", [])
        ]

        # Add the techniques to the intrusion set
        intrusion_set['techniques_used'] = techniques_used

    return intrusion_set


def add_techniques_to_campaigns(campaigns):
    base_url = "https://attack.mitre.org/campaigns/{id}/{id}-enterprise-layer.json"

    for campaign in campaigns:
        external_id = campaign.get('External ID')
        if not external_id:
            continue

        # Construct the URL and fetch the techniques used by the group
        url = base_url.format(id=external_id)
        try:
            response = requests.get(url)
            response.raise_for_status()
            techniques_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for {external_id}: {e}")
            continue

        # Extract the techniques and comments
        techniques_used = [
            {"techniqueID": tech.get("techniqueID"), "comment": tech.get("comment")}
            for tech in techniques_data.get("techniques", [])
        ]

        # Add the techniques to the intrusion set
        campaigns['techniques_used'] = techniques_used

    return campaigns



def add_techniques_to_malwares(malwares):
    base_url = "https://attack.mitre.org/software/{id}/{id}-enterprise-layer.json"

    

    for malware in malwares:
        external_id = malware.get('External ID')
        if not external_id:
            continue

        # Construct the URL and fetch the techniques used by the group
        url = base_url.format(id=external_id)
        try:
            response = requests.get(url)
            response.raise_for_status()
            techniques_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for {external_id}: {e}")
            continue

        # Extract the techniques and comments
        techniques_used = [
            {"techniqueID": tech.get("techniqueID"), "comment": tech.get("comment")}
            for tech in techniques_data.get("techniques", [])
        ]

        # Add the techniques to the intrusion set
        malwares['techniques_used'] = techniques_used

    return malwares

def add_techniques_to_tools(tools):
    base_url = "https://attack.mitre.org/software/{id}/{id}-enterprise-layer.json"

  

    for tool in tools:
        external_id = tool.get('External ID')
        if not external_id:
            continue

        # Construct the URL and fetch the techniques used by the group
        url = base_url.format(id=external_id)
        try:
            response = requests.get(url)
            response.raise_for_status()
            techniques_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for {external_id}: {e}")
            continue

        # Extract the techniques and comments
        techniques_used = [
            {"techniqueID": tech.get("techniqueID"), "comment": tech.get("comment")}
            for tech in techniques_data.get("techniques", [])
        ]

        # Add the techniques to the intrusion set
        tools['techniques_used'] = techniques_used

    return tools

def add_techniques_to_course_of_actions(course_of_actions):
    base_url = "https://attack.mitre.org/mitigations/{id}/{id}-enterprise-layer.json"


    for course_of_action in course_of_actions:
        external_id = course_of_action.get('External ID')
        if not external_id:
            continue

        # Construct the URL and fetch the techniques used by the group
        url = base_url.format(id=external_id)
        try:
            response = requests.get(url)
            response.raise_for_status()
            techniques_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for {external_id}: {e}")
            continue

        # Extract the techniques and comments
        techniques_used = [
            {"techniqueID": tech.get("techniqueID"), "comment": tech.get("comment")}
            for tech in techniques_data.get("techniques", [])
        ]

        # Add the techniques to the intrusion set
        course_of_actions['techniques'] = techniques_used

    return course_of_actions


def add_related_malwares(attack_patterns, malwares):

    
    # Create a dictionary to map technique IDs to related malware information
    technique_to_malwares = {}

    for malware in malwares:
        malware_name = malware.get("Malware Name", "Unknown")
        external_id = malware.get("External ID", "Unknown")
        techniques = malware.get("techniques_used", [])
        for technique in techniques:
            technique_id = technique.get("techniqueID")
            comment = technique.get("comment", "")
            if technique_id:
                if technique_id not in technique_to_malwares:
                    technique_to_malwares[technique_id] = []
                technique_to_malwares[technique_id].append({
                    "comment": comment,
                    "Malware Name": malware_name,
                    "External ID": external_id
                })

    # Add the related_malwares attribute to attack_patterns
    for pattern in attack_patterns:
        technique_id = pattern.get("External ID")
        if technique_id in technique_to_malwares:
            pattern["related_malwares"] = technique_to_malwares[technique_id]

    return attack_patterns

def add_related_tools(attack_patterns, tools):
  
    
    # Create a dictionary to map technique IDs to related tool information
    technique_to_tools = {}

    for tool in tools:
        tool_name = tool.get("Tool Name", "Unknown")
        external_id = tool.get("External ID", "Unknown")
        techniques_used = tool.get("techniques_used", [])
        for technique in techniques_used:
            technique_id = technique.get("techniqueID")
            comment = technique.get("comment", "")
            if technique_id:
                if technique_id not in technique_to_tools:
                    technique_to_tools[technique_id] = []
                technique_to_tools[technique_id].append({
                    "comment": comment,
                    "Tool Name": tool_name,
                    "External ID": external_id
                })

    # Add the related_tools attribute to attack_patterns
    for pattern in attack_patterns:
        technique_id = pattern.get("External ID")
        if technique_id in technique_to_tools:
            pattern["related_tools"] = technique_to_tools[technique_id]

    return attack_patterns
def add_related_intrusion_sets_to_attack_patterns(attack_patterns, intrusion_sets):

    # Create a dictionary to map technique IDs to related intrusion set information
    technique_to_intrusion_sets = {}

    for intrusion_set in intrusion_sets:
        intrusion_set_name = intrusion_set.get("Intrusion Set Name", "Unknown")
        techniques = intrusion_set.get("techniques_used", [])
        for technique in techniques:
            technique_id = technique.get("techniqueID")
            comment = technique.get("comment", "")
            external_id = intrusion_set.get("External ID", "Unknown")
            if technique_id:
                if technique_id not in technique_to_intrusion_sets:
                    technique_to_intrusion_sets[technique_id] = []
                technique_to_intrusion_sets[technique_id].append({
                    "comment": comment,
                    "Intrusion Set Name": intrusion_set_name,
                    "External ID": external_id
                })

    # Add the related_intrusion_sets attribute to attack_patterns
    for pattern in attack_patterns:
        technique_id = pattern.get("External ID")
        if technique_id in technique_to_intrusion_sets:
            pattern["related_intrusion_sets"] = technique_to_intrusion_sets[technique_id]

    return attack_patterns

def add_related_campaigns_to_attack_patterns(attack_patterns, campaigns):
   
    
    # Create a dictionary to map technique IDs to related campaign information
    technique_to_campaigns = {}

    for campaign in campaigns:
        campaign_name = campaign.get("Campaign Name", "Unknown")
        techniques = campaign.get("techniques_used", [])
        for technique in techniques:
            technique_id = technique.get("techniqueID")
            comment = technique.get("comment", "")
            external_id = campaign.get("External ID", "Unknown")
            if technique_id:
                if technique_id not in technique_to_campaigns:
                    technique_to_campaigns[technique_id] = []
                technique_to_campaigns[technique_id].append({
                    "comment": comment,
                    "Campaign Name": campaign_name,
                    "External ID": external_id
                })

    # Add the related_campaigns attribute to attack_patterns
    for pattern in attack_patterns:
        technique_id = pattern.get("External ID")
        if technique_id in technique_to_campaigns:
            pattern["related_campaigns"] = technique_to_campaigns[technique_id]

    return attack_patterns

def add_related_courses_of_action_to_attack_patterns(attack_patterns, courses_of_action):
    
    
    # Create a dictionary to map technique IDs to related courses of action
    technique_to_courses_of_action = {}

    for course in courses_of_action:
        course_name = course.get("Course of Action Name", "Unknown")
        description = course.get("Description", "")
        external_id = course.get("External ID", "Unknown")
        

        if external_id.startswith("T"):
            # For courses of action with External ID starting with "M"
            technique_id = external_id
            if technique_id:
                if technique_id not in technique_to_courses_of_action:
                    technique_to_courses_of_action[technique_id] = []
                technique_to_courses_of_action[technique_id].append({
                    "Course of Action Name": course_name,
                    "Description": description,
                    "Comment": "" ,# No specific comment for these courses of action
                    "External ID" : ""
                })
        else:
            techniques = course.get("techniques", [])
            # For courses of action with techniques
            for technique in techniques:
                technique_id = technique.get("techniqueID")
                comment = technique.get("comment", "")
                if technique_id:
                    if technique_id not in technique_to_courses_of_action:
                        technique_to_courses_of_action[technique_id] = []
                    technique_to_courses_of_action[technique_id].append({
                        "Course of Action Name": course_name,
                        "Description": description,
                        "Comment": comment,
                        "External ID" : external_id
                    })

    # Add the related_courses_of_action attribute to attack_patterns
    for pattern in attack_patterns:
        technique_id = pattern.get("External ID")
        if technique_id in technique_to_courses_of_action:
            pattern["mitigations"] = technique_to_courses_of_action[technique_id]

    return attack_patterns

def scrap_data_related_to_techniques(techniques_base_data):
    attack_patterns = techniques_base_data['attack_pattern']
    clean_attack_pattern(attack_patterns)


    intrusion_sets = techniques_base_data['intrusion_set']
    intrusion_set = add_techniques_to_intrusion_sets(intrusion_sets)


    campaigns = techniques_base_data['campaign']
    campaigns = add_techniques_to_campaigns(campaigns)


    malwares = techniques_base_data['malware']
    malwares = add_techniques_to_malwares(malwares)


    tools = techniques_base_data['tool']
    tools = add_techniques_to_tools(tools)

    course_of_actions = techniques_base_data['course_of_actions']
    course_of_actions = add_techniques_to_course_of_actions(course_of_actions)

    return attack_patterns, intrusion_sets, campaigns , malwares , tools , course_of_actions

def populate_attack_patterns_with_scrapped_data(attack_patterns,malwares,tools,intrusion_sets,campaigns,course_of_actions):
    updated_attack_patterns = add_related_malwares(attack_patterns,malwares)


    updated_attack_patterns = add_related_tools(updated_attack_patterns,tools)


    updated_attack_patterns = add_related_intrusion_sets_to_attack_patterns(updated_attack_patterns, intrusion_sets)


    updated_attack_patterns = add_related_campaigns_to_attack_patterns(updated_attack_patterns,campaigns)

    updated_attack_patterns = add_related_courses_of_action_to_attack_patterns(updated_attack_patterns,course_of_actions)
    
    return updated_attack_patterns

