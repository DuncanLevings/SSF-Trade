import time
import re
from enum import Enum
from app import add_item
import ctypes
from config import Rarity, SubClass, UniqueClass, CleanClusterName, CleanFlaskName, ItemName, Influence, CheckUnique, BossMap

def parse_copied_content(queue):
    while True:
        if not queue.empty():
            copied_content = queue.get()

            if "Unidentified" not in copied_content:
                relevant_content = copied_content.split("--------")[0].strip()
                
                item_class_match = re.search(r"Item Class: (.*)", relevant_content)
                rarity_match = re.search(r"Rarity: (.*)", relevant_content)
                name_match = re.findall(r"Rarity: .*?\n(.*)", relevant_content, re.DOTALL)
                
                item_class = item_class_match.group(1).replace('\r', '') if item_class_match else "Unknown"
                rarity = rarity_match.group(1).replace('\r', '') if rarity_match else "Unknown"
                name = "\n".join(name_match).strip() if name_match else "Unknown"

                if name == "Unknown":
                    ctypes.windll.user32.MessageBoxW(0, "Error parsing item", "Error", 1)
                else:
                    handle_raw_item(item_class, rarity, name, copied_content)
                
        time.sleep(0.1)


def handle_raw_item(item_class, rarity, name, copied_content):
    name_parts = name.split('\n') if '\n' in name else name.split('\r\n')
    name_parts = [part.strip() for part in name_parts if part.strip()]

    if item_class in [i.value for i in UniqueClass]:
        if rarity in [r.value for r in Rarity]: 
            return create_unique_item(item_class, name_parts[0], copied_content)
        elif item_class == UniqueClass.JEWEL.value and "Cluster" in name:
            return create_cluster(name_parts, copied_content)
        elif item_class == UniqueClass.FLASK3.value:
            return create_flask(name_parts, copied_content)
        elif item_class == UniqueClass.CONTRACT.value or item_class == UniqueClass.RELIC.value or item_class == UniqueClass.MAP.value:
            return create_item('item', item_class, name_parts, copied_content)
        elif item_class != UniqueClass.FLASK1.value or item_class != UniqueClass.FLASK2.value or item_class != UniqueClass.FLASK4.value:
            return create_base_item('base', item_class, name_parts, copied_content)
    else:
        return create_item('item', item_class, name_parts, copied_content)

def create_unique_item(item_class, name, copied_content):
    item = {
        'item_type': 'unique',
        'item_class': item_class,
        'sub_class': None,
        'rarity': Rarity.UNIQUE.value,
        'ilev': 0,
        'name': name
    }
    print(item)
    add_item(item)
    create_synthesised_affix(item_class, copied_content)
    create_corrupted_affix(item_class, copied_content)

    if check_unique_roll(name, CheckUnique):
        if name == CheckUnique.VOICES.value:
            voice = parse_voices_affix(copied_content)
            if voice is not None:
                create_unique_affix(item_class, name, voice)
        elif name == CheckUnique.WATCHER_EYE.value:
            watcher_lines = parse_watcher_affixes(copied_content)
            if watcher_lines is not None:
                for watcher in watcher_lines:
                    create_unique_affix(item_class, name, watcher)
        elif name == CheckUnique.FLESH.value or name == CheckUnique.FLAME.value:
            forbidden = parse_forbidden_jewel(copied_content)
            if forbidden is not None:
                create_unique_affix(item_class, name, forbidden)
        elif name == CheckUnique.MEGALOMANIAC.value:
            mega_lines = parse_megalomaniac_jewel(copied_content)
            if mega_lines is not None:
                for mega in mega_lines:
                    create_unique_affix(item_class, name, mega)

def create_item(item_type, item_class, name_parts, copied_content):
    name = name_parts[0]
    if (len(name_parts) > 1):
        name = name_parts[1]
    else:
        name = parse_item_name(name, ItemName)

    name = name.replace('Contract: ', '')
    name = name.replace('Blueprint: ', '')

    if item_class == 'Stackable Currency':
        item_class = 'Currency'

    if item_class == 'Delve Stackable Socketable Currency':
        item_class = 'Resonator'

    if parse_beast(copied_content):
        item_class = 'Beasts'

    sub_class = parse_sub_class(name, SubClass);

    if sub_class == 'Essence' and item_class == 'Skill Gems':
        sub_class = None

    if sub_class == 'Blessing' and item_class == 'Support Gems':
        sub_class = None

    if sub_class == 'Fossil' and item_class == 'Incubators':
        sub_class = 'Incubator'

    if sub_class == 'Essence' and item_class == 'Map Fragments':
        sub_class = 'Scarab'

    if item_class == 'Maps':
        parse_boss_map(copied_content)
        parse_valdo_box(copied_content)

    item = {
        'item_type': item_type,
        'item_class': item_class,
        'sub_class': sub_class,
        'rarity': None,
        'ilev': parse_ilev(copied_content),
        'name': name
    }
    print(item)
    add_item(item)

