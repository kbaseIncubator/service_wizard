package Bio::KBase::ServiceWizard::Client;

use JSON::RPC::Client;
use POSIX;
use strict;
use Data::Dumper;
use URI;
use Bio::KBase::Exceptions;
my $get_time = sub { time, 0 };
eval {
    require Time::HiRes;
    $get_time = sub { Time::HiRes::gettimeofday() };
};

use Bio::KBase::AuthToken;

# Client version should match Impl version
# This is a Semantic Version number,
# http://semver.org
our $VERSION = "0.1.0";

=head1 NAME

Bio::KBase::ServiceWizard::Client

=head1 DESCRIPTION





=cut

sub new
{
    my($class, $url, @args) = @_;
    

    my $self = {
	client => Bio::KBase::ServiceWizard::Client::RpcClient->new,
	url => $url,
	headers => [],
    };

    chomp($self->{hostname} = `hostname`);
    $self->{hostname} ||= 'unknown-host';

    #
    # Set up for propagating KBRPC_TAG and KBRPC_METADATA environment variables through
    # to invoked services. If these values are not set, we create a new tag
    # and a metadata field with basic information about the invoking script.
    #
    if ($ENV{KBRPC_TAG})
    {
	$self->{kbrpc_tag} = $ENV{KBRPC_TAG};
    }
    else
    {
	my ($t, $us) = &$get_time();
	$us = sprintf("%06d", $us);
	my $ts = strftime("%Y-%m-%dT%H:%M:%S.${us}Z", gmtime $t);
	$self->{kbrpc_tag} = "C:$0:$self->{hostname}:$$:$ts";
    }
    push(@{$self->{headers}}, 'Kbrpc-Tag', $self->{kbrpc_tag});

    if ($ENV{KBRPC_METADATA})
    {
	$self->{kbrpc_metadata} = $ENV{KBRPC_METADATA};
	push(@{$self->{headers}}, 'Kbrpc-Metadata', $self->{kbrpc_metadata});
    }

    if ($ENV{KBRPC_ERROR_DEST})
    {
	$self->{kbrpc_error_dest} = $ENV{KBRPC_ERROR_DEST};
	push(@{$self->{headers}}, 'Kbrpc-Errordest', $self->{kbrpc_error_dest});
    }

    #
    # This module requires authentication.
    #
    # We create an auth token, passing through the arguments that we were (hopefully) given.

    {
	my $token = Bio::KBase::AuthToken->new(@args);
	
	if (!$token->error_message)
	{
	    $self->{token} = $token->token;
	    $self->{client}->{token} = $token->token;
	}
    }

    my $ua = $self->{client}->ua;	 
    my $timeout = $ENV{CDMI_TIMEOUT} || (30 * 60);	 
    $ua->timeout($timeout);
    bless $self, $class;
    #    $self->_validate_version();
    return $self;
}




=head2 version

  $version = $obj->version()

=over 4

=item Parameter and return types

=begin html

<pre>
$version is a string

</pre>

=end html

=begin text

$version is a string


=end text

=item Description

Get the version of the deployed service wizard endpoint.

=back

=cut

 sub version
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 0)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function version (received $n, expecting 0)");
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "ServiceWizard.version",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'version',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method version",
					    status_line => $self->{client}->status_line,
					    method_name => 'version',
				       );
    }
}
 


=head2 start

  $status = $obj->start($service)

=over 4

=item Parameter and return types

=begin html

<pre>
$service is a ServiceWizard.Service
$status is a ServiceWizard.ServiceStatus
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceStatus is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	release_tags has a value which is a reference to a list where each element is a string
	hash has a value which is a string
	url has a value which is a string
	up has a value which is a ServiceWizard.boolean
	status has a value which is a string
	health has a value which is a string
boolean is an int

</pre>

=end html

=begin text

$service is a ServiceWizard.Service
$status is a ServiceWizard.ServiceStatus
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceStatus is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	release_tags has a value which is a reference to a list where each element is a string
	hash has a value which is a string
	url has a value which is a string
	up has a value which is a ServiceWizard.boolean
	status has a value which is a string
	health has a value which is a string
boolean is an int


=end text

=item Description

Try to start the specified service; this will generate an error if the
specified service cannot be started.  If the startup did not give any
errors, then the status of the running service is provided.

=back

=cut

 sub start
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function start (received $n, expecting 1)");
    }
    {
	my($service) = @args;

	my @_bad_arguments;
        (ref($service) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"service\" (value was \"$service\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to start:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'start');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "ServiceWizard.start",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'start',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method start",
					    status_line => $self->{client}->status_line,
					    method_name => 'start',
				       );
    }
}
 


=head2 stop

  $status = $obj->stop($service)

