
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
 * <p>Original spec-file type: ConsoleLog</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "stdout",
    "stderr"
})
public class ConsoleLog {

    @JsonProperty("stdout")
    private String stdout;
    @JsonProperty("stderr")
    private String stderr;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("stdout")
    public String getStdout() {
        return stdout;
    }

    @JsonProperty("stdout")
    public void setStdout(String stdout) {
        this.stdout = stdout;
    }

    public ConsoleLog withStdout(String stdout) {
        this.stdout = stdout;
        return this;
    }

    @JsonProperty("stderr")
    public String getStderr() {
        return stderr;
    }

    @JsonProperty("stderr")
    public void setStderr(String stderr) {
        this.stderr = stderr;
    }

    public ConsoleLog withStderr(String stderr) {
        this.stderr = stderr;
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
        return ((((((("ConsoleLog"+" [stdout=")+ stdout)+", stderr=")+ stderr)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