def create_base_item(item_type, item_class, name_parts, copied_content):
    name = 'Unknown'
    if (len(name_parts) > 1):
        name = parse_item_name(name_parts[1], ItemName)
    else:
        name = parse_item_name(name_parts[0], ItemName)

    item = {
        'item_type': item_type,
        'item_class': item_class,
        'sub_class': parse_influence(copied_content, Influence),
        'rarity': None,
        'ilev': parse_ilev(copied_content),
        'name': name
    }
    print(item)
    add_item(item)
    create_fractured_affix(item_class, copied_content)
    create_synthesised_affix(item_class, copied_content)
    create_corrupted_affix(item_class, copied_content)

def create_cluster(name_parts, copied_content):
    cleaned_class_name = clean_cluster_name(name_parts)
    cluster_name = parse_cluster_passive(copied_content)
    item = {
        'item_type': 'cluster',
        'item_class': 'Cluster Jewel',
        'sub_class': cleaned_class_name,
        'rarity': None,
        'ilev': parse_ilev(copied_content),
        'name': cluster_name
    }
    affixes = extract_cluster_affix(copied_content)
    print(item)
    add_item(item)
    create_affixes('cluster_affix', affixes, cleaned_class_name + " Affixes")
    create_corrupted_affix('Cluster Jewel', copied_content)

def create_flask(name_parts, copied_content):
    cleaned_name = parse_sub_class(name_parts[0], CleanFlaskName)
    item = {
        'item_type': 'flask',
        'item_class': 'Utility Flasks',
        'sub_class': None,
        'rarity': None,
        'ilev': parse_ilev(copied_content),
        'name': cleaned_name
    }
    affixes = extract_flask_affix(copied_content)
    print(item)
    add_item(item)
    create_affixes('flask_affix', affixes, 'Utility Flask Affixes')
    create_corrupted_affix('Utility Flasks', copied_content)

def create_affixes(item_type, affixes, item_class):
    for affix in affixes:
        item = {
            'item_type': item_type,
            'item_class': item_class,
            'sub_class': None,
            'rarity': None,
            'ilev': 0,
            'name': affix
        }
        print(item)
        add_item(item)

def create_fractured_affix(item_class, copied_content):
    if "Fractured Item" in copied_content:
        fractured_lines = re.findall(r"(.+ \(fractured\))", copied_content)
        if fractured_lines:
            transformed_lines = [re.sub(r'\d+', '#', line).replace(" (fractured)", "") for line in fractured_lines]
            for line in transformed_lines:
                item = {
                    'item_type': 'base',
                    'item_class': item_class,
                    'sub_class': 'fractured',
                    'rarity': None,
                    'ilev': 0,
                    'name': line
                }
                print(item)
                add_item(item)

def create_synthesised_affix(item_class, copied_content):
    if "Synthesised Item" in copied_content:
        synth_lines = re.findall(r"(.+ \(implicit\))", copied_content)
        if synth_lines:
            transformed_lines = [re.sub(r'\d+', '#', line).replace(" (implicit)", "") for line in synth_lines]
            for line in transformed_lines:
                item = {
                    'item_type': 'base',
                    'item_class': item_class,
                    'sub_class': 'synthesised',
                    'rarity': None,
                    'ilev': 0,
                    'name': line
                }
                print(item)
                add_item(item)

def create_corrupted_affix(item_class, copied_content):
    if "Corrupted" in copied_content:
        synth_lines = re.findall(r"(.+ \(implicit\))", copied_content)
        if synth_lines:
            transformed_lines = [re.sub(r'\d+', '#', line).replace(" (implicit)", "") for line in synth_lines]
            for line in transformed_lines:
                item = {
                    'item_type': 'base',
                    'item_class': item_class,
                    'sub_class': 'corrupted',
                    'rarity': None,
                    'ilev': 0,
                    'name': line
                }
                print(item)
                add_item(item)

def create_unique_affix(item_class, sub_class, affix):
    item = {
        'item_type': 'unique_affix',
        'item_class': item_class,
        'sub_class': sub_class,
        'rarity': Rarity.UNIQUE.value,
        'ilev': 0,
        'name': affix
    }
    print(item)
    add_item(item)

def parse_influence(copied_content, clazz):
    for member in clazz:
        if member.value in copied_content:
            return member.value
    return None

