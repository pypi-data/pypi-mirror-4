from rmas_pm_adapter.pm_api import set_ethics_approved, get_proposal_for_rmas_id
import logging
def parse_ethics_approved_payload(payload):
    '''
    A sample payload looks like:

    <CERIF
        xmlns="urn:xmlns:org:eurocris:cerif-1.4-0" 
        xsi:schemaLocation="urn:xmlns:org:eurocris:cerif-1.4-0http://www.eurocris.org/Uploads/Web%%20pages/CERIF-1.4/CERIF_1.4_0.xsd" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        release="1.4"
        date="2012-04-12"
        sourceDatabase="OpenEthics">
        
        <cfProj>
            <cfProjId>%(rmas_id)s</cfProjId> <!-- RMAS identifier --> 
            <cfProj_Class>
                <cfClassId>11111-11111-11111-11111</cfClassId><!-- this is the uuid for the status "Ethics Approved" -->
                <cfClassSchemeId>759af93a-34ae-11e1-b86c-0800200c9a66</cfClassSchemeId><!--this is the uuid for the CERIF scheme "Activity Statuses"-->
                <cfStartDate>%(start)s</cfStartDate>
                <cfEndDate>%(end)s</cfEndDate>
            </cfProj_Class>
        </cfProj>
    </CERIF> 

    At this stage we are only interested in getting the project id.... we could
    check to make sure that there is a node with the ethics_approved status
    but by virtue of the fact that this is an ethics_approved message we will
    trust that the sender has sent it legitimately.
    
    Returns:
    
    The proposal id.
    '''
    
    projid = payload.xpath('p:cfProj/p:cfProjId', 
                              namespaces={'p':'urn:xmlns:org:eurocris:cerif-1.4-0'}).pop().text
    return projid

def handle_event(payload):
    '''
        Handles the ethics_approved event.
        
        It will attempt to set the ethics_approved flag for the given proposal
        to True
    '''
    
    #parse the payload
    proposal_id = parse_ethics_approved_payload(payload)
    
    proposal = get_proposal_for_rmas_id(proposal_id)
    try:
        #update the proposal to set ethics_approved as true
        set_ethics_approved(proposal['id'])
    except ValueError as e:
        logging.info(e)
        