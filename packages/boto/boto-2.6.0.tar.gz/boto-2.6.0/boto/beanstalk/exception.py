import sys
import json
from boto.exception import BotoServerError


def simple(e):
    err = json.loads(e.error_message)
    code = err['Error']['Code']

    try:
        # Dynamically get the error class.
        simple_e = getattr(sys.modules[__name__], code)(e, err)
    except AttributeError:
        # Return original exception on failure.
        return e

    return simple_e


class SimpleException(BotoServerError):
    def __init__(self, e, err):
        super(SimpleException, self).__init__(e.status, e.reason, e.body)
        self.body = e.error_message
        self.request_id = err['RequestId']
        self.error_code = err['Error']['Code']
        self.error_message = err['Error']['Message']

    def __repr__(self):
        return self.__class__.__name__ + ': ' + self.error_message
    def __str__(self):
        return self.__class__.__name__ + ': ' + self.error_message


class ValidationError(SimpleException): pass

# Common beanstalk exceptions.
class IncompleteSignature(SimpleException): pass
class InternalFailure(SimpleException): pass
class InvalidAction(SimpleException): pass
class InvalidClientTokenId(SimpleException): pass
class InvalidParameterCombination(SimpleException): pass
class InvalidParameterValue(SimpleException): pass
class InvalidQueryParameter(SimpleException): pass
class MalformedQueryString(SimpleException): pass
class MissingAction(SimpleException): pass
class MissingAuthenticationToken(SimpleException): pass
class MissingParameter(SimpleException): pass
class OptInRequired(SimpleException): pass
class RequestExpired(SimpleException): pass
class ServiceUnavailable(SimpleException): pass
class Throttling(SimpleException): pass


# Action specific exceptions.
class TooManyApplications(SimpleException): pass
class InsufficientPrivileges(SimpleException): pass
class S3LocationNotInServiceRegion(SimpleException): pass
class TooManyApplicationVersions(SimpleException): pass
class TooManyConfigurationTemplates(SimpleException): pass
class TooManyEnvironments(SimpleException): pass
class S3SubscriptionRequired(SimpleException): pass
class TooManyBuckets(SimpleException): pass
class OperationInProgress(SimpleException): pass
class SourceBundleDeletion(SimpleException): pass
