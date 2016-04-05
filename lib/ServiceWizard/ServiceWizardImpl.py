#BEGIN_HEADER
#END_HEADER


class ServiceWizard:
    '''
    Module Name:
    ServiceWizard

    Module Description:
    
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        #END_CONSTRUCTOR
        pass

    def start_service(self, ctx, service):
        # ctx is the context object
        #BEGIN start_service
        #END start_service
        pass

    def stop_service(self, ctx, service):
        # ctx is the context object
        #BEGIN stop_service
        #END stop_service
        pass

    def pause_service(self, ctx, service):
        # ctx is the context object
        #BEGIN pause_service
        #END pause_service
        pass

    def list_service_status(self, ctx, params):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN list_service_status
        #END list_service_status

        # At some point might do deeper type checking...
        if not isinstance(returnVal, list):
            raise ValueError('Method list_service_status return value ' +
                             'returnVal is not type list as required.')
        # return the results
        return [returnVal]

    def get_service_status(self, ctx, service):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN get_service_status
        #END get_service_status

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method get_service_status return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]
