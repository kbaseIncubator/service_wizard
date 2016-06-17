
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
 * <p>Original spec-file type: GetServiceLogParams</p>
 * <pre>
 * optional instance_id to get logs for a specific instance.  Otherwise logs from all instances
 * are returned, TODO: add line number constraints.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "service",
    "instance_id"
})
public class GetServiceLogParams {

    /**
     * <p>Original spec-file type: Service</p>
     * <pre>
     * module_name - the name of the service module, case-insensitive
     * version     - specify the service version, which can be either:
     *                 (1) full git commit hash of the module version
     *                 (2) semantic version or semantic version specification
     *                     Note: semantic version lookup will only work for 
     *                     released versions of the module.
     *                 (3) release tag, which is one of: dev | beta | release
     * This information is always fetched from the Catalog, so for more details
     * on specifying the version, see the Catalog documentation for the
     * get_module_version method.
     * </pre>
     * 
     */
    @JsonProperty("service")
    private Service service;
    @JsonProperty("instance_id")
    private String instanceId;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    /**
     * <p>Original spec-file type: Service</p>
     * <pre>
     * module_name - the name of the service module, case-insensitive
     * version     - specify the service version, which can be either:
     *                 (1) full git commit hash of the module version
     *                 (2) semantic version or semantic version specification
     *                     Note: semantic version lookup will only work for 
     *                     released versions of the module.
     *                 (3) release tag, which is one of: dev | beta | release
     * This information is always fetched from the Catalog, so for more details
     * on specifying the version, see the Catalog documentation for the
     * get_module_version method.
     * </pre>
     * 
     */
    @JsonProperty("service")
    public Service getService() {
        return service;
    }

    /**
     * <p>Original spec-file type: Service</p>
     * <pre>
     * module_name - the name of the service module, case-insensitive
     * version     - specify the service version, which can be either:
     *                 (1) full git commit hash of the module version
     *                 (2) semantic version or semantic version specification
     *                     Note: semantic version lookup will only work for 
     *                     released versions of the module.
     *                 (3) release tag, which is one of: dev | beta | release
     * This information is always fetched from the Catalog, so for more details
     * on specifying the version, see the Catalog documentation for the
     * get_module_version method.
     * </pre>
     * 
     */
    @JsonProperty("service")
    public void setService(Service service) {
        this.service = service;
    }

    public GetServiceLogParams withService(Service service) {
        this.service = service;
        return this;
    }

    @JsonProperty("instance_id")
    public String getInstanceId() {
        return instanceId;
    }

    @JsonProperty("instance_id")
    public void setInstanceId(String instanceId) {
        this.instanceId = instanceId;
    }

    public GetServiceLogParams withInstanceId(String instanceId) {
        this.instanceId = instanceId;
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
        return ((((((("GetServiceLogParams"+" [service=")+ service)+", instanceId=")+ instanceId)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
