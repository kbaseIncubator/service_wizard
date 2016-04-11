package us.kbase.clients;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.charset.Charset;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.cert.X509Certificate;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

import us.kbase.auth.AuthConfig;
import us.kbase.auth.AuthException;
import us.kbase.auth.AuthService;
import us.kbase.auth.AuthToken;
import us.kbase.auth.ConfigurableAuthService;
import us.kbase.auth.TokenExpiredException;
import us.kbase.common.service.JacksonTupleModule;
import us.kbase.common.service.JsonClientException;
import us.kbase.common.service.JsonTokenStream;
import us.kbase.common.service.RpcContext;
import us.kbase.common.service.ServerException;
import us.kbase.common.service.UObject;
import us.kbase.common.service.UnauthorizedException;

import com.fasterxml.jackson.core.JsonEncoding;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

public class GenericClient {
    
    public final URL serviceLookupUrl;
    private ObjectMapper mapper;
    private String user = null;
    private char[] password = null;
    private AuthToken accessToken = null;
    private boolean allowInsecureHttp = false;
    private boolean trustAllCerts = false;
    private boolean streamRequest = false;
    private Integer connectionReadTimeOut = 30 * 60 * 1000;
    private File fileForNextRpcResponse = null;
    private final URL authServiceUrl;
    private boolean useUrlLookup = true;
    
    private static TrustManager[] GULLIBLE_TRUST_MGR = new TrustManager[] {
        new X509TrustManager() {
            public X509Certificate[] getAcceptedIssuers() {
                return new X509Certificate[0];
            }
            public void checkClientTrusted(X509Certificate[] certs,
                    String authType) {}
            public void checkServerTrusted(X509Certificate[] certs,
                    String authType) {}
        }
    };
        
    private static HostnameVerifier GULLIBLE_HOSTNAME_VERIFIER =
        new HostnameVerifier() {
            public boolean verify(String hostname, SSLSession session) {
                return true;
            }
    };
    
    public GenericClient(URL serviceLookupUrl) {
        this(serviceLookupUrl, (URL)null);
    }
    
    public GenericClient(URL serviceLookupUrl, URL authServiceUrl) {
        this.serviceLookupUrl = serviceLookupUrl;
        mapper = new ObjectMapper().registerModule(new JacksonTupleModule());
        this.authServiceUrl = authServiceUrl;
    }

    public GenericClient(URL serviceLookupUrl, AuthToken accessToken) throws UnauthorizedException, IOException {
        this(serviceLookupUrl, accessToken, null);
    }
    
    public GenericClient(URL serviceLookupUrl, AuthToken accessToken, URL authServiceUrl) throws UnauthorizedException, IOException {
        this(serviceLookupUrl, authServiceUrl);
        this.accessToken = accessToken;
        try {
            boolean validToken;
            if (authServiceUrl == null) {
                validToken = AuthService.validateToken(accessToken);
            } else {
                try {
                    validToken = new ConfigurableAuthService(new AuthConfig().withKBaseAuthServerURL(
                            authServiceUrl)).validateToken(accessToken);
                } catch (URISyntaxException use) {
                    throw new UnauthorizedException(
                            "Could not contact AuthService url (" + authServiceUrl + 
                            ") to validate user token: " + use.getMessage(), use);
                }
            }
            if (!validToken)
                throw new UnauthorizedException("Token validation failed");
        } catch (TokenExpiredException ex) {
            throw new UnauthorizedException("Token validation failed", ex);
        }
    }

    public GenericClient(URL serviceLookupUrl, String user, String password) throws UnauthorizedException, IOException {
        this(serviceLookupUrl, user, password, null);
    }
    
    public GenericClient(URL serviceLookupUrl, String user, String password, URL authServiceUrl) throws UnauthorizedException, IOException {
        this(serviceLookupUrl, authServiceUrl);
        this.user = user;
        this.password = password.toCharArray();
        accessToken = requestTokenFromKBase(user, this.password, authServiceUrl);
    }
    
    /** Determine whether this client allows insecure http connections
     * (vs. https).
     * @return true if insecure connections are allowed.
     */
    public boolean isInsecureHttpConnectionAllowed() {
        return allowInsecureHttp;
    }

    /** Allow insecure http connections (vs. https). In production the value
     * should always be false.
     * @param allowed - true to allow insecure connections.
     */
    public void setInsecureHttpConnectionAllowed(final boolean allowed) {
        allowInsecureHttp = allowed;
    }
    
    /** Trust all SSL certificates. By default, self-signed certificates
     * may not be trusted and an error will occur when attempting to
     * connect to such a server. 
     * In production the value should always be false.
     * 
     * @param trustAll true to trust all SSL certificates.
     */
    public void setAllSSLCertificatesTrusted(final boolean trustAll) {
        trustAllCerts = trustAll;
    }
    
