class NodeDecorator(object):
    
    # Execution instance property namespace and separator
    globalNamspaceName = 'ss'
    NODE_PROPERTY_SEPARATOR = ':' 
    globalNamspacePrefix = globalNamspaceName + NODE_PROPERTY_SEPARATOR

    ABORT_KEY = 'abort'

    # Node multiplicity index separator - e.g. <nodename>.<index>:<prop>
    NODE_MULTIPLICITY_SEPARATOR = '.'
    nodeMultiplicityStartIndex = '1'
    
    # Counter names
    initCounterName = globalNamspacePrefix + 'initCounter'
    finalizeCounterName = globalNamspacePrefix + 'finalizeCounter'
    terminateCounterName = globalNamspacePrefix + 'terminateCounter'
    
    # Orchestrator name
    orchestratorName = 'orchestrator'

    # Name given to the machine being built for node state
    MACHINE_NAME = 'machine'
    defaultMachineNamePrefix = MACHINE_NAME + NODE_PROPERTY_SEPARATOR

    # List of reserved and special node names
    reservedNodeNames = [globalNamspaceName,orchestratorName,MACHINE_NAME]

    # State names
    STATE_KEY = 'state'
    stateMessagePropertyName = 'statemessage'
    
    urlIgnoreAbortAttributeFragment = '?ignoreabort=true'
    
    SLIPSTREAM_DIID_ENV_NAME = 'SLIPSTREAM_DIID'

    IMAGE = 'Image'
    DEPLOYMENT = 'Deployment'

    MODULE_RESOURCE_URI = 'moduleResourceUri'
