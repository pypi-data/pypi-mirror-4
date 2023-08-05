import requests
import json
from rmas_adapter.conf import settings
import logging
    
    
def get_proposal_for_rmas_id(rmas_id):
    '''
        Gets the proposal details based on the rmas_id.
        
        The is would look like:
        
        curl --request GET 'http://0.0.0.0:3000/proposals.json?rmas_id=urn:rmas:kent:pmtool:2edbb8d0-6ebe-4bec-912a-88fea00c0000'
    '''
    
    proposal_request = requests.get(settings.PM_API_PROPOSAL_ENDPOINT + '.json',
                                           params={'rmas_id':rmas_id})
    
    if proposal_request.status_code == 200:     
        #there should only be one resource returned:
        proposals = proposal_request.json
        
        if len(proposals) > 0:
            proposal = proposals[0]
            logging.info('Got Proposal: %s' % proposal)
            return proposal
        
    return None #no proposal for this rmas_id
    
def set_ethics_approved(proposal_id):
    '''
        Attempts to set the ethics_approved flag to True for the supplied
        proposal id.
        
        If the proposal doesn't exist then this will throw a ValueError.
        
        Doing this manually looks like:
        
        curl -v -H "Accept: application/json" -H 
        "Content-type: application/json" -X PUT 
        -d ' {"proposal":{"ethics_approved":"true"}}' http://0.0.0.0:3000/proposals/1.json
    '''
    headers = {'content-type': 'application/json', 'Accept':'application/json'}
    data = json.dumps({'proposal':{'ethics_approved':True}})
    
    new_application_request = requests.put(settings.PM_API_PROPOSAL_ENDPOINT +'/' +str(proposal_id) + '.json', 
                                           data=data, 
                                           headers=headers)
    
    if new_application_request.status_code == 200: 
        logging.info('Sucesfully set the ethics_approved flag for id: %s' % str(proposal_id))
    else:
        logging.info('FAILED to set the ethics_approved flag for id: %s' % str(proposal_id))
        
        
        
        