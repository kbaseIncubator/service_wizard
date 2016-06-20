
package us.kbase.servicewizard;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: ServiceLogWebSocket</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "instance_id",
    "socket_url"
})
public class ServiceLogWebSocket {

    @JsonProperty("instance_id")
    private String instanceId;
    @JsonProperty("socket_url")
    private String socketUrl;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("instance_id")
    public String getInstanceId() {
        return instanceId;
    }

    @JsonProperty("instance_id")
    public void setInstanceId(String instanceId) {
        this.instanceId = instanceId;
    }

    public ServiceLogWebSocket withInstanceId(String instanceId) {
        this.instanceId = instanceId;
        return this;
    }

    @JsonProperty("socket_url")
    public String getSocketUrl() {
        return socketUrl;
    }

    @JsonProperty("socket_url")
    public void setSocketUrl(String socketUrl) {
        this.socketUrl = socketUrl;
    }

    public ServiceLogWebSocket withSocketUrl(String socketUrl) {
        this.socketUrl = socketUrl;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((("ServiceLogWebSocket"+" [instanceId=")+ instanceId)+", socketUrl=")+ socketUrl)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