    /** Determine whether this client trusts all SSL Certificates.
     * @return true if this client trusts all SSL Certificates.
     */
    public boolean isAllSSLCertificatesTrusted() {
        return trustAllCerts;
    }
    
    /** Sets streaming mode on. In this case, the data will be streamed to
     * the server in chunks as it is read from disk rather than buffered in
     * memory. Many servers are not compatible with this feature.
     * @param streamRequest true to set streaming mode on, false otherwise.
     */
    public void setStreamingModeOn(boolean streamRequest) {
        this.streamRequest = streamRequest;
    }
    
    /** Returns true if streaming mode is on.
     * @return true if streaming mode is on.
     */
    public boolean isStreamingModeOn() {
        return streamRequest;
    }
    
    public Integer getConnectionReadTimeOut() {
        return connectionReadTimeOut;
    }
    
    public void setConnectionReadTimeOut(Integer connectionReadTimeOut) {
        this.connectionReadTimeOut = connectionReadTimeOut;
    }

    public <RET> RET syncCall(String serviceMethod, String serviceVersion, TypeReference<RET> retType, 
            boolean authRequired, RpcContext context, List<Object> arg)
                    throws IOException, JsonClientException {
        String serviceModuleName = serviceMethod.split(Pattern.quote("."))[0];
        URL serviceUrl = null;
        if (useUrlLookup) {
            List<Object> serviceStatusArgs = new ArrayList<Object>();
            Map<String, String> serviceStruct = new LinkedHashMap<String, String>();
            serviceStruct.put("module_name", serviceModuleName);
            serviceStruct.put("version", serviceVersion);
            serviceStatusArgs.add(serviceStruct);
            List<Map<String, Object>> serviceState = jsonrpcCall(serviceLookupUrl, "ServiceWizard.get_service_status",
                    serviceStatusArgs, null, new TypeReference<List<Map<String, Object>>>() {}, false, null);
            serviceUrl = new URL((String)serviceState.get(0).get("url"));
        } else {
            serviceUrl = serviceLookupUrl;
        }
        return jsonrpcCall(serviceUrl, serviceMethod, arg, null, retType, authRequired, context);
    }
    
    private HttpURLConnection setupCall(URL serviceUrl, boolean authRequired) throws IOException, JsonClientException {
        HttpURLConnection conn = (HttpURLConnection) serviceUrl.openConnection();
        conn.setConnectTimeout(10000);
        if (connectionReadTimeOut != null) {
            conn.setReadTimeout(connectionReadTimeOut);
        }
        conn.setDoOutput(true);
        conn.setRequestMethod("POST");
        if (authRequired || accessToken != null) {
            if (!(conn instanceof HttpsURLConnection || allowInsecureHttp)) {
                throw new UnauthorizedException("RPC method required authentication shouldn't " +
                        "be called through unsecured http, use https instead or call " +
                        "setInsecureHttpConnectionAllowed(true) for your client");
            }
            if (accessToken == null || accessToken.isExpired()) {
                if (user == null) {
                    if (accessToken == null) {
                        throw new UnauthorizedException("RPC method requires authentication but neither " +
                                "user nor token was set");
                    } else {
                        throw new UnauthorizedException("Token is expired and can not be reloaded " +
                                "because user wasn't set");
                    }
                }
                accessToken = requestTokenFromKBase(user, password, authServiceUrl);
            }
            conn.setRequestProperty("Authorization", accessToken.toString());
        }
        if (conn instanceof HttpsURLConnection && trustAllCerts) {
            final HttpsURLConnection hc = (HttpsURLConnection) conn;
            final SSLContext sc;
            try {
                sc = SSLContext.getInstance("SSL");
            } catch (NoSuchAlgorithmException e) {
                throw new RuntimeException(
                        "Couldn't get SSLContext instance", e);
            }
            try {
                sc.init(null, GULLIBLE_TRUST_MGR, new SecureRandom());
            } catch (KeyManagementException e) {
                throw new RuntimeException(
                        "Couldn't initialize SSLContext", e);
            }
            hc.setSSLSocketFactory(sc.getSocketFactory());
            hc.setHostnameVerifier(GULLIBLE_HOSTNAME_VERIFIER);
        }
        return conn;
    }

