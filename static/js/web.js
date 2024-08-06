let apiData = {
    unique: [],
    unique_affix: [],
    item: [],
    flask: [],
    flask_affix: [],
    cluster: [],
    cluster_affix: [],
    base: []
};

let obtainedFilter = {};
let msnryInstances = {};

async function fetchData() {
    try {
        const response = await fetch('http://127.0.0.1:8000/items/');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        organizeData(data);
        console.log(apiData)
        displayData();
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function organizeData(data) {
    apiData.unique = [];
    apiData.unique_affix = [];
    apiData.item = [];
    apiData.flask = [];
    apiData.flask_affix = [];
    apiData.cluster = [];
    apiData.cluster_affix = [];
    apiData.base = [];

    data.forEach(itemType => {
        itemType.items.forEach(itemClass => {
            itemClass.items.forEach(item => {
                if (item.item_type === 'unique') {
                    const groupKey = item.sub_class || item.item_class;
                    if (!apiData.unique[groupKey]) {
                        apiData.unique[groupKey] = [];
                    }
                    apiData.unique[groupKey].push(item);
                } else if (item.item_type === 'unique_affix') {
                    const groupKey = item.sub_class || item.item_class;
                    if (!apiData.unique_affix[groupKey]) {
                        apiData.unique_affix[groupKey] = [];
                    }
                    apiData.unique_affix[groupKey].push(item);
                } else if (item.item_type === 'item') {
                    const groupKey = item.sub_class || item.item_class;
                    if (!apiData.item[groupKey]) {
                        apiData.item[groupKey] = [];
                    }
                    apiData.item[groupKey].push(item);
                } else if (item.item_type === 'flask') {
                    if (!apiData.flask[itemClass.item_class]) {
                        apiData.flask[itemClass.item_class] = [];
                    }
                    apiData.flask[itemClass.item_class].push(item);
                } else if (item.item_type === 'flask_affix') {
                    if (!apiData.flask_affix[itemClass.item_class]) {
                        apiData.flask_affix[itemClass.item_class] = [];
                    }
                    apiData.flask_affix[itemClass.item_class].push(item);
                } else if (item.item_type === 'cluster') {
                    const groupKey = item.sub_class || item.item_class;
                    if (!apiData.cluster[groupKey]) {
                        apiData.cluster[groupKey] = [];
                    }
                    apiData.cluster[groupKey].push(item);
                } else if (item.item_type === 'cluster_affix') {
                    if (!apiData.cluster_affix[itemClass.item_class]) {
                        apiData.cluster_affix[itemClass.item_class] = [];
                    }
                    apiData.cluster_affix[itemClass.item_class].push(item);
                } else if (item.item_type === 'base') {
                    const groupKey = item.sub_class || item.item_class;
                    if (!apiData.base[groupKey]) {
                        apiData.base[groupKey] = [];
                    }
                    apiData.base[groupKey].push(item);
                }
            });
        });
    });

    for (const category in apiData) {
        for (const group in apiData[category]) {
            apiData[category][group].sort((a, b) => a.name.localeCompare(b.name));
        }
    }
}

function displayData() {
    const sections = [
        'currency', 'crafting', 'base', 'uniques', 'cards', 
        'fragments', 'maps', 'flasks', 'clusters', 'gems', 'misc'
    ];

    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section != null) {
            section.innerHTML = '';
        }
    });

    const processAndDisplayItems = (sectionId, data, groupCondition = null) => {
        const sortedGroups = Object.keys(data).sort();
        sortedGroups.forEach(group => {
            if (groupCondition && !groupCondition(group)) return;
            if (data[group].length > 0) {
                createCollapsibleSection(sectionId, data[group], group);
            }
        });
    };

    // Display Uniques
    processAndDisplayItems('uniques', apiData.unique);
    processAndDisplayItems('uniques', apiData.unique_affix);

    // Display Currency
    const currencyTypes = ["Currency", "Delirium Orb", "Scouting Report", "Ichor", "Ember", "Tainted", "Lifeforce", "Blessing", "Tattoo", "Omen", "Incubator"];
    processAndDisplayItems(
        'currency',
        apiData.item,
        (group) => currencyTypes.includes(group)
    );

    // Display Crafting
    const craftingTypes = ["Fossil", "Oil", "Catalyst", "Fossil", "Resonator", "Essence", "Beasts", "Rune"];
    processAndDisplayItems(
        'crafting',
        apiData.item,
        (group) => craftingTypes.includes(group)
    );

    // Display Base Types
    processAndDisplayItems('base', apiData.base);
    processAndDisplayItems('base', apiData.item, (group) => group === 'Abyss Jewels');

    // Display Cards
    processAndDisplayItems('cards', apiData.item, (group) => group === 'Divination Cards');

    // Display Fragments
    const fragmentTypes = ["Emblem", "Breachstone", "Sanctum Research", "Expedition Logbooks", 
        "Map Fragments", "Splinter", "Blueprints", "Contracts", "Vault Key", "Piece"];
    processAndDisplayItems(
        'fragments',
        apiData.item,
        (group) => fragmentTypes.includes(group)
    );

    // Display Maps
    const mapTypes = ["Maps", "Misc Map Items", "Memories", "Scarab", "Foil", "Boss"];
    processAndDisplayItems(
        'maps',
        apiData.item,
        (group) => mapTypes.includes(group)
    );

    // Display Flasks
    processAndDisplayItems('flasks', apiData.flask);
    processAndDisplayItems('flasks', apiData.flask_affix);

    // Display Clusters
    processAndDisplayItems('clusters', apiData.cluster);
    processAndDisplayItems('clusters', apiData.cluster_affix);

    // Display Gems
    const gemTypes = ["Skill Gems", "Support Gems"];
    processAndDisplayItems(
        'gems',
        apiData.item,
        (group) => gemTypes.includes(group)
    );

    // Display Misc
    const miscTypes = ["Tincture", "Heist Cloak", "Heist Brooche", "Heist Tool",
         "Heist Gear", "Charm", "Relic", "Sentinel", "Incubator", "Trinket"];
    processAndDisplayItems(
        'misc',
        apiData.item,
        (group) => miscTypes.includes(group)
    );

    sections.forEach(sectionId => {
        const grid = document.querySelector(`#${sectionId}.tab-inner-content`);
        if (grid) {
            msnryInstances[sectionId] = new Masonry(grid, {
                itemSelector: '.section-container',
                columnWidth: '.section-container',
                gutter: 16,
                percentPosition: true,
                horizontalOrder: true,
                transitionDuration: '0.1s'
            });
        }
    });
}

