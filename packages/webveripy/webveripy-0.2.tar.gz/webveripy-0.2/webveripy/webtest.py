
import sys
import unittest
import warnings
import httplib2
import types
from functools import wraps
from unittest.case import SkipTest, _ExpectedFailure, _UnexpectedSuccess

def failfast(method):
    @wraps(method)
    def inner(self, *args, **kw):
        if getattr(self, 'failfast', False):
            self.stop()
        return method(self, *args, **kw)
    return inner

@failfast
def addError(self, test, err, httpCallHistory):
    """Called when an error has occurred. 'err' is a tuple of values as
    returned by sys.exc_info().
    """
    print "Calling my addError()"
    message = self.addHistoryToExcInfo(self._exc_info_to_string(err, test), httpCallHistory)
    self.errors.append((test, message))
    self._mirrorOutput = True

@failfast
def addFailure(self, test, err, httpCallHistory):
    """Called when an error has occurred. 'err' is a tuple of values as
    returned by sys.exc_info()."""
    message = self.addHistoryToExcInfo(self._exc_info_to_string(err, test), httpCallHistory)
    self.failures.append((test, message))
    self._mirrorOutput = True
        
def addHistoryToExcInfo(self, excInfo, history):
    historyDumps = []
    for car in history:
        historyDumps.append(car.dump())
    return excInfo.join(historyDumps)


class Webtest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self.history = []
        self.httpClient = httplib2.Http(".cache")

    def request(self, uri, method="GET", body=None, headers=None, redirections=5, connection_type=None):
        callInfo = {'method':method, 'uri':uri, 'headers':headers}
        responseInfo, responseBody = self.httpClient.request(uri, method, body, headers, redirections, connection_type)
        car = HTTPCallAndResponse(callInfo, body, responseInfo, responseBody)
        self.history.append(car)
        return car
    
    def clearHistory(self):
        del self.history[:]
        
    def run(self, result=None):
        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()

        ae = types.MethodType(addError, result, unittest.TestResult)
        af = types.MethodType(addFailure, result, unittest.TestResult)
        ah = types.MethodType(addHistoryToExcInfo, result, unittest.TestResult)
        result.addError = ae
        result.addFailure = af
        result.addHistoryToExcInfo = ah
        
        self._resultForDoCleanups = result
        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)
        if (getattr(self.__class__, "__unittest_skip__", False) or
            getattr(testMethod, "__unittest_skip__", False)):
            # If the class or method was skipped.
            try:
                skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                            or getattr(testMethod, '__unittest_skip_why__', ''))
                self._addSkip(result, skip_why)
            finally:
                result.stopTest(self)
            return
        try:
            success = False
            try:
                self.setUp()
            except SkipTest as e:
                self._addSkip(result, str(e))
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, sys.exc_info(), self.history)
            else:
                try:
                    testMethod()
                except KeyboardInterrupt:
                    raise
                except self.failureException:
                    result.addFailure(self, sys.exc_info(), self.history)
                except _ExpectedFailure as e:
                    addExpectedFailure = getattr(result, 'addExpectedFailure', None)
                    if addExpectedFailure is not None:
                        addExpectedFailure(self, e.exc_info)
                    else:
                        warnings.warn("TestResult has no addExpectedFailure method, reporting as passes",
                                      RuntimeWarning)
                        result.addSuccess(self)
                except _UnexpectedSuccess:
                    addUnexpectedSuccess = getattr(result, 'addUnexpectedSuccess', None)
                    if addUnexpectedSuccess is not None:
                        addUnexpectedSuccess(self)
                    else:
                        warnings.warn("TestResult has no addUnexpectedSuccess method, reporting as failures",
                                      RuntimeWarning)
                        result.addFailure(self, sys.exc_info())
                except SkipTest as e:
                    self._addSkip(result, str(e))
                except:
                    result.addError(self, sys.exc_info())
                else:
                    success = True

                try:
                    self.tearDown()
                except KeyboardInterrupt:
                    raise
                except:
                    result.addError(self, sys.exc_info())
                    success = False

            cleanUpSuccess = self.doCleanups()
            success = success and cleanUpSuccess
            if success:
                result.addSuccess(self)
        finally:
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()


class HTTPCallAndResponse():
    def __init__(self, callInfo, callBody, responseInfo, responseBody):
        self.callInfo = callInfo
        if callBody is not None:
            self.callBody = callBody
        else: self.callBody = "No request body sent\n"
        self.responseInfo = responseInfo
        self.responseHeaders = self.resolveResponseHeaders()
        self.responseBody = responseBody
        
    def dump(self):
        lines = ["*** HTTP Call Info ***\n"]
        uriNorm = httplib2.urlnorm(self.callInfo['uri'])
        lines.append("{0} {1} {2}/1.1\n".format(self.callInfo['method'], uriNorm[2], uriNorm[0].upper()))
        if self.callInfo['headers'] is not None:
            for chName, chValue in self.callInfo['headers']:
                lines.append("{0} : {1}\n".format(chName, chValue))
        else: lines.append("No request headers sent")
            
        lines.append("\n")    
        lines.append(self.callBody)
        
        lines.append("\n*** HTTP Response Info ***\n")
        lines.append("HTTP/1.1 {0} {1}\n".format(self.responseInfo.status, self.responseInfo.reason))
        if self.responseHeaders is not None:
            for rhName, rhValue in self.responseHeaders.iteritems():
                lines.append("{0} : {1}\n".format(rhName, rhValue))
            
        lines.append("\n")    
        lines.append(self.responseBody)
        
        return ''.join(lines)
         
    def resolveResponseHeaders(self):
        headers = {}
        for key, value in self.responseInfo.iteritems():
            if key not in ["fromcache", "version", "status", "reason", "previous"]:
                headers[key.upper()] = value
        return headers
        
        
        