    private static AuthToken requestTokenFromKBase(String user, char[] password, 
            URL authServiceUrl) throws UnauthorizedException, IOException {
        try {
             if (authServiceUrl == null) {
                 return AuthService.login(user, new String(password)).getToken();
             } else {
                 try {
                     return new ConfigurableAuthService(new AuthConfig().withKBaseAuthServerURL(
                             authServiceUrl)).login(user, new String(password)).getToken();
                 } catch (URISyntaxException use) {
                     throw new UnauthorizedException(
                             "Could not contact AuthService url (" + authServiceUrl + 
                             ") to get user token: " + use.getMessage(), use);
                 }
             }
        } catch (AuthException ex) {
            throw new UnauthorizedException("Could not authenticate user", ex);
        }
    }

    private <ARG, RET> RET jsonrpcCall(URL serviceUrl, String method, ARG arg, Class<RET> cls1,
            TypeReference<RET> cls2, boolean authRequired, RpcContext context)
            throws IOException, JsonClientException {
        boolean ret = cls1 != null || cls2 != null;
        HttpURLConnection conn = setupCall(serviceUrl, authRequired);
        String id = ("" + Math.random()).replace(".", "");
        if (streamRequest) {
            // Calculate content-length before
            final long size = calculateResponseLength(method, arg, id, context);
            // Set content-length
            conn.setFixedLengthStreamingMode(size);
        }
        // Write real data into http output stream
        writeRequestData(method, arg, conn.getOutputStream(), id, context);
        // Read response
        int code = conn.getResponseCode();
        conn.getResponseMessage();
        InputStream istream;
        if (code == 500) {
            istream = conn.getErrorStream();
        } else {
            istream = conn.getInputStream();
        }
        // Parse response into json
        UnclosableInputStream wrapStream = new UnclosableInputStream(istream);
        if (fileForNextRpcResponse == null) {
            JsonParser jp = mapper.getFactory().createParser(wrapStream);
            try {
                checkToken(JsonToken.START_OBJECT, jp.nextToken());
            } catch (JsonParseException ex) {
                String receivedHeadingMessage = wrapStream.getHeadingBuffer();
                if (receivedHeadingMessage.startsWith("{"))
                    throw ex;
                throw new JsonClientException("Server response is not in JSON format:\n" + 
                        receivedHeadingMessage);
            }
            Map<String, String> retError = null;
            RET res = null;
            while (jp.nextToken() != JsonToken.END_OBJECT) {
                checkToken(JsonToken.FIELD_NAME, jp.getCurrentToken());
                String fieldName = jp.getCurrentName();
                if (fieldName.equals("error")) {
                    jp.nextToken();
                    retError = jp.getCodec().readValue(jp, new TypeReference<Map<String, String>>(){});
                } else if (fieldName.equals("result")) {
                    checkFor500(code, wrapStream);
                    jp.nextToken();
                    try {
                        if (cls1 != null) {
                            res = jp.getCodec().readValue(jp, cls1);
                        } else if (cls2 != null) {
                            res = jp.getCodec().readValue(jp, cls2);
                        }
                    } catch (JsonParseException e) {
                        throw new JsonClientException(
                                "Parse error while parsing response in: " +
                                wrapStream.getHeadingBuffer(), e);
                    }
                } else {
                    jp.nextToken();
                    jp.getCodec().readValue(jp, Object.class);
                }
            }
            if (retError != null) {
                String data = retError.get("data") == null ? retError.get("error") : retError.get("data");
                throw new ServerException(retError.get("message"),
                        new Integer(retError.get("code")), retError.get("name"),
                        data);
            }
            if (res == null && ret)
                throw new ServerException("An unknown server error occured", 0, "Unknown", null);
            return res;
        } else {
            FileOutputStream fos = null;
            try {
                fos = new FileOutputStream(fileForNextRpcResponse);
                byte[] rpcBuffer = new byte[10000];
                while (true) {
                    int count = wrapStream.read(rpcBuffer);
                    if (count < 0)
                        break;
                    fos.write(rpcBuffer, 0, count);
                }
                fos.close();
                JsonTokenStream jts = new JsonTokenStream(fileForNextRpcResponse);
                Map<String, UObject> resp;
                try {
                    resp = mapper.readValue(jts, new TypeReference<Map<String, UObject>>() {});
                } catch (JsonParseException ex) {
                    String receivedHeadingMessage = wrapStream.getHeadingBuffer();
                    if (receivedHeadingMessage.startsWith("{"))
                        throw ex;
                    throw new JsonClientException("Server response is not in JSON format:\n" + 
                            receivedHeadingMessage);
                } finally {
                    jts.close();
                }
                if (resp.containsKey("error")) {
                    Map<String, String> retError = resp.get("error").asClassInstance(new TypeReference<Map<String, String>>(){});
                    String data = retError.get("data") == null ? retError.get("error") : retError.get("data");
                    throw new ServerException(retError.get("message"),
                            new Integer(retError.get("code")), retError.get("name"),
                            data);
                } if (resp.containsKey("result")) {
                    checkFor500(code, wrapStream);
                    if (cls1 != null) {
                        RET res = mapper.readValue(resp.get("result").getPlacedStream(), cls1);
                        return res;
                    } else if (cls2 != null) {
                        RET res = mapper.readValue(resp.get("result").getPlacedStream(), cls2);
                        return res;
                    } else {
                        throw new IllegalStateException("Return type is not defined");
                    }
                } else {
                    throw new ServerException("An unknown server error occured", 0, "Unknown", null);
                }
            } finally {
                fileForNextRpcResponse = null;
                if (fos != null)
                    try {
                        fos.close();
                    } catch (Exception ignore) {}
            }
        }
    }