def parse_item_name(name, clazz):
    prefix = ''
    if "Blight-ravaged" in name:
        prefix = "Blight-ravaged "
    elif "Blighted" in name:
        prefix = "Blighted "

    for member in clazz:
        if member.value in name:
            return prefix + member.value
    return name

def parse_sub_class(name, clazz):
    for member in clazz:
        if member.value in name:
            return member.value
    return None

def parse_ilev(copied_content):
    match = re.search(r'Item Level: (\d+)', copied_content)
    if match:
        return int(match.group(1))
    else:
        return 0
    
def parse_beast(copied_content):
    match = re.search(r'add this to your bestiary.', copied_content)
    if match:
        return 1
    else:
        return 0
    
def check_unique_roll(name, clazz):
    for member in clazz:
        if member.value in name:
            return 1
    return 0

def clean_cluster_name(name_parts):
    if (len(name_parts) > 1):
        return name_parts[1]
    else:
        return parse_sub_class(name_parts[0], CleanClusterName)
    
def parse_cluster_passive(copied_content):
    match = re.search(r"Added Small Passive Skills grant: ([^(\n]+)", copied_content)
    if match:
        return replace_numbers_with_hashes(match.group(1).strip().replace('\r', ''))
    return None

def replace_numbers_with_hashes(text):
    return re.sub(r'\d+', '#', text)

def extract_cluster_affix(text):
    sections = text.split('--------')
    relevant_section = sections[-2] if len(sections) > 1 else ''

    pattern_also_grant = re.compile(r"Added Small Passive Skills also grant: ([^\r\n]+)")
    pattern_have = re.compile(r"Added Small Passive Skills have ([^\r\n]+)")
    pattern_is = re.compile(r"Added Passive Skill is ([^\r\n]+)")
    
    also_grant_matches = pattern_also_grant.findall(relevant_section)
    have_matches = pattern_have.findall(relevant_section)
    is_matches = pattern_is.findall(relevant_section)
    
    also_grant_matches = [replace_numbers_with_hashes(match.strip().replace('\r', '')) for match in also_grant_matches]
    have_matches = [replace_numbers_with_hashes(match.strip().replace('\r', '')) for match in have_matches]

    is_matches = [match.strip().replace('\r', '') for match in is_matches if match.strip().replace('\r', '') != "a Jewel Socket (enchant)"]

    return also_grant_matches + have_matches + is_matches

def extract_flask_affix(text):   
    sections = text.split('--------')
    if len(sections) < 3:
        return []
    relevant_section = sections[-2].strip()
    lines = relevant_section.split('\n')
    lines = [line.strip() for line in lines if line.strip() and not re.match(r'^Item Level:\s*\d+$', line.strip())]

    if not lines:
        return []
    
    cleaned_lines = [replace_numbers_with_hashes(line) for line in lines]
    
    return cleaned_lines

def parse_boss_map(copied_content):
    for member in BossMap:
        if member.value in copied_content:
            item = {
                'item_type': 'item',
                'item_class': 'Maps',
                'sub_class': 'Boss',
                'rarity': None,
                'ilev': 0,
                'name': member.value
            }
            print(item)
            add_item(item)

def parse_valdo_box(copied_content):
    if 'Map Tier: 17' in copied_content:
        reward = re.search(r"Reward: (.+)\r\n", copied_content)
        if reward:
            item = {
                'item_type': 'item',
                'item_class': 'Maps',
                'sub_class': 'Foil',
                'rarity': None,
                'ilev': 0,
                'name': reward.group(1)
            }
            print(item)
            add_item(item)
        

def parse_voices_affix(copied_content):
    specific_line = re.search(r"(Adds \d+ Small Passive Skills which grant nothing)", copied_content)
    if specific_line:
        return specific_line.group(1)
    else:
        return None
    
def parse_watcher_affixes(copied_content):
    start_match = re.search(r"% increased maximum Mana\r\n", copied_content)
    if start_match:
        start_index = start_match.end()
        end_index = copied_content.find("--------", start_index)
        if end_index == -1:
            end_index = len(copied_content)
        relevant_lines = copied_content[start_index:end_index].strip().split('\n')
        
        transformed_lines = [re.sub(r'\d+', '#', line).strip().replace('\r', '') for line in relevant_lines]
        return transformed_lines
    else:
        return None
    
def parse_forbidden_jewel(copied_content):
    specific_line = re.search(r"Allocates (.+) if you have", copied_content)
    if specific_line:
        return specific_line.group(1)
    else:
        return None
    
def parse_megalomaniac_jewel(copied_content):
    passive_skill_lines = re.findall(r"Added Passive Skill is (.+)", copied_content)
    return [line.strip().replace('\r', '') for line in passive_skill_lines]