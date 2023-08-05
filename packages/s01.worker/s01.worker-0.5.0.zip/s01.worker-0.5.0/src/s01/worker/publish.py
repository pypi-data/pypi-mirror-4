###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import sys

import zope.component
from zope.publisher.interfaces import Retry
from zope.publisher.interfaces import IReRaiseException


def debug_call(obj, args):
    # The presence of this function allows us to set a pdb breakpoint
    return obj(*args)


def publish(request, handle_errors=True):
    try: # finally to clean up to_raise and close request
        to_raise = None
        while True:
            publication = request.publication
            try:
                try:
                    obj = None
                    try:
                        try:
                            # call start request
                            publication.startRequest(request)
                            request.processInputs()
                            publication.beforeTraversal(request)

                            obj = publication.getApplication(request)
                            obj = request.traverse(obj)
                            # skip after traveral call
                            #publication.afterTraversal(request, obj)

                            result = publication.callObject(request, obj)
                            response = request.response
                            if result is not response:
                                response.setResult(result)

                            publication.afterCall(request, obj)

                        except:
                            exc_info = sys.exc_info()
                            publication.handleException(
                                obj, request, exc_info, True)

                            if not handle_errors:
                                # Reraise only if there is no adapter
                                # indicating that we shouldn't
                                reraise = zope.component.queryAdapter(
                                    exc_info[1], IReRaiseException,
                                    default=None)
                                if reraise is None or reraise():
                                    raise
                    finally:
                        publication.endRequest(request, obj)

                    break # Successful.

                except Retry, retryException:
                    if request.supportsRetry():
                        # Create a copy of the request and use it.
                        newrequest = request.retry()
                        request.close()
                        request = newrequest
                    elif handle_errors:
                        # Output the original exception.
                        publication = request.publication
                        publication.handleException(
                            obj, request,
                            retryException.getOriginalException(), False)
                        break
                    else:
                        to_raise = retryException.getOriginalException()
                        if to_raise is None:
                            # There is no original exception inside
                            # the Retry, so just reraise it.
                            raise
                        break

            except:
                # Bad exception handler or retry method.
                # Re-raise after outputting the response.
                if handle_errors:
                    request.response.internalError()
                    to_raise = sys.exc_info()
                    break
                else:
                    raise

        response = request.response
        if to_raise is not None:
            raise to_raise[0], to_raise[1], to_raise[2]

    finally:
        to_raise = None  # Avoid circ. ref.
        request.close()  # Close database connections, etc.

    # Return the request, since it might be a different object than the one
    # that was passed in.
    return request