=over 4

=item Parameter and return types

=begin html

<pre>
$service is a ServiceWizard.Service
$status is a ServiceWizard.ServiceStatus
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceStatus is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	release_tags has a value which is a reference to a list where each element is a string
	hash has a value which is a string
	url has a value which is a string
	up has a value which is a ServiceWizard.boolean
	status has a value which is a string
	health has a value which is a string
boolean is an int

</pre>

=end html

=begin text

$service is a ServiceWizard.Service
$status is a ServiceWizard.ServiceStatus
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceStatus is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	release_tags has a value which is a reference to a list where each element is a string
	hash has a value which is a string
	url has a value which is a string
	up has a value which is a ServiceWizard.boolean
	status has a value which is a string
	health has a value which is a string
boolean is an int


=end text

=item Description

Try to stop the specified service; this will generate an error if the
specified service cannot be stopped.  If the stop did not give any
errors, then the status of the stopped service is provided.

=back

=cut

 sub stop
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function stop (received $n, expecting 1)");
    }
    {
	my($service) = @args;

	my @_bad_arguments;
        (ref($service) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"service\" (value was \"$service\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to stop:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'stop');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "ServiceWizard.stop",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'stop',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method stop",
					    status_line => $self->{client}->status_line,
					    method_name => 'stop',
				       );
    }
}
 


=head2 list_service_status

  $return = $obj->list_service_status($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a ServiceWizard.ListServiceStatusParams
$return is a reference to a list where each element is a ServiceWizard.ServiceStatus
ListServiceStatusParams is a reference to a hash where the following keys are defined:
	is_up has a value which is a ServiceWizard.boolean
	module_names has a value which is a reference to a list where each element is a string
boolean is an int
ServiceStatus is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	release_tags has a value which is a reference to a list where each element is a string
	hash has a value which is a string
	url has a value which is a string
	up has a value which is a ServiceWizard.boolean
	status has a value which is a string
	health has a value which is a string

</pre>

=end html

=begin text

$params is a ServiceWizard.ListServiceStatusParams
$return is a reference to a list where each element is a ServiceWizard.ServiceStatus
ListServiceStatusParams is a reference to a hash where the following keys are defined:
	is_up has a value which is a ServiceWizard.boolean
	module_names has a value which is a reference to a list where each element is a string
boolean is an int
ServiceStatus is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	release_tags has a value which is a reference to a list where each element is a string
	hash has a value which is a string
	url has a value which is a string
	up has a value which is a ServiceWizard.boolean
	status has a value which is a string
	health has a value which is a string


=end text

=item Description



=back

=cut

 sub list_service_status
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function list_service_status (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to list_service_status:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'list_service_status');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "ServiceWizard.list_service_status",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'list_service_status',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method list_service_status",
					    status_line => $self->{client}->status_line,
					    method_name => 'list_service_status',
				       );
    }
}
 


=head2 get_service_status

  $status = $obj->get_service_status($service)

=over 4

=item Parameter and return types

=begin html

<pre>
$service is a ServiceWizard.Service
$status is a ServiceWizard.ServiceStatus
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceStatus is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	release_tags has a value which is a reference to a list where each element is a string
	hash has a value which is a string
	url has a value which is a string
	up has a value which is a ServiceWizard.boolean
	status has a value which is a string
	health has a value which is a string
boolean is an int

</pre>

=end html

=begin text

$service is a ServiceWizard.Service
$status is a ServiceWizard.ServiceStatus
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceStatus is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	release_tags has a value which is a reference to a list where each element is a string
	hash has a value which is a string
	url has a value which is a string
	up has a value which is a ServiceWizard.boolean
	status has a value which is a string
	health has a value which is a string
boolean is an int


=end text

=item Description

For a given service, check on the status.  If the service is down or
not running, this function will attempt to start or restart the
service once, then return the status.

This function will throw an error if the specified service cannot be
found or encountered errors on startup.

=back

=cut

 sub get_service_status
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_service_status (received $n, expecting 1)");
    }
    {
	my($service) = @args;

	my @_bad_arguments;
        (ref($service) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"service\" (value was \"$service\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_service_status:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_service_status');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "ServiceWizard.get_service_status",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_service_status',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_service_status",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_service_status',
				       );
    }
}
 


=head2 get_service_status_without_restart

  $status = $obj->get_service_status_without_restart($service)

=over 4

=item Parameter and return types

=begin html

<pre>
$service is a ServiceWizard.Service
$status is a ServiceWizard.ServiceStatus
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceStatus is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	release_tags has a value which is a reference to a list where each element is a string
	hash has a value which is a string
	url has a value which is a string
	up has a value which is a ServiceWizard.boolean
	status has a value which is a string
	health has a value which is a string
