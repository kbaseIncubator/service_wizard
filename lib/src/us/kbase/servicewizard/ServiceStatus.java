
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
 * <p>Original spec-file type: ServiceStatus</p>
 * <pre>
 * version is the semantic version of the module
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "version",
    "git_commit_hash",
    "release_tags",
    "hash",
    "url",
    "node",
    "up",
    "status",
    "health",
    "last_request_timestamp"
})
public class ServiceStatus {

    @JsonProperty("module_name")
    private java.lang.String moduleName;
    @JsonProperty("version")
    private java.lang.String version;
    @JsonProperty("git_commit_hash")
    private java.lang.String gitCommitHash;
    @JsonProperty("release_tags")
    private List<String> releaseTags;
    @JsonProperty("hash")
    private java.lang.String hash;
    @JsonProperty("url")
    private java.lang.String url;
    @JsonProperty("node")
    private java.lang.String node;
    @JsonProperty("up")
    private Long up;
    @JsonProperty("status")
    private java.lang.String status;
    @JsonProperty("health")
    private java.lang.String health;
    @JsonProperty("last_request_timestamp")
    private java.lang.String lastRequestTimestamp;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("module_name")
    public java.lang.String getModuleName() {
        return moduleName;
    }

    @JsonProperty("module_name")
    public void setModuleName(java.lang.String moduleName) {
        this.moduleName = moduleName;
    }

    public ServiceStatus withModuleName(java.lang.String moduleName) {
        this.moduleName = moduleName;
        return this;
    }

    @JsonProperty("version")
    public java.lang.String getVersion() {
        return version;
    }

    @JsonProperty("version")
    public void setVersion(java.lang.String version) {
        this.version = version;
    }

    public ServiceStatus withVersion(java.lang.String version) {
        this.version = version;
        return this;
    }

    @JsonProperty("git_commit_hash")
    public java.lang.String getGitCommitHash() {
        return gitCommitHash;
    }

    @JsonProperty("git_commit_hash")
    public void setGitCommitHash(java.lang.String gitCommitHash) {
        this.gitCommitHash = gitCommitHash;
    }

    public ServiceStatus withGitCommitHash(java.lang.String gitCommitHash) {
        this.gitCommitHash = gitCommitHash;
        return this;
    }

    @JsonProperty("release_tags")
    public List<String> getReleaseTags() {
        return releaseTags;
    }

    @JsonProperty("release_tags")
    public void setReleaseTags(List<String> releaseTags) {
        this.releaseTags = releaseTags;
    }

    public ServiceStatus withReleaseTags(List<String> releaseTags) {
        this.releaseTags = releaseTags;
        return this;
    }

    @JsonProperty("hash")
    public java.lang.String getHash() {
        return hash;
    }

    @JsonProperty("hash")
    public void setHash(java.lang.String hash) {
        this.hash = hash;
    }

    public ServiceStatus withHash(java.lang.String hash) {
        this.hash = hash;
        return this;
    }

    @JsonProperty("url")
    public java.lang.String getUrl() {
        return url;
    }

    @JsonProperty("url")
    public void setUrl(java.lang.String url) {
        this.url = url;
    }

    public ServiceStatus withUrl(java.lang.String url) {
        this.url = url;
        return this;
    }

    @JsonProperty("node")
    public java.lang.String getNode() {
        return node;
    }

    @JsonProperty("node")
    public void setNode(java.lang.String node) {
        this.node = node;
    }

    public ServiceStatus withNode(java.lang.String node) {
        this.node = node;
        return this;
    }

    @JsonProperty("up")
    public Long getUp() {
        return up;
    }

    @JsonProperty("up")
    public void setUp(Long up) {
        this.up = up;
    }

    public ServiceStatus withUp(Long up) {
        this.up = up;
        return this;
    }

    @JsonProperty("status")
    public java.lang.String getStatus() {
        return status;
    }

    @JsonProperty("status")
    public void setStatus(java.lang.String status) {
        this.status = status;
    }

    public ServiceStatus withStatus(java.lang.String status) {
        this.status = status;
        return this;
    }

    @JsonProperty("health")
    public java.lang.String getHealth() {
        return health;
    }

    @JsonProperty("health")
    public void setHealth(java.lang.String health) {
        this.health = health;
    }

    public ServiceStatus withHealth(java.lang.String health) {
        this.health = health;
        return this;
    }

    @JsonProperty("last_request_timestamp")
    public java.lang.String getLastRequestTimestamp() {
        return lastRequestTimestamp;
    }

    @JsonProperty("last_request_timestamp")
    public void setLastRequestTimestamp(java.lang.String lastRequestTimestamp) {
        this.lastRequestTimestamp = lastRequestTimestamp;
    }

    public ServiceStatus withLastRequestTimestamp(java.lang.String lastRequestTimestamp) {
        this.lastRequestTimestamp = lastRequestTimestamp;
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
        return ((((((((((((((((((((((((("ServiceStatus"+" [moduleName=")+ moduleName)+", version=")+ version)+", gitCommitHash=")+ gitCommitHash)+", releaseTags=")+ releaseTags)+", hash=")+ hash)+", url=")+ url)+", node=")+ node)+", up=")+ up)+", status=")+ status)+", health=")+ health)+", lastRequestTimestamp=")+ lastRequestTimestamp)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
