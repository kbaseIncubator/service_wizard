
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
 * <p>Original spec-file type: ListServiceStatusParams</p>
 * <pre>
 * not yet implemented
 * funcdef pause(Service service) returns (ServiceStatus status);
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "is_up",
    "module_names"
})
public class ListServiceStatusParams {

    @JsonProperty("is_up")
    private Long isUp;
    @JsonProperty("module_names")
    private List<String> moduleNames;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("is_up")
    public Long getIsUp() {
        return isUp;
    }

    @JsonProperty("is_up")
    public void setIsUp(Long isUp) {
        this.isUp = isUp;
    }

    public ListServiceStatusParams withIsUp(Long isUp) {
        this.isUp = isUp;
        return this;
    }

    @JsonProperty("module_names")
    public List<String> getModuleNames() {
        return moduleNames;
    }

    @JsonProperty("module_names")
    public void setModuleNames(List<String> moduleNames) {
        this.moduleNames = moduleNames;
    }

    public ListServiceStatusParams withModuleNames(List<String> moduleNames) {
        this.moduleNames = moduleNames;
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
        return ((((((("ListServiceStatusParams"+" [isUp=")+ isUp)+", moduleNames=")+ moduleNames)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
