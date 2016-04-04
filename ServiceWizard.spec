

module ServiceWizard {
    

    typedef structure {
        string module_name;
        string semantic_version;
        string hash;
    } Service;


    typedef structure {
        string module_name;

        string semantic_version;
        string hash;

        string url;
        string node;

        boolean up;
        string status;
        string health;
        string last_request_timestamp;
    } ServiceStatus;


    funcdef start(Service service) returns () authentication required;
    funcdef stop(Service service) returns () authentication required;
    funcdef pause(Service service) returns () authentication required;



    typedef structure {
        boolean is_up;
        list <string> module_names;
    } ListServiceStatusParams;

    funcdef list_service_status(ListServiceStatusParams params) returns (list<ServiceStatus>);


    funcdef get_service_status(Service service) returns (ServiceStatus);






};
