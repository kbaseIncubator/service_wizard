

module ServiceWizard {
    
    typedef int boolean;

    /* Get the version of the deployed service wizard endpoint. */
    funcdef version() returns (string version);

    /*
        version - unified version field including semantic version, git commit hash and
            case of last version of tag (dev/beta/release).
    */
    typedef structure {
        string module_name;
        string version;
    } Service;

    /* version is the semantic version of the module */
    typedef structure {
        string module_name;
        string version;
        string git_commit_hash;

        list <string> release_tags;

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

    /*
        For a given service, check on the status.  If the service is down, attempt to restart.
    */
    funcdef get_service_status(Service service) returns (ServiceStatus);






};