function createCollapsibleSection(containerId, data, headerText) {
    const container = document.getElementById(containerId);
    const sectionContainer = document.createElement('div'); // New container for each section
    sectionContainer.classList.add('section-container');

    const classContainer = document.createElement('div');
    const collapsibleButton = document.createElement('button');
    collapsibleButton.classList.add('collapsible', 'active');
    collapsibleButton.innerHTML = headerText;
    classContainer.appendChild(collapsibleButton);

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('content');
    contentDiv.style.display = 'block';

    data.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.classList.add('item');

        if (item.ilev > 0) {
            const ilevElement = document.createElement('div');
            ilevElement.classList.add('ilev');
            ilevElement.textContent = `ilev: ${item.ilev}`;

            const nameElement = document.createElement('div');
            nameElement.classList.add('name');
            nameElement.textContent = `${item.name}`;

            itemElement.appendChild(nameElement);
            itemElement.appendChild(ilevElement);
        } else {
            const nameElement = document.createElement('div');
            nameElement.classList.add('name');
            nameElement.textContent = `${item.name}`;

            itemElement.appendChild(nameElement);
        }

        
        itemElement.dataset.obtained = item.obtained;
        if (item.obtained) {
            itemElement.classList.add('obtained');
        }

        contentDiv.appendChild(itemElement);
    });

    classContainer.appendChild(contentDiv);
    sectionContainer.appendChild(classContainer); // Add classContainer to sectionContainer
    container.appendChild(sectionContainer); // Add sectionContainer to the main container

    collapsibleButton.addEventListener('click', function() {
        this.classList.toggle('active');
        const content = this.nextElementSibling;
        if (content.style.display === 'block') {
            content.style.display = 'none';
        } else {
            content.style.display = 'block';
        }
        msnryInstances[containerId]?.layout();
    });
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