boolean is an int

</pre>

=end html

=begin text

$service is a ServiceWizard.Service
$status is a ServiceWizard.ServiceStatus
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceStatus is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
	git_commit_hash has a value which is a string
	release_tags has a value which is a reference to a list where each element is a string
	hash has a value which is a string
	url has a value which is a string
	up has a value which is a ServiceWizard.boolean
	status has a value which is a string
	health has a value which is a string
boolean is an int


=end text

=item Description



=back

=cut

 sub get_service_status_without_restart
{
    my($self, @args) = @_;

# Authentication: none

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_service_status_without_restart (received $n, expecting 1)");
    }
    {
	my($service) = @args;

	my @_bad_arguments;
        (ref($service) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"service\" (value was \"$service\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_service_status_without_restart:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_service_status_without_restart');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "ServiceWizard.get_service_status_without_restart",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_service_status_without_restart',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_service_status_without_restart",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_service_status_without_restart',
				       );
    }
}
 


=head2 get_service_log

  $logs = $obj->get_service_log($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a ServiceWizard.GetServiceLogParams
$logs is a reference to a list where each element is a ServiceWizard.ServiceLog
GetServiceLogParams is a reference to a hash where the following keys are defined:
	service has a value which is a ServiceWizard.Service
	instance_id has a value which is a string
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceLog is a reference to a hash where the following keys are defined:
	instance_id has a value which is a string
	log has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

$params is a ServiceWizard.GetServiceLogParams
$logs is a reference to a list where each element is a ServiceWizard.ServiceLog
GetServiceLogParams is a reference to a hash where the following keys are defined:
	service has a value which is a ServiceWizard.Service
	instance_id has a value which is a string
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceLog is a reference to a hash where the following keys are defined:
	instance_id has a value which is a string
	log has a value which is a reference to a list where each element is a string


=end text

=item Description



=back

=cut

 sub get_service_log
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_service_log (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_service_log:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_service_log');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "ServiceWizard.get_service_log",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_service_log',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_service_log",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_service_log',
				       );
    }
}
 


=head2 get_service_log_web_socket

  $sockets = $obj->get_service_log_web_socket($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a ServiceWizard.GetServiceLogParams
$sockets is a reference to a list where each element is a ServiceWizard.ServiceLogWebSocket
GetServiceLogParams is a reference to a hash where the following keys are defined:
	service has a value which is a ServiceWizard.Service
	instance_id has a value which is a string
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceLogWebSocket is a reference to a hash where the following keys are defined:
	instance_id has a value which is a string
	socket_url has a value which is a string

</pre>

=end html

=begin text

$params is a ServiceWizard.GetServiceLogParams
$sockets is a reference to a list where each element is a ServiceWizard.ServiceLogWebSocket
GetServiceLogParams is a reference to a hash where the following keys are defined:
	service has a value which is a ServiceWizard.Service
	instance_id has a value which is a string
Service is a reference to a hash where the following keys are defined:
	module_name has a value which is a string
	version has a value which is a string
ServiceLogWebSocket is a reference to a hash where the following keys are defined:
	instance_id has a value which is a string
	socket_url has a value which is a string


=end text

=item Description

returns connection info for a websocket connection to get realtime service logs

=back

=cut

 sub get_service_log_web_socket
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function get_service_log_web_socket (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to get_service_log_web_socket:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'get_service_log_web_socket');
	}
    }

    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
	method => "ServiceWizard.get_service_log_web_socket",
	params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'get_service_log_web_socket',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method get_service_log_web_socket",
					    status_line => $self->{client}->status_line,
					    method_name => 'get_service_log_web_socket',
				       );
    }
}
 
  

sub version {
    my ($self) = @_;
    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
        method => "ServiceWizard.version",
        params => [],
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(
                error => $result->error_message,
                code => $result->content->{code},
                method_name => 'get_service_log_web_socket',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method get_service_log_web_socket",
            status_line => $self->{client}->status_line,
            method_name => 'get_service_log_web_socket',
        );
    }
}

sub _validate_version {
    my ($self) = @_;
    my $svr_version = $self->version();
    my $client_version = $VERSION;
    my ($cMajor, $cMinor) = split(/\./, $client_version);
    my ($sMajor, $sMinor) = split(/\./, $svr_version);
    if ($sMajor != $cMajor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Major version numbers differ.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor < $cMinor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Client minor version greater than Server minor version.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor > $cMinor) {
        warn "New client version available for Bio::KBase::ServiceWizard::Client\n";
    }
    if ($sMajor == 0) {
        warn "Bio::KBase::ServiceWizard::Client version is $svr_version. API subject to change.\n";
    }
}

