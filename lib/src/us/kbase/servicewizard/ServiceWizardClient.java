package us.kbase.servicewizard;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import us.kbase.auth.AuthToken;
import us.kbase.common.service.JsonClientCaller;
import us.kbase.common.service.JsonClientException;
import us.kbase.common.service.RpcContext;
import us.kbase.common.service.UnauthorizedException;

/**
 * <p>Original spec-file module name: ServiceWizard</p>
 * <pre>
 * </pre>
 */
public class ServiceWizardClient {
    private JsonClientCaller caller;


    /** Constructs a client with a custom URL and no user credentials.
     * @param url the URL of the service.
     */
    public ServiceWizardClient(URL url) {
        caller = new JsonClientCaller(url);
    }
    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param token the user's authorization token.
     * @throws UnauthorizedException if the token is not valid.
     * @throws IOException if an IOException occurs when checking the token's
     * validity.
     */
    public ServiceWizardClient(URL url, AuthToken token) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, token);
    }

    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param user the user name.
     * @param password the password for the user name.
     * @throws UnauthorizedException if the credentials are not valid.
     * @throws IOException if an IOException occurs when checking the user's
     * credentials.
     */
    public ServiceWizardClient(URL url, String user, String password) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, user, password);
    }

    /** Get the token this client uses to communicate with the server.
     * @return the authorization token.
     */
    public AuthToken getToken() {
        return caller.getToken();
    }

    /** Get the URL of the service with which this client communicates.
     * @return the service URL.
     */
    public URL getURL() {
        return caller.getURL();
    }

    /** Set the timeout between establishing a connection to a server and
     * receiving a response. A value of zero or null implies no timeout.
     * @param milliseconds the milliseconds to wait before timing out when
     * attempting to read from a server.
     */
    public void setConnectionReadTimeOut(Integer milliseconds) {
        this.caller.setConnectionReadTimeOut(milliseconds);
    }

    /** Check if this client allows insecure http (vs https) connections.
     * @return true if insecure connections are allowed.
     */
    public boolean isInsecureHttpConnectionAllowed() {
        return caller.isInsecureHttpConnectionAllowed();
    }

    /** Deprecated. Use isInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public boolean isAuthAllowedForHttp() {
        return caller.isAuthAllowedForHttp();
    }

    /** Set whether insecure http (vs https) connections should be allowed by
     * this client.
     * @param allowed true to allow insecure connections. Default false
     */
    public void setIsInsecureHttpConnectionAllowed(boolean allowed) {
        caller.setInsecureHttpConnectionAllowed(allowed);
    }

    /** Deprecated. Use setIsInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public void setAuthAllowedForHttp(boolean isAuthAllowedForHttp) {
        caller.setAuthAllowedForHttp(isAuthAllowedForHttp);
    }

    /** Set whether all SSL certificates, including self-signed certificates,
     * should be trusted.
     * @param trustAll true to trust all certificates. Default false.
     */
    public void setAllSSLCertificatesTrusted(final boolean trustAll) {
        caller.setAllSSLCertificatesTrusted(trustAll);
    }
    
    /** Check if this client trusts all SSL certificates, including
     * self-signed certificates.
     * @return true if all certificates are trusted.
     */
    public boolean isAllSSLCertificatesTrusted() {
        return caller.isAllSSLCertificatesTrusted();
    }
    /** Sets streaming mode on. In this case, the data will be streamed to
     * the server in chunks as it is read from disk rather than buffered in
     * memory. Many servers are not compatible with this feature.
     * @param streamRequest true to set streaming mode on, false otherwise.
     */
    public void setStreamingModeOn(boolean streamRequest) {
        caller.setStreamingModeOn(streamRequest);
    }

    /** Returns true if streaming mode is on.
     * @return true if streaming mode is on.
     */
    public boolean isStreamingModeOn() {
        return caller.isStreamingModeOn();
    }

    public void _setFileForNextRpcResponse(File f) {
        caller.setFileForNextRpcResponse(f);
    }

    /**
     * <p>Original spec-file function name: version</p>
     * <pre>
     * Get the version of the deployed service wizard endpoint.
     * </pre>
     * @return   parameter "version" of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public String version(RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        TypeReference<List<String>> retType = new TypeReference<List<String>>() {};
        List<String> res = caller.jsonrpcCall("ServiceWizard.version", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: start</p>
     * <pre>
     * Try to start the specified service; this will generate an error if the
     * specified service cannot be started.  If the startup did not give any
     * errors, then the status of the running service is provided.
     * </pre>
     * @param   service   instance of type {@link us.kbase.servicewizard.Service Service}
     * @return   parameter "status" of type {@link us.kbase.servicewizard.ServiceStatus ServiceStatus}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ServiceStatus start(Service service, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(service);
        TypeReference<List<ServiceStatus>> retType = new TypeReference<List<ServiceStatus>>() {};
        List<ServiceStatus> res = caller.jsonrpcCall("ServiceWizard.start", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: stop</p>
     * <pre>
     * Try to stop the specified service; this will generate an error if the
     * specified service cannot be stopped.  If the stop did not give any
     * errors, then the status of the stopped service is provided.
     * </pre>
     * @param   service   instance of type {@link us.kbase.servicewizard.Service Service}
     * @return   parameter "status" of type {@link us.kbase.servicewizard.ServiceStatus ServiceStatus}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ServiceStatus stop(Service service, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(service);
        TypeReference<List<ServiceStatus>> retType = new TypeReference<List<ServiceStatus>>() {};
        List<ServiceStatus> res = caller.jsonrpcCall("ServiceWizard.stop", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: list_service_status</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.servicewizard.ListServiceStatusParams ListServiceStatusParams}
     * @return   instance of list of type {@link us.kbase.servicewizard.ServiceStatus ServiceStatus}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<ServiceStatus> listServiceStatus(ListServiceStatusParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<List<ServiceStatus>>> retType = new TypeReference<List<List<ServiceStatus>>>() {};
        List<List<ServiceStatus>> res = caller.jsonrpcCall("ServiceWizard.list_service_status", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_service_status</p>
     * <pre>
     * For a given service, check on the status.  If the service is down or
     * not running, this function will attempt to start or restart the
     * service once, then return the status.
     * This function will throw an error if the specified service cannot be
     * found or encountered errors on startup.
     * </pre>
     * @param   service   instance of type {@link us.kbase.servicewizard.Service Service}
     * @return   parameter "status" of type {@link us.kbase.servicewizard.ServiceStatus ServiceStatus}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ServiceStatus getServiceStatus(Service service, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(service);
        TypeReference<List<ServiceStatus>> retType = new TypeReference<List<ServiceStatus>>() {};
        List<ServiceStatus> res = caller.jsonrpcCall("ServiceWizard.get_service_status", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_service_status_without_restart</p>
     * <pre>
     * </pre>
     * @param   service   instance of type {@link us.kbase.servicewizard.Service Service}
     * @return   parameter "status" of type {@link us.kbase.servicewizard.ServiceStatus ServiceStatus}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ServiceStatus getServiceStatusWithoutRestart(Service service, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(service);
        TypeReference<List<ServiceStatus>> retType = new TypeReference<List<ServiceStatus>>() {};
        List<ServiceStatus> res = caller.jsonrpcCall("ServiceWizard.get_service_status_without_restart", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_service_log</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.servicewizard.GetServiceLogParams GetServiceLogParams}
     * @return   parameter "logs" of list of type {@link us.kbase.servicewizard.ServiceLog ServiceLog}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<ServiceLog> getServiceLog(GetServiceLogParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<List<ServiceLog>>> retType = new TypeReference<List<List<ServiceLog>>>() {};
        List<List<ServiceLog>> res = caller.jsonrpcCall("ServiceWizard.get_service_log", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_service_log_web_socket</p>
     * <pre>
     * returns connection info for a websocket connection to get realtime service logs
     * </pre>
     * @param   params   instance of type {@link us.kbase.servicewizard.GetServiceLogParams GetServiceLogParams}
     * @return   parameter "sockets" of list of type {@link us.kbase.servicewizard.ServiceLogWebSocket ServiceLogWebSocket}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<ServiceLogWebSocket> getServiceLogWebSocket(GetServiceLogParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<List<ServiceLogWebSocket>>> retType = new TypeReference<List<List<ServiceLogWebSocket>>>() {};
        List<List<ServiceLogWebSocket>> res = caller.jsonrpcCall("ServiceWizard.get_service_log_web_socket", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }
}