const debouncedFilterItems = debounce((containerId, filterValue) => {
    filterItems(containerId, filterValue);
}, 150);

function toggleFilter(containerId, filterType) {
    if (!obtainedFilter[containerId]) {
        obtainedFilter[containerId] = { showObtained: true, showNotObtained: true, filterValue: '' };
    }
    obtainedFilter[containerId][filterType] = !obtainedFilter[containerId][filterType];
    filterItems(containerId, obtainedFilter[containerId].filterValue);
    msnryInstances[containerId]?.layout();
}

function filterItems(containerId, filterValue) {
    if (!obtainedFilter[containerId]) {
        obtainedFilter[containerId] = { showObtained: true, showNotObtained: true, filterValue: '' };
    }
    obtainedFilter[containerId].filterValue = filterValue;

    const container = document.getElementById(containerId);
    const collapsibleSections = container.getElementsByClassName('content');
    const filterLower = filterValue.toLowerCase();
    const showObtained = obtainedFilter[containerId].showObtained;
    const showNotObtained = obtainedFilter[containerId].showNotObtained;

    for (const section of collapsibleSections) {
        const items = section.getElementsByClassName('item');
        for (const item of items) {
            const itemText = item.textContent.toLowerCase();
            const isObtained = item.dataset.obtained === "1";
            if (itemText.includes(filterLower) && ((showObtained && isObtained) || (showNotObtained && !isObtained))) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        }
    }
}

async function addItems() {
    const names = document.getElementById('names').value.split('\n').map(name => name.trim()).filter(name => name !== '');
    const itemType = document.getElementById('itemType').value;
    const itemClass = document.getElementById('itemClass').value;
    const subClass = document.getElementById('subClass').value;
    const rarity = document.getElementById('rarity').value;

    const response = await fetch('http://127.0.0.1:8000/add_items/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ names, item_type: itemType, item_class: itemClass, sub_class: subClass, rarity })
    });

    if (response.ok) {
        alert('Items added successfully!');
        fetchData();
        closeModal();
    } else {
        alert('Failed to add items.');
    }
}

function openModal() {
    document.getElementById('myModal').style.display = "block";
}

function closeModal() {
    document.getElementById('myModal').style.display = "none";
}

function openTab(evt, tabName) {
    const tabcontents = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontents.length; i++) {
        tabcontents[i].style.display = "none";
    }
    const tablinks = document.getElementsByClassName("tablinks");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";

    if (tabName === 'Settings') {
        fetchCurrentLeagueName();
    }

    msnryInstances[tabName.toLowerCase()]?.layout();
}


window.onclick = function(event) {
    if (event.target == document.getElementById('myModal')) {
        closeModal();
    }
}

async function fetchCurrentLeagueName() {
    try {
        const response = await fetch('http://127.0.0.1:8000/get_league_name');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        document.getElementById('currentLeagueName').textContent = data.league_name;
    } catch (error) {
        console.error('Error fetching league name:', error);
        document.getElementById('currentLeagueName').textContent = 'Error fetching league name';
    }
}

async function resetAllData() {
    const response = await fetch('http://127.0.0.1:8000/reset_all/', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (response.ok) {
        alert('All data reset!');
        fetchData();
    } else {
        alert('Failed to reset data.');
    }
}

function collapseAllSections(tabId) {
    const container = document.getElementById(tabId);
    const collapsibleButtons = container.getElementsByClassName('collapsible');
    const contentDivs = container.getElementsByClassName('content');

    for (let i = 0; i < collapsibleButtons.length; i++) {
        collapsibleButtons[i].classList.remove('active');
        contentDivs[i].style.display = 'none';
    }
    msnryInstances[tabId]?.layout();
}

function expandAllSections(tabId) {
    const container = document.getElementById(tabId);
    const collapsibleButtons = container.getElementsByClassName('collapsible');
    const contentDivs = container.getElementsByClassName('content');

    for (let i = 0; i < collapsibleButtons.length; i++) {
        collapsibleButtons[i].classList.add('active');
        contentDivs[i].style.display = 'block';
    }
    msnryInstances[tabId]?.layout();
}

fetchData()
setInterval(fetchData, 600000);  // Fetch data every 10 min