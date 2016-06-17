
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
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "version"
})
public class Service {

    @JsonProperty("module_name")
    private String moduleName;
    @JsonProperty("version")
    private String version;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("module_name")
    public String getModuleName() {
        return moduleName;
    }

    @JsonProperty("module_name")
    public void setModuleName(String moduleName) {
        this.moduleName = moduleName;
    }

    public Service withModuleName(String moduleName) {
        this.moduleName = moduleName;
        return this;
    }

    @JsonProperty("version")
    public String getVersion() {
        return version;
    }

    @JsonProperty("version")
    public void setVersion(String version) {
        this.version = version;
    }

    public Service withVersion(String version) {
        this.version = version;
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
        return ((((((("Service"+" [moduleName=")+ moduleName)+", version=")+ version)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
