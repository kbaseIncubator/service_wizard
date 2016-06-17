
package us.kbase.servicewizard;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: ServiceLog</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "instance_id",
    "log"
})
public class ServiceLog {

    @JsonProperty("instance_id")
    private java.lang.String instanceId;
    @JsonProperty("log")
    private List<String> log;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("instance_id")
    public java.lang.String getInstanceId() {
        return instanceId;
    }

    @JsonProperty("instance_id")
    public void setInstanceId(java.lang.String instanceId) {
        this.instanceId = instanceId;
    }

    public ServiceLog withInstanceId(java.lang.String instanceId) {
        this.instanceId = instanceId;
        return this;
    }

    @JsonProperty("log")
    public List<String> getLog() {
        return log;
    }

    @JsonProperty("log")
    public void setLog(List<String> log) {
        this.log = log;
    }

    public ServiceLog withLog(List<String> log) {
        this.log = log;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((("ServiceLog"+" [instanceId=")+ instanceId)+", log=")+ log)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
