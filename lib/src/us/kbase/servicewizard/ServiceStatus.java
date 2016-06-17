
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
 * module_name     - name of the service module
 * version         - semantic version number of the service module
 * git_commit_hash - git commit hash of the service module
 * release_tags    - list of release tags currently for this service module (dev/beta/release)
 * url             - the url of the service
 * up              - 1 if the service is up, 0 otherwise
 * status          - status of the service as reported by rancher
 * health          - health of the service as reported by Rancher
 * TODO: 
 *   add something to return: string last_request_timestamp;
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
    "up",
    "status",
    "health"
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
    @JsonProperty("up")
    private Long up;
    @JsonProperty("status")
    private java.lang.String status;
    @JsonProperty("health")
    private java.lang.String health;
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
        return ((((((((((((((((((((("ServiceStatus"+" [moduleName=")+ moduleName)+", version=")+ version)+", gitCommitHash=")+ gitCommitHash)+", releaseTags=")+ releaseTags)+", hash=")+ hash)+", url=")+ url)+", up=")+ up)+", status=")+ status)+", health=")+ health)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