=head1 TYPES



=head2 boolean

=over 4



=item Definition

=begin html

<pre>
an int
</pre>

=end html

=begin text

an int

=end text

=back



=head2 Service

=over 4



=item Description

module_name - the name of the service module, case-insensitive
version     - specify the service version, which can be either:
                (1) full git commit hash of the module version
                (2) semantic version or semantic version specification
                    Note: semantic version lookup will only work for 
                    released versions of the module.
                (3) release tag, which is one of: dev | beta | release

This information is always fetched from the Catalog, so for more details
on specifying the version, see the Catalog documentation for the
get_module_version method.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
version has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
version has a value which is a string


=end text

=back



=head2 ServiceStatus

=over 4



=item Description

module_name     - name of the service module
version         - semantic version number of the service module
git_commit_hash - git commit hash of the service module
release_tags    - list of release tags currently for this service module (dev/beta/release)

url             - the url of the service

up              - 1 if the service is up, 0 otherwise
status          - status of the service as reported by rancher
health          - health of the service as reported by Rancher

TODO: 
  add something to return: string last_request_timestamp;


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
module_name has a value which is a string
version has a value which is a string
git_commit_hash has a value which is a string
release_tags has a value which is a reference to a list where each element is a string
hash has a value which is a string
url has a value which is a string
up has a value which is a ServiceWizard.boolean
status has a value which is a string
health has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
module_name has a value which is a string
version has a value which is a string
git_commit_hash has a value which is a string
release_tags has a value which is a reference to a list where each element is a string
hash has a value which is a string
url has a value which is a string
up has a value which is a ServiceWizard.boolean
status has a value which is a string
health has a value which is a string


=end text

=back



=head2 ListServiceStatusParams

=over 4



=item Description

not yet implemented
funcdef pause(Service service) returns (ServiceStatus status);


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
is_up has a value which is a ServiceWizard.boolean
module_names has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
is_up has a value which is a ServiceWizard.boolean
module_names has a value which is a reference to a list where each element is a string


=end text

=back



=head2 ServiceLog

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
instance_id has a value which is a string
log has a value which is a reference to a list where each element is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
instance_id has a value which is a string
log has a value which is a reference to a list where each element is a string


=end text

=back



=head2 GetServiceLogParams

=over 4



=item Description

optional instance_id to get logs for a specific instance.  Otherwise logs from all instances
are returned, TODO: add line number constraints.


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
service has a value which is a ServiceWizard.Service
instance_id has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
service has a value which is a ServiceWizard.Service
instance_id has a value which is a string


=end text

=back



=head2 ServiceLogWebSocket

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
instance_id has a value which is a string
socket_url has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
instance_id has a value which is a string
socket_url has a value which is a string


=end text

=back



=cut

package Bio::KBase::ServiceWizard::Client::RpcClient;
use base 'JSON::RPC::Client';
use POSIX;
use strict;

#
# Override JSON::RPC::Client::call because it doesn't handle error returns properly.
#

sub call {
    my ($self, $uri, $headers, $obj) = @_;
    my $result;


    {
	if ($uri =~ /\?/) {
	    $result = $self->_get($uri);
	}
	else {
	    Carp::croak "not hashref." unless (ref $obj eq 'HASH');
	    $result = $self->_post($uri, $headers, $obj);
	}

    }

    my $service = $obj->{method} =~ /^system\./ if ( $obj );

    $self->status_line($result->status_line);

    if ($result->is_success) {

        return unless($result->content); # notification?

        if ($service) {
            return JSON::RPC::ServiceObject->new($result, $self->json);
        }

        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    elsif ($result->content_type eq 'application/json')
    {
        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    else {
        return;
    }
}


sub _post {
    my ($self, $uri, $headers, $obj) = @_;
    my $json = $self->json;

    $obj->{version} ||= $self->{version} || '1.1';

    if ($obj->{version} eq '1.0') {
        delete $obj->{version};
        if (exists $obj->{id}) {
            $self->id($obj->{id}) if ($obj->{id}); # if undef, it is notification.
        }
        else {
            $obj->{id} = $self->id || ($self->id('JSON::RPC::Client'));
        }
    }
    else {
        # $obj->{id} = $self->id if (defined $self->id);
	# Assign a random number to the id if one hasn't been set
	$obj->{id} = (defined $self->id) ? $self->id : substr(rand(),2);
    }

    my $content = $json->encode($obj);

    $self->ua->post(
        $uri,
        Content_Type   => $self->{content_type},
        Content        => $content,
        Accept         => 'application/json',
	@$headers,
	($self->{token} ? (Authorization => $self->{token}) : ()),
    );
}



1;