    private <ARG> long calculateResponseLength(String method, ARG arg,
            String id, RpcContext context) throws IOException {
        final long[] sizeWrapper = new long[] {0};
        OutputStream os = new OutputStream() {
            @Override
            public void write(int b) {sizeWrapper[0]++;}
            @Override
            public void write(byte[] b) {sizeWrapper[0] += b.length;}
            @Override
            public void write(byte[] b, int o, int l) {sizeWrapper[0] += l;}
        };
        writeRequestData(method, arg, os, id, context);
        return sizeWrapper[0];
    }

    private static void checkFor500(int code, UnclosableInputStream wrapStream)
            throws IOException, JsonClientException {
        if (code == 500) {
            String header = wrapStream.getHeadingBuffer();
            if (header.length() > 300)
                header = header.substring(0, 300) + "...";
            throw new JsonClientException("Server response contains result but has error code 500, " +
                    "response header is:\n" + header);
        }
    }

    private static void checkToken(JsonToken expected, JsonToken actual) throws JsonClientException {
        if (expected != actual)
            throw new JsonClientException("Expected " + expected + " token but " + actual + " was occured");
    }
        
    private void writeRequestData(String method, Object arg, OutputStream os, String id, RpcContext context) 
            throws IOException {
        JsonGenerator g = mapper.getFactory().createGenerator(os, JsonEncoding.UTF8);
        g.writeStartObject();
        g.writeObjectField("params", arg);
        g.writeStringField("method", method);
        g.writeStringField("version", "1.1");
        g.writeStringField("id", id);
        if (context != null)
            g.writeObjectField("context", context);         
        g.writeEndObject();
        g.close();
        os.flush();
    }
    
    public void setFileForNextRpcResponse(File f) {
        this.fileForNextRpcResponse = f;
    }
    
    public AuthToken getToken() {
        return accessToken;
    }
    
    public URL getLookupURL() {
        return serviceLookupUrl;
    }
    
    private static class UnclosableInputStream extends InputStream {
        private InputStream inner;
        private boolean isClosed = false;
        private ByteArrayOutputStream headingBuffer = new ByteArrayOutputStream();
        
        public UnclosableInputStream(InputStream inner) {
            this.inner = inner;
        }
        
        private boolean isHeadingBufferFull() {
            return headingBuffer.size() > 10000;
        }
        
        public String getHeadingBuffer() throws IOException {
            while ((!isClosed) && (!isHeadingBufferFull()))
                read();
            return new String(headingBuffer.toByteArray(), Charset.forName("UTF-8"));
        }
        
        @Override
        public int read() throws IOException {
            if (isClosed)
                return -1;
            int ret = inner.read();
            if (ret < 0) {
                isClosed = true;
            } else if (!isHeadingBufferFull()) {
                headingBuffer.write(ret);
            }
            return ret;
        }
        
        @Override
        public int available() throws IOException {
            if (isClosed)
                return 0;
            return inner.available();
        }
        
        @Override
        public void close() throws IOException {
            isClosed = true;
        }
        
        @Override
        public synchronized void mark(int readlimit) {
            inner.mark(readlimit);
        }
        
        @Override
        public boolean markSupported() {
            return inner.markSupported();
        }
        
        @Override
        public int read(byte[] b) throws IOException {
            return read(b, 0, b.length);
        }
        
        @Override
        public int read(byte[] b, int off, int len) throws IOException {
            if (isClosed)
                return -1;
            int realLen = inner.read(b, off, len);
            if (realLen < 0) {
                isClosed = true;
            } else if (realLen > 0 && !isHeadingBufferFull()) {
                headingBuffer.write(b, off, realLen);
            }
            return realLen;
        }
        
        @Override
        public synchronized void reset() throws IOException {
            if (isClosed)
                return;
            inner.reset();
        }
        
        @Override
        public long skip(long n) throws IOException {
            if (isClosed)
                return 0;
            return inner.skip(n);
        }
    }
}
